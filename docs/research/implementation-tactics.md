# Implementation tactics: bounded PE vtable-function locator

## Artifact

- `tools/research/locate_vtable_function.py` — original bounded offline PE locator.
- No other implementation, SDK, inventory, or UI files were changed.

## Purpose

Locate vtables in a PE where a specified slot contains an exact target function RVA, and annotate each candidate with its validated Complete Object Locator (COL) and RTTI type name. This supports identifying underlying business/tactic receiver types from a known function RVA without reading UI instances or process memory.

## Usage

```text
python tools/research/locate_vtable_function.py <pe> <func_rva_hex> <slot_index> [--rtti SUBSTR] [--cap N] [--scan-cap N] [--output FILE]
python tools/research/locate_vtable_function.py --self-test
```

Examples:

```text
python tools/research/locate_vtable_function.py game_plugin.dll 0x123456 0 --rtti Tactic --cap 50
python tools/research/locate_vtable_function.py --self-test
```

Inputs and bounds:
- `pe`: a local PE file (PE32+ / x64 focus). Opened as data only.
- `func_rva`: exact function RVA in hexadecimal. No fuzzy/partial matching.
- `slot`: zero-based vtable slot index.
- `--cap`: maximum candidates reported (1..10000, default 100).
- `--scan-cap`: maximum 8-aligned positions examined (1..10000000, default 2000000).
- `--rtti`: optional case-insensitive RTTI name substring filter.

Output is JSON with image base, target RVA, scan counts, truncation flags, and candidate list (vtable RVA, COL RVA, slot RVA, slot count, RTTI name). No raw process data, names from saves, or credentials are involved.

## Method

1. Parse PE headers and sections.
2. Iterate 8-aligned positions in non-code (data) sections.
3. For each position, derive `vtable_base = position - slot*8` and `col = vtable_base - 8`.
4. Validate COL: signature == 1, primary offset == 0, `pSelf` equals COL RVA, type descriptor and class descriptor RVAs resolve to sections, and the RTTI name decodes as an ASCII `.?A...` symbol.
5. Require the slot value to equal `imageBase + func_rva`.
6. Require `slot_index < vtable_slot_count`, where the count is the number of contiguous code pointers starting at `vtable_base`, stopping at the first non-code or section boundary. No slots beyond that boundary are read.
7. Deduplicate by vtable base and cap results.

## Evidence and limitations

- This is a pure static PE-analysis aid. It does not open a process, call game functions, read UI, or access network/external directories.
- It assumes MSVC x64 RTTI Complete Object Locator layout with `pSelf`. PE32 (32-bit) is rejected.
- It reports candidate vtables only; COL/RTTI validation reduces false positives but does not prove a business/tactic relationship. Each candidate must be confirmed by instruction-boundary disassembly and, if needed, a separately authorized bounded live read.
- Vtable boundaries are inferred from contiguous code pointers; unusual layouts (gaps, data slots) may truncate counts.
- No real game binaries, samples, or captures are bundled. Synthetic `--self-test` constructs a minimal in-memory PE and checks one candidate, boundary count, slot-index rejection, and RTTI filtering. Those checks are synthetic and do not represent game data or a compatibility claim.
- No live read was performed in this wave.
