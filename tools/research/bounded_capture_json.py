#!/usr/bin/env python3
"""Bounded capture JSON input loader (standalone research utility).

Offline only: no process, game, UI, network, native, or subprocess access.
Reads a single JSON capture from disk or bytes with strict, explicit limits:
  * maximum input size (default 1 MiB)
  * UTF-8 BOM / UTF-16 BOM handling
  * rejection of duplicate JSON object keys
  * nesting-depth and record/node limits
  * output-mode protection against overwriting an input file

This is research tooling, not an SDK or adapter. It performs no game reads.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Optional, Tuple

MAX_INPUT_BYTES_DEFAULT = 1 * 1024 * 1024  # 1 MiB
MAX_DEPTH_DEFAULT = 64
MAX_NODES_DEFAULT = 50_000
MAX_CONTAINER_ITEMS_DEFAULT = 10_000

UTF8_BOM = b"\xef\xbb\xbf"
UTF16_LE_BOM = b"\xff\xfe"
UTF16_BE_BOM = b"\xfe\xff"
UTF32_LE_BOM = b"\xff\xfe\x00\x00"
UTF32_BE_BOM = b"\x00\x00\xfe\xff"


class BoundedJsonError(ValueError):
    """Raised when an input violates a bounded JSON loading rule."""


@dataclass(frozen=True)
class LoadResult:
    data: Any
    encoding: str
    byte_count: int
    node_count: int
    max_depth: int


def _detect_encoding(raw: bytes) -> Tuple[str, bytes]:
    if raw.startswith(UTF32_LE_BOM):
        return "utf-32-le", raw[len(UTF32_LE_BOM):]
    if raw.startswith(UTF32_BE_BOM):
        return "utf-32-be", raw[len(UTF32_BE_BOM):]
    if raw.startswith(UTF8_BOM):
        return "utf-8-sig", raw[len(UTF8_BOM):]
    if raw.startswith(UTF16_LE_BOM):
        return "utf-16-le", raw[len(UTF16_LE_BOM):]
    if raw.startswith(UTF16_BE_BOM):
        return "utf-16-be", raw[len(UTF16_BE_BOM):]
    return "utf-8", raw


def _measure_depth(raw_text: str, max_depth: int) -> int:
    depth = 0
    max_seen = 0
    in_string = False
    escape = False
    i = 0
    n = len(raw_text)
    while i < n:
        ch = raw_text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
        elif ch in "{[":
            depth += 1
            if depth > max_depth:
                raise BoundedJsonError(
                    f"JSON nesting depth {depth} exceeds limit {max_depth}"
                )
            if depth > max_seen:
                max_seen = depth
        elif ch in "}]":
            if depth <= 0:
                raise BoundedJsonError("Unbalanced JSON brackets")
            depth -= 1
        i += 1
    if depth != 0:
        raise BoundedJsonError("Unbalanced JSON brackets")
    if in_string:
        raise BoundedJsonError("Unterminated JSON string")
    return max_seen


def _reject_duplicate_keys(pairs):
    result = {}
    seen = set()
    for key, value in pairs:
        marker = key if isinstance(key, str) else repr(key)
        if marker in seen:
            raise BoundedJsonError(f"Duplicate JSON object key: {key!r}")
        seen.add(marker)
        result[key] = value
    return result


def _count_nodes(value, max_nodes, max_items):
    total = 0
    work = [value]
    while work:
        current = work.pop()
        total += 1
        if total > max_nodes:
            raise BoundedJsonError(
                f"JSON node count {total} exceeds limit {max_nodes}"
            )
        if isinstance(current, dict):
            if len(current) > max_items:
                raise BoundedJsonError(
                    f"JSON object has {len(current)} members, exceeds limit {max_items}"
                )
            for v in current.values():
                work.append(v)
        elif isinstance(current, list):
            if len(current) > max_items:
                raise BoundedJsonError(
                    f"JSON array has {len(current)} items, exceeds limit {max_items}"
                )
            for item in current:
                work.append(item)
    return total


def load_capture_json_bytes(
    raw,
    *,
    max_bytes=MAX_INPUT_BYTES_DEFAULT,
    max_depth=MAX_DEPTH_DEFAULT,
    max_nodes=MAX_NODES_DEFAULT,
    max_container_items=MAX_CONTAINER_ITEMS_DEFAULT,
):
    if not isinstance(raw, (bytes, bytearray)):
        raise BoundedJsonError("Input must be bytes")
    if len(raw) == 0:
        raise BoundedJsonError("Empty input")
    if len(raw) > max_bytes:
        raise BoundedJsonError(
            f"Input size {len(raw)} bytes exceeds limit {max_bytes}"
        )

    encoding, payload = _detect_encoding(bytes(raw))
    try:
        text = payload.decode(encoding)
    except UnicodeDecodeError as exc:
        raise BoundedJsonError(f"Input is not valid {encoding}: {exc}") from exc

    depth = _measure_depth(text, max_depth)

    try:
        data = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise BoundedJsonError(f"Invalid JSON: {exc}") from exc
    except BoundedJsonError:
        raise
    except Exception as exc:
        raise BoundedJsonError(f"JSON parse failed: {exc}") from exc

    node_count = _count_nodes(data, max_nodes, max_container_items)
    return LoadResult(
        data=data,
        encoding=encoding,
        byte_count=len(raw),
        node_count=node_count,
        max_depth=depth,
    )


def load_capture_json_file(
    path,
    *,
    max_bytes=MAX_INPUT_BYTES_DEFAULT,
    max_depth=MAX_DEPTH_DEFAULT,
    max_nodes=MAX_NODES_DEFAULT,
    max_container_items=MAX_CONTAINER_ITEMS_DEFAULT,
):
    if not isinstance(path, str) or not path:
        raise BoundedJsonError("Input path must be a non-empty string")
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        raise BoundedJsonError(f"Cannot stat input: {exc}") from exc
    if size > max_bytes:
        raise BoundedJsonError(
            f"Input size {size} bytes exceeds limit {max_bytes}"
        )
    try:
        with open(path, "rb") as handle:
            raw = handle.read(max_bytes + 1)
    except OSError as exc:
        raise BoundedJsonError(f"Cannot read input: {exc}") from exc
    if len(raw) > max_bytes:
        raise BoundedJsonError(f"Input size exceeds limit {max_bytes}")
    return load_capture_json_bytes(
        raw,
        max_bytes=max_bytes,
        max_depth=max_depth,
        max_nodes=max_nodes,
        max_container_items=max_container_items,
    )


def normalize_path(path):
    return os.path.abspath(os.path.expanduser(path))


def reject_output_overwrite(inputs, output):
    if not isinstance(output, str) or not output:
        raise BoundedJsonError("Output path must be a non-empty string")
    out_norm = normalize_path(output)
    input_norms = [normalize_path(p) for p in inputs]
    for inp in input_norms:
        if inp == out_norm:
            raise BoundedJsonError(f"Output path would overwrite input: {output}")
    if os.path.exists(out_norm):
        try:
            out_stat = os.stat(out_norm)
        except OSError:
            out_stat = None
        if out_stat is not None:
            for inp in input_norms:
                if os.path.exists(inp):
                    try:
                        in_stat = os.stat(inp)
                        if in_stat.st_ino == out_stat.st_ino and in_stat.st_dev == out_stat.st_dev:
                            raise BoundedJsonError(
                                f"Output path resolves to an existing input: {output}"
                            )
                    except OSError:
                        continue
    if os.path.exists(out_norm):
        raise BoundedJsonError(f"Refusing to overwrite existing output file: {output}")


def write_output_json(inputs, output, data, indent=2):
    reject_output_overwrite(inputs, output)
    out_norm = normalize_path(output)
    parent = os.path.dirname(out_norm)
    if parent and not os.path.isdir(parent):
        raise BoundedJsonError(f"Output directory does not exist: {parent}")
    try:
        with open(out_norm, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=indent)
            handle.write("\n")
    except OSError as exc:
        raise BoundedJsonError(f"Cannot write output: {exc}") from exc


def _self_test():
    failures = []

    def check(name, fn):
        try:
            fn()
        except Exception as exc:
            failures.append(f"{name}: {exc!r}")

    def t1():
        r = load_capture_json_bytes(b'{"a": 1, "b": [2, 3]}')
        assert r.data == {"a": 1, "b": [2, 3]}
        assert r.encoding == "utf-8"

    def t2():
        r = load_capture_json_bytes(b"\xef\xbb\xbf" + b'{"x": true}')
        assert r.data == {"x": True}
        assert r.encoding == "utf-8-sig"

    def t3():
        raw = b"\xff\xfe" + '{"y": 42}'.encode("utf-16-le")
        r = load_capture_json_bytes(raw)
        assert r.data == {"y": 42}
        assert r.encoding == "utf-16-le"

    def t4():
        raw = b"\xfe\xff" + '{"z": null}'.encode("utf-16-be")
        r = load_capture_json_bytes(raw)
        assert r.data == {"z": None}
        assert r.encoding == "utf-16-be"

    def t5():
        try:
            load_capture_json_bytes(b'{"k": 1, "k": 2}')
        except BoundedJsonError:
            return
        raise AssertionError("duplicate key not rejected")

    def t6():
        try:
            load_capture_json_bytes(b'{"outer": {"a": 1, "a": 2}}')
        except BoundedJsonError:
            return
        raise AssertionError("nested duplicate key not rejected")

    def t7():
        deep = ("[" * 5) + "1" + ("]" * 5)
        load_capture_json_bytes(deep.encode("utf-8"))
        too_deep = ("[" * (MAX_DEPTH_DEFAULT + 1)) + "1" + ("]" * (MAX_DEPTH_DEFAULT + 1))
        try:
            load_capture_json_bytes(too_deep.encode("utf-8"))
        except BoundedJsonError:
            return
        raise AssertionError("depth limit not enforced")

    def t8():
        big = b'"' + b'a' * MAX_INPUT_BYTES_DEFAULT + b'"'
        assert len(big) > MAX_INPUT_BYTES_DEFAULT
        try:
            load_capture_json_bytes(big, max_bytes=MAX_INPUT_BYTES_DEFAULT)
        except BoundedJsonError:
            return
        raise AssertionError("size limit not enforced")

    def t9():
        try:
            load_capture_json_bytes(b"")
        except BoundedJsonError:
            return
        raise AssertionError("empty input not rejected")

    def t10():
        payload = "[" + ",".join("1" for _ in range(100)) + "]"
        load_capture_json_bytes(payload.encode("utf-8"), max_nodes=101)
        try:
            load_capture_json_bytes(payload.encode("utf-8"), max_nodes=10)
        except BoundedJsonError:
            return
        raise AssertionError("node limit not enforced")

    def t11():
        payload = "[" + ",".join("1" for _ in range(20)) + "]"
        try:
            load_capture_json_bytes(payload.encode("utf-8"), max_container_items=5)
        except BoundedJsonError:
            return
        raise AssertionError("container item limit not enforced")

    def t12():
        try:
            load_capture_json_bytes(b'{"a": 1')
        except BoundedJsonError:
            return
        raise AssertionError("unbalanced input accepted")

    def t13():
        try:
            reject_output_overwrite(["/tmp/input.json"], "/tmp/input.json")
        except BoundedJsonError:
            return
        raise AssertionError("output overwrite not rejected")

    for name, fn in [
        ("valid_minimal", t1),
        ("utf8_bom", t2),
        ("utf16_le_bom", t3),
        ("utf16_be_bom", t4),
        ("duplicate_key", t5),
        ("nested_duplicate_key", t6),
        ("depth_limit", t7),
        ("size_limit", t8),
        ("empty_input", t9),
        ("node_limit", t10),
        ("container_item_limit", t11),
        ("unbalanced", t12),
        ("output_overwrite", t13),
    ]:
        check(name, fn)

    if failures:
        for f in failures:
            print("FAIL", f, file=sys.stderr)
        raise SystemExit(1)
    print("bounded_capture_json self-test: all checks passed")


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Bounded capture JSON loader (offline research utility)."
    )
    parser.add_argument("--input", "-i", help="Input JSON file path.")
    parser.add_argument("--output", "-o", help="Output JSON file path.")
    parser.add_argument(
        "--max-bytes", type=int, default=MAX_INPUT_BYTES_DEFAULT,
        help=f"Maximum input bytes (default {MAX_INPUT_BYTES_DEFAULT}).",
    )
    parser.add_argument(
        "--max-depth", type=int, default=MAX_DEPTH_DEFAULT,
        help=f"Maximum nesting depth (default {MAX_DEPTH_DEFAULT}).",
    )
    parser.add_argument(
        "--max-nodes", type=int, default=MAX_NODES_DEFAULT,
        help=f"Maximum parsed nodes (default {MAX_NODES_DEFAULT}).",
    )
    parser.add_argument(
        "--max-container-items", type=int, default=MAX_CONTAINER_ITEMS_DEFAULT,
        help=f"Maximum items per container (default {MAX_CONTAINER_ITEMS_DEFAULT}).",
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="Run synthetic self-tests and exit.",
    )
    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        _self_test()
        return 0

    if not args.input:
        parser.error("--input is required unless --self-test is used")

    result = load_capture_json_file(
        args.input,
        max_bytes=args.max_bytes,
        max_depth=args.max_depth,
        max_nodes=args.max_nodes,
        max_container_items=args.max_container_items,
    )

    if args.output:
        write_output_json([args.input], args.output, result.data)
    else:
        summary = {
            "encoding": result.encoding,
            "byte_count": result.byte_count,
            "node_count": result.node_count,
            "max_depth": result.max_depth,
        }
        print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
