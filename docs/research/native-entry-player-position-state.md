> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry evidence: player-position-state

Status: offline static evidence plus original manifest/validator scaffold. No live process read, game install access, UI access, memory write, injection, native call, match advance, network access or private sample read was performed for this document. The only executed probe is the coordinator-approved read-only command recorded below.

## 1. Executed probe evidence

Command (run once, exactly as authorized):

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-probe.ps1' -Lane 'player-position-state'
```

Result:

```json
{"lane":"player-position-state","mode":"static-pinned-file","types":3,"vtables":3,"liveRecordsRead":0,"outputTruncated":false}
SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F ImageBase 0x180000000
TYPE 0x569D2E0 .?AVEXTERN_ACTUAL_PLAYER@db@@
TYPE 0x56AB140 .?AV?$_Func_base@HAEAVACTUAL_PLAYER@db@@@std@@
TYPE 0x56B8BF0 .?AVACTUAL_PLAYER@db@@
VTABLE 0x4D27228 .?AVACTUAL_PLAYER@db@@ slots=0x16361F0,0x15D4F70,0x15F7060,0x15F7070,0x15D4F80,0x15D4F60,0x15D4F50,0x15F7F00,0x15EAF40,0x15EB200,0x15EAF30,0x15E1760
VTABLE 0x4D27708 .?AVACTUAL_PLAYER@db@@ slots=0x15E9950,0x19260A0,0x16336A0,0x3012190,0x161FA20,0x161FA10,0x161FA30,0x16336B0,0x16336F0,0x4D28090,0x1633700,0x161D860
VTABLE 0x4D27758 .?AVACTUAL_PLAYER@db@@ slots=0x1633700,0x161D860,0x160E7A0,0x15E9960,0x161DDD0,0x1633890,0x16338C0,0x5E6920,0xF80D60,0xF75E90,0x4143D0,0xF6E0A0
RIP_CANDIDATE displacement=0x15C52B3 function=0x15C5210 target=0x4D27228 .?AVACTUAL_PLAYER@db@@
RIP_CANDIDATE displacement=0x15C52C5 function=0x15C5210 target=0x4D27708 .?AVACTUAL_PLAYER@db@@
RIP_CANDIDATE displacement=0x15C52D9 function=0x15C5210 target=0x4D27758 .?AVACTUAL_PLAYER@db@@
RIP_CANDIDATE displacement=0x15C55D2 function=0x15C55C0 target=0x4D27228 .?AVACTUAL_PLAYER@db@@
RIP_CANDIDATE displacement=0x15C55EB function=0x15C55C0 target=0x4D27708 .?AVACTUAL_PLAYER@db@@
RIP_CANDIDATE displacement=0x15C5605 function=0x15C55C0 target=0x4D27758 .?AVACTUAL_PLAYER@db@@
```

Interpretation limits:

- `liveRecordsRead=0`. This is structural RTTI/vtable evidence only.
- The three vtable rows are all RTTI-named `.?AVACTUAL_PLAYER@db@@`; they are distinct vtable objects at distinct RVAs.
- The six RIP rows are static RIP-relative references only. Instruction boundaries and function semantics are not established by this probe.
- No object field offsets, slot names, callable targets, or business rules are established by this probe.

## 2. Confirmed type evidence

| RTTI RVA | Type name |
|---|---|
| `0x569D2E0` | `.?AVEXTERN_ACTUAL_PLAYER@db@@` |
| `0x56AB140` | `.?AV?$_Func_base@HAEAVACTUAL_PLAYER@db@@@std@@` |
| `0x56B8BF0` | `.?AVACTUAL_PLAYER@db@@` |

No RTTI type named for a position, position state, player position, or position-state entry was present in this probe output. Proposed narrower names for any future type search are `ACTUAL_PLAYER`, `EXTERN_ACTUAL_PLAYER`, and `?$_Func_base@HAEAVACTUAL_PLAYER@db@@`.

## 3. Confirmed vtable evidence

All three vtables are owned by RTTI type `.?AVACTUAL_PLAYER@db@@`. Their slot values are module-relative RVAs from the probe output and are reproduced exactly.

| Vtable RVA | Slot RVAs |
|---|---|
| `0x4D27228` | `0x16361F0, 0x15D4F70, 0x15F7060, 0x15F7070, 0x15D4F80, 0x15D4F60, 0x15D4F50, 0x15F7F00, 0x15EAF40, 0x15EB200, 0x15EAF30, 0x15E1760` |
| `0x4D27708` | `0x15E9950, 0x19260A0, 0x16336A0, 0x3012190, 0x161FA20, 0x161FA10, 0x161FA30, 0x16336B0, 0x16336F0, 0x4D28090, 0x1633700, 0x161D860` |
| `0x4D27758` | `0x1633700, 0x161D860, 0x160E7A0, 0x15E9960, 0x161DDD0, 0x1633890, 0x16338C0, 0x5E6920, 0xF80D60, 0xF75E90, 0x4143D0, 0xF6E0A0` |

Slot names, slot ordinals, object layouts, and any field offsets are unresolved and are deliberately not present in the machine-readable manifest.

## 4. Candidate entry functions

Two functions contain RIP-relative references to all three confirmed vtables.

| Function RVA | Displacement | Target vtable RVA |
|---|---|---|
| `0x15C5210` | `0x15C52B3` | `0x4D27228` |
| `0x15C5210` | `0x15C52C5` | `0x4D27708` |
| `0x15C5210` | `0x15C52D9` | `0x4D27758` |
| `0x15C55C0` | `0x15C55D2` | `0x4D27228` |
| `0x15C55C0` | `0x15C55EB` | `0x4D27708` |
| `0x15C55C0` | `0x15C5605` | `0x4D27758` |

These are candidate entry points only. Their roles, argument types, return types, and whether they construct, query, convert, or guard `ACTUAL_PLAYER` objects are unresolved.

## 5. Narrow business-object entry hypothesis

Hypothesis: `EXTERN_ACTUAL_PLAYER` and `std::_Func_base<int, ACTUAL_PLAYER&>` are adjacent to an `ACTUAL_PLAYER` business-object boundary, and the two RIP-candidate functions at `0x15C5210` and `0x15C55C0` are the narrowest currently known static entry points into that boundary because each references all three confirmed `ACTUAL_PLAYER` vtables. The three vtables likely represent distinct `ACTUAL_PLAYER` object forms or base/derived layouts used by that boundary.

This is a hypothesis only. It does not establish:

- which function is an entry point versus a helper, guard, factory, converter, or destructor-related routine;
- whether `EXTERN_ACTUAL_PLAYER` wraps, owns, borrows, or merely names an `ACTUAL_PLAYER`;
- what `std::_Func_base<int, ACTUAL_PLAYER&>` is called with or returns in game context;
- any object field offset, slot semantics, position field, employment field, condition field, or availability field;
- any roster, team, club, match, tactic, or UI relationship.

## 6. Exact missing semantics

- Instruction-boundary disassembly of `0x15C5210` and `0x15C55C0`, including call targets and stack/argument usage.
- Type relationship between `EXTERN_ACTUAL_PLAYER`, `std::_Func_base<int, ACTUAL_PLAYER&>`, and the three `ACTUAL_PLAYER` vtables.
- Slot names and calling conventions for all 36 slot RVAs.
- Any confirmed object field offsets. In particular, no position, condition, sharpness, fatigue, morale, happiness, injury, medical, preferred-foot, nationality, age-basis, name, DOB, height, or team/club offset may be invented from this evidence.
- Whether either candidate function is reachable in the observed session and under what state.
- Whether the candidate functions are stable across reloads, selection changes, or different saves.
- Any UI or external-reader comparison for values derived from this boundary.

## 7. No-match handling

This probe did not emit a position-specific or position-state-specific RTTI type. The manifest validator therefore records an exact no-match for names such as `PLAYER_POSITION_STATE` and proposes the narrower confirmed names `ACTUAL_PLAYER`, `EXTERN_ACTUAL_PLAYER`, and `?$_Func_base@HAEAVACTUAL_PLAYER@db@@`. It does not create a live reader or synthetic field map for an unmatched type.

## 8. Next bounded read request

Request one coordinator-approved bounded static read before any process read:

1. Offline disassembly only of RVA `0x15C5210` and `0x15C55C0` in the pinned `game_plugin.dll`, with instruction boundaries and direct call targets, under the existing static PE tooling.
2. If that disassembly shows a safe, bounded object read, request a later process probe limited to at most 32 already validated `ACTUAL_PLAYER` entries and the existing 64 KiB capture budget.
3. Any new field must be added only with a proven getter/offset path and same-save comparison. Until then, unresolved offsets remain absent or `unknown` in `tools/research/entry_player_position_state.py`.

## 9. Machine-readable scaffold

`tools/research/entry_player_position_state.py` implements the manifest/validator for this evidence. It contains only the confirmed type RVAs, vtable RVAs and slot RVAs, and candidate function RVAs/displacements from this probe. It rejects unsupported native hashes, invented offsets, unconfirmed types, unconfirmed vtables, and unconfirmed entry candidates. Run:

```text
python tools/research/entry_player_position_state.py --self-test
```

## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
