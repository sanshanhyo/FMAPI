# Implementation wave: bounded PE property-key reference locator

Task lane: FIX-01 / CMP-01 / MAT-01 / MAT-02 support tooling (offline only).

## Artifact

- File: `tools/research/locate_property_key.py`
- Purpose: aid future fixture/registration work by locating explicit 32-bit property-key constants in a pinned PE image.
- It is not a fixture reader, does not identify fixtures/competitions/match statistics, and does not claim any game data.

## Usage

```text
python tools/research/locate_property_key.py <pe.dll> --key 0x78754F31 --key 0x3324C50
python tools/research/locate_property_key.py <pe.dll> --keys-file keys.txt --max-candidates 128
python tools/research/locate_property_key.py --self-test
```

- `--expected-hash` defaults to the pinned `game_plugin.dll` SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`.
- `--max-candidates` caps total returned candidates (default 256).
- Output is JSON with per-candidate section, RVA, file offset, `.pdata` containment annotation, and a flag that candidate immediate bytes are not confirmed instructions.

## Evidence and limitations

- Inputs: one explicitly supplied PE file, explicit 32-bit keys, pinned hash. No process, game installation, UI, private capture, credentials, network, or subprocess access.
- Executable sections only (`IMAGE_SCN_MEM_EXECUTE`); non-executable data is ignored.
- `.pdata` RUNTIME_FUNCTION ranges are parsed and used only to annotate containment; absence of a function range is reported, not treated as proof.
- Hits are candidate byte occurrences. Disassembly is required before treating any as an instruction operand or assigning semantics.
- This tool does not identify fixtures, competitions, seasons, tables, matches, appearances, ratings, or statistics.
- Synthetic self-test covers PE parsing, pdata containment, scanning, and key parsing on an in-memory synthetic PE; it is not a real-game validation.
- Coordinator will execute/build/verify; no claim of an unrun test or new game read is made here.
- No SDK, UI, inventory, or other implementation files were modified by this wave.
