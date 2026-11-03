> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property-entry evidence: training-development lane

Status: static property-candidate probe only. One coordinator-approved read-only probe was run. It read only the pinned `game_plugin.dll` and printed bounded property-name/literal-index/slot evidence. `liveRecordsRead=0`; no process memory, UI, game call, save, network, or private capture access was used.

## Executed probe

Command family: reviewed fixed-file static property probe, lane `training-development`.

Result:
- `matches`: 35
- `truncated`: true
- `liveRecordsRead`: 0
- `returnedCandidates`: 24
- `imageBase`: `0x180000000`
- `game_plugin.dll` SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`

The probe returned 24 of 35 matches. The remaining 11 matches were not returned and are not fabricated here.

## Returned candidates

All returned names are metadata property names with literal indices and one slot RVA each. None has a proven native key, entry RVA, offset, business field, news field, or operation implementation.

| Rank | Property name | Literal index | Slot RVA | Classification |
|---:|---|---:|---|---|
| 1 | TrainingSchedule | 20370 | 0x32b50c8 | identifier-or-label-unverified |
| 2 | TrainingScheduleID | 20375 | 0x32b55b0 | identifier-or-label-unverified |
| 3 | TrainingScheduleName | 20377 | 0x32b5798 | identifier-or-label-unverified |
| 4 | TrainingScheduleCategory | 20371 | 0x32b51d0 | identifier-or-label-unverified |
| 5 | TrainingScheduleIndex | 20376 | 0x32b56a8 | identifier-or-label-unverified |
| 6 | CurrentTrainingSchedule | 6283 | 0x3337990 | ui-view-state |
| 7 | CustomTrainingSchedule | 6344 | 0x333b180 | ui-view-state |
| 8 | FirstTrainingSchedule | 8684 | 0x3324f00 | ui-view-state |
| 9 | FirstTrainingScheduleCategory | 8685 | 0x3324fe0 | ui-view-state |
| 10 | NextTrainingScheduleWeek | 13734 | 0x330d930 | ui-view-state |
| 11 | IsTrainingScheduleCategoryValid | 11581 | 0x332e6f0 | ui-validation |
| 12 | CanEditTrainingSchedule | 4313 | 0x32c81b8 | ui-capability |
| 13 | CanPasteTrainingWeek | 4336 | 0x32c96f8 | ui-capability |
| 14 | CanResetTrainingSchedule | 4355 | 0x32ca7f8 | ui-capability |
| 15 | ExportTrainingSchedule | 8142 | 0x33062d0 | operation |
| 16 | ExportTrainingScheduleType | 8143 | 0x33063b8 | operation |
| 17 | LoadTrainingScheduleType | 12244 | 0x32b8e60 | operation |
| 18 | ShowSimplifiedTrainingSchedule | 17677 | 0x32b7470 | ui-display-preference |
| 19 | DebugPotentialTrainingSchedules | 6879 | 0x32be638 | ui-debug |
| 20 | DebugTrainingSchedule | 7055 | 0x32c8c38 | ui-debug |
| 21 | DebugTrainingScheduleIndex | 7056 | 0x32c8d20 | ui-debug |
| 22 | TrainingScheduleCategoryDropdown | 20372 | 0x32b52d0 | ui-control |
| 23 | TrainingScheduleDropdown | 20373 | 0x32b53c8 | ui-control |
| 24 | TrainingScheduleDropdownName | 20374 | 0x32b54c0 | ui-control |

## UI, news, operations, or business fields?

All 24 names are training-schedule property names. Based on the names alone, they are not proven business fields. They are best classified as UI/view-model, capability, validation, display, debug, control, or operation properties. No name is news-related. No name is proven to be a readable training business field, collection entry, UID linkage, calendar value, session value, load value, attendance value, report, mentor relation, adaptation value, attribute-change value, long-term curve, or youth output.

The native-entry probe for this lane found only training-schedule UI handlers and helper types. Therefore the property names above are treated as UI/operation/view-model candidates until instruction-boundary disassembly assigns native keys and entry functions.

## Coordinator dependency evidence

- Current club2 TEAM pointers match their TEAM_BASE low23-bit index entries: 2/2.
- NextFixture literal 13696, slot `0x330B698`, native key `0x6E654669` first resolves TEAM_BASE context via global `0x5703768`, not fixtures.

Use this to sharpen the lane: if training-schedule entries are team-scoped, investigate them through TEAM_BASE/global context rather than fixture context. This does not prove any training property key or entry.

## Missing semantics

- No native key is assigned to any returned property candidate.
- No entry RVA or function is proven.
- No offset, object size, base class, collection entry, or UID linkage is proven.
- No business-field meaning, unit, enum, range, date/time semantics, refresh timing, snapshot consistency, reload behavior, or multi-manager behavior is proven.
- The probe returned only 24 of 35 matches.
- No live process, game UI, save, network, or private capture evidence was used.

## Next bounded live request

Only if coordinator-approved: in one loaded save, verify the current club2 TEAM_BASE pointer through global `0x5703768` and confirm it matches the current club's TEAM pointer low 23 bits using the established 2/2 precedent. Then, only for ranked candidates whose native keys have been proven by instruction-boundary disassembly, read at most 32 explicitly supplied training-schedule candidate property values. Limits: 64 KiB per capture, bounded rechecks, no all-registry scan, no writes, no game calls, no UI reads, no process control, no state advancement, no network access, and no private capture reads. Fail closed on fingerprint mismatch. If no training native key is proven, limit this request to team/club identity and TEAM_BASE context verification.

## Tool

`tools/research/property_entry_training_development.py` is a machine-readable manifest and validator for the returned property candidates above. It is an original offline scaffold, not SDK code, and is not a live reader. Unresolved native keys and offsets are null/unknown rather than invented.
