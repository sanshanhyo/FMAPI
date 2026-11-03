> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry evidence: training-development lane

Status: static pinned-file probe only. One coordinator-approved read-only probe was run. It read only the pinned `game_plugin.dll` and printed bounded structural RTTI evidence. `liveRecordsRead=0`; no process memory, UI, game call, save, or network access was used.

## Pinned evidence

- `game_plugin.dll` SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Probe mode: `static-pinned-file`
- Probe result: `types=8`, `vtables=7`, `liveRecordsRead=0`, `outputTruncated=false`

## Confirmed RTTI types

| RVA | RTTI type |
|---|---|
| `0x5671B70` | `.?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@` |
| `0x5671BE0` | `.?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@` |
| `0x5676AF0` | `.?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@` |
| `0x5676B70` | `.?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@` |
| `0x567AEC0` | `.?AV?$_Func_impl_no_alloc@V<lambda_3>@?0??is_training_session_available@calendar_ui_handler_helper@game_plugin@@...` |
| `0x567AFE0` | `.?AV<lambda_3>@?0??is_training_session_available@calendar_ui_handler_helper@game_plugin@@...` |
| `0x567EC30` | `.?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER@game_plugin@@` |
| `0x5680AE0` | `.?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER_SERVER@game_plugin@@` |

## Confirmed vtables

| Vtable RVA | Type | Slot count |
|---|---|---:|
| `0x4AE5858` | `PERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER` | 12 |
| `0x4AE59C8` | `PERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER` | 12 |
| `0x4AF4BA8` | `PERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER` | 12 |
| `0x4AF4C68` | `PERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER` | 12 |
| `0x4AFC418` | `$_Func_impl_no_alloc` lambda for `is_training_session_available` | 12 |
| `0x4B0F1A8` | `CUSTOM_TRAINING_SCHEDULE_UI_HANDLER` | 12 |
| `0x4B14168` | `CUSTOM_TRAINING_SCHEDULE_UI_HANDLER_SERVER` | 12 |

Slot RVAs are recorded verbatim in `tools/research/entry_training_development.py`. Several slots are reported by the probe as `invalid` or non-RVA-looking values; those values are preserved as probe output and are not interpreted as valid RVAs or offsets.

## Confirmed RIP candidates

| Displacement | Function | Target vtable | Target type |
|---|---|---|---|
| `0x1E74C4` | `0x1E66D0` | `0x4AE5858` | `PERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER` |
| `0x1E862A` | `0x1E66D0` | `0x4AE59C8` | `PERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER` |
| `0x1ECF0A` | `0x1EC790` | `0x4AF4C68` | `PERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER` |
| `0x1EDD47` | `0x1EC790` | `0x4AF4BA8` | `PERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER` |
| `0x22D14F` | `0x22D0D0` | `0x4AFC418` | `$_Func_impl_no_alloc` lambda |
| `0x234B1A` | `0xFFFFFFFF` | `0x4AFC418` | `$_Func_impl_no_alloc` lambda |
| `0x234B3A` | `0xFFFFFFFF` | `0x4AFC418` | `$_Func_impl_no_alloc` lambda |
| `0x385310` | `0x385300` | `0x4B0F1A8` | `CUSTOM_TRAINING_SCHEDULE_UI_HANDLER` |
| `0x385C2A` | `0x3853B0` | `0x4B14168` | `CUSTOM_TRAINING_SCHEDULE_UI_HANDLER_SERVER` |

## Narrow business-object entry hypothesis

The confirmed names are UI handlers and helper types, not validated training business objects. They show that the pinned build has training-schedule UI/action surfaces for resting/cancelling rest, custom training schedules, and an `is_training_session_available` predicate over `TRAINING_SCHEDULE_WEEK`, `TRAINING_SESSION_TYPE`, `TRAINING_SESSION_INDEX`, `RECORD`, and `TEAM_BASE`.

No RTTI type for a training business object was returned by the probe. Therefore the status is `no-business-object-type-in-probe`. The observed UI-handler names are not evidence of a readable training data object, collection, field layout, UID linkage, or load semantics.

Proposed narrower names for the next static search:
- `TRAINING_SCHEDULE`
- `TRAINING_SCHEDULE_WEEK`
- `TRAINING_SESSION`
- `TRAINING_SESSION_TYPE`
- `TRAINING_SESSION_INDEX`
- `CUSTOM_TRAINING_SCHEDULE`
- `PERSON_REST_TRAINING_SCHEDULE`
- `PERSON_CANCEL_REST_TRAINING_SCHEDULE`
- `calendar_ui_handler_helper`
- `action_ui_handler_helper`

## Exact missing semantics

- No training business-object RTTI type or vtable is confirmed.
- No field offsets, collection entry, object size, base class, or vtable slot meaning is confirmed.
- No UID linkage to person/player/team/club/staff is confirmed.
- No training calendar, session, individual focus, coach grouping, load, attendance, performance, report, mentor, adaptation, attribute-change, long-term curve, or youth-output semantics are confirmed.
- No units, enums, ranges, date/time semantics, refresh timing, snapshot consistency, reload behavior, or multi-manager behavior are confirmed.
- No staff/coach object dependency is satisfied; STF-01 and STF-02 remain unstarted.
- The probe did not read any live record, so no value-level evidence exists.

## Next bounded read request

1. Static phase, no process:
   - Use the pinned `game_plugin.dll` and `global-metadata.dat` only.
   - Search metadata strings and RTTI names for the proposed narrower names.
   - Record only type/method/string names and offsets; do not add binaries or raw dumps.
   - Fail closed on fingerprint mismatch.
2. If a candidate business type is found, coordinator-approved bounded process phase:
   - Verify pinned hashes before every capture.
   - Read only manager/team/club identity and the candidate training collection.
   - Reuse the existing transport limits: 64 KiB per capture, at most 32 explicitly supplied UIDs, bounded rechecks, no all-registry scan.
   - No game calls, writes, UI, process control, state advancement, or private sample reads.
3. Validation:
   - Manual UI comparison by the coordinator in the same state.
   - Repeat-read and reload behavior recorded separately.
   - Missing or unavailable fields remain explicit; no simulated values.
   - Synthetic decoder tests for any new parser.

## Tool

`tools/research/entry_training_development.py` is a machine-readable manifest and validator for the confirmed type/vtable evidence above. It is an original offline scaffold, not SDK code, and is not a live reader. Unresolved offsets are absent/unknown rather than invented.
