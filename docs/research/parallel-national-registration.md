# Parallel research audit: national registration (NAT-01..03, REG-01..04)

## Scope and constraints

- Branch/worktree: `research/parallel-national-registration`.
- Task IDs: `NAT-01`, `NAT-02`, `NAT-03`, `REG-01`, `REG-02`, `REG-03`, `REG-04`.
- This wave is offline only. No process, game install, UI, private captures, credentials, network, bash/subprocess, native calls, writes, save changes, match advancement, or live reads were performed.
- Reused existing repository research and pinned native evidence only. No SDK design or implementation is proposed.
- Existing task rows aggregate multiple goals; dependency or partial evidence is not counted as completion of these IDs.

## Pinned baseline

- Pinned upstream commit: `01b53c5`.
- Local research base: `99aba1d`.
- Accepted native game binary hash (`game_plugin.dll`): `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`.
- Accepted GameAssembly hash: `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`.
- Installed metadata signature/version: `0xFAB11BAF` / v39.
- PositionMask metadata SHA-256: `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`.
- Evidence sources are pinned to the above profile. A different binary hash must fail closed.
- No live capture was run for this audit; all findings below are from checked-in source/docs.

## Audited source locations

| Source | Relevant content |
|---|---|
| `docs/research/interface-inventory.md:83-89` | ID definitions, priority, status, dependency notes for NAT-01..03 and REG-01..04. |
| `docs/research/data-discovery-todo.md:110-116` | NAT/REG task goals and dependencies. |
| `docs/research/data-discovery-todo.md:277-280` | Player availability/suspension/registration wording and B-package acceptance. |
| `docs/research/native-entity-evidence.md:1-87` | Pinned fingerprints, current-manager selection, person UID lookup, actual-player layout, position fields. |
| `docs/research/manager-player-links-checkpoint.md:1-67` | Human manager collection, contract kind, team/club UID, PERSON registry, goalkeeper familiarity. |
| `tools/FMAPI.MessageProbe/EntityLinks.cs:37-71` | Bounded PERSON UID lookup, exact actual-player checks, position slot reads. |
| `tools/FMAPI.MessageProbe/EntityLinks.cs:72-123` | Human manager collection, contract kind, team/club UID, current selection. |
| `tools/FMAPI.MessageProbe/Program.cs:60-97` | Bounds, text, date, safe-read primitives and self-tests. |
| `tools/FMAPI.MessageProbe/Program.cs:98-123` | Hash/profile acceptance and read-only process handle. |

## Reusable dependency evidence

| Dependency | Status in repository | Relevance to NAT/REG |
|---|---|---|
| `PLY-01` | Partial: person UID at `PERSON +0x0C`; actual-player layout and 14 named position bytes at `player +0x150..+0x15E`. | Provides person identity only; no nationality, eligibility, suspension, or registration fields. |
| `CLB-01` | Partial for current manager's employment club only: club UID at `CLUB +0x0C`; team at `TEAM`, club at `TEAM +0x30`. | Provides club identity only; no national team, squad registration, or competition assignment. |
| `CON-01` | Partial: contract kind at `FULL_CONTRACT +0x26`; contract-to-team-to-club pointers. | Provides contract linkage only; no registration window, quota, work permit, or discipline fields. |
| `FIX-01` | Research candidate only; fixture UID, competition, date/time, status are not validated. | Required before any next-match eligibility or suspension scope can be interpreted. |
| `CMP-01` | Not started. | Required before competition rules, standings, cards, promotion/relegation, or transfer-window boundaries. |

## ID audit

### NAT-01

- Inventory definition: national team/tiers, call-ups, report and return dates, squads/camps, and club availability impact.
- Source locations: `docs/research/interface-inventory.md:83`; `docs/research/data-discovery-todo.md:110`; `docs/research/data-discovery-todo.md:280`.
- Target field meaning: national-team entity UID, age-group/tier, call-up status, report/return dates, squad membership, camp, club availability impact.
- Evidence strength: `not_started` for this ID. No national-team object, call-up field, or availability field has been observed. Reusable person UID and club identity evidence exists, but it does not establish any national-team relation.
- Missing dependencies: stable `PLY-01` person identity across saves; validated `FIX-01` fixture/competition identity; club availability semantics.
- Unknown semantics: national-team entity type; person-to-national-team relation; whether report/return dates are game dates or real dates; whether club availability is stored, calculated, or UI-derived; age-group eligibility.
- Minimal bounded follow-up read plan: first keep all outputs `unavailable` for this ID. In a later authorized read, use only the existing bounded PERSON UID lookup and manager/club relation, request at most 32 explicitly supplied person UIDs from a save with a known international call-up, and compare captured bytes against the known UI. Do not infer availability from a missing field. No full-registry scan.

### NAT-02

- Inventory definition: multiple nationality, eligibility, represented country, caps, and selection status.
- Source locations: `docs/research/interface-inventory.md:84`; `docs/research/data-discovery-todo.md:111`.
- Target field meaning: nationality list, eligibility flags, represented country, cap counts, selection status.
- Evidence strength: `not_started`. No nationality or eligibility field is implemented or observed. The position bytes at `player +0x150..+0x15E` are position familiarity fields and must not be interpreted as nationality or eligibility.
- Missing dependencies: `NAT-01` national-team entity and call-up evidence; stable person identity.
- Unknown semantics: nationality storage; dual/multiple nationality handling; eligibility rules and mutability; cap history scope; whether selection status is stored or derived.
- Minimal bounded follow-up read plan: static metadata/string inspection only in the offline phase, then an authorized bounded capture of person records for known dual-national or capped players. Compare against known UI. Keep unknown values explicit.

### NAT-03

- Inventory definition: global national-team match history, world ranking/coefficients, and age-group qualification scope.
- Source locations: `docs/research/interface-inventory.md:85`; `docs/research/data-discovery-todo.md:112`.
- Target field meaning: national-team competition history, ranking/coefficient values, age-group qualification scope.
- Evidence strength: `not_started`. No competition-history or ranking evidence exists in the repository.
- Missing dependencies: `NAT-02` and `CMP-02`, both not started; world database traversal.
- Unknown semantics: whether national-team competitions and rankings are loaded in ordinary saves; coverage by loaded leagues; historical depth; ranking calculation.
- Minimal bounded follow-up read plan: do not attempt until `CMP-02` has candidate competition entities. Then use bounded collection reads and compare against known UI for one current ranking and one historical result.

### REG-01

- Inventory definition: next-match eligibility, registration status, suspension/discipline reason and applicable competition; absence of evidence is not availability.
- Source locations: `docs/research/interface-inventory.md:86`; `docs/research/data-discovery-todo.md:113`; `docs/research/data-discovery-todo.md:277-278`.
- Target field meaning: eligibility flag, registration status, suspension/discipline reason, applicable competition, reason for unavailability.
- Evidence strength: `not_started`. No registration or discipline field has been observed. The B-package wording explicitly requires distinguishing "not found" from "available"; current tooling must report `unavailable`.
- Missing dependencies: validated `FIX-01` fixture/competition identity; `PLY-01` person identity; person-to-fixture relation.
- Unknown semantics: eligibility calculation; suspension scope; competition-specific discipline; whether registration status is stored per competition, team, or person; whether a missing field means eligible or unknown.
- Minimal bounded follow-up read plan: validate `FIX-01` first. Then capture known suspended/ineligible and known available players in the same competition context, using at most 32 UIDs and the existing 64 KiB aggregate budget. Compare against UI. Never mark an unobserved player as available.

### REG-02

- Inventory definition: registration windows, squad-size/age/homegrown quotas, foreign-player limits, work permits, registration/loan limits.
- Source locations: `docs/research/interface-inventory.md:87`; `docs/research/data-discovery-todo.md:114`.
- Target field meaning: registration window dates, squad size, age/homegrown quotas, foreign-player count/limit, work-permit status, registration/loan limits.
- Evidence strength: `not_started`. `CON-01` provides contract linkage only; no registration-rule or quota field has been observed.
- Missing dependencies: `REG-01`; `CON-01` (partial); competition/club context.
- Unknown semantics: where rules are stored (competition, club, nation); whether quotas are calculated or stored; transfer/loan interaction; work-permit representation.
- Minimal bounded follow-up read plan: offline metadata/string inspection for registration/squad/foreign/work-permit tokens; then an authorized capture during a registration window with known club and known squad counts. Compare against UI. No writes or registration actions.

### REG-03

- Inventory definition: promotion/relegation/competition format, cumulative card/suspension rules, financial compliance, transfer-window boundaries.
- Source locations: `docs/research/interface-inventory.md:88`; `docs/research/data-discovery-todo.md:115`.
- Target field meaning: competition format, promotion/relegation rules, cumulative card thresholds, suspension rules, financial compliance indicators, transfer-window boundaries.
- Evidence strength: `not_started`. No competition-rule or financial-compliance evidence exists. `FIN-03` also depends on this ID.
- Missing dependencies: `CMP-01` (not started); competition entity traversal.
- Unknown semantics: rule definition versus engine result; competition format differences; card accumulation; transfer-window date semantics; financial compliance calculation.
- Minimal bounded follow-up read plan: do not attempt until `CMP-01` has candidate competition entities. Then inspect bounded competition tables and compare rules/results against UI for one competition.

### REG-04

- Inventory definition: jurisdiction/competition-specific rules and historical changes; distinguish rule definition, engine result, and inference.
- Source locations: `docs/research/interface-inventory.md:89`; `docs/research/data-discovery-todo.md:116`.
- Target field meaning: jurisdiction-specific rules, historical changes, rule-definition versus engine-result distinction.
- Evidence strength: `not_started`. No jurisdiction-specific rule evidence exists.
- Missing dependencies: `REG-02` and `REG-03`.
- Unknown semantics: all fields unknown; historical coverage; version differences.
- Minimal bounded follow-up read plan: defer until `REG-02` and `REG-03` produce at least candidate rule structures. Then compare two competitions/jurisdictions if available, without claiming cross-version stability.

## Classification

| ID | Priority | Completed | Candidate | Missing |
|---|---|---|---|---|
| NAT-01 | P1 | None | Person UID and club identity only; no national-team evidence. | National-team entity, call-up, dates, squad, availability. |
| NAT-02 | P1 | None | Person UID only. | Nationality, eligibility, caps, selection status. |
| NAT-03 | P2 | None | None. | National-team history, ranking, qualification. |
| REG-01 | P0 | None | Fixture candidate only; unvalidated. | Eligibility, registration, suspension/discipline. |
| REG-02 | P1 | None | Contract linkage only. | Registration windows, quotas, work permits, limits. |
| REG-03 | P1 | None | None. | Competition rules, cards, financial compliance, transfer windows. |
| REG-04 | P2 | None | None. | Jurisdiction-specific rules and historical changes. |

## Inventory status note

The interface inventory rows for `NAT-01`, `NAT-02`, `NAT-03`, `REG-01`, `REG-02`, `REG-03`, and `REG-04` remain `未开始`. This audit found no direct implementation evidence for those IDs; only dependency evidence exists. See this document for exact source locations and follow-up plans.

## Live-read status

No live read was performed in this wave. All results above are offline source/evidence audit findings.
