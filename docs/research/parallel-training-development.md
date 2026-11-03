# Parallel research: training and development (TRA-01, TRA-02, TRA-03)

Status: offline audit only. Branch: `research/parallel-training-development`. IDs: TRA-01, TRA-02, TRA-03. No live process, game install, UI, private captures, credentials, network, bash/subprocess, scan, injection, native function call, game/save write, match advancement, subagent, git push or release was used. No live read was performed in this wave.

## 1. Scope and dependency position

TRA rows are P1/P2 read-only discovery tasks from `docs/research/interface-inventory.md` and `docs/research/data-discovery-todo.md`. They are not implemented by FMAPI. Their stated dependencies are not currently satisfied:

- TRA-01 depends on PLY-01 and STF-02.
- TRA-02 depends on TRA-01.
- TRA-03 depends on TRA-02 and YTH-02.
- STF-02 depends on STF-01, which depends on IDX-01 and CLB-01.
- YTH-02 depends on YTH-01 and SCT-02.
- All rows also depend on ENV-01 and LOC-01 for build/session/date/unit baselines, and on IDX-01/MGR-01/CLB-01 for identity and scope.

Current inventory status for all three IDs remains "未开始": no implementation evidence was found. Indirect provenance below is not training data and does not change that status.

## 2. Audit result

No training-specific source, type name, offset, field decoder, capture, or test was found in this worktree. Searches for training/staff/coach/workload/development/mentor/session/calendar/course terms found only generic documentation references and unrelated host/session code. The SDK/Core mock skeleton is intentionally not counted as native implementation. No candidate training object was identified.

Reusable, non-training provenance that can support later TRA work:

| Source location | What it establishes | Relevance to TRA | Limit |
|---|---|---|---|
| `tools/FMAPI.MessageProbe/EntityLinks.cs:72-123` (`CaptureEntityLinks`) | Native current-manager selection global at module RVA `0x56F32C8`; human manager collection at `0x56F3008`; `FULL_CONTRACT -> TEAM` at contract `+0x10`; `TEAM -> CLUB` at team `+0x30`; contract kind byte at `+0x26`. | Provides manager/team/club scope for future training queries. | Single observed session; no active-user stability across reloads/hotseat; no atomic snapshot. |
| `tools/FMAPI.MessageProbe/EntityLinks.cs:37-71` (`ReadRequestedPositions`) | `DATABASE_TABLE<PERSON>` at module RVA `0x5703738`; ordered UID lookup by record `+0x0C`; exact `ACTUAL_PLAYER` conversion and 15 position bytes at player `+0x150..+0x15E`. | Provides player UID and position familiarity inputs if training data references player UIDs. | Club membership is input provenance, not rebuilt here; no training fields. |
| `tools/FMAPI.MessageProbe/PositionFields.cs:1-37` | Named 14 familiarity fields and natural-position mask using threshold 18; goalkeeper business rule threshold 15; reserved slot `+0x151` excluded. | Candidate input for role/position-related training grouping only. | Field meanings are position familiarity, not training role/load. |
| `docs/research/native-entity-evidence.md` | Binary fingerprints and instruction-boundary evidence for manager selection and goalkeeper predicate. | Establishes pinned binary profile required before any future live read. | No training-specific evidence. |
| `docs/research/manager-player-links-checkpoint.md` | Manager employment chain and 27-UID position capture limits. | Scope/identity baseline for future training association. | No training data captured. |
| `docs/research/message-reader-checkpoint.md` | Message/news object and localization evidence. | Possible future source of training-related inbox messages, not training state. | Message body formatting remains partial; no training semantics. |
| `tools/research/position_layout_probe.py` | Offline static verification of pinned position table/metadata. | Pattern for future static training metadata verification. | Does not inspect training. |

No staff/coach implementation exists. STF-01 and STF-02 remain "未开始", so training coach grouping/workload cannot yet be associated with verified staff objects.

## 3. Pinned version and hash baseline

All future TRA work must fail closed unless these match:

- `game_plugin.dll` SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- `GameAssembly.dll` SHA-256: `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`
- Metadata SHA-256: `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`
- Installed metadata signature/version: `0xFAB11BAF` / `39`
- UnityPlayer product/file: `6000.3.18f1-custom` (`96cdb67fb884`) / `6000.3.18.9883062`
- Observed FM producer manifest build cited in manager-player-links checkpoint: `21bfd30`
- Local research commits cited in inventory/checkpoint: `10a5724`, `d1f5177`, `99aba1d` (unpushed); remote research branch `1c0c561`; main `9cdd806`; CI commit `48331a5`
- Native RVAs/offsets cited above are valid only for the pinned `game_plugin.dll` hash.

## 4. Field meaning and candidate inventory

No training field has been observed. The following are target fields derived from task definitions, with status `missing` unless a later capture validates them. Raw and decoded values must remain separate; unknown units/enums remain unknown.

### TRA-01: team training calendar, sessions, individual training, role/focus, coach grouping, planned load

| Candidate field group | Candidate fields | Raw/decoded expectation | Unit/status |
|---|---|---|---|
| Training calendar | team training days, rest days, session schedule, date/time boundaries | Unknown native representation; must distinguish game date vs real capture time | missing; date semantics unverified |
| Team sessions | session type/category, duration, intensity, location/facility reference, squad scope | Unknown enum; no values assigned | missing |
| Individual training | player UID, role/position focus, personal focus, additional focus, intensity | Must join to PLY-01 UIDs; no field found | missing |
| Coach grouping | coach/staff UID, group assignment, responsibility, workload share | Blocked by STF-01/STF-02; no staff objects verified | missing |
| Planned load | planned load/fatigue cost, recovery expectation, load category | Unknown whether readable; no unit or scale | missing |
| Scope | current team only vs all managed teams; loaded save scope | Must be explicit; no evidence | missing |

### TRA-02: training performance, attendance, development reports, mentor/guidance, adaptation, attribute-change evidence

| Candidate field group | Candidate fields | Raw/decoded expectation | Unit/status |
|---|---|---|---|
| Performance | session rating/performance score, progress score, improvement/decline indicator | Unknown scale; no observed values | missing |
| Attendance | present/absent/excused, injury/availability reason, session count | Must not infer availability from absence | missing |
| Development reports | report date, author/coach, summary/structured fields, player UID | No report object or template found | missing |
| Mentor/guidance | mentor UID, mentee UID, group, start/end, status | No mentor relation found; depends on staff/player UIDs | missing |
| Adaptation | adaptation score/status, role adaptation, new-club/new-position adaptation | Unknown enum/scale | missing |
| Attribute change | attribute delta, period, source attribution | Must separate correlation from mechanism; no evidence | missing |

### TRA-03: long-term development curve, youth training output, training impact readable results

| Candidate field group | Candidate fields | Raw/decoded expectation | Unit/status |
|---|---|---|---|
| Development curve | time series of ability/performance/training load, sampling cadence, gaps | Unknown storage; may be historical only | missing |
| Youth training output | youth squad UIDs, generated/promoted players, training outcome | Blocked by YTH-01/YTH-02 | missing |
| Training impact | measured or attributed effect of training on attributes/performance | Must not convert correlation to mechanism | missing |
| Scope | current save only vs historical seasons; loaded vs unloaded data | Unknown | missing |

## 5. Evidence strength

- Direct training evidence: none.
- Candidate indirect provenance: manager/team/club and player UID/position sources listed in section 2. These are not training observations.
- Staff/coach evidence: none (STF-01/STF-02 unstarted).
- Youth evidence: none (YTH-01/YTH-02 unstarted).
- No runtime value, UI comparison, reload test, or multi-manager result exists for any TRA field.

## 6. Missing dependencies and blockers

1. STF-01 and STF-02 are unstarted; without verified staff identities and coach assignment, coach grouping/workload cannot be interpreted.
2. PLY-01 provides player UID/name/age/team/club baseline, but training-specific player linkage is unverified.
3. CLB-01/IDX-01/MGR-01 provide club/team/manager identity; training scope and ownership are unverified.
4. YTH-01/YTH-02 are unstarted; TRA-03 cannot be evaluated.
5. ENV-01/LOC-01 baselines are required for date/unit consistency; training date and load units are undefined.
6. No candidate native type or offset for training has been found; static metadata search has not been performed in this wave.

## 7. Unknown semantics

- Whether team training schedules are stored as calendar objects, arrays, bitmasks, or computed from other state.
- Whether individual training focus is a player field, a team assignment, or a derived recommendation.
- Coach grouping/workload representation and whether workload values are raw weights, percentages, or enum levels.
- Training load units and whether load is planned vs actual.
- Attendance and development report availability and retention.
- Mentor/guidance object model and UID stability.
- Adaptation score semantics and valid range.
- Attribute-change attribution and whether training influence is stored or only observed post hoc.
- Long-term development storage, sampling cadence, and historical availability.
- Youth training output linkage and whether it is global or club-scoped.
- Refresh timing, snapshot consistency, and whether reads are safe during date advancement/match state.
- Multi-manager/hotseat and reload behavior for training data.

## 8. Minimal bounded follow-up read plan

This plan is for coordinator scheduling; it does not perform any read now.

1. Offline static phase (no process):
   - If the pinned `game_plugin.dll` and `global-metadata.dat` are available to an authorized local researcher, use the existing bounded static approach (`tools/research/position_layout_probe.py` pattern) to search metadata strings/types for training-related identifiers.
   - Record only type/method/string names and offsets; do not add binaries or raw dumps to the repository.
   - Fail closed on fingerprint mismatch.
2. Dependency phase:
   - Complete STF-01/STF-02 first to obtain verified staff/coach objects and assignments.
   - Complete PLY-01/CLB-01/MGR-01 validation before associating training with players/clubs.
3. Minimal live phase (coordinator-approved, one process):
   - Verify pinned hashes before every capture.
   - Read-only only; no game calls, writes, UI, process control, or state advancement.
   - Reuse `tools/FMAPI.MessageProbe` transport limits: 64 KiB per capture, at most 32 explicitly supplied UIDs, bounded rechecks, no all-registry scan.
   - First target: manager/team/club identity and a candidate training collection if static phase found one.
   - Then: calendar/session fields, individual focus, coach grouping, load.
   - Then: performance/attendance/report/mentor/adaptation/attribute-change evidence.
   - Then: historical/long-term/youth outputs, only after TRA-02 and YTH-02.
4. Validation:
   - Manual UI comparison by the coordinator in the same state, without automation.
   - Repeat-read and reload behavior recorded separately.
   - Missing/unavailable fields remain explicit; no simulated values.
   - Synthetic decoder tests for any new parser.

## 9. Completion status

- Completed: none for TRA-01/02/03. No training-specific implementation or evidence exists.
- Candidate: indirect manager/team/club and player UID/position provenance only; not training data.
- Missing: all TRA-01/02/03 fields, staff/coach dependency, youth dependency, native training objects/offsets, semantics, units, validation, and live-read evidence.

No live read was performed in this wave.
