# Manager/club offline source audit: ENV-01, IDX-01, MGR-01, MGR-02, CLB-01, CLB-02

> Status: offline audit only. **No live read, process access, UI read, network access, private capture access, credential/account access, injection, native call, scan, save/game write, match advance, subagent, or subprocess was performed in this wave.** All live observations cited below are historical source evidence, not results reproduced here. No raw names, UID lists, message prose or private capture payloads are reproduced.

This document audits existing source for the assigned IDs at the pinned research evidence base. The rows in `interface-inventory.md` aggregate several goals; evidence below is therefore partial evidence, not full completion of any task row.

## 1. Provenance and pinned versions

| Item | Value recorded here | Verification limit in this wave |
|---|---|---|
| Inventory/todo baseline | `docs/research/interface-inventory.md`, `docs/research/data-discovery-todo.md`, pinned upstream `01b53c5` as assigned | Not re-verified with git, because the worktree `.git` points outside the sandbox and no subprocess tools were allowed |
| Research evidence base | Local base `99aba1d` as assigned | Same; commit identity was supplied by the task, not independently verified here |
| Branch | `research/parallel-manager-club` as assigned | Same |
| Game edition/platform | Windows FM27, x64 | Declared in source docs; no game/process access this wave |
| Native module fingerprint | `game_plugin.dll` SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F` | Fingerprint is a hard gate in `tools/FMAPI.MessageProbe/Program.cs:100`; not re-hashed here |
| Generated assembly fingerprint | `GameAssembly.dll` SHA-256 `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A` | Checked at `tools/FMAPI.MessageProbe/EntityLinks.cs:75-77`; not re-hashed here |
| Metadata fingerprint | Metadata SHA-256 `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`; signature/version `0xFAB11BAF` / 39 | Declared in `tools/FMAPI.MessageProbe/PositionFields.cs:8` and `docs/research/native-entity-evidence.md:7-9`; not re-derived here |
| Unity runtime label | Product `6000.3.18f1-custom (96cdb67fb884)`, file `6000.3.18.9883062` | Historical checkpoint `docs/research/message-reader-checkpoint.md:69`; not re-read here |
| External reader build label | External reader manifest build `21bfd30` | Historical cross-check only, `docs/research/manager-player-links-checkpoint.md:17`; no FA implementation was copied into FMAPI |

All RVAs/field offsets below are module-relative to the pinned `game_plugin.dll` fingerprint unless explicitly marked as metadata/GameAssembly evidence. A different binary hash must fail closed.

Files audited:

- `tools/FMAPI.MessageProbe/Program.cs`
- `tools/FMAPI.MessageProbe/EntityLinks.cs`
- `tools/FMAPI.MessageProbe/PositionFields.cs`
- `tools/FMAPI.MessageProbe/README.md`
- `docs/research/native-entity-evidence.md`
- `docs/research/manager-player-links-checkpoint.md`
- `docs/research/message-reader-checkpoint.md`
- `docs/adr/0003-share-verified-match-reader.md`
- `docs/compatibility.md`
- `src/FMAPI.Sdk/Game.cs`
- `src/FMAPI.Adapters.Windows/UnavailableWindowsAdapter.cs`
- `src/FMAPI.Adapters.Mock/MockGameAdapter.cs`

## 2. Evidence strength key

| Label | Meaning in this audit |
|---|---|
| static-pinned | Instruction-boundary or pinned metadata evidence tied to the native fingerprint. Establishes layout/selection semantics, not current-save values. |
| code-pinned + synthetic | Read/decode logic exists in the probe with synthetic self-tests and fail-closed checks. Does not prove a live path or a game-level contract. |
| live-historical | A prior session observation recorded in checked-in research notes. Not repeated in this wave; not a cross-save or cross-build guarantee. |
| candidate | An entry/field exists, but its meaning, completeness or stability is not established. |
| missing | No source evidence for the target capability. Must remain unknown/unavailable rather than inferred. |

## 3. Per-ID audit

### ENV-01 — build, process session, game date, load state, pause/match phase, snapshot time

**Target and current status:** read; inventory status remains `部分实现`.

**Completed source evidence**

- Native binary identity is a hard precondition: SHA-256 gate in `tools/FMAPI.MessageProbe/Program.cs:100-111`, repeated for GameAssembly in `EntityLinks.cs:75-77`; pinned position profile hashes in `PositionFields.cs:6-8`.
- Process session identity: `Process.GetProcessById`, start time stored, and reads fail if the process exits or its start time changes (`Program.cs:113,122`). Output carries `processId` and `processStartedAt` (`EntityLinks.cs:122`).
- Bounded read transport: per-read address/size validation and 64 KiB per-capture budget (`Program.cs:88-97,107,121`).
- Date layout decoder: packed year in the high word and a one-based day-of-year in the low nine bits; leap-year handling and the native `1900/day 1` invalid sentinel (`Program.cs:79-87`); synthetic cases cover leap/non-leap, masked flags, invalid sentinel and day 366 (`Program.cs:22`). Native formatter evidence is recorded at `docs/research/message-reader-checkpoint.md:40`.
- Snapshot rechecks: roots, vectors, selected pointers and identity fields are re-read and compared at the end of a capture (`EntityLinks.cs:34,69,117,119`); output explicitly says `atomicSnapshot=false` (`EntityLinks.cs:122`). `--verify-repeat` compares two fresh captures and fails closed on disagreement (`Program.cs:50`; `tools/FMAPI.MessageProbe/README.md:11,15`).

**Candidate / partial**

- The date decoder is proven as a codec, but it is applied only to a message-object date field at `Program.cs:166-169`; that is not a global game-date source.
- Build identity is currently a binary fingerprint, not a full game-build descriptor. The build label `21bfd30` comes from an external reader manifest, not from the probe.
- Process session identity is not the same as a save/load epoch. There is no `load_epoch` capture field.

**Missing in this worktree**

- Global game date object/pointer and its update rules.
- Load start/finish state, save/session identity, load epoch.
- Pause state or match phase.
- Snapshot capture timestamp, mixed/invalid snapshot detection beyond root/vector rechecks, and a documented lifecycle lock.
- Independent UI/game-date comparison.

**Unknown semantics**

- Meaning of unused packed date bits other than the low nine bits; any timezone/display-time interaction (dates are treated as calendar values).
- Whether rechecks are sufficient during load/unload or whether a coherent in-process lifecycle integration is required.

**Minimal bounded follow-up read plan (not executed here; coordinator scheduling required)**

1. Offline static, later: resolve named candidates for game date, load state and pause/match phase through pinned metadata/key registration and function-bounded disassembly. Record name-to-key-to-getter evidence; no process read.
2. Live, later: read only the proven candidate global pointers plus a 4-byte packed date and a small state word; cap at 64 bytes per object, 64 KiB per capture, 2 fresh captures, one stable session. Expected evidence: date agrees with the in-game calendar; pause/match phase state agrees with the user-visible state.
3. Invalidate on any changed root/pointer/date/state mismatch; return `unavailable`, never a substituted value.
4. Reload/date-change/load-state tests must be separately scheduled; do not advance a date or match for verification in this wave.

### IDX-01 — person/team/club/contract/fixture UID, type, dedup, references

**Target and current status:** read; inventory status remains `部分实现`.

**Completed source evidence**

- PERSON registry/database table: global RVA `0x5703738`, validated vtable `0x4CA5278` (`EntityLinks.cs:39-40`).
- Ordered UID index layout: mode byte `0x5703DE0`; indirect vector behind table `+0x80` when `+0x5C` bit 0 is clear, otherwise inline vector `+0x88/+0x90/+0x98`; `+0xA0` is a dirty/sort-needed flag (`EntityLinks.cs:41-45`). The probe refuses the dirty-cache case and never calls native sorting (`EntityLinks.cs:42`; checkpoint `manager-player-links-checkpoint.md:23`).
- UID lookup: signed positive UID compared against record `+0x0C`, binary search capped at 32 steps per UID and 32 explicitly supplied UIDs (`EntityLinks.cs:47-58`).
- Type validation: exact RTTI for `HUMAN_NON_PLAYER_MANAGER`, `HUMAN_NON_PLAYER`, `ACTUAL_PLAYER`, `FULL_CONTRACT`, `TEAM`, `CLUB` (`EntityLinks.cs:24-25,82,89,98,103-104`; `Program.cs:153,158`).
- Reference chain: human PERSON UID at `+0x0C` → `FULL_CONTRACT` → contract `+0x10` `TEAM` → team `+0x30` `CLUB`; club UID read from `+0x0C` (`EntityLinks.cs:90-104`).
- Dedup safeguards: requested UIDs must be distinct (`Program.cs:47`); more than one selected-owner match is rejected (`EntityLinks.cs:118`); no first/unique-owner fallback (`EntityLinks.cs:107-113`).
- Addresses are used only as transient read locations with end-of-capture rechecks; entity output is UID/type based, not a stored address.

**Candidate / partial**

- Person UID is established at `+0x0C`; the separate `+0x8` four-byte value is reported only as `personReferenceCandidate` (`EntityLinks.cs:90,115`), not a second UID.
- Club UID is read for the manager’s employment chain. Team `+0x0C` is used in a special-team-ID comparison (`Program.cs:312`) but is not emitted as a general team UID.
- Contract type/kind is read, but no contract UID field is read.
- No fixture UID path exists in this worktree.

**Missing**

- Typed contract UID, team UID and fixture UID.
- Cross-entity index/reference validation beyond the single manager employment chain.
- Registry-wide dedup and reference integrity; pagination/coverage boundaries (IDX-02 scope).
- Cross-save/load UID persistence proof.
- Fixture-to-competition/match relations.

**Unknown semantics**

- Whether record `+0x0C` is a stable database-scoped UID for every entity type or only the observed types.
- Whether `personReferenceCandidate` at `+0x8` is stable, a local reference or a different identifier.

**Minimal bounded follow-up read plan (not executed here)**

1. Offline static, later: locate UID accessors for `TEAM`, `FULL_CONTRACT` and `FIXTURE` from known vtables/RTTI, bounded to the identified functions. Record fields and recheck rules; no process access.
2. Live, later: for one active manager chain, read at most 3 objects (contract/team/club) plus one available fixture, 64 bytes each, 2 fresh captures, one session. Emit opaque type/UID tokens only, never names or a UID list.
3. Reject any path that would publish an address as an ID or that cannot recheck the same UID at end of capture.
4. Cross-entity relation and dedup acceptance requires a separate bounded roster/index request (IDX-02), not this row.

### MGR-01 — current human manager UID/name, club, contract; active vs candidate vs page object

**Target and current status:** read; inventory status remains `部分实现`.

**Completed source evidence**

- Human-manager owner collection: global RVA `0x56F3008`, vtable `0x4E2D678`, pointer vector at `+0x18/+0x20/+0x28` (`EntityLinks.cs:81-84`; `Program.cs:152-155`; checkpoint `manager-player-links-checkpoint.md:13`).
- Human object layout: vbtable `0x4CC086C`, PERSON subobject at `+0x440` with vtable `0x4CC08D8` (`EntityLinks.cs:89`; `message-reader-checkpoint.md:42`).
- Employment path: PERSON virtual `+0x3C0` = RVA `0xF48D30`; establishes vtordisp at PERSON − 4, complete-object vbtable `+8` offset and contract pointer at the resulting virtual base `+0x80` (`EntityLinks.cs:91-96`; checkpoint `manager-player-links-checkpoint.md:15`).
- Contract: `FULL_CONTRACT` kind byte `+0x26`, kind accessor virtual `+0x50` = RVA `0x301970`; contract `+0x10` → `TEAM`; team `+0x30` → `CLUB`; club UID `+0x0C` (`EntityLinks.cs:98-104`).
- Current-selected manager source: metadata literal index 9070 `GameCurrentManager`, index 9071 adds `UniqueId`; GameAssembly encoded literal slot RVA `0x333AD88`; key `GCuM` `0x4743754D` built at RVA `0x4F9DE0` and paired at `0x4F9E39..0x4F9E4F`; dispatch `0x380020` branches at `0x380223`; selected global at RVA `0x56F32C8` written at `0x38027D`; getters `0x378FC0/0x3810B0`; teardown `0x381150/0x6CEFC70`; UID property path `0x37C980`; context getter `0x37CB40` (`docs/research/native-entity-evidence.md:15-17`).
- Probe acceptance: selected record must have `HUMAN_NON_PLAYER` PERSON RTTI and exactly one pointer match among validated human-owner PERSON subobjects (`EntityLinks.cs:107-113`); zero/unmatched selections are unavailable; duplicate matches are rejected (`EntityLinks.cs:118`); selection pointer/identity are rechecked (`EntityLinks.cs:119`).
- Historical live evidence: a focused selection/employment capture in the then-running session returned an available matching selection and employment club (`docs/research/native-entity-evidence.md:31`; `tools/FMAPI.MessageProbe/README.md:39`). This is historical, not a result of this wave.
- Name candidates: PERSON virtual getters `+0x138/+0x140/+0x148` = RVAs `0xF479F0/0xF47A10/0xF47A30`, three pointer fields at virtual-base `+0x28/+0x30/+0x38` (`docs/research/message-reader-checkpoint.md:89`; read at `Program.cs:249-272`). They remain candidate-only.

**Candidate / partial**

- Active-manager selection is established for the observed native source, but only for that source/session class. It is not a general multiplayer/hotseat authority guarantee.
- Name strings are candidates only; no FIRST_NAME/LAST_NAME identity is claimed.
- Page/UI objects and controller instances are deliberately not read; only the native business selection global is used.

**Missing**

- First/last/display-name formatter semantics and a validated name field contract.
- Reload, selection-switch, multi-human and hotseat behavior.
- National-team concurrent employment, unemployment and employment-status semantics.
- Cross-save UID persistence and active-selection lifetime locking.
- Page object versus active business selection comparison.

**Unknown semantics**

- Whether `GCuM` is the local foreground user, the save’s primary user, or a broader current-selection property under all modes.
- Meaning of the raw human flag at `+0x422` (`EntityLinks.cs:106`); it is emitted raw and must not be promoted to active state.
- The raw contract-kind byte’s full enumeration; only the native `>=2` affiliation check is evidenced (`manager-player-links-checkpoint.md:15,51`).

**Minimal bounded follow-up read plan (not executed here)**

1. Live, later: run the existing minimal selection/employment capture in one stable loaded session; 64 KiB cap, 2 fresh captures, no UI/controller reads. Expected evidence: selection available, one matched owner, person UID, contract kind, club UID token.
2. Separately schedule one reload and one user-authorized manager switch; repeat the same bounded capture after each and record pass/fail/not_tested. Do not force a switch in this wave.
3. Offline static, later: finish the person name formatter/getter semantics before exposing any name. Then read at most the three known candidate pointers under the existing budget; never publish raw names.
4. Keep active selection fail-closed on zero/unmatched/duplicate/changed state; never fall back to first/unique owner.

### MGR-02 — multiple managers, national-team dual role, unemployment, switch/reload identity and employment state

**Target and current status:** read; this audit upgrades the inventory row from `未开始` to `研究中` only because a candidate multi-owner enumeration entry now has source evidence. The target capability is still not delivered.

**Completed source evidence**

- The probe can enumerate the human-owner collection up to 16 entries and validate each owner’s PERSON identity, contract type/kind, contract→team→club pointers and raw `+0x422` flag (`EntityLinks.cs:81-116`).
- The native selection global can identify at most one selected owner; duplicate matched ownership is rejected (`EntityLinks.cs:118`).
- The message probe still requires exactly one human manager and explicitly throws otherwise (`Program.cs:156`); multiple human managers are declared unsupported in `message-reader-checkpoint.md:30` and `tools/FMAPI.MessageProbe/README.md:7`.

**Candidate / partial**

- Multi-owner enumeration is structural only. No capture with more than one human manager is recorded in this worktree.
- Unemployment is not represented as a status. A selected owner without a `FULL_CONTRACT` payload simply yields no club UID; that is not a validated employment state.
- No national-team dual-role, hotseat, switch or reload evidence exists.

**Missing**

- Multi-manager identity rules and active selection after switching.
- National-team concurrent employment.
- Unemployment/retirement/inbox ownership state.
- Reload and hotseat behavior; lifetime locking.
- Semantics of raw `+0x422` and any per-owner active/foreground flag.
- Employment history and contract state changes (MGR-03/CON domains).

**Unknown semantics**

- Which human-owner entry is the active user in a multi-manager session; a single `GCuM` match is evidence only for the observed mode.
- Whether national-team contracts use the same `FULL_CONTRACT`/`TEAM` path or a distinct relation.
- Whether unemployment corresponds to a null contract, a distinct contract kind, or another state field.

**Minimal bounded follow-up read plan (not executed here; environment-dependent)**

1. Requires a user-provided save/session with at least two human managers and/or a national-team job; without such a session, record `blocked` and do not scan/guess.
2. Live, later: enumerate at most 16 owner entries, 64 bytes per owner plus the existing contract/team/club reads; 64 KiB cap, 2 fresh captures. Output counts and opaque UID tokens only.
3. With prior authorization, repeat after one user-driven switch and one reload; compare selected pointer/UID and contract chain. Record pass/fail/not_tested, not a general rule.
4. No active selection fallback to first/unique owner; no UI/controller/page-object reads.

### CLB-01 — club and first-team UID/name, roster entry, reserve/youth/national hierarchy

**Target and current status:** read; inventory status remains `部分实现`.

**Completed source evidence**

- Club object reached from team `+0x30`; club UID read from `+0x0C` (`EntityLinks.cs:103-104`).
- Club short-name candidate: club `+0xC8` strict length-prefixed UTF-8 (`Program.cs:245-247`). It is a candidate field, not the final rendered name.
- Club alternate names: container at `+0xD0`, entries with kind/language metadata, kinds `0x18/0x19` selected for text candidates; standalone flag at `+0xBA` (`Program.cs:283-303`; `message-reader-checkpoint.md:99-103`).
- Team name-related candidates: custom short name `+0x20`, name-kind `+0x28`, special team-ID comparison (`Program.cs:273-280,312-313`).
- Roster provenance is explicit input, not rebuilt here: `clubMembershipVerifiedHere=false` (`EntityLinks.cs:70`); the probe only reads the first 64 PERSON-index slots without input, and only the explicitly supplied 1–32 UIDs with input (`EntityLinks.cs:14-35,37-71`; `tools/FMAPI.MessageProbe/README.md:33,35`). A prior historical capture used a requested roster input (count only; no UID list retained).

**Candidate / partial**

- Club/team UID and club short-name candidates exist, but final club/team name formatting is not established.
- First-team identification is implicit in the manager’s employment `TEAM`; there is no explicit team-type/level field emitted.
- Roster membership is not independently reconstructed; the earlier requested-UID set has external provenance only.

**Missing**

- Club roster collection entry and independent roster enumeration.
- Reserve/youth/national-team hierarchy and team-type classification.
- Complete club/team name semantics (short/long/common/override).
- Roster count versus UI/external roster reconciliation and dedup rules.
- National-team club/team distinction.

**Unknown semantics**

- Meaning of team `+0x28` name-kind and club `+0xBA` standalone flag beyond their observed raw roles.
- Which team object is the true first team when a club has multiple levels.
- Whether club `+0xC8` or alternate-name kinds define the final displayed name under overrides/localization.

**Minimal bounded follow-up read plan (not executed here)**

1. Offline static, later: locate the team/club roster collection and team-type/classification fields from known vtables and RTTI; record exact vector offsets and bounds checks before live use.
2. Live, later: for one club, read at most 2 team objects and at most 64 roster pointer entries, 64 bytes per object, 2 fresh captures, one session. Emit aggregate counts and opaque UID tokens only; no names/UID list.
3. Compare roster count and membership summary against the user-visible/external roster; report discrepancies explicitly, do not fill gaps.
4. Add reserve/youth/national classification only after a static type field is proven; otherwise leave hierarchy `unavailable`.
5. Do not claim final club/team name until the formatter semantics are established.

### CLB-02 — club country, league, type/pro status, reputation, rivals/relations, affiliates, ownership

**Target and current status:** read; inventory status remains `未开始`.

**Completed source evidence**

- None for the target fields. Existing source only covers CLB-01 identity/name candidates (club `+0x0C`, `+0xC8`, `+0xD0`, `+0xBA`) and contract kind, not club country/league/type/reputation/relations/affiliates/ownership.
- Team `+0x28` is a name-kind candidate, not a club type/pro-status field.
- Contract kind `+0x26` is contract-scoped, not club-scoped.

**Candidate / partial**

- None promoted. Club `+0xBA` and alternate-name records are not evidence for club type, country, league, reputation, rivals, affiliates or ownership.

**Missing**

- All target fields and their relation UIDs.
- A club metadata/competition/ownership entry point.
- Reputation raw/scale semantics, relation types and ownership structures.
- Any UI/known-fact comparison.

**Unknown semantics**

- Entire domain remains unknown in this worktree; no field name may be inferred from generic football vocabulary.

**Minimal bounded follow-up read plan (not executed here; depends on CLB-01)**

1. Offline static, later: resolve named club metadata candidates (country, competition, type/pro status, reputation, rivals, affiliates, ownership) through pinned metadata/literal registration and function-bounded disassembly. Keep a candidate list; do not bulk-scan process memory.
2. Live, later: only after a proven candidate, read one club object with at most 8 candidate fields, 64 bytes each, 2 fresh captures, one session. Compare country/league/type against UI; keep reputation raw + scale unknown unless proven.
3. Emit relation/affiliate/ownership references as opaque UID/type tokens only; do not infer names from proximity or ordering.
4. If no candidate is found, mark `blocked`/`unavailable`; do not synthesize defaults.

## 4. Cross-cutting observations

- The SDK/Core state in this repository is still generic and synthetic. `FMAPI.Sdk.GameSnapshot` is a string dictionary plus build info (`src/FMAPI.Sdk/Game.cs:29-39`), and `UnavailableWindowsAdapter` explicitly has no reads (`src/FMAPI.Adapters.Windows/UnavailableWindowsAdapter.cs:9-17`). `MockGameAdapter` is synthetic and is not evidence for any ID here.
- Entity output is UID-based only where a UID field is actually read. Addresses remain transient read locations with end-of-capture rechecks; no address is presented as an ID.
- Snapshot reads are non-atomic by design. Rechecks can detect a change but do not provide a lock or a load epoch (`EntityLinks.cs:122`; `tools/FMAPI.MessageProbe/README.md:11`).
- `docs/adr/0003-share-verified-match-reader.md:17` still records that global date, managed club and complete roster were unresolved in the reported FA observations. The native GCuM work later establishes a current-selected manager/club path for the observed session, but not a global-date or full-roster contract.
- Historical live results must not be relabeled as this wave’s results. No new names, UID lists or private samples are recorded.

## 5. Minimal bounded follow-up read plan summary

All requests below require separate coordinator scheduling and authorization. They are not executed in this wave. No request includes a write, UI action, match advance, date advance, scan or native call.

| ID | First bounded target | Budget / bound | Repeats | State requirement | Expected evidence |
|---|---|---|---|---|---|
| ENV-01 | Candidate game-date/load/pause globals after offline name/key proof | ≤64 bytes per object; 64 KiB per capture | 2 | Stable loaded save; no advancing | Date/state agrees with game calendar/UI; changed value fails closed |
| IDX-01 | UID accessors for TEAM/CONTRACT/FIXTURE | ≤3 objects + 1 fixture; 64 bytes each; ≤32 UIDs | 2 | Same loaded save | Opaque typed UID tokens; no address-as-ID |
| MGR-01 | Existing `--manager-selection` path | 64 KiB per capture | 2, plus separately scheduled reload/switch | Stable out-of-match session | Selection status, person UID, contract kind, club UID |
| MGR-02 | Human-owner enumeration on a multi-manager/national-team save | ≤16 owners; 64 bytes each; 64 KiB | 2 per state | User-provided multi-manager save; user-driven switch/reload only | Owner count and selected-owner behavior; no fallback |
| CLB-01 | Club roster/team-type collection after offline proof | ≤2 teams; ≤64 roster pointers; 64 KiB | 2 | Same loaded save | Aggregate roster count/types; discrepancies explicit |
| CLB-02 | Club metadata candidates after offline discovery | ≤8 fields; 64 bytes each; 64 KiB | 2 | Same loaded save | Country/league/type candidates; raw reputation; opaque relation tokens |

Failure policy for every request: stop at the stated bound, return `unavailable` on any validation or identity mismatch, and never substitute a default, mock value, or UI guess.

## 6. Completed / candidate / missing

**Completed (offline source audit only; not live validation)**

- Pinned provenance and fingerprint gates are documented for `game_plugin.dll`, `GameAssembly.dll` and metadata.
- ENV-01: process-session identity, read budgets/rechecks, date codec and synthetic date tests are located.
- IDX-01: PERSON UID field/index, UID lookup bounds, exact RTTI checks and the manager employment reference chain are located.
- MGR-01: native GCuM selection source, owner collection, employment chain, selection matching and name-candidate locations are documented.
- MGR-02: bounded multi-owner enumeration exists as a candidate entry; single-manager-only message path is explicit.
- CLB-01: club UID, team→club relation, club name candidates and explicit roster-input provenance are documented.
- CLB-02: absence of target-field evidence is confirmed for this worktree.

**Candidate**

- ENV-01 global game date/load/pause state (codec exists, global source missing).
- IDX-01 team/contract/fixture UIDs and full reference integrity.
- MGR-01 manager name semantics, page-object distinction, reload/switch behavior.
- MGR-02 multi-manager identity, national-team dual role, unemployment, switch/reload.
- CLB-01 final name semantics, independent roster entry, reserve/youth/national hierarchy.
- CLB-02 all target fields remain without a candidate entry.

**Missing**

- Global game-date/load-epoch/pause/match-phase source and mixed-snapshot detection.
- Typed UIDs for contract/team/fixture and cross-entity reference validation.
- Multi-manager/national-team/unemployment/switch/reload evidence.
- Independent roster reconstruction and team hierarchy/type classification.
- Club country/league/type/reputation/rivals/affiliates/ownership evidence.

**Explicit statement:** no live read was performed in this wave; the findings above are an audit of checked-in source and historical notes only. No raw samples, names or UID lists are included.
