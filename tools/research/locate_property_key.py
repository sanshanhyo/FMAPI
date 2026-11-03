#!/usr/bin/env python3
"""Bounded offline locator for explicit 32-bit property keys in a PE image.

Original research aid for future fixture/registration work. It does not read
any process, game state, UI, or live data. It only reports where the supplied
constant bytes occur in executable, file-backed PE sections. A hit is a
candidate byte reference, not a confirmed instruction operand; disassembly is
required before any semantic conclusion.

Usage:
  python tools/research/locate_property_key.py <pe.dll> --key 0x78754F31 --key 0x3324C50
  python tools/research/locate_property_key.py <pe.dll> --keys-file keys.txt --max-candidates 128
  python tools/research/locate_property_key.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

PINNED_HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_KEYS = 64
MAX_CANDIDATES_DEFAULT = 256
MAX_OUTPUT_BYTES = 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def parse_pe(data: bytes):
    if len(data) < 0x40:
        raise ValueError("file too small for DOS header")
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if e_lfanew + 24 > len(data) or data[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        raise ValueError("PE signature")
    coff_off = e_lfanew + 4
    machine, num_sections, _t, _sp, _ns, size_opt = struct.unpack_from("<HHIIIH", data, coff_off)
    if machine not in (0x8664, 0x14C):
        raise ValueError("unsupported machine")
    if num_sections == 0 or num_sections > 96:
        raise ValueError("section count")
    opt_off = coff_off + 20
    if opt_off + size_opt > len(data):
        raise ValueError("optional header bounds")
    magic = struct.unpack_from("<H", data, opt_off)[0]
    if magic not in (0x10B, 0x20B):
        raise ValueError("optional header magic")
    if magic == 0x10B:
        nrvas_off = opt_off + 92
    else:
        nrvas_off = opt_off + 108
    if nrvas_off + 4 > len(data):
        raise ValueError("optional header truncated")
    num_rva = struct.unpack_from("<I", data, nrvas_off)[0]
    if num_rva > 16:
        raise ValueError("data directory count")
    data_dir_off = nrvas_off + 4
    exception_rva = 0
    exception_size = 0
    if num_rva >= 4:
        exception_rva, exception_size = struct.unpack_from("<II", data, data_dir_off + 3 * 8)
    sec_off = opt_off + size_opt
    sections = []
    for i in range(num_sections):
        off = sec_off + i * 40
        if off + 40 > len(data):
            raise ValueError("section header bounds")
        name_raw = data[off:off + 8]
        name = name_raw.split(b"\0", 1)[0].decode("ascii", errors="replace")
        virtual_size, virtual_address, raw_size, raw_ptr, _rel, _lin, _nrel, _nlin, characteristics = struct.unpack_from(
            "<IIIIIIHHI", data, off + 8
        )
        sections.append(
            {
                "name": name,
                "virtual_size": virtual_size,
                "virtual_address": virtual_address,
                "raw_size": raw_size,
                "raw_ptr": raw_ptr,
                "characteristics": characteristics,
            }
        )
    return sections, exception_rva, exception_size


def make_rva_to_offset(sections, data_len):
    def convert(rva):
        for s in sections:
            start = s["virtual_address"]
            size = max(s["virtual_size"], s["raw_size"])
            if start <= rva < start + size:
                delta = rva - start
                off = s["raw_ptr"] + delta
                if 0 <= off and off + 4 <= data_len and delta < s["raw_size"]:
                    return off, s
        return None, None

    return convert


def parse_pdata(data, sections, exception_rva, exception_size):
    functions = []
    if exception_rva == 0 or exception_size == 0:
        return functions
    conv = make_rva_to_offset(sections, len(data))
    off, _ = conv(exception_rva)
    if off is None:
        return functions
    end = off + exception_size
    if end > len(data):
        end = len(data)
    pos = off
    while pos + 12 <= end:
        begin, finish, _unwind = struct.unpack_from("<III", data, pos)
        if begin != 0 and finish != 0 and begin < finish:
            functions.append((begin, finish))
        pos += 12
    return functions


def containing_function(functions, rva):
    for begin, finish in functions:
        if begin <= rva < finish:
            return begin, finish
    return None, None


def parse_one_key(text):
    text = text.strip()
    if not text:
        return None
    if text.lower().startswith("0x"):
        return int(text, 16)
    try:
        return int(text, 0)
    except ValueError:
        return int(text, 10)


def parse_keys(args):
    keys = set()
    if args.key:
        for k in args.key:
            v = parse_one_key(k)
            if v is None:
                continue
            keys.add(v)
    if args.keys_file:
        text = Path(args.keys_file).read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            v = parse_one_key(line)
            if v is not None:
                keys.add(v)
    if not keys:
        raise ValueError("no keys supplied")
    if len(keys) > MAX_KEYS:
        raise ValueError(f"too many keys (max {MAX_KEYS})")
    for k in keys:
        if k < 0 or k > 0xFFFFFFFF:
            raise ValueError("key outside 32-bit range")
    return keys


def scan(data, sections, functions, keys, max_candidates):
    candidates = []
    total_found = 0
    truncated = False
    for s in sections:
        if not (s["characteristics"] & 0x20000000):
            continue
        raw_ptr = s["raw_ptr"]
        raw_size = s["raw_size"]
        va = s["virtual_address"]
        if raw_ptr + raw_size > len(data) or raw_size < 4:
            continue
        blob = data[raw_ptr:raw_ptr + raw_size]
        i = 0
        limit = len(blob) - 3
        while i < limit:
            val = struct.unpack_from("<I", blob, i)[0]
            if val in keys:
                total_found += 1
                if len(candidates) < max_candidates:
                    rva = va + i
                    fbegin, ffinish = containing_function(functions, rva)
                    candidates.append(
                        {
                            "key": f"0x{val:08X}",
                            "section": s["name"],
                            "rva": f"0x{rva:X}",
                            "fileOffset": f"0x{raw_ptr + i:X}",
                            "containingFunctionBeginRva": (f"0x{fbegin:X}" if fbegin is not None else None),
                            "containingFunctionEndRva": (f"0x{ffinish:X}" if ffinish is not None else None),
                            "inPdataFunction": fbegin is not None,
                            "candidateImmediateBytesAreInstructions": False,
                            "note": "Candidate byte occurrence; not a confirmed instruction operand until disassembled.",
                        }
                    )
                else:
                    truncated = True
            i += 1
    if total_found > len(candidates):
        truncated = True
    return candidates, total_found, truncated


def self_test():
    dos = bytearray(64)
    struct.pack_into("<I", dos, 0x3C, 64)
    pe_sig = b"PE\0\0"
    coff = struct.pack("<HHIIIHH", 0x8664, 2, 0, 0, 0, 0xF0, 0x0022)
    opt = bytearray(0xF0)
    struct.pack_into("<H", opt, 0, 0x20B)
    struct.pack_into("<I", opt, 32, 0x1000)
    struct.pack_into("<I", opt, 36, 0x200)
    struct.pack_into("<I", opt, 56, 0x3000)
    struct.pack_into("<I", opt, 60, 0x400)
    struct.pack_into("<I", opt, 108, 16)
    struct.pack_into("<I", opt, 136, 0x2000)
    struct.pack_into("<I", opt, 140, 12)
    text_hdr = struct.pack(
        "<8sIIIIIIHHI",
        b".text\0\0\0",
        0x1000, 0x1000, 0x200, 0x400, 0, 0, 0, 0, 0x60000020,
    )
    pdata_hdr = struct.pack(
        "<8sIIIIIIHHI",
        b".pdata\0\0",
        0xC, 0x2000, 0x200, 0x600, 0, 0, 0, 0, 0x40000040,
    )
    headers = bytes(dos) + pe_sig + coff + bytes(opt) + text_hdr + pdata_hdr
    headers = headers.ljust(0x400, b"\0")
    text = bytearray(0x200)
    key = 0x78754F31
    struct.pack_into("<I", text, 0, key)
    struct.pack_into("<I", text, 0x20, key)
    pdata = struct.pack("<III", 0x1000, 0x1010, 0).ljust(0x200, b"\0")
    image = headers + bytes(text) + pdata

    sections, erva, esize = parse_pe(image)
    assert erva == 0x2000 and esize == 12, (erva, esize)
    fns = parse_pdata(image, sections, erva, esize)
    assert fns == [(0x1000, 0x1010)], fns
    cands, total, trunc = scan(image, sections, fns, {key}, 10)
    assert total == 2, total
    assert len(cands) == 2
    assert cands[0]["inPdataFunction"] is True
    assert cands[1]["inPdataFunction"] is False
    b, e = containing_function(fns, 0x1005)
    assert (b, e) == (0x1000, 0x1010)
    b, e = containing_function(fns, 0x1020)
    assert (b, e) == (None, None)
    assert parse_one_key("0x78754F31") == 0x78754F31
    assert parse_one_key("123") == 123
    assert parse_keys(type("A", (), {"key": ["0x78754F31"], "keys_file": None})()) == {0x78754F31}
    print("self-test: PASS (synthetic PE parsing, pdata containment, scan, key parsing)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Bounded offline PE property-key reference locator")
    parser.add_argument("pe", nargs="?", help="PE file to inspect")
    parser.add_argument("--key", action="append", help="Explicit 32-bit property key (hex or decimal); repeatable")
    parser.add_argument("--keys-file", help="File with one key per line (# comments allowed)")
    parser.add_argument("--expected-hash", default=PINNED_HASH, help="Pinned SHA-256 of the PE (default: pinned game_plugin hash)")
    parser.add_argument("--max-candidates", type=int, default=MAX_CANDIDATES_DEFAULT, help="Total candidate cap")
    parser.add_argument("--output", help="Write JSON to this file instead of stdout")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic checks and exit")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.pe:
        parser.error("pe is required unless --self-test")
    pe_path = Path(args.pe)
    if not pe_path.is_file():
        raise SystemExit(f"file not found: {pe_path}")
    size = pe_path.stat().st_size
    if size <= 0 or size > MAX_INPUT_BYTES:
        raise SystemExit("input size out of bounds")

    expected = args.expected_hash.strip().upper()
    actual = sha256_file(pe_path)
    if actual != expected:
        raise SystemExit(f"hash mismatch: expected {expected}, got {actual}")

    try:
        keys = parse_keys(args)
    except (ValueError, OSError) as exc:
        raise SystemExit(f"key parse error: {exc}")

    max_cands = args.max_candidates
    if max_cands <= 0 or max_cands > 100000:
        raise SystemExit("max-candidates out of bounds")

    data = pe_path.read_bytes()
    try:
        sections, erva, esize = parse_pe(data)
        functions = parse_pdata(data, sections, erva, esize)
    except ValueError as exc:
        raise SystemExit(f"PE parse error: {exc}")
    candidates, total_found, truncated = scan(data, sections, functions, keys, max_cands)

    result = {
        "tool": "locate_property_key.py",
        "mode": "offline-static",
        "pePath": str(pe_path),
        "peSha256": actual,
        "expectedSha256": expected,
        "keys": sorted(f"0x{k:08X}" for k in keys),
        "executableSectionsScanned": [s["name"] for s in sections if s["characteristics"] & 0x20000000],
        "pdataFunctionCount": len(functions),
        "candidatesReturned": len(candidates),
        "candidatesTotalFound": total_found,
        "truncatedByCap": truncated or total_found > len(candidates),
        "candidateImmediateBytesAreInstructions": False,
        "disassemblyRequired": True,
        "candidates": candidates,
        "limitations": [
            "Occurrences are candidate byte references in executable sections, not confirmed instruction operands.",
            "Disassembly is required before assigning any semantic meaning.",
            "No process, game, UI, or live data was accessed.",
            "This tool does not identify fixtures, competitions, or match statistics.",
        ],
    }
    text = json.dumps(result, indent=2)
    if len(text.encode("utf-8")) > MAX_OUTPUT_BYTES:
        while len(text.encode("utf-8")) > MAX_OUTPUT_BYTES and result["candidates"]:
            result["candidates"].pop()
            result["truncatedByCap"] = True
            text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
