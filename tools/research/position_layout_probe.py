"""Read only the pinned native position table and its named metadata enum.
Outputs structural evidence only; never opens a process or reads player records.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

NATIVE = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
METADATA = "A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C"


def pinned(path, expected, limit):
    if not 0 < path.stat().st_size <= limit:
        raise ValueError("input size limit")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest().upper() != expected:
        raise ValueError("unsupported input fingerprint")
    return data


def table_offset(data, rva, size):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("PE signature")
    count = struct.unpack_from("<H", data, pe + 6)[0]
    start = pe + 24 + struct.unpack_from("<H", data, pe + 20)[0]
    if count > 64:
        raise ValueError("PE section count")
    for i in range(count):
        _, address, raw_size, raw = struct.unpack_from("<IIII", data, start + i * 40 + 8)
        if address <= rva and rva + size <= address + raw_size:
            offset = raw + rva - address
            if offset + size <= len(data):
                return offset
    raise ValueError("RVA outside file-backed section")


def enum_names(data):
    if struct.unpack_from("<II", data) != (0xFAB11BAF, 39):
        raise ValueError("metadata signature/version")
    sections = [struct.unpack_from("<III", data, 8 + i * 12) for i in range(31)]
    if any(offset + size > len(data) for offset, size, _ in sections):
        raise ValueError("metadata section bounds")
    if sections[19][1] != sections[19][2] * 76 or sections[11][1] != sections[11][2] * 10 or sections[7][1] != sections[7][2] * 10:
        raise ValueError("unsupported metadata record widths")
    def name(index):
        base, size, _ = sections[2]
        if index >= size:
            raise ValueError("metadata string index")
        end = data.index(0, base + index, min(base + size, base + index + 512))
        return data[base + index:end].decode("utf-8", errors="strict")
    matches = []
    for i in range(sections[19][2]):
        pos = sections[19][0] + i * 76
        if name(struct.unpack_from("<I", data, pos)[0]) == "PositionMask" and name(struct.unpack_from("<I", data, pos + 4)[0]) == "":
            if not struct.unpack_from("<I", data, pos + 68)[0] & 2:
                raise ValueError("PositionMask is not enum")
            matches.append((struct.unpack_from("<i", data, pos + 20)[0], struct.unpack_from("<H", data, pos + 56)[0]))
    if len(matches) != 1:
        raise ValueError("ambiguous PositionMask enum")
    first, count = matches[0]
    if first < 0 or not 1 <= count <= 32 or first + count > sections[11][2]:
        raise ValueError("enum field range")
    defaults = {}
    for i in range(sections[7][2]):
        field, _, index = struct.unpack_from("<IHi", data, sections[7][0] + i * 10)
        if first <= field < first + count:
            defaults[field] = index
    def unsigned(index):
        base, size, _ = sections[8]
        if not 0 <= index < size:
            raise ValueError("constant index")
        value = data[base + index]
        if value < 0x80:
            return value
        length = 2 if value < 0xC0 else 4 if value < 0xE0 else 0
        if not length or index + length > size:
            raise ValueError("unsupported compressed uint")
        result = value & (0x3F if length == 2 else 0x1F)
        for item in data[base + index + 1:base + index + length]:
            result = (result << 8) | item
        return result
    values = {}
    for field in range(first, first + count):
        if field in defaults:
            label = name(struct.unpack_from("<I", data, sections[11][0] + field * 10)[0])
            value = unsigned(defaults[field])
            if value in values:
                raise ValueError("duplicate enum value")
            values[value] = label
    return values


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: position_layout_probe.py <game_plugin.dll> <global-metadata.dat>")
    native = pinned(Path(sys.argv[1]), NATIVE, 512 * 1024 * 1024)
    metadata = pinned(Path(sys.argv[2]), METADATA, 32 * 1024 * 1024)
    names = enum_names(metadata)
    table = struct.unpack_from("<15I", native, table_offset(native, 0x4D36ACC, 60))
    if table[0] != 1 or names.get(1) != "Goalkeeper" or names.get(table[1]) != "SweeperCentreNotInUse":
        raise ValueError("unexpected mask anchors")
    fields = []
    for index in [0] + list(range(2, 15)):
        value = table[index]
        if value not in names or value == 0 or value & (value - 1):
            raise ValueError("unnamed or non-single-bit position")
        fields.append({"playerOffset": 0x150 + index, "maskBit": value, "nativeName": names[value]})
    print(json.dumps({"nativeSha256": NATIVE, "metadataSha256": METADATA, "nativeMaskTableRva": 0x4D36ACC, "fields": fields,
                      "skippedSlot": {"playerOffset": 0x151, "tableName": names[table[1]], "emittedByCurrentMaskLoop": False}}, indent=2))


if __name__ == "__main__":
    main()
