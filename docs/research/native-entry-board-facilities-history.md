> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry research: board, facilities and history (`board-facilities-history`)

## Probe execution

Read-only static probe command:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-probe.ps1' -Lane 'board-facilities-history'
```

Result header:

```json
{"lane":"board-facilities-history","mode":"static-pinned-file","types":6,"vtables":4,"liveRecordsRead":0,"outputTruncated":false}
```

- Pinned `game_plugin.dll` SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Live records read: `0`; no process memory was read.

## Confirmed type evidence (RTTI type descriptors)

| Type descriptor RVA | Mangled name |
|---|---|
| `0x569D5C0` | `.?AVEXTERN_CLUB@db@@` |
| `0x56A0540` | `.?AV?$DATABASE_TABLE@VCLUB@db@@@db@@` |
| `0x56A1E10` | `.?AVLEAGUE_BODY_CLUB@db@@` |
| `0x56A2310` | `.?AVCLUB@db@@` |
| `0x56CCF00` | `.?AV?$_Func_impl_no_alloc@V<lambda_0>@?0??assign_three_letter_name_to_created_club@fantasy_draft_utilities@@YAXAEBVCLUB@db@@@Z@_NAEBVSTRING@sicore@@@std@@` |
| `0x56CCFF0` | `.?AV<lambda_0>@?0??assign_three_letter_name_to_created_club@fantasy_draft_utilities@@YAXAEBVCLUB@db@@@Z@` |

## Confirmed vtable evidence

| Vtable RVA | Type | Slot RVAs |
|---|---|---|
| `0x4CA4E18` | `.?AV?$DATABASE_TABLE@VCLUB@db@@@db@@` | `0xD943A0, 0xD10D70, 0xD11140, 0xD11160, 0xD114F0, 0xD114E0, 0xCB0F10, 0xD11500, 0xD11510, 0xD10DC0, 0xC8E110, 0xD11700` |
| `0x4CDA1F8` | `.?AVCLUB@db@@` | `0x1120560, 0x1102950, 0x10F38C0, 0x10DF910, 0x1100D70, 0x414390, 0x4143A0, 0x11206D0, 0x111CEA0, 0x10B5610, 0x1100D60, 0x1144F60` |
| `0x4E205D8` | `.?AV?$_Func_impl_no_alloc@...@std@@` | `0x263BF70, 0x263BF90, 0x263BFB0, 0x263C090, 0x263C0A0, 0x263C0B0, invalid, invalid, 0x56CCEFE80000000, 0x4E2060E84E20628, invalid, 0x4E2063680000002` |
| `0x4F65538` | `.?AVLEAGUE_BODY_CLUB@db@@` | `0x388C600, 0x1102950, 0x10F38C0, 0x10DF910, 0x1100D70, 0x414390, 0x388C770, 0x11206D0, 0x111CEA0, 0x10B5610, 0x1100D60, 0x1144F60` |

## RIP candidate references

| Displacement | Function RVA | Target vtable RVA | Target type |
|---|---|---|---|
| `0xC711D5` | `0xC70F90` | `0x4CA4E18` | `.?AV?$DATABASE_TABLE@VCLUB@db@@@db@@` |
| `0xCB556E` | `0xCB41B0` | `0x4F65538` | `.?AVLEAGUE_BODY_CLUB@db@@` |
| `0xCC025A` | `0xCBEB80` | `0x4F65538` | `.?AVLEAGUE_BODY_CLUB@db@@` |
| `0x10A7954` | `0x10A7930` | `0x4CDA1F8` | `.?AVCLUB@db@@` |
| `0x10A7B11` | `0x10A7AF0` | `0x4CDA1F8` | `.?AVCLUB@db@@` |
| `0x2639BC5` | `0x2639A70` | `0x4E205D8` | `.?AV?$_Func_impl_no_alloc@...@std@@` |
| `0x263BF7A` | unresolved (`0xFFFFFFFF`) | `0x4E205D8` | `.?AV?$_Func_impl_no_alloc@...@std@@` |
| `0x263BF9A` | unresolved (`0xFFFFFFFF`) | `0x4E205D8` | `.?AV?$_Func_impl_no_alloc@...@std@@` |
| `0x9361C73` | `0x9361BE0` | `0x4F65538` | `.?AVLEAGUE_BODY_CLUB@db@@` |

## Narrow business-object entry hypothesis

No RTTI type name among the six returned types contains `BOARD`, `STADIUM`, `FACILITY`, `HISTORY`, `HONOUR`, `AWARD`, or `RECORD`. The confirmed entries are club-adjacent only: `EXTERN_CLUB`, `CLUB`, `DATABASE_TABLE<CLUB>`, and `LEAGUE_BODY_CLUB`, plus an unrelated `fantasy_draft_utilities` lambda for three-letter club-name assignment.

The narrowest candidate anchor is `LEAGUE_BODY_CLUB@db@@` (vtable `0x4F65538`): its vtable shares 10 of 12 slots with `CLUB@db@@` and differs only in slots 0 and 6, which is consistent with a club-derived/body composite type rather than a standalone board, facility, or history type. `DATABASE_TABLE<CLUB>` and `CLUB` remain generic anchors. This is a candidate entry only; it does not establish any board, facility, or history semantics.

## Exact missing semantics

- No dedicated board, stadium, facility, history, honour, award, or record RTTI type was present in this probe.
- No field offsets, struct layouts, property keys, enums, or collection shapes for board targets, season expectations, club vision, manager evaluation/safety, commitments, requests/resolutions, stadium capacity/location/condition, training/youth facility ratings, expansion/relocation progress, attendance/tickets, season history, honours, awards, or records.
- `LEAGUE_BODY_CLUB` slot differences are uninterpreted; it is not proven to represent board, facility, or history data.
- No live capture, UI comparison, reload, or multi-manager validation was performed.
- Club UID, club short-name, team UID, and manager identity evidence from other lanes are anchors only and do not imply board/facility/history data.

## Next bounded read request

1. Offline/static search only, within the pinned binary and with explicit byte limits, for RTTI type names and property keys containing `BOARD`, `STADIUM`, `FACILITY`, `HISTORY`, `HONOUR`, `AWARD`, `RECORD`, `VISION`, `SATISFACTION`, `COMMITMENT`, `REQUEST`, `RESOLUTION`, `EXPANSION`, `RELOCATION`, `ATTENDANCE`, `TICKET`, `UPGRADE`, `CAPACITY`, `CONDITION`, and `RATING`, plus narrower variants `LEAGUE_BODY_CLUB`, `CLUB_BODY`, `CLUB_FACILITIES`.
2. If candidate types or keys are found, schedule one bounded read-only capture against the current club/manager anchor with rechecks and no writes; maximum 64 KiB; no full process scan.
3. Do not infer board, facility, or history state from club UID, team UID, manager identity, messages, or UI similarity.

## No-match statement

Exact no-match: none of the six confirmed RTTI types is a board, stadium, facility, history, honour, award, or record type. Proposed narrower names for the next static search: `LEAGUE_BODY_CLUB`, `CLUB_BODY`, `BOARD`, `STADIUM`, `FACILITY`, `FACILITIES`, `HISTORY`, `HONOUR`, `AWARD`, `RECORD`, `VISION`, `SATISFACTION`, `COMMITMENT`, `REQUEST`, `RESOLUTION`, `EXPANSION`, `RELOCATION`, `ATTENDANCE`, `TICKET`, `UPGRADE`, `CAPACITY`, `CONDITION`, `RATING`.

## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
