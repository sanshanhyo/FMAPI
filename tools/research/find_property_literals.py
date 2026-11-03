#!/usr/bin/env python3
"""Offline bounded lookup of metadata string literals.

This tool reads one explicitly supplied global-metadata.dat as data. It verifies
the pinned metadata profile, validates the 31-triple header and section
boundaries, and reports only literal indices whose UTF-8 value exactly equals a
requested name.

It does not access a process, call native code, use the network, or export
metadata. Returned indices are candidate literal references only; they are not
proof of property registration, dispatch, roster membership, or runtime behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

METADATA_SHA256 = "A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C"
METADATA_SANITY = 0xFAB11BAF
METADATA_VERSION = 39
SECTION_COUNT = 31
HEADER_SIZE = 8 + SECTION_COUNT * 12
CONTROL_LITERAL_INDEX = 9070
CONTROL_LITERAL_NAME = "GameCurrentManager"

MAX_METADATA_BYTES = 512 * 1024 * 1024
MAX_REQUESTED_NAMES = 256
MAX_NAME_BYTES = 4096


class MetadataError(Exception):
    """Raised for any profile, boundary, or decoding failure."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def parse_sections(data: bytes) -> tuple[list[int], int, int, int]:
    if len(data) < HEADER_SIZE:
        raise MetadataError("metadata file is shorter than the required header")
    if len(data) > MAX_METADATA_BYTES:
        raise MetadataError("metadata file exceeds the bounded size limit")

    sanity, version = struct.unpack_from("<II", data, 0)
    if sanity != METADATA_SANITY:
        raise MetadataError(f"unsupported metadata sanity value: 0x{sanity:08X}")
    if version != METADATA_VERSION:
        raise MetadataError(f"unsupported metadata version: {version}")

    sections = [struct.unpack_from("<III", data, 8 + i * 12) for i in range(SECTION_COUNT)]
    for index, (offset, size, count) in enumerate(sections):
        if offset < 0 or size < 0 or count < 0:
            raise MetadataError(f"section {index} has a negative field")
        if offset + size > len(data):
            raise MetadataError(f"section {index} extends beyond the metadata file")

    section0_offset, section0_size, section0_count = sections[0]
    section1_offset, section1_size, _section1_count = sections[1]

    if section0_size % 4 != 0:
        raise MetadataError("section 0 is not a uint32 boundary table")
    if section0_count != section0_size // 4:
        raise MetadataError("section 0 count does not match its uint32 boundary count")
    if section0_count < 2:
        raise MetadataError("section 0 has no literal boundaries")
    if section0_offset + section0_size > len(data):
        raise MetadataError("section 0 extends beyond the metadata file")

    boundaries = list(struct.unpack_from(f"<{section0_count}I", data, section0_offset))
    if boundaries[0] != 0:
        raise MetadataError("section 0 does not start at a zero boundary")
    if any(later < earlier for earlier, later in zip(boundaries, boundaries[1:])):
        raise MetadataError("section 0 boundaries are not nondecreasing")
    if boundaries[-1] != section1_size:
        raise MetadataError("section 0 sentinel does not match section 1 size")
    if any(boundary > section1_size for boundary in boundaries):
        raise MetadataError("section 0 contains an out-of-range boundary")

    literal_count = section0_count - 1
    if literal_count <= CONTROL_LITERAL_INDEX:
        raise MetadataError("section 0 does not contain the control literal index")

    if section1_offset + section1_size > len(data):
        raise MetadataError("section 1 extends beyond the metadata file")

    return boundaries, section1_offset, section1_size, literal_count


def decode_literal(data: bytes, section1_offset: int, boundaries: list[int], index: int) -> str:
    start = boundaries[index]
    end = boundaries[index + 1]
    if end < start or end > boundaries[-1]:
        raise MetadataError(f"literal {index} has invalid adjacent boundaries")
    raw = data[section1_offset + start : section1_offset + end]
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise MetadataError(f"literal {index} is not valid UTF-8") from error


def lookup_literals(data: bytes, names: list[str]) -> dict:
    boundaries, section1_offset, section1_size, literal_count = parse_sections(data)
    requested = list(dict.fromkeys(names))
    result_map = {name: [] for name in requested}

    control_value = decode_literal(data, section1_offset, boundaries, CONTROL_LITERAL_INDEX)
    if control_value != CONTROL_LITERAL_NAME:
        raise MetadataError(
            f"control literal at index {CONTROL_LITERAL_INDEX} is not {CONTROL_LITERAL_NAME!r}"
        )

    for index in range(literal_count):
        value = decode_literal(data, section1_offset, boundaries, index)
        if value in result_map:
            result_map[value].append(index)

    return {
        "metadataProfile": {
            "sanity": METADATA_SANITY,
            "version": METADATA_VERSION,
            "sectionCount": SECTION_COUNT,
            "controlLiteralIndex": CONTROL_LITERAL_INDEX,
            "controlLiteralVerified": True,
        },
        "section0": {
            "boundaryCount": len(boundaries),
            "literalCount": literal_count,
        },
        "section1": {
            "size": section1_size,
        },
        "requestedNames": requested,
        "matches": [
            {"name": name, "literalIndices": result_map[name], "candidate": True}
            for name in requested
        ],
    }


def make_synthetic_metadata() -> bytes:
    example = "ExampleStaffProperty"
    control = CONTROL_LITERAL_NAME
    slices = [b""] * CONTROL_LITERAL_INDEX + [control.encode("utf-8")]
    slices[0] = example.encode("utf-8")

    boundaries = [0]
    payload = bytearray()
    for item in slices:
        payload.extend(item)
        boundaries.append(len(payload))

    section0_count = len(boundaries)
    section0_size = section0_count * 4
    section1_size = len(payload)

    section0_offset = HEADER_SIZE
    section1_offset = section0_offset + section0_size

    sections = [(0, 0, 0) for _ in range(SECTION_COUNT)]
    sections[0] = (section0_offset, section0_size, section0_count)
    sections[1] = (section1_offset, section1_size, section1_size)

    header = struct.pack("<II", METADATA_SANITY, METADATA_VERSION)
    for offset, size, count in sections:
        header += struct.pack("<III", offset, size, count)

    section0_bytes = struct.pack(f"<{section0_count}I", *boundaries)
    return header + section0_bytes + bytes(payload)


def self_test() -> None:
    data = make_synthetic_metadata()
    result = lookup_literals(data, [CONTROL_LITERAL_NAME, "ExampleStaffProperty", "MissingName"])
    by_name = {item["name"]: item["literalIndices"] for item in result["matches"]}
    assert by_name[CONTROL_LITERAL_NAME] == [CONTROL_LITERAL_INDEX]
    assert by_name["ExampleStaffProperty"] == [0]
    assert by_name["MissingName"] == []

    bad_sanity = bytearray(data)
    struct.pack_into("<I", bad_sanity, 0, 0)
    bad_version = bytearray(data)
    struct.pack_into("<I", bad_version, 4, 40)
    bad_boundary = bytearray(data)
    struct.pack_into("<I", bad_boundary, 8 + 0 * 12 + 8, 1)  # section 0 count

    boundaries = list(struct.unpack_from(f"<{CONTROL_LITERAL_INDEX + 2}I", data, HEADER_SIZE))
    section1_offset = struct.unpack_from("<III", data, 8 + 1 * 12)[0]
    bad_control = bytearray(data)
    control_start = boundaries[CONTROL_LITERAL_INDEX]
    control_end = boundaries[CONTROL_LITERAL_INDEX + 1]
    for pos in range(section1_offset + control_start, section1_offset + control_end):
        bad_control[pos] ^= 0xFF

    for case in (bytes(bad_sanity), bytes(bad_version), bytes(bad_boundary), bytes(bad_control)):
        try:
            lookup_literals(case, [CONTROL_LITERAL_NAME])
        except MetadataError:
            continue
        raise AssertionError("invalid metadata was accepted")

    print("PASS: synthetic metadata profile, adjacent boundaries, UTF-8 lookup, and fail-closed checks")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline bounded lookup of exact metadata string-literal names."
    )
    parser.add_argument("metadata", nargs="?", help="path to global-metadata.dat")
    parser.add_argument("names", nargs="*", help="exact literal names to look up")
    parser.add_argument("--name", action="append", default=[], help="exact literal name to look up")
    parser.add_argument("--output", help="write JSON result to this path instead of stdout")
    parser.add_argument("--self-test", action="store_true", help="run synthetic checks only")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        return 0

    if not args.metadata:
        parser.error("metadata path is required unless --self-test is used")

    names = list(args.names) + list(args.name)
    if not names:
        parser.error("at least one literal name is required")
    if len(names) > MAX_REQUESTED_NAMES:
        raise MetadataError("too many requested literal names")
    for name in names:
        if not name or len(name.encode("utf-8")) > MAX_NAME_BYTES:
            raise MetadataError("requested literal name is empty or too large")

    path = Path(args.metadata)
    if not path.is_file():
        raise MetadataError(f"metadata file not found: {path}")

    actual_hash = sha256_file(path)
    if actual_hash != METADATA_SHA256:
        raise MetadataError(
            f"unsupported metadata SHA-256: {actual_hash}; expected {METADATA_SHA256}"
        )

    data = path.read_bytes()
    result = lookup_literals(data, names)
    result["metadataFile"] = {
        "pathProvided": True,
        "sha256": actual_hash,
        "size": len(data),
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MetadataError, OSError, ValueError) as error:
        sys.stderr.write(json.dumps({"status": "unavailable", "reason": str(error)}, ensure_ascii=False) + "\n")
        raise SystemExit(3)
PYEOF