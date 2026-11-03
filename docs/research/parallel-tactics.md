# Parallel tactics research: TAC-01, TAC-02, TAC-03

Status: offline source audit only. No live process read was performed. No game function was called, no UI or screenshot was read, no process memory or save was written, and no network or repository remote was used. This document records findings and a bounded follow-up plan; it does not claim runtime results.

## Scope and pinned baseline

- Task IDs: TAC-01, TAC-02, TAC-03 (read-only tactics, lineup and instruction research).
- Assigned branch: `research/parallel-tactics`.
- Task-provided local research base: `99aba1d`.
- The baseline provenance is recorded in `docs/research/data-discovery-todo.md:188` and `docs/research/interface-inventory.md:196`: `99aba1d` is one of the unpushed Windows commits on `research/alawell-message-reader`, alongside `10a5724` and `d1f5177`. This worktree did not invoke git or any subprocess, so the current HEAD/base was not independently re-resolved; the pinned identifier is accepted from the task statement.
- Reused binary/profile evidence, not re-measured in this wave: `game_plugin.dll` SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`, `GameAssembly.dll` SHA-256 `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`, global-metadata SHA-256 `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`, metadata signature/version `0xFAB11BAF / 39`. Sources: `docs/research/native-entity-evidence.md:7-9,60`, `docs/research/message-reader-checkpoint.md:11,54`, `tools/FMAPI.MessageProbe/PositionFields.cs:6-8`.
- Build/consumer context from prior checkpoints: the external producer manifest identified build `21bfd30` (`docs/research/manager-player-links-checkpoint.md:17`); UnityPlayer product `6000.3.18f1-custom (96cdb67fb884)` (`docs/research/message-reader-checkpoint.md:69`). These identify the prior evidence profile only; they are not re-verified here.

## Method and search coverage

Read-only text review covered `AGENTS.md`, `docs/scope.md`, `docs/architecture.md`, `docs/compatibility.md`, the ADRs, `docs/research/interface-inventory.md`, `docs/research/data-discovery-todo.md`, the three existing research checkpoints, and the tool sources under `tools/`.

Case-insensitive repository searches for `tactic`, `formation`, `lineup`/`line-up`, `squad`, `roster`, `starting eleven`, `bench`, `substitute`, `position slot`, `setpiece`/`set piece`/`dead ball`, `penalty`, `corner`, `free kick`, `captain`, `mentality`, `instruction`, `role`, and `duty` found no tactic implementation outside these documents and one explicit unsupported declaration.

The only code-level TAC-related statement is `tools/FMAPI.MessageProbe/EntityLinks.cs:122`, which lists `"current match/tactic position assignment"` in an `unsupported` array. That is a limitation statement, not an entry point.

This absence is a statement about the audited worktree/base, not proof that no private or external research exists. The inventory's TAC-01 phrase "有战术候选" is a record without a source path in this baseline; it cannot be verified here.

## Reusable evidence and its limits

| Source | What it actually establishes | Relevance to TAC | Limits |
|---|---|---|---|
| `docs/research/interface-inventory.md:55-58` | Current TAC-01/02/03 status rows and dependencies | Task framing only | No entry point, field layout, hash-specific path or test evidence |
| `docs/research/data-discovery-todo.md:82-85,328-345` | Required TAC goals and acceptance criteria | Defines what would count as complete | Checklist, not data evidence |
| `docs/research/manager-player-links-checkpoint.md:13-27,67` | Current-selected manager, `humanmanager -> FULL_CONTRACT -> TEAM -> CLUB`, PERSON UID lookup, goalkeeper byte | Supplies team/club/player UID dependencies and position bytes | Explicitly says current match/tactic assignment is outside the result |
| `docs/research/native-entity-evidence.md:17-31,48,58-87` | Native selection global, exact actual-player layout, 14 named position familiarities and natural mask | Player position familiarity only; can support a player-side join | Natural position is not a lineup slot, role, duty or tactic familiarity |
| `tools/FMAPI.MessageProbe/EntityLinks.cs:37-70,96-104,122` | Ordered PERSON UID lookup; manager contract/team/club relation; explicit unsupported statement | Reusable player UID and club UID candidate; manager-owned team pointer | No tactic object, formation, lineup or instruction field; club membership is input provenance, not rebuilt |
| `tools/FMAPI.MessageProbe/PositionFields.cs:1-37` | Pure decoder for player `+0x150..+0x15E`, 14 named familiarities, natural mask threshold 18 | Only player positional familiarity | Not tactic role, not formation geometry, not tactical familiarity |
| `docs/adr/0003-share-verified-match-reader.md:7` | Attributed FA report of match player identities/names/positions and players on the pitch | Nearest external "position" report | External/user-attributed; no source in this worktree; provenance/licence review paused; does not establish tactics |
| `docs/compatibility.md:38` | States managed club and complete roster remain unresolved for FMAPI | Confirms the dependency gap | No tactic capability claimed |

## TAC-01: active/selected tactical slot, identity, formation, lineup, slots

Target from `docs/research/data-discovery-todo.md:82`: distinguish the currently active slot from the selected slot; read tactic name/identifier, formation, starters, substitutes, unselected players, position slots and player UID linkage.

| Sub-goal | Existing source | Evidence strength | Finding |
|---|---|---|---|
| Active tactic slot | None | Missing | No tactic root, collection or slot field in the audited base |
| Selected/UI-page tactic slot | None | Missing | The active-vs-selected distinction is an explicit acceptance question (`data-discovery-todo.md:345`), not a solved field |
| Tactic name/identifier | None | Missing | No tactic RTTI, UID or name pointer was found |
| Formation | None | Missing | No formation mask, enum, slot count or geometry was found |
| Starters | None | Missing | No lineup collection or starter flag was found |
| Substitutes | None | Missing | No bench collection or substitute flag was found |
| Position slots | `PositionFields.cs`; `native-entity-evidence.md:58-81` | Candidate dependency only | These are player natural-position familiarities at `+0x150..+0x15E`, not lineup slot indices |
| Player UID linkage | `EntityLinks.cs:37-70`; `manager-player-links-checkpoint.md:21-27` | Candidate dependency only | A supplied player UID can be resolved through the PERSON index; tactic membership is not read |
| Club/team context | `EntityLinks.cs:96-104`; `manager-player-links-checkpoint.md:13-17` | Candidate dependency only | Club UID candidate and team pointer exist through contract/team/club; team UID is not emitted and the tactic owner relation is unknown |

TAC-01 is therefore not implemented and not demonstrated in this baseline. The inventory's earlier "candidate" is not a reproducible source location here.

## TAC-02: roles, duties, mentality, team and individual instructions

Target from `docs/research/data-discovery-todo.md:83`: raw enums and validated text meanings for roles, duties, mentality, team instructions and individual instructions.

| Sub-goal | Existing source | Evidence strength | Finding |
|---|---|---|---|
| Role raw enum | None | Missing | No role enum names, values, metadata table or property key found |
| Role text meaning | None | Missing | No localization key or formatter evidence for roles |
| Duty raw enum | None | Missing | No duty field or enum found |
| Mentality raw enum | None | Missing | No mentality field or enum found |
| Team instructions | None | Missing | No instruction collection, bitmask or property key found |
| Individual instructions | None | Missing | No per-player instruction structure found |
| Defaults/unknown handling | None | Missing | No evidence for whether unset values are zero, inherited or absent |

No TAC-02 field is implemented. The existing player position familiarity, contract kind byte and goalkeeper predicate are unrelated raw enums and must not be reused as role, duty, mentality or instruction evidence.

## TAC-03: multiple schemes, opposition instructions, set pieces, captain/takers, familiarity

Target from `docs/research/data-discovery-todo.md:84`: multiple tactical schemes, opposition instructions, set-piece arrangements, captain and set-piece taker order, and tactical familiarity.

| Sub-goal | Existing source | Evidence strength | Finding |
|---|---|---|---|
| Multiple tactical schemes | None | Missing | No tactic collection, ordering or scheme identity found |
| Opposition instructions | None | Missing | No opposition-instruction structure or per-opponent field found |
| Set-piece arrangements | None | Missing | No corner/free-kick/penalty routine or taker structure found |
| Captain | None | Missing | No captain field or team-person relation found |
| Set-piece taker order | None | Missing | No taker list or ordering field found |
| Tactical familiarity | None | Missing | No tactic familiarity field or scale found |
| Player positional familiarity | `PositionFields.cs`; `native-entity-evidence.md:58-85` | Unrelated dependency | This is player position familiarity, not tactical familiarity; the names must not be conflated |

No TAC-03 field is implemented. TAC-03 remains blocked on TAC-02 evidence in addition to its own absent entry points.

## Unknown semantics that must remain explicit

- Whether the "active" tactic is stored on a team, a manager, a club or a separate tactic manager object.
- Whether the currently selected UI slot and the team's active tactic slot are distinct objects, indices or the same value.
- How formation is represented: slot array, bitmask, enum or derived from position slots.
- Whether tactics have stable UIDs, save-scoped identities or only ordering.
- Raw role/duty/mentality enum values, their names and their localized text; no defaults should be invented.
- Team versus individual instruction encoding, inheritance and reset semantics.
- Opposition instruction scope and whether it is per-fixture or per-tactic.
- Set-piece routine, taker ordering and captain storage; whether they are tactic-owned or team-owned.
- Tactical familiarity value range, update timing and relationship to player positional familiarity.
- Distinction between planned lineup, selected match squad and actual in-match lineup.
- Object lifetime and refresh behavior across tactic edits, formation changes, save/load, reload, manager change and process restart.
- Whether a complete roster can be joined to tactic slots using existing UID lookup, or whether club membership must be rebuilt independently.

## Missing dependencies

- CLB-01 is only partial: club/team identity and club UID candidate exist, but a complete roster and team UID are not established (`interface-inventory.md:29`; `compatibility.md:38`).
- PLY-01 is only partial: person UID, names and some physical fields exist, but the full target set is not complete (`interface-inventory.md:32`).
- TAC-02 depends on TAC-01, and TAC-03 depends on TAC-02; neither parent has a verified entry point in this baseline.
- There is no identified tactic type, tactic collection, formation field, role/duty enum, instruction structure or set-piece structure.
- There is no confirmed localization route for role/duty/instruction labels; the existing localization work is message/template-specific and only partially resolved.
- A live loaded-save session and the shared read coordinator are required for any future read. This wave did not have or use either.
- The pinned binary profile must be rechecked before any future read; the hashes above are reused evidence, not a new measurement.

## Minimal bounded follow-up read plan

This is a request plan for a later authorized phase, not work performed here. All stages are read-only. No stage may call game functions, write memory, advance a match or use UI/OCR.

### Stage 0: offline static localization (no process)

- Inputs: the operator-selected pinned `game_plugin.dll`, `GameAssembly.dll`, `global-metadata.dat`, and the matching interop map if available. Keep all paths and outputs outside the repository.
- Reuse: `tools/research/StaticProbe` for RTTI/type/string/vtable/xref/disassembly inspection; `tools/FMAPI.PeProbe` for PE/RTTI candidates. Both are research prototypes and may reject malformed input.
- Bounded queries: type/name fragments for tactic, formation, role, duty, mentality, instruction, set piece, captain, taker and familiarity; metadata enum constants; named-property literal registration analogous to the documented `GCuM` chain (`native-entity-evidence.md:13-17`).
- Budget: explicit files only; no address-space scan; stop at 40 matches per search or 100 candidate types, whichever comes first; confirm candidate references with instruction-boundary disassembly before use.
- Exit criteria: a short list of candidate types/properties with RVA/vtable/field offsets and confidence, or a documented absence. No runtime claim from Stage 0.

### Stage 1: one bounded live read of team context and candidate tactic root

- Coordinator: single owner holds the live-process lock and schedules the read; this worker does not operate the game.
- Preconditions: matching binary hashes, new process identity/start time, loaded save, stable state, no load/menu transition during the read.
- Read: current-selected manager and existing contract/team/club relation, then only a Stage 0 candidate tactic pointer. Follow at most two already-analyzed pointer hops with exact expected RTTI/vtable checks.
- Budget: at most 64 KiB total, at most 32 objects, at most 8 KiB per read, at most two passes, no full-registry or full-address scan; abort and report unavailable on any pointer, type or state change.
- Output: sanitized structural JSON only: counts, RTTI names, module-relative offsets, raw enum values and status. No names, UID lists, prose or raw dumps.
- Exit criteria: candidate root is repeatable across two reads and its relation to the manager/team is explicit; otherwise record `blocked` or `unavailable`.

### Stage 2: lineup and position-slot mapping

- Inputs: the observed team/club context and a private roster UID set from an existing reader; the candidate tactic/lineup structure from Stage 1.
- Read: starters, substitutes and position slots only; resolve supplied player UIDs through the existing ordered PERSON lookup (`EntityLinks.cs:37-70`) with the existing 32-UID and 64 KiB limits.
- Do not rebuild club membership in this probe; keep that as supplied provenance, as the current tool does (`EntityLinks.cs:70`).
- Acceptance: starter/substitute distinction, slot count and player UID join are consistent across two reads and with a user-provided manual UI observation. If the active-vs-selected slot cannot be distinguished, record `blocked`.

### Stage 3: raw enums, instructions and text meanings

- Combine Stage 0 static enum/property evidence with a bounded read of one known tactic that has non-default roles, duties, mentality and instructions.
- Preserve every raw value; map text only where a loaded localization entry and formatter path are independently established. Leave unobserved values unknown.
- Acceptance: each observed raw enum has a validated text counterpart or remains explicitly unknown; no default is guessed.

### Stage 4: P1 extras

- Only after Stages 1-3: multiple schemes, opposition instructions, set-piece arrangements, captain/taker order and tactical familiarity.
- Reuse the same budgets and fail-closed rules. Any UI state change needed to expose multiple schemes must be scheduled and performed by the user/coordinator, never by this worker.
- Acceptance: each sub-goal independently passes or is marked missing; one successful scheme must not be reported as full TAC-03 coverage.

## Verification matrix (planned, not executed)

| Case | TAC-01 | TAC-02 | TAC-03 | Status |
|---|---|---|---|---|
| Current stable state, repeated read | Required | Required | Required | Not tested |
| Save/load same save | Required | Required | Required | Not tested |
| Process restart | Required | Required | Required | Not tested |
| Two existing tactical schemes | Required | Required | Required | Not tested |
| Active vs selected slot distinction | Required | Dependency | Dependency | Not tested |
| Different manager/club | Optional | Optional | Optional | Not tested |
| Planned vs actual match lineup | Required | Dependency | Dependency | Not tested, no match advancement allowed |

Every cell starts as `not_tested`; no cell may be upgraded without the corresponding evidence.

## Single most concrete missing relationship (blocker)

The one relationship that would unlock this entire lane is **team (or manager) → active tactic slot object/identifier**: which business object owns the currently active tactic, and whether that slot is distinct from the currently selected UI slot. No such owner, RTTI type, property key, collection root, field offset, or pointer hop is present in the audited base. The only tactic-related code statement is the explicit unsupported declaration at `tools/FMAPI.MessageProbe/EntityLinks.cs:122` (`"current match/tactic position assignment"`). Therefore no pure decoder is warranted and no decoder was created in this wave; a decoder would require an anchor that does not exist. The Stage 0 static pass in the follow-up plan is the smallest next action that could produce such an anchor, and it is blocked only on operator-provided pinned binaries, not on game access.

## Conclusion

- Completed: none. No TAC-01, TAC-02 or TAC-03 field has a tactic-specific source location, decoder or validation result in this baseline.
- Candidate: only dependency-level and external leads. The existing team/club/player UID chain, player natural-position decoder and the attributed match-position report can support a future join, but none reads a tactic. TAC-01's prior "candidate" record has no source path in this worktree and remains unverified. TAC-02 and TAC-03 have no candidate.
- Missing: active/selected tactic slot, tactic identity, formation, starters/substitutes, lineup position slots, role/duty/mentality enums, team and individual instructions, multiple schemes, opposition instructions, set-piece arrangements, captain/taker order and tactical familiarity.
- Live read performed: no. No process, game install, UI, private capture, credential, account configuration or network was accessed; no bash/subprocess was used; no writes, injections, game calls or remote pushes were performed.

See `docs/research/interface-inventory.md:55-57` for the updated TAC status notes.
