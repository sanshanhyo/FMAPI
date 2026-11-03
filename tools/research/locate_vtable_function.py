#!/usr/bin/env python3
"""Bounded offline PE vtable-function locator (research tool).

Given a PE file, an exact target function RVA and a vtable slot index, report
vtable candidates where that slot contains the target function. Each candidate
is annotated with its validated Complete Object Locator (COL) and RTTI type
name. The scan is bounded by a result cap and a position cap. No process, game
or UI access occurs; the PE is opened as data only.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path


def parse_pe(data):
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise ValueError("not a PE (MZ)")
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if e_lfanew + 0x18 > len(data) or data[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        raise ValueError("PE signature")
    coff = e_lfanew + 4
    machine, num_sections, _ts, _sym, _nsym, opt_size, _char = struct.unpack_from(
        "<HHIIIHH", data, coff)
    if machine not in (0x8664, 0x14C):
        raise ValueError("unsupported machine")
    opt = coff + 20
    if opt + opt_size > len(data):
        raise ValueError("optional header bounds")
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic == 0x20B:  # PE32+
        image_base = struct.unpack_from("<Q", data, opt + 24)[0]
        is_pe32plus = True
    elif magic == 0x10B:  # PE32
        image_base = struct.unpack_from("<I", data, opt + 28)[0]
        is_pe32plus = False
    else:
        raise ValueError("unsupported optional header magic")
    section_alignment = struct.unpack_from("<I", data, opt + 32)[0]
    file_alignment = struct.unpack_from("<I", data, opt + 36)[0]
    size_of_image = struct.unpack_from("<I", data, opt + 56)[0]
    num_rva = struct.unpack_from("<I", data, opt + opt_size - 4)[0] if opt_size >= 4 else 0
    _ = (section_alignment, file_alignment, size_of_image, num_rva)

    sec_off = opt + opt_size
    sections = []
    for i in range(num_sections):
        off = sec_off + i * 40
        if off + 40 > len(data):
            raise ValueError("section header bounds")
        name = data[off:off + 8].split(b"\0", 1)[0].decode("ascii", "replace")
        virtual_size, virtual_address, raw_size, raw_ptr = struct.unpack_from(
            "<IIII", data, off + 8)
        characteristics = struct.unpack_from("<I", data, off + 36)[0]
        sections.append({
            "name": name,
            "virtualSize": virtual_size,
            "virtualAddress": virtual_address,
            "rawSize": raw_size,
            "rawPointer": raw_ptr,
            "characteristics": characteristics,
        })
    return {
        "data": data,
        "machine": machine,
        "isPe32Plus": is_pe32plus,
        "imageBase": image_base,
        "sections": sections,
    }


def section_for(pe, rva):
    for s in pe["sections"]:
        start = s["virtualAddress"]
        end = start + max(s["virtualSize"], s["rawSize"])
        if start <= rva < end:
            return s
    return None


def rva_to_offset(pe, rva):
    s = section_for(pe, rva)
    if s is None:
        return None
    off = s["rawPointer"] + (rva - s["virtualAddress"])
    if off < 0 or off >= len(pe["data"]):
        return None
    return off


def read_u64(pe, rva):
    off = rva_to_offset(pe, rva)
    if off is None or off + 8 > len(pe["data"]):
        return None
    return struct.unpack_from("<Q", pe["data"], off)[0]


def read_u32(pe, rva):
    off = rva_to_offset(pe, rva)
    if off is None or off + 4 > len(pe["data"]):
        return None
    return struct.unpack_from("<I", pe["data"], off)[0]


def read_i32(pe, rva):
    v = read_u32(pe, rva)
    if v is None:
        return None
    return struct.unpack("<i", struct.pack("<I", v))[0]


def is_code_rva(pe, rva):
    s = section_for(pe, rva)
    if s is None:
        return False
    return bool(s["characteristics"] & 0x20)


def validate_col(pe, col_rva):
    """Validate a Complete Object Locator at col_rva. Return type name or None."""
    if not pe["isPe32Plus"]:
        return None
    # Signature at +0
    sig = read_u32(pe, col_rva)
    if sig != 1:
        return None
    off = read_u32(pe, col_rva + 4)
    if off != 0:
        # Primary vtable expected offset 0; allow 0 only.
        return None
    _cd = read_i32(pe, col_rva + 8)
    td_rva = read_i32(pe, col_rva + 12)
    cd_rva = read_i32(pe, col_rva + 16)
    self_rva = read_i32(pe, col_rva + 20)
    if td_rva is None or cd_rva is None or self_rva is None:
        return None
    if self_rva != col_rva:
        return None
    # Type descriptor must be in a section.
    if section_for(pe, td_rva) is None:
        return None
    # Read name at type descriptor + 16.
    name_rva = td_rva + 16
    off_name = rva_to_offset(pe, name_rva)
    if off_name is None:
        return None
    # Read up to 256 bytes, null-terminated.
    buf = pe["data"][off_name:off_name + 256]
    nul = buf.find(b"\0")
    if nul < 1:
        return None
    try:
        name = buf[:nul].decode("ascii")
    except UnicodeDecodeError:
        return None
    if not name.startswith(".?A"):
        return None
    return name


def vtable_slot_count(pe, vtable_base_rva):
    """Count contiguous code pointers starting at vtable_base_rva."""
    s = section_for(pe, vtable_base_rva)
    if s is None:
        return 0
    sec_start = s["virtualAddress"]
    sec_end = s["virtualAddress"] + max(s["virtualSize"], s["rawSize"])
    count = 0
    rva = vtable_base_rva
    while rva + 8 <= sec_end:
        val = read_u64(pe, rva)
        if val is None:
            break
        target_rva = val - pe["imageBase"]
        if target_rva < 0 or target_rva > 0x7FFFFFFF:
            break
        if not is_code_rva(pe, target_rva):
            break
        count += 1
        rva += 8
        if count >= 4096:
            break
    return count


def locate(pe, func_rva, slot_index, rtti_filter, result_cap, scan_cap):
    target_va = pe["imageBase"] + func_rva
    candidates = []
    seen_vtables = set()
    examined = 0
    truncated = False
    # Scan data sections (non-code) for 8-aligned positions.
    data_sections = [s for s in pe["sections"]
                     if not (s["characteristics"] & 0x20) and s["rawSize"] > 0]
    if not data_sections:
        data_sections = pe["sections"]
    for s in data_sections:
        sec_start = s["virtualAddress"]
        sec_end = s["virtualAddress"] + max(s["virtualSize"], s["rawSize"])
        # align start up
        pos = sec_start
        if pos % 8:
            pos += 8 - (pos % 8)
        while pos + 8 <= sec_end:
            if examined >= scan_cap:
                truncated = True
                break
            examined += 1
            vtable_base = pos - slot_index * 8
            if vtable_base < sec_start:
                pos += 8
                continue
            if vtable_base + 8 > sec_end:
                pos += 8
                continue
            col_ptr_va = read_u64(pe, vtable_base - 8)
            if col_ptr_va is None:
                pos += 8
                continue
            col_rva = col_ptr_va - pe["imageBase"]
            if col_rva < 0 or col_rva > 0x7FFFFFFF:
                pos += 8
                continue
            if section_for(pe, col_rva) is None:
                pos += 8
                continue
            if vtable_base - 8 < sec_start:
                pos += 8
                continue
            # Validate COL first.
            rtti = validate_col(pe, col_rva)
            if rtti is None:
                pos += 8
                continue
            if rtti_filter and rtti_filter.lower() not in rtti.lower():
                pos += 8
                continue
            # Check slot value.
            slot_val = read_u64(pe, pos)
            if slot_val != target_va:
                pos += 8
                continue
            if vtable_base in seen_vtables:
                pos += 8
                continue
            sc = vtable_slot_count(pe, vtable_base)
            if sc <= slot_index:
                pos += 8
                continue
            seen_vtables.add(vtable_base)
            candidates.append({
                "vtableRva": "0x%X" % vtable_base,
                "colRva": "0x%X" % col_rva,
                "slotRva": "0x%X" % pos,
                "slotCount": sc,
                "rtti": rtti,
            })
            if len(candidates) >= result_cap:
                # mark truncated? no, cap reached
                pass
            pos += 8
        if truncated:
            break
        if len(candidates) >= result_cap:
            break
    # If cap reached, note via truncated? We'll add a separate flag in output.
    return candidates, examined, truncated, len(candidates) >= result_cap


def self_test():
    # Build a PE-like structure directly (bypass PE parsing) to test locate().
    import struct as _s
    image_base = 0x100000000
    data = bytearray(0x600)
    # .text at RVA 0x1000, file 0x200: function at RVA 0x1100.
    data[0x300] = 0xC3
    rdata_file = 0x400
    rdata_rva = 0x2000
    col_rva = rdata_rva
    td_rva = rdata_rva + 0x100
    cd_rva = rdata_rva + 0x100
    _s.pack_into("<IIiiiI", data, rdata_file, 1, 0, 0, td_rva, cd_rva, col_rva)
    _s.pack_into("<Q", data, rdata_file + 0x18, image_base + col_rva)
    name = b".?AVSynthetic@@\0"
    data[rdata_file + 0x100:rdata_file + 0x100 + 16] = b"\x00" * 16
    data[rdata_file + 0x110:rdata_file + 0x110 + len(name)] = name
    slot0_va = image_base + 0x1100
    _s.pack_into("<Q", data, rdata_file + 0x20, slot0_va)
    pe = {
        "data": bytes(data),
        "imageBase": image_base,
        "isPe32Plus": True,
        "sections": [
            {"name": ".text", "virtualSize": 0x1000, "virtualAddress": 0x1000,
             "rawSize": 0x200, "rawPointer": 0x200, "characteristics": 0x60000020},
            {"name": ".rdata", "virtualSize": 0x1000, "virtualAddress": 0x2000,
             "rawSize": 0x200, "rawPointer": 0x400, "characteristics": 0x40000040},
        ],
    }
    # Directly verify validate_col and slot count.
    assert validate_col(pe, col_rva) == ".?AVSynthetic@@", validate_col(pe, col_rva)
    assert vtable_slot_count(pe, rdata_rva + 0x20) == 1
    cands, examined, trunc, cap_reached = locate(pe, 0x1100, 0, None, 10, 100000)
    assert len(cands) == 1, cands
    assert cands[0]["rtti"] == ".?AVSynthetic@@", cands[0]
    assert cands[0]["slotCount"] == 1, cands[0]
    cands2, _, _, _ = locate(pe, 0x1100, 1, None, 10, 100000)
    assert len(cands2) == 0, cands2
    cands3, _, _, _ = locate(pe, 0x1100, 0, "Nope", 10, 100000)
    assert len(cands3) == 0, cands3
    print("PASS: synthetic vtable+COL locator, boundary and filter checks")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Bounded offline PE vtable-function locator")
    parser.add_argument("pe", nargs="?", help="PE file path")
    parser.add_argument("func_rva", nargs="?", help="Target function RVA (hex, e.g. 0x1234)")
    parser.add_argument("slot", nargs="?", type=int, help="Vtable slot index (0-based)")
    parser.add_argument("--rtti", default=None, help="RTTI name substring filter")
    parser.add_argument("--cap", type=int, default=100, help="Max candidates to report")
    parser.add_argument("--scan-cap", type=int, default=2000000, help="Max positions to examine")
    parser.add_argument("--output", default=None, help="Write JSON to file instead of stdout")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic checks")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.pe or not args.func_rva or args.slot is None:
        parser.error("pe, func_rva and slot are required (or --self-test)")
    if args.cap < 1 or args.cap > 10000:
        raise ValueError("cap out of range")
    if args.scan_cap < 1 or args.scan_cap > 10000000:
        raise ValueError("scan-cap out of range")
    if args.slot < 0 or args.slot > 4095:
        raise ValueError("slot out of range")

    data = Path(args.pe).read_bytes()
    if len(data) > 512 * 1024 * 1024:
        raise ValueError("PE too large")
    pe = parse_pe(data)
    func_rva = int(args.func_rva, 16)
    if func_rva < 0:
        raise ValueError("func_rva must be non-negative")
    cands, examined, truncated, cap_reached = locate(
        pe, func_rva, args.slot, args.rtti, args.cap, args.scan_cap)
    result = {
        "pe": Path(args.pe).name,
        "imageBase": "0x%X" % pe["imageBase"],
        "targetFunctionRva": "0x%X" % func_rva,
        "slotIndex": args.slot,
        "rttiFilter": args.rtti,
        "scan": {
            "positionsExamined": examined,
            "truncatedByScanCap": truncated,
            "resultCapReached": cap_reached,
        },
        "candidates": cands,
        "count": len(cands),
        "cap": args.cap,
    }
    text = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(json.dumps({"status": "unavailable", "reason": str(e)}))
        sys.exit(3)
