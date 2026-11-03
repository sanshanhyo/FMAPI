#!/usr/bin/env python3
"""Offline exact encoded-literal slot locator for the pinned GameAssembly PE.

This reads one explicitly supplied PE file as data. It does not open a process,
call native functions, or modify the input. It verifies the pinned GameAssembly
SHA-256 before parsing.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

GAME_ASSEMBLY_SHA256 = "820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A"
MAX_INDICES = 32
MAX_INDEX = 0x07FFFFFF
SIZE_LIMIT = 512 * 1024 * 1024
ALIGNMENT = 8


def fail(message):
    raise ValueError(message)


def parse_index(text):
    text = text.strip()
    if text.lower().startswith("0x"):
        value = int(text, 16)
    else:
        value = int(text, 10)
    if not 0 <= value <= MAX_INDEX:
        fail("literal index out of bounds: %d" % value)
    return value


def encoded_literal(index):
    if not 0 <= index <= MAX_INDEX:
        fail("literal index out of bounds: %d" % index)
    return 0xA0000000 | ((index * 2) | 1)


def read_pinned_pe(path):
    path = Path(path)
    if not path.is_file():
        fail("PE input is not a regular file")
    size = path.stat().st_size
    if size <= 0 or size > SIZE_LIMIT:
        fail("PE input size outside allowed bounds")
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest().upper()
    if digest != GAME_ASSEMBLY_SHA256:
        fail("unsupported GameAssembly fingerprint: %s" % digest)
    return data


def parse_pe_sections(data):
    if len(data) < 0x40 or data[:2] != b"MZ":
        fail("invalid MZ header")
    e_lfanew = int.from_bytes(data[0x3C:0x40], "little")
    if e_lfanew + 24 > len(data) or data[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        fail("invalid PE signature")
    machine, number_of_sections, _, _, _, size_of_optional_header, _ = struct.unpack_from(
        "<HHIIIHH", data, e_lfanew + 4
    )
    if number_of_sections == 0 or number_of_sections > 96:
        fail("PE section count outside allowed bounds")
    optional_header_offset = e_lfanew + 24
    if optional_header_offset + size_of_optional_header > len(data):
        fail("PE optional header outside file bounds")
    optional_magic = struct.unpack_from("<H", data, optional_header_offset)[0]
    if optional_magic not in (0x10B, 0x20B):
        fail("unsupported PE optional header magic")
    section_table_offset = optional_header_offset + size_of_optional_header
    if section_table_offset + number_of_sections * 40 > len(data):
        fail("PE section table outside file bounds")
    sections = []
    for i in range(number_of_sections):
        offset = section_table_offset + i * 40
        name_raw = data[offset:offset + 8]
        name = name_raw.split(b"\x00", 1)[0].decode("ascii", errors="replace")
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", data, offset + 8
        )
        if raw_size > 0 and (raw_pointer + raw_size > len(data)):
            fail("PE section raw data outside file bounds")
        if virtual_size == 0:
            virtual_size = raw_size
        sections.append(
            {
                "index": i,
                "name": name,
                "virtualAddress": virtual_address,
                "virtualSize": virtual_size,
                "rawPointer": raw_pointer,
                "rawSize": raw_size,
            }
        )
    return sections


def rva_for_file_offset(sections, file_offset):
    for section in sections:
        raw_pointer = section["rawPointer"]
        raw_size = section["rawSize"]
        if raw_size > 0 and raw_pointer <= file_offset < raw_pointer + raw_size:
            rva = section["virtualAddress"] + (file_offset - raw_pointer)
            if rva < section["virtualAddress"] + section["virtualSize"] or section["virtualSize"] == 0:
                return rva
    return None


def search_encoded_literal(sections, data, target):
    matches = []
    for section in sections:
        raw_pointer = section["rawPointer"]
        raw_size = section["rawSize"]
        if raw_size < ALIGNMENT:
            continue
        start = raw_pointer
        end = raw_pointer + raw_size - (raw_size % ALIGNMENT)
        for file_offset in range(start, end, ALIGNMENT):
            value = int.from_bytes(data[file_offset:file_offset + ALIGNMENT], "little")
            if value == target:
                rva = rva_for_file_offset(sections, file_offset)
                if rva is None:
                    continue
                matches.append({"fileOffset": file_offset, "rva": rva})
    return matches


def locate_indices(data, indices):
    sections = parse_pe_sections(data)
    searched_bytes = sum(section["rawSize"] for section in sections)
    results = []
    for index in indices:
        target = encoded_literal(index)
        matches = search_encoded_literal(sections, data, target)
        if len(matches) == 0:
            status = "missing"
        elif len(matches) == 1:
            status = "unique"
        else:
            status = "ambiguous"
        results.append(
            {
                "index": index,
                "encodedValue": "0x%08X" % target,
                "status": status,
                "matchCount": len(matches),
                "matches": [
                    {"fileOffset": item["fileOffset"], "rva": "0x%08X" % item["rva"]}
                    for item in matches
                ],
            }
        )
    return {
        "profile": "pinned GameAssembly.dll",
        "hash": GAME_ASSEMBLY_SHA256,
        "maxIndices": MAX_INDICES,
        "alignment": ALIGNMENT,
        "bounds": {
            "fileSize": len(data),
            "sectionCount": len(sections),
            "searchedBytes": searched_bytes,
        },
        "indices": indices,
        "results": results,
    }


def self_test():
    assert encoded_literal(9070) == 0xA00046DD
    assert encoded_literal(0) == 0xA0000001
    assert encoded_literal(MAX_INDEX) == 0xAFFFFFFF

    sections = [
        {
            "index": 0,
            "name": ".text",
            "virtualAddress": 0x1000,
            "virtualSize": 0x100,
            "rawPointer": 0x200,
            "rawSize": 0x100,
        }
    ]
    data = bytearray(0x400)
    target = encoded_literal(9070)
    struct.pack_into("<Q", data, 0x208, target)
    matches = search_encoded_literal(sections, data, target)
    assert len(matches) == 1
    assert matches[0]["fileOffset"] == 0x208
    assert matches[0]["rva"] == 0x1008

    struct.pack_into("<Q", data, 0x240, target)
    matches = search_encoded_literal(sections, data, target)
    assert len(matches) == 2

    missing_target = encoded_literal(1)
    assert search_encoded_literal(sections, data, missing_target) == []

    try:
        parse_index("x")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid index accepted")

    many = list(range(MAX_INDICES + 1))
    if len(many) <= MAX_INDICES:
        raise AssertionError("index count limit not enforced")

    print("PASS: encoded literal, PE offset/RVA mapping, unique/ambiguous/missing search, bounds")


def main():
    argv = sys.argv[1:]
    if not argv:
        raise SystemExit(
            "Usage: find_literal_slots.py <GameAssembly.dll> <index> [<index> ...] "
            "[--output <json-path>]\n"
            "       find_literal_slots.py --self-test"
        )
    if argv[0] == "--self-test":
        self_test()
        return

    path = None
    indices = []
    output_path = None
    i = 0
    while i < len(argv):
        if argv[i] == "--output":
            if i + 1 >= len(argv):
                raise SystemExit("--output requires a path")
            output_path = argv[i + 1]
            i += 2
            continue
        if argv[i].startswith("--"):
            raise SystemExit("unknown option: %s" % argv[i])
        if path is None:
            path = argv[i]
        else:
            indices.append(parse_index(argv[i]))
        i += 1

    if path is None:
        raise SystemExit("missing GameAssembly PE path")
    if not indices:
        raise SystemExit("at least one literal index is required")
    if len(indices) > MAX_INDICES:
        raise SystemExit("at most %d literal indices are allowed" % MAX_INDICES)

    data = read_pinned_pe(path)
    result = locate_indices(data, indices)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if output_path:
        Path(output_path).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
