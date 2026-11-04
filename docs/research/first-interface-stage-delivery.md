# First-interface stage delivery - 2026-11-04

Status: experimental0.1.0; no package/Release or stable SDK promise. Checked against current source, no new tests or game operations in this documentation-only stage.

## Exact reviewed baseline

- Remote branch: development/windows-session-gate-20261104.
- Remote reviewed commit: bc606c84c295c986650805697381bf0b68c81a11.
- Local content-equivalent commit: f77d0035bd62c480f66d4a32f1ca0fbfeaa2153a.
- Exact shared tree: d2a034bbd7279d68a2f088f59441675d5b3bd292.
- Last production integration: remote d6d5150054f7a4f54af52ac09190dbd9e6523adc / local20bfdc20fceab994cd617be3f815528f3174a0de. Later commits add tests/evidence/documentation.
- Remote commits are content-equivalent connector backups with different history/commit IDs, not byte-identical local commit objects. main unchanged.

## First domain interface types (FMAPI.Sdk/SaveContext.cs)

| Public type | Actual role |
| --- | --- |
| SaveContextSnapshot | SessionId, SaveLabel, Date(DateOnly), ManagerId, TeamId, IsSynthetic; immutable value record, no native pointers |
| SaveContextStatus | Available / Unavailable |
| SaveContextError | None, Unknown, NoSave, Denied, Unsupported, Expired, Failed, Closed |
| SaveContextResult | Validated status/reason/snapshot/error; retained3-argument constructor and3-value deconstruction |
| ISaveContextReader | ReadCurrentSave() |
| IModSaveContext | Optional SaveContext property; existing IModContext implementers need not change |
| ISaveContextSessionSource | Trusted source plus monotonic Generation; caller serialized, source owns reliable invalidation |

Existing foundation remains: IMod/IModContext/ModManifest/FmApiVersion/ModCapability; IModEvents/EventDispatchReport/EventHandlerFailure; IModUi/UiExtension/RegisteredUiExtension/UiExtensionKind; IModGame/IGameAdapter/GameBuildInfo/AdapterDescriptor/GameSnapshot/GameReadResult/GameReadStatus; GameCommand/CommandResult/CommandStatus/CommandValidation/CommandExecutionOptions. These older result types are not all validated constructors; do not assume new result invariants apply to them.

## Errors and permission behavior

Available requires non-null snapshot/Error=None; Unavailable requires null snapshot/non-None error. Invalid enum, blank reason or blank snapshot identity/label rejected by constructor. Legacy unavailable constructor maps to Unknown. Snapshot alone can be constructed with invalid strings, but a result rejects it. DateOnly validity is structural, not evidence of a real game date.

Host order: expired registration -> Expired; missing manifest request or host grant -> Denied; no composed source -> Unsupported. These do not invoke source capture. After capture: original registration revoked or Generation changed -> Expired/no snapshot. Null source result or source exception -> Failed/no snapshot; exception text not exposed. A source exception after revocation currently returns Failed, not necessarily Expired; both carry no value. Valid source results otherwise preserved. Mock supplies NoSave/Closed and synthetic snapshots; host does not reinterpret these as real compatibility.

## Lifecycle, identity and ownership

Original ModHost(adapter, options) remains; explicit3-argument overload supplies optional source. Source is caller-owned, not disposed by host. Core context implements optional extension and returns scoped wrapper, never raw source. Failed load, unload, shutdown and same-ID replacement revoke old registration. A new read on still-active mod may observe a new save generation; old immutable values remain historical and cannot be erased by revocation.

OnLoad completion requires original scope still active. Revoked load reports ModLoadException without repeated cleanup/removing a replacement; callback exceptions after revocation retain failure cause. ReadSnapshot rejects null adapter output and discards results after reentrant revocation. General nested lifecycle semantics remain partly undefined; broad transition guard proposal is not implemented.

IDs are scoped to SessionId, not persistent cross-save identity. Trusted source must increment Generation on every relevant change. Host cannot detect missed signals or dishonest sources. No atomic snapshot/native lifetime lock follows from rechecks.

## Thread and version boundary

Caller serializes host lifecycle, service calls, publishing and inspection. Internal locks are not overall thread safety. Event callbacks run synchronously on publishing thread before Publish returns. No scheduler, arbitrary concurrent runtime or game-thread dispatch provided. Avoid blocking callbacks on worker tasks that need the same host.

API Current=0.1.0; assembly version0.1.0.0/package metadata0.1.0-alpha.1. Host currently accepts matching major/minor, requested Build<=host Build and Revision<=0; not a blanket SemVer guarantee. Result init/with mutation removal and rejection of formerly contradictory construction are experimental breaking changes; selected old constructors/deconstruction remain tested. Full binary API compatibility is not claimed.

## Evidence users can inspect

| Evidence | Result and scope | Library file |
| --- | --- | --- |
| Scoped integration |83 net10 tests + offline demo passed |libfile_ea2645463fb88191a69a0e5ff193e36c |
| Edge cases/current old consumer |86 net10 tests passed; retained old binary calls passed; initial net6 harness failures retained |libfile_202f60d066808191aba085d8db88bf6d |
| net6 harness repair |86 net6 tests passed in isolated and repaired-root harness; candidate DLL pollution identified |libfile_87d84d9133cc819184c5089fd8cbd0f8 |
| OnLoad completion |3 normative regressions failed before;75 full tests + demo passed after |libfile_b95779bfb884819199c8f93fb0d098b0 |
| Reentrant read revocation |2 failed before;70 + demo passed after |libfile_b194fb8d6db88191a32468256641ea6e |

All are offline owned fixtures. SDK10.0.403; net10 runtime10.0.14 and net6 runtime6.0.36/reference pack6.0.36. Cached test versions: Test.Sdk17.11.1/xunit2.9.2/runner2.8.2; pinned project versions and coverlet not restored. Mock/Sample declare net10; supplemental net6 builds use explicit overrides, not newly declared support. Last86-test runs include new save failure cases. No new run claimed here.

## Unpassed gates and concrete next prerequisites

1. Restore pinned official dependencies using verified TLS or approved verified local package closure; generate/review transitive lock before locked-mode acceptance. No TLS bypass or install done.
2. Keep serial execution lane and clarify remaining nested lifecycle cases before broader public stabilization; do not market general concurrency safety.
3. Obtain Alpha acceptance owner's released read window. Agree process/start identity, exact native/GameAssembly fingerprints, one save and bounded target; no shared game mutation or uncoordinated read.
4. Implement independently qualified exact-build source, explicit unknown-build refusal, reliable save/selection teardown invalidation, native identity/type/collection bounds and source pointer rechecks. A Generation counter alone is insufficient.
5. Prove current-game-date source independently. Existing shared decoder concerns historical message dates. Manager/club/team links are historical bounded observations; team hierarchy and complete rosters are unproven.
6. Before in-process host integration, separately validate BepInEx/Il2CppInterop pinned runtime compatibility, scheduling/ABI/lifetime and licenses. Existing bridge evidence is offline, no chainloader/live compatibility guarantee.
7. Publish only sanitized reproducible evidence; keep saves, game binaries/metadata, names/UID captures, credentials and private records outside git. No Release/main changes authorized.
