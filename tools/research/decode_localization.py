"""Offline, bounded template-only decoding for the observed FMF/LTC layout.
Requires the separately installed zstandard Python package. No process/game calls.
"""
import argparse
import io
import json
import struct
from pathlib import Path

MAX_ARCHIVE = 512 * 1024 * 1024
MAX_ENTRY = 64 * 1024 * 1024


def u32(data, offset):
    if offset < 0 or offset + 4 > len(data):
        raise ValueError("truncated uint32")
    return struct.unpack_from("<I", data, offset)[0]


def templates(data, ids):
    if len(data) < 16 or data[:8] != bytes.fromhex("030163746c2e1000"):
        raise ValueError("unsupported LTC header")
    index = struct.unpack_from("<Q", data, 8)[0] + 8
    count = u32(data, index)
    if count > 250000 or index + 4 + count * 8 + 4 != len(data):
        raise ValueError("LTC index bounds")
    if u32(data, len(data) - 4) != 0:
        raise ValueError("LTC index sentinel")
    records = {}
    previous = -1
    for pos in range(index + 4, index + 4 + count * 8, 8):
        key, relative = struct.unpack_from("<II", data, pos)
        identity = key & 0x0FFFFFFF
        if identity < previous or key in records or (relative < 0x80000000 and not 16 <= relative + 8 < index):
            raise ValueError("LTC key/order/offset bounds")
        records[key] = None if relative >= 0x80000000 else relative + 8
        previous = identity
    boundaries = sorted({value for value in records.values() if value is not None} | {index})
    ends = dict(zip(boundaries, boundaries[1:]))
    result = []
    for key in ids:
        start = records.get(key | 0x10000000)
        if start is None:
            result.append({"templateId": key, "status": "unavailable", "reason": "missing key or unsupported offset flag"})
            continue
        end = ends[start]
        pos = start
        variants = data[pos]
        pos += 1
        if not 1 <= variants <= 16:
            raise ValueError("variant count bounds")
        texts = []
        for _ in range(variants):
            size = u32(data, pos)
            pos += 4
            if size > 8192 or pos + size > end:
                raise ValueError("template string bounds")
            texts.append(data[pos:pos + size].decode("utf-8", errors="strict"))
            pos += size
        if pos != end:
            raise ValueError("template record boundary mismatch")
        result.append({"templateId": key, "status": "template-only", "variants": texts,
                       "parametersResolved": False, "formattedText": None})
    return result


def archive_entry(path, language):
    import zstandard
    size = path.stat().st_size
    if not 25 <= size <= MAX_ARCHIVE:
        raise ValueError("archive size limit")
    magic = bytes.fromhex("28b52ffd")
    with path.open("rb") as source:
        head = source.read(25)
        if head[:9] != bytes.fromhex("0201666d662e080000"):
            raise ValueError("unsupported FMF header")
        index_offset = struct.unpack_from("<Q", head, 9)[0]
        if not 25 <= index_offset < size or size - index_offset > 65536:
            raise ValueError("archive index bounds")
        source.seek(index_offset)
        tail = source.read(65536)
        start = tail.find(magic, 0, 64)
        if start < 0:
            raise ValueError("index frame absent")
        index = zstandard.ZstdDecompressor().decompress(tail[start:], max_output_size=65536)
        pos = 0
        def string():
            nonlocal pos
            length = u32(index, pos)
            pos += 4
            if length > 128 or pos + length > len(index):
                raise ValueError("archive name bounds")
            value = index[pos:pos + length].decode("utf-8", errors="strict")
            pos += length
            return value
        if string() != "languages":
            raise ValueError("unexpected archive root")
        count = u32(index, pos)
        pos += 4
        if count > 128:
            raise ValueError("archive entry count limit")
        selected = []
        for _ in range(count):
            name, extension = string(), string()
            if pos + 40 > len(index):
                raise ValueError("truncated archive entry")
            offset, stored, decoded = struct.unpack_from("<QQQ", index, pos)
            pos += 40  # Three sizes/offsets plus two opaque eight-byte metadata fields.
            if offset + stored > index_offset:
                raise ValueError("archive payload bounds")
            if name == language and extension == ".ltc":
                if stored > MAX_ENTRY or decoded > MAX_ENTRY:
                    raise ValueError("selected entry size limit")
                selected.append((offset, stored, decoded))
        if len(selected) != 1:
            raise ValueError("requires exactly one selected language entry")
        offset, stored, decoded = selected[0]
        source.seek(offset)
        payload = source.read(stored)
        if len(payload) != stored:
            raise ValueError("short archive read")
        start = payload.find(magic, 0, 64)
        if start < 0:
            raise ValueError("entry frame absent")
        with zstandard.ZstdDecompressor().stream_reader(io.BytesIO(payload[start:]), read_across_frames=True) as reader:
            data = reader.read(decoded + 1)
        if len(data) != decoded:
            raise ValueError("decoded entry size mismatch")
        return data


def self_test():
    text = "Synthetic [%team#1-short]".encode()
    record = bytes([1]) + struct.pack("<I", len(text)) + text
    data = bytes.fromhex("030163746c2e1000") + struct.pack("<Q", 8 + len(record)) + record
    data += struct.pack("<IIII", 1, 0x1000002A, 8, 0)
    assert templates(data, [42])[0]["variants"] == [text.decode()]
    assert templates(data, [43])[0]["status"] == "unavailable"
    for invalid in (data[:-1], data[:16] + bytes([255]) + data[17:], data[:17] + struct.pack("<I", 9000) + data[21:]):
        try:
            templates(invalid, [42])
        except (ValueError, UnicodeError):
            continue
        raise AssertionError("malformed input accepted")
    print("PASS: synthetic template, missing key, truncated index, variant and string bounds")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, nargs="?")
    parser.add_argument("--language", default="chinese")
    parser.add_argument("--template-id", type=lambda s: int(s, 0), action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.archive is None or args.output is None or not args.template_id or len(args.template_id) > 16:
        parser.error("archive, 1-16 --template-id values, and --output required")
    repo = Path(__file__).resolve().parents[2]
    output = args.output.resolve()
    if output.is_relative_to(repo):
        parser.error("private output must be outside the repository")
    result = templates(archive_entry(args.archive, args.language), args.template_id)
    output.write_text(json.dumps({"status": "template-only", "language": args.language, "templates": result}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote private template-only result; no parameters resolved")


if __name__ == "__main__":
    main()
