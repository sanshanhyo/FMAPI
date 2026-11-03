> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property-entry research: board, facilities and history (`board-facilities-history`)

## Executed probe

Read-only static property-candidate probe command:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'board-facilities-history'
```

Result header:

```json
{"lane":"board-facilities-history","mode":"static-property-candidates","matches":10,"truncated":false,"liveRecordsRead":0}
```

- Pinned `game_plugin.dll` SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Live records read: `0`; no process memory was read.
- GameAssembly.dll was not re-fingerprinted by this probe; its pinned fingerprint remains `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`.

## Actual returned candidates

| Property name | Literal index | Slot RVA(s) | Name-based surface class |
|---|---:|---|---|
| `BoardConfidenceOverallGrade` | 3803 | `0x32AA778` | UI display/debug grade |
| `BoardConfidenceOverallString` | 3804 | `0x32AA840` | UI display string |
| `DebugBoardConfidenceModifier` | 6638 | `0x32B03C0` | Debug |
| `DebugBoardConfidenceOverallScore` | 6639 | `0x32B04B0` | Debug |
| `StadiumCapacityList` | 18078 | `0x32CE660` | UI list |
| `StadiumCapacityListCount` | 18079 | `0x32CE748` | UI list count |
| `TrainingFacilitiesLongString` | 20348 | `0x32B3AE8` | UI display string |
| `compStadiumCapacity` | 25019 | `0x33221D8` | Possible business-field name only |
| `o(stadiumCapacity)={0},{1} ` | 28596 | `0x32B7110` | Format string |
| `stadiumCapacity` | 30028 | `0x33087B0` | Possible business-field name only |

## UI/news/operations versus business fields

- `BoardConfidenceOverallGrade`, `BoardConfidenceOverallString`, `DebugBoardConfidenceModifier`, and `DebugBoardConfidenceOverallScore` are names with UI/debug surface wording. They are not proven board-evaluation, satisfaction, safety, or business-state fields.
- `StadiumCapacityList` and `StadiumCapacityListCount` are list/count surface names. They may be view-facing and do not prove a stadium-capacity collection or its semantics.
- `TrainingFacilitiesLongString` is a long-string surface name. It does not prove a facility rating, condition, upgrade, or business field.
- `compStadiumCapacity` and `stadiumCapacity` are the only candidates whose names resemble business fields, but their names alone do not establish property keys, owning entries, field offsets, units, or read routes.
- `o(stadiumCapacity)={0},{1} ` is a format string, not a property registration or field.
- No candidate has a proven native property key, RTTI type, vtable, function RVA, struct offset, enum, collection shape, or business meaning. All corresponding fields remain null in `tools/research/property_entry_board_facilities_history.py`.

## Coordinator dependency evidence used to sharpen this lane

- Current club2 TEAM pointers match their `TEAM_BASE` low23-bit index entries: 2/2.
- `NextFixture` (literal index 13696, slot RVA `0x330B698`, native key `0x6E654669`) first resolves `TEAM_BASE` context via global `0x5703768`, not fixture data.
- Consequence: stadium-capacity candidates must be inspected through club/team context, not fixture data. This dependency does not prove any board, facility, or history field and does not justify a live read.

## Machine-readable artifact

`tools/research/property_entry_board_facilities_history.py` records all 10 candidates, 10 ranked next registrations, the dependency evidence above, and explicit nulls for native keys, entry RVAs, function RVAs, and offsets. It provides `manifest()`, `validate()`, `--self-test`, and JSON validation. It performs no process, game, UI, network, or private-data access.

## No proven mapping

Exact no-match: no candidate has a proven property-to-entry mapping. Proven business fields: 0. Proven native keys: 0. Proven entry RVAs: 0. Proven field offsets: 0.

## Next bounded request

No live read is approved. The next request is static instruction-boundary inspection of the property registration blocks for slot RVAs `0x33087B0`, `0x33221D8`, and `0x32CE660` in the pinned `game_plugin.dll`/`GameAssembly.dll`, with explicit byte limits and no process access. A bounded live read is only justified after a candidate's native key and owning entry/context are proven and rechecked; until then all keys, entries, functions, and offsets remain null.

## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
