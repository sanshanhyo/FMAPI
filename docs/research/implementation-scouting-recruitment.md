# Implementation note: bounded capture JSON input loader

Artifact: tools/research/bounded_capture_json.py (standalone research utility).

## Purpose
Shared bounded loader for capture JSON inputs. Offline only; no process/game/UI/network/native/subprocess access. Enforces explicit limits before parsing and provides output-mode protection.

## Usage
- Self-test (synthetic only): python tools/research/bounded_capture_json.py --self-test
- Summarize an input: python tools/research/bounded_capture_json.py --input capture.json
- Write normalized output (refuses overwriting input): python tools/research/bounded_capture_json.py --input capture.json --output out.json

Library API:
- load_capture_json_bytes(raw, max_bytes=..., max_depth=..., max_nodes=..., max_container_items=...)
- load_capture_json_file(path, ...)
- reject_output_overwrite(inputs, output)
- write_output_json(inputs, output, data)

## Limits enforced
- Max input size: default 1 MiB (MAX_INPUT_BYTES_DEFAULT).
- Encoding: UTF-8 BOM (utf-8-sig), UTF-16 LE/BE BOM; UTF-32 BOM; no-BOM defaults to strict UTF-8 (UTF-16 without BOM not guessed).
- Duplicate JSON object keys rejected at any depth via object_pairs_hook.
- Nesting depth limit (default 64) via pre-parse bracket scanner respecting strings/escapes.
- Node count limit (default 50,000) and per-container item limit (default 10,000).
- Output mode refuses paths resolving to any input or any existing file.

## Evidence
- Synthetic self-test covers valid minimal JSON, UTF-8/UTF-16 BOMs, duplicate/nested duplicate keys, depth/size/node/container limits, unbalanced brackets, empty input, output overwrite rejection. Self-test uses in-memory bytes only; no real samples or files.
- No game/process/UI/live reads were performed; no runtime data is included.

## Limitations
- Depth is measured by a lightweight bracket scanner; it guards parse recursion but is not a full JSON validator.
- UTF-16 without BOM is not supported by design.
- Output refuses to overwrite any existing file (conservative).
- No schema validation or semantic interpretation of capture contents; only bounded JSON loading.
- Coordinator must run/build/verify; this note does not claim unrun tests passed.
