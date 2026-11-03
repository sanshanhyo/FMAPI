# Research audit: board, facilities and history (BRD-01..03, FAC-01..02, HIS-01..02)

Scope: offline only. No process, game install, UI, private capture, credential, account, network or subprocess access was used. No live read was performed. No SDK design or code changes are included.

## Baseline

| Item | Value |
|---|---|
| Branch | `research/parallel-board-facilities-history` |
| Pinned upstream documentation commit (as supplied) | `01b53c5` |
| Local research base (as supplied) | `99aba1d` |
| `game_plugin.dll` SHA-256 | `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F` |
| `GameAssembly.dll` SHA-256 | `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A` |
| Installed metadata signature / version | `0xFAB11BAF` / `39` |
| Observed UnityPlayer (from resumed preparation) | product `6000.3.18f1-custom`, file `6000.3.18.9883062` |
| Audit date | 2026-11-03 |

All RVAs/offsets below are specific to the pinned `game_plugin.dll` hash and must fail closed for another hash.

## Method and reuse

This audit reused existing sanitized research records and source, especially:

- `docs/research/interface-inventory.md:19-20,90-97` for the target ID definitions and status.
- `docs/research/data-discovery-todo.md:46-47,117-124` for target scope and dependencies.
- `docs/research/native-entity-evidence.md:1-12,50-56` for pinned fingerprints and reusable probe locations.
- `docs/research/manager-player-links-checkpoint.md:10-20,22-31,47-53` for manager, contract, team and club relation evidence.
- `docs/research/message-reader-checkpoint.md:28-96` for message/localization and welcome relation candidate evidence.
- `tools/FMAPI.MessageProbe/EntityLinks.cs:96-116` for manager candidate, contract, team and club UID candidate reads.
- `tools/FMAPI.MessageProbe/Program.cs:159-178,233-331` for message inbox and welcome relation candidate reads.

No implementation evidence for board, facility or history target fields was found in the audited source. Adjacent identity and club/team relation reads are not substitutes for those domains and are recorded as candidate-only support.

## Existing code audit summary

| Area | Source location | Relevance to this wave | Evidence strength |
|---|---|---|---|
| Manager candidate chain | `tools/FMAPI.MessageProbe/EntityLinks.cs:81-116` | Manager PERSON UID, `HUMAN_NON_PLAYER` collection, `FULL_CONTRACT`, contract kind, team UID candidate, club UID candidate | Candidate only; active selection proven only in observed session |
| Contract -> team -> club | `tools/FMAPI.MessageProbe/EntityLinks.cs:96-105` | `FULL_CONTRACT +0x10 -> TEAM`, `TEAM +0x30 -> CLUB`, `CLUB +0x0C` UID candidate | Candidate only; club membership provenance comes from separate roster input |
| Club relation candidates | `tools/FMAPI.MessageProbe/Program.cs:239-304` | Team type, club type, club short-name candidate, team short override, alternate club names, name override presence, standalone flag candidate | Candidate only; no board/facility/history fields |
| Manager selection global | `docs/research/native-entity-evidence.md:15-31` | `GameCurrentManager` / `GCuM` selection global and validation method | Candidate/observed in one session; reload and hotseat untested |
| Message inbox and welcome relation | `tools/FMAPI.MessageProbe/Program.cs:159-178,233-331` | Single-human-manager-associated messages, welcome relation team/club candidates | Candidate/partial; no board decision or facility event proven |
| Position and goalkeeper fields | `tools/FMAPI.MessageProbe/EntityLinks.cs:12-71` | Player UID, actual-player layout, goalkeeper familiarity, 14 named position slots | Candidate/observed for 27 requested UIDs; not board/facility/history |

No source in the audited repository contains board target, vision, safety, satisfaction, commitment, request, resolution, facility, stadium, capacity, condition, rating, upgrade, relocation, attendance, ticket, history, honour, award, record or season-history fields.

## Per-ID audit

### BRD-01 - Board targets, season expectations, club vision, manager evaluation/safety and actual status

- Target: board goals, season expectations, club vision, manager evaluation/safety and actual status.
- Source locations: `docs/research/interface-inventory.md:90`; `docs/research/data-discovery-todo.md:117`; dependencies `MGR-01`, `CLB-01`.
- Pinned hash/version: see Baseline. No board-specific RVAs, vtables or fields are recorded.
- Field meaning: unknown. No board object, property key, field offset or status enum has been identified.
- Evidence strength: missing. Manager and club identity candidates exist, but no board target, expectation, vision, evaluation or safety field has been observed.
- Missing dependencies: proven `MGR-01` current manager identity and `CLB-01` club identity across reloads; a candidate board/club-vision object or property path; UI or known-fact comparison samples.
- Unknown semantics: whether board data is attached to club, manager, competition or a separate board object; whether "evaluation" and "safety" are stored, derived or UI-only; whether values are current-season only or historical.
- Minimal bounded follow-up read plan: first perform offline/static type and property-key search in the pinned binaries for board/vision/satisfaction/safety/expectation strings and candidate RTTI names, with explicit byte limits and no process access; then, only if candidates are found, schedule one bounded read-only capture against the club/manager anchor with rechecks and no writes. Do not infer board state from manager identity or club UID.

### BRD-02 - Commitments, board requests/resolutions, facility projects, budget changes, fan satisfaction and due dates

- Target: commitments, board requests/resolutions, facility projects, budget changes, fan satisfaction and due dates.
- Source locations: `docs/research/interface-inventory.md:91`; `docs/research/data-discovery-todo.md:118`; dependency `BRD-01`.
- Pinned hash/version: see Baseline. No BRD-02-specific fields are recorded.
- Field meaning: unknown. Facility projects and budget changes may overlap with `FAC-01`/`FAC-02` and `FIN-02`, but no proven relation exists.
- Evidence strength: missing. No commitment, request, resolution, facility project, budget-change, satisfaction or due-date field has been observed.
- Missing dependencies: `BRD-01`; facility identity fields (`FAC-01`); financial amount and currency semantics (`FIN-02`); message or inbox relation evidence if board requests are delivered as messages.
- Unknown semantics: whether requests are message objects, task objects or club state; whether due dates use game date or real capture time; whether facility projects are separate objects or club fields; whether satisfaction is scalar, enum or derived.
- Minimal bounded follow-up read plan: audit message and club object candidates for request/task/resolution-like structures after static type search; keep each candidate as candidate-only until correlated with a known UI state. No writes, replies, clicks or date advancement.

### BRD-03 - Ownership/acquisition history, long-term vision changes and stakeholder evaluation

- Target: ownership/acquisition history, long-term vision changes and stakeholder evaluation.
- Source locations: `docs/research/interface-inventory.md:92`; `docs/research/data-discovery-todo.md:119`; dependency `BRD-02`.
- Pinned hash/version: see Baseline. No ownership or history fields are recorded.
- Field meaning: unknown. Club UID and short-name candidates are identity data only and do not establish ownership, acquisition, history or stakeholder evaluation.
- Evidence strength: missing.
- Missing dependencies: `BRD-02`; `IDX-03` world database scope for historical or global records; proven club history containers.
- Unknown semantics: whether ownership history exists as a traversable collection or only as current owner; whether long-term vision changes are versioned; whether stakeholder evaluation is stored or derived.
- Minimal bounded follow-up read plan: defer until `BRD-01`/`BRD-02` have candidate objects. Then inspect candidate history collections with bounded entry counts and rechecks. Do not construct history from message prose or club identity.

### FAC-01 - Stadium UID/name, capacity, location, conditions, training/youth facilities and ratings

- Target: stadium UID/name, capacity, location, conditions, training/youth facilities and ratings.
- Source locations: `docs/research/interface-inventory.md:93`; `docs/research/data-discovery-todo.md:120`; dependency `CLB-01`.
- Pinned hash/version: see Baseline. No stadium, facility, capacity, location, condition or rating fields are recorded.
- Field meaning: unknown. Club UID candidate and club short-name candidate are not stadium or facility data.
- Evidence strength: missing.
- Missing dependencies: proven club identity and team-to-club relation; a stadium/facility object or club field; UI or known-fact capacity/location comparison.
- Unknown semantics: whether stadium and club are one object or separate objects; whether capacity is total, seated or safe; whether facility ratings are enum, score or text; whether training and youth facilities are separate fields or one combined rating.
- Minimal bounded follow-up read plan: static search for stadium/facility/capacity/rating/type names in pinned binaries; if candidates exist, inspect club object and related objects with bounded reads and rechecks. Keep all values candidate-only until UI comparison.

### FAC-02 - Facility expansion/relocation plans, progress, shared ground, attendance/tickets and related schedule

- Target: expansion/relocation plans, progress, shared ground, attendance/tickets and related schedule.
- Source locations: `docs/research/interface-inventory.md:94`; `docs/research/data-discovery-todo.md:121`; dependencies `FAC-01`, `FIN-02`.
- Pinned hash/version: see Baseline. No expansion, relocation, progress, attendance, ticket or schedule fields are recorded.
- Field meaning: unknown.
- Evidence strength: missing.
- Missing dependencies: `FAC-01`; financial amount semantics (`FIN-02`); schedule/fixture identity (`FIX-01`); possible message or task relation for project requests.
- Unknown semantics: whether plans are mutable state or historical records; whether progress is percentage, date or stage; whether attendance/ticket data is per match, season or aggregate; whether shared-ground state is boolean or club reference.
- Minimal bounded follow-up read plan: only after `FAC-01` candidate fields exist. Then inspect candidate project/schedule objects with bounded entry counts. No writes, no match advancement, no date advancement.

### HIS-01 - Player/manager/club season history, honours, awards and visible records

- Target: season history, honours, awards and visible records for players, managers and clubs.
- Source locations: `docs/research/interface-inventory.md:96`; `docs/research/data-discovery-todo.md:123`; dependency `IDX-01`.
- Pinned hash/version: see Baseline. No history, honour, award or record fields are recorded.
- Field meaning: unknown. Message templates and club short-name candidates are not season history.
- Evidence strength: missing.
- Missing dependencies: `IDX-01` entity identity and relation baseline; candidate history containers; known season/honour comparison data.
- Unknown semantics: whether history is stored per entity, per season or in global records; whether awards are enum or object references; whether records are current-save only or include historical seasons; whether missing seasons mean unavailable or zero.
- Minimal bounded follow-up read plan: static search for history/honour/award/record type names; then bounded inspection of candidate containers attached to player/manager/club anchors. Do not infer honours from names, messages or UI similarity.

### HIS-02 - Global records, past winners/champions, historical statistics and missing-season coverage

- Target: global records, past winners/champions, historical statistics and missing-season coverage.
- Source locations: `docs/research/interface-inventory.md:97`; `docs/research/data-discovery-todo.md:124`; dependencies `HIS-01`, `IDX-03`.
- Pinned hash/version: see Baseline. No global history or record fields are recorded.
- Field meaning: unknown.
- Evidence strength: missing.
- Missing dependencies: `HIS-01`; `IDX-03` world database scope; coverage and pagination boundaries.
- Unknown semantics: whether global records are loaded in an offline save; whether historical seasons are complete or partial; how missing seasons are represented.
- Minimal bounded follow-up read plan: defer until `HIS-01` candidate fields and `IDX-03` boundaries exist. Then build a coverage checklist with explicit missing-season markers. No full-world scan without budget approval.

## Cross-cutting unknowns

- No `BOARD`, `STADIUM`, `FACILITY`, `HISTORY`, `HONOUR`, `AWARD` or `RECORD` RTTI/type references were found in the audited repository. Static binary search is still required before any live read.
- Club UID, club short-name candidate, team UID and manager identity reads are identity/anchor evidence only. They do not imply board, facility or history data.
- No message has been proven to represent a board request/resolution or facility project.
- No live capture was performed in this wave, so no UI comparison, repeated-read stability or reload result exists for these IDs.

## Status summary

| ID | Priority | Status | Completed | Candidate | Missing |
|---|---|---|---|---|---|
| BRD-01 | P1 | 未开始 | 0 target fields | Manager/club identity anchors only | All board target/vision/evaluation fields |
| BRD-02 | P1 | 未开始 | 0 target fields | Club/team/message anchors only | All commitment/request/resolution/facility/budget/satisfaction fields |
| BRD-03 | P2 | 未开始 | 0 target fields | Club identity anchors only | All ownership/history/stakeholder fields |
| FAC-01 | P1 | 未开始 | 0 target fields | Club identity anchors only | All stadium/facility/capacity/condition/rating fields |
| FAC-02 | P1 | 未开始 | 0 target fields | Club/team anchors only | All project/progress/attendance/ticket fields |
| HIS-01 | P1 | 未开始 | 0 target fields | Entity identity anchors only | All season history/honour/award/record fields |
| HIS-02 | P2 | 未开始 | 0 target fields | Entity identity anchors only | All global record/coverage fields |

No live read performed.
No SDK design performed.
No git push or release performed.
