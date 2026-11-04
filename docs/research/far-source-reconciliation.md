# FAR/FA source reconciliation - read-only

This supersedes the earlier license-unknown conclusion only for the newer inspected FA snapshot, not for all historical copies or active binaries. No game/process/save/binary read, runtime action, file modification in FA or tests performed.

## Resolved source identity and limits

Newer diagnostic repository HEAD dcd5c6d26e30abef96528d51d874933054ca8e01, branch diagnostic/alpha15-empty-reply. Reader paths are tracked and git diff --quiet HEAD for LICENSE/LICENSE-SCOPE and match/offseason sources returned0. Untracked candidate binaries/profiles/logs exist; they were not treated as committed source or inspected for private contents. Last source-change commit for match/offseason tree:0de0614c278a434e7be5bc2b748bad44c64d3645 (reuse pinned native binary lease per capture).

Older separate repository HEAD3bf4c3a83b24c4e21946ae9232f47316f80516ab lacks top-level LICENSE and match-reader. Its object is not in the newer clone, so direct cross-repository git diff fails Invalid revision range; no missing history was fabricated. Directory/source inventory differs. Current runtime provenance is NOT proven: no process inspected, installed/candidate binary source receipt or hash-to-commit binding established. The term FAR does not uniquely identify a repository/module in available evidence; match-reader versus offseason-reader must be distinguished in handoff.

## License correction and provenance

Newer root LICENSE is MIT, Copyright2026 FootballAssistant contributors. LICENSE-SCOPE says own source/documentation covered; third-party notices retained; fonts/images/bubbles excluded; prior GPL copies retain granted rights. License migration commit e2da689d97c4a806d2b245bae5ffab4f314dd6d6. This is actual repository notice inspection, not a comprehensive rights audit. Earlier speculation that FA may be GPL or unlicensed is historical and not current for this exact snapshot.

match-reader/vendor/LICENSE is MIT, Copyright2026 osnsyc. Historical ADR0003 identifies upstream FMMatchLens276d17ff677f90a0f13a75565c7af7d855756768. Reconcile exact upstream tree/deltas and preserve both upstream and project notices before extraction; root MIT does not relicense unrelated dependencies/assets. No code copied in this review. WorldDateLookup cites GPL3 fm-editor research and explicitly says no code copied; source comment alone does not independently audit provenance.

Newer dependency record pins BepInEx b782da4ac54e1072d2857f4a2f77c80c3ef08005 and Il2CppInterop81a6f78c8b653e0da4a3420ac4cd00819e8b6292 (recorded LGPL2.1 and LGPL3-only respectively). These differ from FMAPI's historical BepInEx6abdba4 compilation profile. Dependency record is not proof of actual shipped binaries. Match csproj targets net6 and references external BepInEx/MonoMod DLLs with Private=false. Inventory actual distribution separately.

## Evidence classification

- ADR0003 historical attributed match/user checks remain evidence only for their old session. Current acceptance doc windows-match-acceptance explicitly states hook_installed/producerVerified are not football-fact or release acceptance; stale/process/instance/sidecar checks do not authenticate native provenance.
- alpha15-local-diagnostic records HTTP200/nonempty response/renderer acceptance for an isolated candidate, not correctness of club answer, bubble/speech completion or FMAPI data support. No raw diagnostic events/screenshots opened/copied here.
- WorldDateLookup source comment reports one normal day advance matched. Still experimental; save/session switching and other builds unverified. This adds an attributed historical clue beyond message-date decoding, not fresh FMAPI date acceptance.
- NativeReadProfile requires native BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F, GameAssembly820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A and metadataA380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C. Read from source constants only; no files matched in this stage.

## Reusable component queue, not an approved copy list

| Component | Eligible review path | Missing proof |
| --- | --- | --- |
| Pure position/player value decoders | Review own/source MIT and upstream deltas; synthetic fixtures only | Field provenance and held-out semantics per field |
| NativeReadProfile/NativeReadContext | Reuse concepts: exact hashes, capture-scoped lease, bounded read/error handling | Source/commit/hash manifest, lifetime and thread proof |
| NativeManagerReader/TEAM relation | Map copied IDs behind existing session source after exact type/backlink checks | Reliable selected-owner/save invalidation, hierarchy/completeness |
| WorldDateLookup | Independently validate historical date route; no message-date substitution | Current coordinated evidence and reload behavior |
| Match tick/buffers | Single shared capture owner; host delivers copied values outside native hook | ABI/runtime license reconciliation and no second hook |
| FA transport/status | Reuse specification ideas for freshness and unknown status | Do not import FA paths/env/HTTP/JSON as FMAPI domain API |

Working-file source SHA256 hashes for selected files are delivered in evidence. They differ from ADR0003 historical hashes, but CRLF/normalization and changed source both affect byte hashes; without historical bytes, hashes alone do not prove semantic delta. Git commit IDs and notices are separate from working-file hash identity.

## Next required handoff

FA owner supplies active match/offseason reader selection, exact source commit plus dirty patch manifest, built binary hashes and source receipts, approved dependency/notices inventory and sanitized acceptance logs tied to the same process/build/session. Do not infer any from repository HEAD or candidate folder. Then reconcile upstream deltas, select one bounded manager/team/date slice, and test lifecycle/unknown-build failures offline before requesting released Alpha window. Current game remains untouched; no runtime activation/port authorized by these notes.

Later evidence capture from parent workspace using git -C was rejected by Git dubious-ownership safety check (exit128). No safe.directory exception or ownership change attempted. Earlier successful inspections from repository execution context supply the reported commit/diff result; final fresh Git state is not confirmed. Evidence package preserves this distinction.
