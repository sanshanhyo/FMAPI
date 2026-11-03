# Fixtures, competitions and match statistics: offline audit

Task IDs: FIX-01, CMP-01, MAT-01, MAT-02.

Status: offline source/evidence audit only. No SDK design, no adapter implementation, no live read, no process/game install/UI/private-capture/network access. No bash or subprocess command was run, and no commit, push or release was performed.

## Scope and provenance

- Task brief pins the FMAPI/documentation upstream at `01b53c5` and the local research base at `99aba1d`; this worktree is branch `research/parallel-fixtures-matches`. Those commit identifiers are accepted as task inputs and were not re-derived here because this wave prohibited subprocess and out-of-worktree access.
- Read for this audit: `AGENTS.md`, `docs/research/interface-inventory.md`, `docs/research/data-discovery-todo.md`, `docs/adr/0003-share-verified-match-reader.md`, `docs/compatibility.md`, `docs/research/message-reader-checkpoint.md`, `docs/research/manager-player-links-checkpoint.md`, `docs/research/native-entity-evidence.md`, and the checked-in `src/`, `tools/`, `tests/`, `examples/` trees.
- Inherited native profile, not newly measured: `game_plugin.dll` SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`; `GameAssembly.dll` SHA-256 `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`; metadata signature/version `0xFAB11BAF` / 39 (`docs/research/native-entity-evidence.md:5-9`). The separate match report identifies FMMatchLens upstream commit `276d17ff677f90a0f13a75565c7af7d855756768` (`docs/adr/0003-share-verified-match-reader.md:9`).
- Nothing in this file is a new runtime result. No names, UID lists, raw samples, pointers, captures, saves, or message prose are included.

Evidence strength used below:

- `E0`: no implementation or symbol located.
- `E1`: related symbol/offset only; no field schema proven.
- `E2`: third-party or user report of a field, no FMAPI-reproducible source or capture in this worktree.
- `E3`: checked-in reproducible source/offset with a defined layout.
- `E4`: repeated live read plus UI/known-fact validation. Nothing in this audit reaches E4.

## Source map: what actually exists

| Location | What it contains | Relevance and limit |
|---|---|---|
| `docs/adr/0003-share-verified-match-reader.md:7-9` | Reported FA native match hook: team identities, score updates, ticks, 50 player identities/names/positions, 22 players on the pitch; user confirmed score, shots, shots on target, xG and corners, plus attributes, height and birth date. | Closest existing evidence for MAT-01/MAT-02. It is a reported observation from the FA session, explicitly not an FMAPI test. It does not define a stable field list, offsets, dimensions or units. |
| `docs/adr/0003-share-verified-match-reader.md:58-67` | SHA-256 identifiers for inspected FA source files such as `GameMatchTickHook.cs`, `GamePluginBuildCatalog.cs`, `MemoryReader.cs`, `Offsets.cs`, `PlayerUidReader.cs`. | Identifies a source snapshot for later reconciliation. Those files are not present in this worktree. The ADR says extraction is paused pending provenance/licence review. |
| `docs/compatibility.md:36-38` | States that FA match/player reads are reported separately from FMAPI runtime evidence; no FMAPI capability is supported from that report. | Confirms MAT/FIX/CMP have no FMAPI compatibility claim. |
| `docs/research/message-reader-checkpoint.md:91` | Mentions `MATCH_TEAM_DEFAULT_FORMATTER` at RVA `0x4992920` only to distinguish it from the person-hidden rule. | E1 related symbol only. No fixture, competition or match-stat layout is established by this mention. |
| `tools/FMAPI.MessageProbe/EntityLinks.cs:122` | Current manager/player diagnostic reports unsupported items including `current match/tactic position assignment`. | The probe deliberately does not read fixtures, competitions or match results. |
| `tools/FMAPI.MessageProbe/README.md:31-43` | Documents manager employment and goalkeeper/position diagnostics. | No fixture/match/competition entry point or field inventory. |
| `src/FMAPI.Sdk/Game.cs:29-39` | Generic `GameSnapshot` with string key/value values. | No typed fixture, competition, result or statistics contract. This is not an implementation of the task IDs. |
| `src/FMAPI.Adapters.Windows/UnavailableWindowsAdapter.cs:17-21` | Always throws/returns unsupported. | No real-game read path. |
| `src/FMAPI.Adapters.Mock/MockGameAdapter.cs:14-32` | Synthetic club/key-value snapshot; the string "FMAPI offline fixture" means a test fixture. | Must not be mistaken for a football fixture. |
| `docs/research/data-discovery-todo.md:309-326` | D-group acceptance targets and minimum sample expectations. | Target definition only; no implementation. |

Repo-wide searches for `fixture`, `schedule`, `competition`, `standing`, `score`, `appearance`, `rating`, `shot`, `xG` and related terms found no fixture/competition/match-stat reader beyond the reported material above. The only "fixture" hit in `src/` is the synthetic test-build label in `MockGameAdapter.cs:16`.

## FIX-01: next and recent fixtures

Target: fixture UID, home/away team UID, competition/season, date/time, venue, status, and score entry for scheduled/recent fixtures.

Findings:

- No fixture collection, fixture lookup, schedule reader, or fixture field decoder is present in this worktree. Evidence level: E0.
- The FA match report describes an active match hook, not a schedule/fixture record. Scores and teams observed during a match do not establish next/recent fixture UID, competition, venue, scheduled time or status semantics. Evidence level for FIX-01: E0; the match report is adjacent context only.
- The prior "fixture candidate" recorded in `docs/research/interface-inventory.md:65` is not accompanied by a checked-in path or field table. It remains an unverified prior research clue, not a recoverable implementation.
- `docs/research/data-discovery-todo.md:313` requires at least an upcoming and a completed fixture sample, but no such sample or code is in this worktree.

Exact fields still missing:

| Field | Status |
|---|---|
| Fixture stable UID and fixture-vs-match identity | missing |
| Home team UID / away team UID / neutral flag | missing |
| Competition and season reference | missing |
| Calendar date and kick-off time; timezone/game-calendar meaning | missing |
| Venue / stadium reference | missing |
| Status (scheduled, played, postponed, abandoned, etc.) and status enum | missing |
| Score entry in the fixture record, including extra time/penalties distinction | missing |

Dependencies and unknown semantics: requires the validated club/team/contract base (CLB-01, IDX-01), a fixture collection route or fixture object reference, and ENV-01 date/session context. Unknown: whether a "fixture" is a distinct native type, whether match data is embedded in the fixture, whether UIDs are save-scoped, and whether dates use the same packed-date layout already decoded for messages.

## CMP-01: competition, season, table and draw

Target: competition/season/stage, group, league table, round, promotion/relegation/elimination relations, and draw results.

Findings:

- No competition, season, stage, group, standing, round, draw or qualification reader was located. Evidence level: E0.
- The only related statement is the target relationship `fixture→competition/match` in the discovery map (`docs/research/data-discovery-todo.md:232`); it is a desired relation, not evidence of a native route.
- No standings values, points, played counts, goal differences, tie-break rules or draw records exist in the checked-in source or docs.
- CMP-01 cannot be advanced before FIX-01 provides a fixture/competition reference or before static metadata identifies a competition/season object independently.

Dependencies and unknown semantics: FIX-01 is the declared dependency (`docs/research/interface-inventory.md:66`). Unknown: competition-vs-season identity, stage/group hierarchy, whether tables are materialized or computed, how promotion/relegation/elimination is represented, and whether draw results are recorded separately from fixtures.

## MAT-01: completed results, appearances, minutes, positions, ratings, old-plugin fields

Target: completed result, lineups/appearances, minutes, positions, ratings, and whatever the old match plugin actually read.

Findings:

- The only concrete reported evidence is the FA match hook summary: team identities, score updates, ticks, 50 player identities/names/positions and 22 players on the pitch (`docs/adr/0003-share-verified-match-reader.md:7`). The same paragraph says the user confirmed agreement for score, shots, shots on target, xG and corners. Evidence level: E2 for score and the reported player/position set.
- That report describes in-match capture. It does not establish a completed-fixture record, appearance records, minutes played, an unused-substitute list, a post-match rating scale, or event order. Do not turn "22 players on the pitch" into a full appearance table.
- The user-confirmed old match plugin is recorded as a report only. No plugin source, binary, field list, or sample exists in this worktree. The exact fields it read are unavailable. `docs/research/interface-inventory.md:68` already flags code, precise fields and retest as pending.
- No checked-in `MAT` or match-result decoder exists under `src/` or `tools/`. `tools/FMAPI.MessageProbe` is manager/message/player-position focused and explicitly lists current match/tactic assignment as unsupported (`tools/FMAPI.MessageProbe/EntityLinks.cs:122`).

Field status:

| Field | Evidence status |
|---|---|
| Final score | Reported/user-checked in an FA session; not FMAPI-reproduced. |
| Team identities in an active match | Reported; not a fixture/result key. |
| Player identities/names/positions in an active match | Reported counts only; not a post-match appearance record. |
| Appearances (starter/substitute/unused) | missing |
| Minutes played and substitution minutes | missing |
| Post-match position record | missing; live position is not the same record |
| Rating and rating scale | missing |
| Old-plugin statistics field list | unavailable; user report only |

Dependencies and unknown semantics: depends on FIX-01 for a completed fixture/match entry and PLY-01 for stable player identity. Unknown: whether the match hook's live capture is the only route, whether a finished match is retained as a separate object, whether ratings are engine-native or derived, and how minutes/appearances handle substitutions and stoppage time.

## MAT-02: per-team and per-player match statistics

Target: shots, shots on target, xG, possession, passing, defensive statistics, with explicit dimensions and units.

Findings:

- The FA report gives the strongest partial field evidence: user-confirmed shots, shots on target, xG and corners (`docs/adr/0003-share-verified-match-reader.md:7`). It does not state how these are keyed, whether they are team totals, player totals, full-match or half-match, or what unit/precision applies.
- Possession, passes, pass accuracy, tackles, interceptions, clearances, duels, saves and other defensive fields are not reported. Evidence level: E0 for those fields.
- Corners are reported but are outside the current MAT-02 wording; they are adjacent evidence, not a complete statistics schema.
- No statistic decoder, stat object layout or field-name table is present in this worktree. The FA source hashes in `docs/adr/0003-share-verified-match-reader.md:63-67` identify files for future reconciliation only.

Field status:

| Field | Evidence status |
|---|---|
| Shots | reported/user-checked; dimensions and unit unknown |
| Shots on target | reported/user-checked; dimensions and unit unknown |
| xG | reported/user-checked; provider/version/precision unknown |
| Corners | reported/user-checked; adjacent to the MAT-02 target |
| Possession | missing |
| Passes / pass accuracy | missing |
| Defensive statistics | missing |
| Player-level versus team-level split | missing |
| Full-match versus half/period split | missing |
| Season aggregation | missing |
| Zero versus unavailable semantics | missing |

Dependencies and unknown semantics: MAT-01 must first establish a completed match entry. Unknown: whether statistics are stored on the match, team-match, player-match, or computed by an analysis layer; whether xG is available for every competition; and whether missing values are zero, absent, or unsupported.

## Missing dependencies and blockers

- No old match-plugin code, no FA `match-reader` tree, and no FMMatchLens source in this worktree. The ADR records that extraction is paused and that FA-added changes have unresolved provenance/licence; do not copy them.
- No private sanitized capture, save or match snapshot is available for offline audit.
- No fixture or competition entry point has been recovered, so CMP-01 is blocked behind FIX-01.
- MAT-01/MAT-02 field lists cannot be reconstructed from the current report alone; the four confirmed stats do not define a schema.
- Live access was forbidden in this wave. No process, game installation, UI, capture, network, account configuration, injection, native call, write, or match advancement was performed.
- No build or test command was run. This is a documentation/source audit; the absence of a run is not a pass result.

## Minimal bounded follow-up plan

### Phase 0: offline recovery, no game process

1. Recover the old match-plugin source and the FA `match-reader` tree into a controlled private directory outside the repository; hash every file and compare the FA snapshot with the recorded source hashes in `docs/adr/0003-share-verified-match-reader.md:63-67`. Do not import or copy unreviewed code.
2. Compare the recovered reader with the pinned FMMatchLens commit `276d17ff677f90a0f13a75565c7af7d855756768`; separate upstream MIT material from FA modifications and keep unresolved material out of FMAPI.
3. Using the pinned `game_plugin.dll` and metadata only, statically search for fixture, competition, season, table, match-result and statistic types/strings. Record exact RVA/type/field candidates and fail closed on a different binary hash. No process scan.
4. Produce a per-ID field inventory with `raw type`, `semantic`, `unit`, `dimension`, `status`, `source path/RVA`, and `unknown` reasons. No invented fields.

### Phase 1: later coordinator-scheduled live reads, read-only

All of the following require a separate authorization and the shared capture queue. None is performed by this audit.

- FIX-01: start from the already validated current manager/club/team context; locate one fixture collection edge. Read at most 32 fixture entries and one upcoming plus one recent fixture, within a 64 KiB aggregate budget. Record fixture UID, team references, competition reference, date/time, venue, home/away, status and score. Re-read twice; compare with the schedule UI. Do not advance the date or create a match.
- CMP-01: use the competition reference from the FIX-01 sample. Read one season/stage and at most 32 table rows; check group/round/draw references. Compare with the competition table UI. Do not perform a draw or change qualification.
- MAT-01: use one already completed match present in the save. Read at most 64 player rows plus the team result record; capture score, lineup, minutes, position and rating only if the field layout is proven. Compare with the match report UI. Do not start, replay or advance a match.
- MAT-02: reuse the same completed match only. Read team-level and player-level statistics separately; mark possession/passing/defence absent until proven. Cross-check only the fields the user already confirmed (score, shots, shots on target, xG, corners) plus any newly proven field. Record dimension, unit, zero-versus-unavailable and provider/version.

Acceptance for any later live claim: exact binary fingerprint, exact capture budget, repeat-read agreement, UI/known-fact comparison, and explicit unknown fields. A single successful read is not cross-save or cross-build support.

## Disposition

Completed in this wave:

- Read-only audit of the checked-in source, tools and research docs for FIX-01, CMP-01, MAT-01 and MAT-02.
- Source map, evidence-strength classification, dependency list, unknown-semantics list and bounded follow-up plan.
- Narrow inventory notes updated to distinguish reported evidence from reproducible implementation.

Candidate:

- FIX-01: prior "fixture candidate" exists only as an unrecovered clue; no checked-in code or field table.
- MAT-01: reported active-match score/team/player evidence, plus a user-confirmed old plugin whose fields are unavailable.
- MAT-02: reported/user-checked shots, shots on target, xG and corners only; no possession, passing, defensive fields or dimensions.

Missing/blocked:

- CMP-01: no competition/season/table/draw evidence at all.
- FIX-01 exact fixture fields, stable fixture UID and schedule entry point.
- MAT-01 appearances, minutes, post-match positions, ratings and reproducible old-plugin field list.
- MAT-02 possession, passing, defensive statistics, dimensions, units and zero/missing semantics.
- All live/capture evidence and all source code for the old match plugin and FA reader in this worktree.

No live read was performed. No process, game installation, UI, private capture, credentials, account configuration, network, subprocess, injection, native call, memory/save write or match advancement was accessed.

## Anchor and decoder status (this wave)

Most concrete missing relationship for this lane: `fixture → competition/match` (and the prerequisite `team → fixture`). Both are desired relations in `docs/research/data-discovery-todo.md:232`, but no fixture or competition native type, collection, field layout, or sanitized sample exists in this worktree. The nearest historical anchor is the FA in-match hook (`docs/adr/0003-share-verified-match-reader.md:7`) reporting team identities and score updates; that is an active-match observation, not a fixture/competition record, and its source hashes (`docs/adr/0003-share-verified-match-reader.md:63-67`) cannot be reconciled without the paused extraction.

Safe pure decoder status: no pure decoder was added. There is no documented fixture/competition/match-result/statistics format to decode, and reusing the message packed-date layout (`0x9E56D0`, `docs/research/message-reader-checkpoint.md:39`) for fixture dates would be unsupported inference. Any decoder must wait for Phase 0 static recovery or a later coordinator-scheduled read-only capture.

Specific blocker: absence of any fixture/competition entry point or field layout in the checked-in source/docs, combined with no recovered old-match-plugin or FA match-reader code in this worktree. Until that is resolved, FIX-01, CMP-01, MAT-01 and MAT-02 cannot move beyond candidate/missing.
