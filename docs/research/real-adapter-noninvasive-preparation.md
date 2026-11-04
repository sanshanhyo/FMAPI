# Non-invasive real-adapter preparation

Reviewed FMAPI baseline: remote62153aea951e2e941944cd9b466b0940cbc4402c / local220dcf63fa12a7524094ba91207c4e19faaddd7b, tree d48b8e4342793b9d6b199ab5f17773e4de55e532. Documentation/source-record review only; no game/process/save/binary read, injection, installation or test execution. FAR is treated as the requested reader-evidence track; no authoritative FAR repository/revision identity was resolved, so no FA/FAR equivalence is asserted.

## Evidence ledger

| Source | Evidence level and reusable conclusion | Not established |
| --- | --- | --- |
| ADR0003 FA match report | Historical attributed FA/user observations: identities, score/ticks, reported50 identities/22 on pitch and checked score/shots/xG/corners; one selected-player attribute/height/DOB comparison | Not repeated by FMAPI; counts not universal; not current FA acceptance or world/save context |
| live-session-20261103/native-entity-evidence | Historical bounded FMAPI manager GCuM/owner/employment checks; pinned native type/identity rechecks | General save/load observer, hotseat and lifetime guarantees |
| club-team-container-checkpoint | Historical2 TEAM backlinks and current employment membership | Team hierarchy, stable team IDs, complete roster |
| Local FA git3bf4c3a83b24c4e21946ae9232f47316f80516ab README/license record | Source documentation reports two experimental saved-summary facts for build27.0.0+2486695/schema31; fmsave container API reused; FA's own license not selected | No private save opened, no fresh output or current-game-date proof; summary label does not supply team ID |
| Shared GameDate decoder | Pure decoder for historical message-record encoding, offline-tested | Current game clock source |
|86 net10/net6 offline contract tests | Host permission/revocation/session machinery and fixture behavior | Real observer, pointer validity, BepInEx discovery or game compatibility |

Local FA git snapshot has no top-level LICENSE and no modules/game-bridge/match-reader at this revision. ADR0003 refers to another historical inspected source. Do not reconcile these as a single current runtime or assume either contains latest Alpha fixes. FA-provided evidence needs exact active reader commit, source hashes, acceptance logs and explicit license per changed file before reuse.

## Fingerprint profile (historical, not checked against current game)

- game_plugin.dll SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F
- GameAssembly.dll SHA256 820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A
- Metadata signature0xFAB11BAF/version39 per native-entity-evidence.
- Save-summary build27.0.0+2486695/schema31 is a separate reported save format gate, not interchangeable with native fingerprints.
- Before enablement also record platform/arch/storefront/release channel and process start identity. No friendly version string or filename may authorize offsets; mismatch returns Unsupported without fallback.

## Reuse and licensing gate

FMAPI-authored contracts/gates/decoder remain MIT. Prefer independently authored semantic integration around verified facts, without copying FA implementation or fixtures. ADR0003 records vendor FMMatchLens commit276d17ff677f90a0f13a75565c7af7d855756768 and an MIT notice; upstream identity/notices and FA delta rights still need direct reconciliation. That is not permission to copy the whole FA tree.

Pinned BepInEx6abdba4 license states LGPL2.1-or-later: https://github.com/BepInEx/BepInEx/blob/6abdba4/LICENSE . Candidate package6.0.0-be.785+6abdba4 historically hosts net6.0/.NET6.0.7; tests on6.0.36 do not prove that hosted runtime. Il2CppInterop upstream master LICENSE currently contains LGPL3 and incorporated GPL3 text: https://github.com/BepInEx/Il2CppInterop/blob/master/LICENSE . This is a moving-source license observation, NOT a selected dependency pin or metadata39 compatibility result. Pin exact shipped revision, review file notices/transitive components and distribution/source/relink requirements before bundling. No dependency added or legal clearance claimed.

FA local docs identify fmsave0.7.0 container API as MIT at e7b65cf60caaf0191330201b755bdcfe458777fa; its full FM26 reader reportedly rejects FM27. Independently verify upstream license/version before any use. FA-specific FM27 grammar remains unlicensed for copying until rights resolved. No game-owned generated assemblies/metadata/saves enter git.

## Minimal adapter design (not implemented)

1. ExactBuildProfile owns fingerprints/semantic field provenance internally, no offsets/native types in SDK.
2. One coordinated capture owner resolves selected manager -> employment TEAM -> CLUB and yields copied pointer-free identities only after exact type/backlink/bounds/end rechecks. Do not install a second match hook or call unknown native methods.
3. Verified lifecycle observer advances Generation before relevant selection/save change or disconnect. Start unready; missing/ambiguous owner/load state remains unavailable. A reliable observer is a hard prerequisite, not a flag set because reads looked plausible.
4. Current date requires a separate verified source with meaning/time boundary; save-summary dates and message dates cannot be substituted. SaveLabel is display metadata, not a private save path. Define mapping of manager/team identity to session-scoped strings before returning values.
5. Implement ISaveContextSessionSource only when all required fields and lifetime are qualified. If one required field is unknown, return Unavailable (NoSave/Unsupported/Failed as appropriate), never synthesize. Avoid widening public DTO now.
6. Compose through existing3-argument ModHost overload. GameRead grant, registration checks and generation comparison remain enforced. Trusted source is caller-owned/serialized; host has no game scheduler. Keep Windows placeholder unavailable until separately accepted.

## Concrete test/coordination queue

Offline first: obtain active-reader provenance manifest; classify original upstream versus FA deltas; record build-profile hashes; plan owned decoder fixtures, mismatched fingerprint/no-read tests, invalid identity/backlinks, field absence and generation invalidation. Reuse existing host tests for denied/no source/failed load/exception/null/stale registration; do not count them as native source tests. Do not duplicate proven probe paths or claim an implementation exists from this plan.

After Alpha owner releases a window: agree exact process/start/build, one save and a bounded manager/team/date target. Use one capture owner, aggregate64KiB ceiling initially, bounded collections and repeated identity checks; no game method calls, broad scans, writes, save manipulation or second hooks. Capture before-ready, ready, selection/save invalidation and shutdown only where explicitly coordinated. Acceptance must include versions, commands, sanitized actual output, expected/observed result and failures. Manual comparison is optional validation, never UI automation as a data source. Unknown build and missing field must fail closed.

Next non-invasive deliverable: active-reader revision/license/acceptance-log handoff from FA owner. Blocked here: unresolved FAR identity/current reader provenance, current-date/lifecycle source qualification, pinned dependencies and actual coordinated game window. No new simulated feature or production adapter added in this stage.
