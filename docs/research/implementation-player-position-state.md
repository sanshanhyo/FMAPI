# Implementation artifact: player position capture validator/summarizer

File: `tools/research/summarize_positions.py`

## Purpose

Pure offline Python validator/summarizer for FMAPI player-position captures. It consumes
one explicitly supplied capture JSON and emits aggregate counts, coverage and unknowns.
It performs no process, game-file, native, network or UI access and emits no player,
club or UID identities.

## Usage

```text
python tools/research/summarize_positions.py <capture.json> <new-private-output.json>
python tools/research/summarize_positions.py --self-test
```

- `<capture.json>`: a position capture produced by the existing bounded diagnostic
  (`--entity-links`), supplied by the coordinator. Must declare the pinned native hash.
- `<new-private-output.json>`: a new path outside the repository; existing files are refused.
- `--self-test`: runs synthetic validation only, including malformed inputs and the
  unsupported-profile guard.

## What it validates

- Native profile: `game_plugin.dll` SHA-256 must equal the pinned hash.
- Record count: 1..32.
- Explicit-UID match: `uidMatched == true`.
- Value range: all 15 bytes (goalkeeper familiarity plus 14 named familiarities) in 0..20.
- Natural mask: recomputed from the 14 named familiarities using threshold >=18 and the
  proven offset/bit mapping, compared with `positionFields.naturalPositionMask`.
- Skipped slot: `+0x151` (`SweeperCentreNotInUse`) is preserved and excluded from the mask.
- Goalkeeper business rule: `goalkeeperFamiliarity >= 15` matches
  `businessRuleIsGoalkeeper`.
- Position names: `positionNamesVerified == true`.
- Contract-linked club evidence: presence of employment fields and club type/UID for
  available records. This is reported separately and is not roster membership.
- `clubMembershipVerifiedHere` is reported as-is; it is expected to be false.

## Evidence basis

- `tools/FMAPI.MessageProbe/PositionFields.cs`: 14 named familiarities, natural threshold
  18, goalkeeper threshold 15, skipped `+0x151`, synthetic self-test.
- `tools/FMAPI.MessageProbe/EntityLinks.cs`: explicit UID lookup, actual-player type
  validation, `clubMembershipVerifiedHere=false`.
- `docs/research/native-entity-evidence.md`: native table/builder and metadata pairing.
- `docs/research/implementation-wave-input.md`: coordinator-confirmed employment schema
  (`status`, `contractType`, `kind`, `teamType`, `clubType`, `clubUid`, `source`,
  `atomicSnapshot`) and candidate `activeManager.clubTeams` structure.
- `tools/research/position_layout_probe.py`: independent static recovery of the 14
  offsets/bits.

## Output (aggregate only)

Counts for records, available, uidMatched, positionNamesVerified, values in range,
natural-mask consistency, goalkeeper-rule consistency, employment present,
contract-linked club, fully valid, and record errors. Plus coverage flags and an
explicit unknowns list. No identities are emitted.

## Limitations

- Does not read any process, file outside the supplied capture, or game binary.
- Does not establish roster membership; `clubMembershipVerifiedHere` must remain false.
- Does not resolve `employment.kind` semantics, preferred foot, current match/tactic
  position, display scaling or UI semantics.
- The coordinator's single-UID observation and 27/27 historical observation are not
  reproduced by this tool; they are attributed evidence only.
- Synthetic self-test covers structural validation only, not live data.
- No SDK, adapter, inventory or other implementation file was changed.

## Synthetic edge-case expected outputs (machine-readable)

These are the expected aggregate results for synthetic captures; no raw samples are included.

### Edge case A: valid single record (self-test fixture)

Input: one record, status=available, uidMatched=true, positionNamesVerified=true,
goalkeeperFamiliarity=15, otherPositionSlotsRaw=[20,18,17,1,18,5,5,5,18,18,18,18,5,5],
positionFields.naturalPositionMask recomputed, unusedSlot151Raw=20 (skipped),
businessRuleIsGoalkeeper=true, employment complete with atomicSnapshot=false,
clubMembershipVerifiedHere=false, activeManager.clubTeams notPlayerRoster=true.

Expected:
```json
{
  "status": "validated",
  "counts": {
    "records": 1,
    "available": 1,
    "uidMatched": 1,
    "positionNamesVerified": 1,
    "valuesInRange0To20": 1,
    "naturalMaskConsistent": 1,
    "goalkeeperRuleConsistent": 1,
    "employmentPresent": 1,
    "contractLinkedClub": 1,
    "fullyValid": 1,
    "recordErrors": 0
  },
  "clubMembershipVerifiedHere": false,
  "clubMembershipExpectedFalse": true,
  "activeManagerClubTeams": null
}
```

### Edge case B: malformed record

Input: goalkeeperFamiliarity=21, one slot=21, uidMatched=false, atomicSnapshot=true,
clubMembershipVerifiedHere=true.

Expected:
```json
{
  "status": "partial",
  "counts": {
    "records": 1,
    "available": 1,
    "uidMatched": 0,
    "positionNamesVerified": 1,
    "valuesInRange0To20": 0,
    "naturalMaskConsistent": 0,
    "goalkeeperRuleConsistent": 1,
    "employmentPresent": 1,
    "contractLinkedClub": 0,
    "fullyValid": 0,
    "recordErrors": 4
  },
  "clubMembershipVerifiedHere": true,
  "clubMembershipExpectedFalse": true
}
```

Note: recordErrors is the sum of positionErrors and employmentErrors. For Edge case B:
positionErrors = ["value outside 0..20", "natural mask inconsistent", "skipped slot mismatch"] (3)
and employmentErrors = ["employment claims atomic snapshot (not supported)"] (1), total 4.

### Edge case C: unsupported profile

Input: binarySha256 != pinned hash.

Expected: ValueError "unsupported native binary profile"; no output file written.

### Edge case D: output path inside repository

Expected: ValueError "output must be outside repository"; no file written.

### Edge case E: missing employment

Input: valid position record with employment absent.

Expected: position validity can still be true; employmentPresent=0; contractLinkedClub=0;
employmentErrors=["employment absent"]; recordErrors=1 (from employment only).
