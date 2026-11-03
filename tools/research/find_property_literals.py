#!/usr/bin/env python3
"""Offline bounded lookup of Il2Cpp global-metadata string literals.

This tool reads one explicitly supplied global-metadata.dat as data. It verifies
the pinned metadata profile, validates the string-literal section boundaries, and
reports only the literal indices whose decoded UTF-16 value exactly equals a
requested name.

It does not access a process, call native code, use the network, or export
metadata. Returned indices are candidate literal references only; they are not
proof of property registration, dispatch, or runtime behavior.
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
CONTROL_LITERAL_INDEX = 9070
CONTROL_LITERAL_NAME = "GameCurrentManager"

# Bounded input limits.
MAX_METADATA_BYTES = 512 * 1024 * 1024
MAX_LITERAL_ENTRIES = 10_000_000
MAX_LITERAL_LENGTH = 1_000_000
MAX_REQUESTED_NAMES = 256
MAX_NAME_BYTES = 4096

HEADER_STRUCT = struct.Struct("<IIIIII")  # sanity, version, section0 off/size, section1 off/size
ENTRY_STRUCT = struct.Struct("<II")      # length, dataIndex


class MetadataError(Exception):
    """Raised for any profile, boundary, or decoding failure."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def parse_sections(data: bytes) -> tuple[int, int, int, int]:
    if len(data) < HEADER_STRUCT.size:
        raise MetadataError("metadata file is shorter than the required header")
    if len(data) > MAX_METADATA_BYTES:
        raise MetadataError("metadata file exceeds the bounded size limit")
    sanity, version, section0_offset, section0_size, section1_offset, section1_size = (
        HEADER_STRUCT.unpack_from(data, 0)
    )
    if sanity != METADATA_SANITY:
        raise MetadataError(f"unsupported metadata sanity value: 0x{sanity:08X}")
    if version != METADATA_VERSION:
        raise MetadataError(f"unsupported metadata version: {version}")
    for label, offset, size in (
        ("section 0", section0_offset, section0_size),
        ("section 1", section1_offset, section1_size),
    ):
        if offset < 0 or size < 0:
            raise MetadataError(f"{label} has a negative offset or size")
        if offset + size > len(data):
            raise MetadataError(f"{label} extends beyond the metadata file")
    if section0_offset < HEADER_STRUCT.size:
        raise MetadataError("section 0 begins before the header boundary")
    if section0_size % ENTRY_STRUCT.size != 0:
        raise MetadataError("section 0 size is not a whole literal-entry table")
    entry_count = section0_size // ENTRY_STRUCT.size
    if entry_count > MAX_LITERAL_ENTRIES:
        raise MetadataError("section 0 exceeds the bounded entry count")
    if entry_count <= CONTROL_LITERAL_INDEX:
        raise MetadataError("section 0 does not contain the control literal index")
    return section0_offset, section0_size, section1_offset, section1_size


def decode_literal(data: bytes, section1_offset: int, section1_size: int, length: int, data_index: int) -> str:
    if length < 0 or length > MAX_LITERAL_LENGTH:
        raise MetadataError("literal length is outside the bounded range")
    byte_length = length * 2
    if data_index < 0 or data_index + byte_length > section1_size:
        raise MetadataError("literal data index extends beyond section 1")
    raw = data[section1_offset + data_index : section1_offset + data_index + byte_length]
    try:
        text = raw.decode("utf-16-le")
    except UnicodeDecodeError as error:
        raise MetadataError("literal data is not valid UTF-16LE") from error
    if "\x00" in text:
        raise MetadataError("literal data contains an embedded NUL")
    return text


def lookup_literals(data: bytes, names: list[str], verify_control: bool = True) -> dict:
    section0_offset, section0_size, section1_offset, section1_size = parse_sections(data)
    entry_count = section0_size // ENTRY_STRUCT.size
    results = {name: [] for name in names}

    # Validate and decode the known control literal before reporting candidates.
    control_offset = section0_offset + CONTROL_LITERAL_INDEX * ENTRY_STRUCT.size
    control_length, control_data_index = ENTRY_STRUCT.unpack_from(data, control_offset)
    control_value = decode_literal(data, section1_offset, section1_size, control_length, control_data_index)
    if verify_control and control_value != CONTROL_LITERAL_NAME:
        raise MetadataError(
            f"control literal at index {CONTROL_LITERAL_INDEX} is not {CONTROL_LITERAL_NAME!r}"
        )

    for index in range(entry_count):
        entry_offset = section0_offset + index * ENTRY_STRUCT.size
        length, data_index = ENTRY_STRUCT.unpack_from(data, entry_offset)
        try:
            value = decode_literal(data, section1_offset, section1_size, length, data_index)
        except MetadataError:
            # A malformed entry makes the whole bounded lookup unusable.
            raise
        if value in results:
            results[value].append(index)

    return {
        "metadataProfile": {
            "sanity": METADATA_SANITY,
            "version": METADATA_VERSION,
            "controlLiteralIndex": CONTROL_LITERAL_INDEX,
            "controlLiteralVerified": verify_control,
        },
        "section0": {
            "offset": section0_offset,
            "size": section0_size,
            "entryCount": entry_count,
            "entrySize": ENTRY_STRUCT.size,
        },
        "section1": {
            "offset": section1_offset,
            "size": section1_size,
        },
        "requestedNames": names,
        "matches": [
            {"name": name, "literalIndices": results[name], "candidate": True}
            for name in names
        ],
    }


def make_synthetic_metadata() -> bytes:
    control = CONTROL_LITERAL_NAME
    example = "ExampleStaffProperty"
    section1 = control.encode("utf-16-le") + example.encode("utf-16-le")
    entry_count = CONTROL_LITERAL_INDEX + 1
    table = bytearray(entry_count * ENTRY_STRUCT.size)
    struct.pack_into(ENTRY_STRUCT.format, table, 0 * ENTRY_STRUCT.size, len(example), len(control.encode("utf-16-le")))
    struct.pack_into(ENTRY_STRUCT.format, table, CONTROL_LITERAL_INDEX * ENTRY_STRUCT.size, len(control), 0)
    header = HEADER_STRUCT.pack(
        METADATA_SANITY,
        METADATA_VERSION,
        HEADER_STRUCT.size,
        len(table),
        HEADER_STRUCT.size + len(table),
        len(section1),
    )
    return header + bytes(table) + section1


def self_test() -> None:
    data = make_synthetic_metadata()
    result = lookup_literals(data, [CONTROL_LITERAL_NAME, "ExampleStaffProperty", "MissingName"])
    assert result["metadataProfile"]["controlLiteralVerified"] is True
    by_name = {item["name"]: item["literalIndices"] for item in result["matches"]}
    assert by_name[CONTROL_LITERAL_NAME] == [CONTROL_LITERAL_INDEX]
    assert by_name["ExampleStaffProperty"] == [0]
    assert by_name["MissingName"] == []

    # Boundary and profile failures must fail closed.
    cases = []
    truncated = data[:-1]
    cases.append(truncated)
    bad_sanity = bytearray(data)
    struct.pack_into("<I", bad_sanity, 0, 0)
    cases.append(bytes(bad_sanity))
    bad_version = bytearray(data)
    struct.pack_into("<I", bad_version, 4, 40)
    cases.append(bytes(bad_version))
    bad_control = bytearray(data)
    struct.pack_into("<I", bad_control, HEADER_STRUCT.size + CONTROL_LITERAL_INDEX * ENTRY_STRUCT.size, 999)
    cases.append(bytes(bad_control))
    for case in cases:
        try:
            lookup_literals(case, [CONTROL_LITERAL_NAME])
        except MetadataError:
            continue
        raise AssertionError("invalid metadata was accepted")

    # Section boundary failure.
    bad_section = bytearray(data)
    struct.pack_into("<I", bad_section, 12, 1)  # section0 size not entry-aligned / too small
    try:
        lookup_literals(bytes(bad_section), [CONTROL_LITERAL_NAME])
    except MetadataError:
        pass
    else:
        raise AssertionError("invalid section boundary was accepted")

    print("PASS: synthetic metadata profile, control literal, exact lookup, and fail-closed boundaries")


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
    result = lookup_literals(data, names, verify_control=True)
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