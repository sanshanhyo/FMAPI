# Implementation note: offline encoded-literal slot locator

Artifact: `tools/research/find_literal_slots.py`

## Purpose

Offline locator for exact encoded literal slots in the pinned `GameAssembly.dll` PE. It verifies the pinned GameAssembly SHA-256, parses PE sections, searches 8-byte-aligned occurrences of `0xA0000000 | ((index * 2) | 1)`, and maps each file offset to an RVA. It reports `unique`, `ambiguous`, or `missing` per requested index.

## Usage

```text
python tools/research/find_literal_slots.py <GameAssembly.dll> <index> [<index> ...] [--output <json-path>]
python tools/research/find_literal_slots.py --self-test
```

- At most 32 explicit indices are accepted.
- Each index must be in `0..0x07FFFFFF`, the representable range for `0xA0000000 | ((index << 1) | 1)` without usage-kind overlap.
- Output is JSON with per-index status, match count, file offsets, RVAs, and search bounds.
- Known control: index `9070` encodes to `0xA00046DD` and is expected to resolve to RVA `0x333AD88` in the pinned binary.

## Evidence basis

- Pinned hash: `GameAssembly.dll` SHA-256 `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`.
- Encoding and expected slot from `docs/research/native-entity-evidence.md`: GameCurrentManager literal index 9070 maps to GameAssembly encoded literal slot RVA `0x333AD88`.
- PE section offset-to-RVA mapping is derived only from the supplied PE headers.

## Synthetic checks

`--self-test` checks encoding, PE offset/RVA mapping, unique/ambiguous/missing search behavior, invalid index rejection, and the 32-index limit. These are synthetic checks only; no game file or process is used.

## Limitations

- This tool performs no live process access, native calls, UI reads, network access, or writes to the input PE.
- It does not establish runtime meaning, ownership, or stability of any located slot.
- It only searches file-backed, aligned 8-byte values; unaligned or non-file-backed matches are not reported.
- It verifies the pinned GameAssembly fingerprint but cannot verify game build compatibility beyond that hash.
- Coordinator execution/build/verification remains required; this note does not claim unrun tests passed.
