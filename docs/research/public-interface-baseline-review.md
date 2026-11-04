# First public interface baseline and stability review

Status: reviewed design baseline, not a stable SDK declaration. Stability takes priority over further integration. No game integration work is authorized by this review.

## Baseline

Existing SDK: IMod/IModContext, scoped events/UI declarations, IModGame and IGameAdapter, default-deny command policy. SDK/Core target net6.0 and net10.0. Windows remains unavailable. BepInEx bridge compilation and offline session contracts do not establish chainloader compatibility.

First domain slice proposed: ISaveContextReader.ReadCurrentSave -> SaveContextResult -> SaveContextSnapshot. Values cover SessionId, SaveLabel, Date, ManagerId, TeamId and IsSynthetic. Scope is a single observed context, not save-file editing, roster enumeration or cross-save identity. Current executable implementation is owned mock fixtures only. This interface is experimental and is NOT approved as stable or exposed via IModContext.

## Review findings and release gates

| Area | Current implementation/evidence | Required decision before stabilization |
| --- | --- | --- |
| Compatibility | Additive SDK types; existing host interfaces untouched; DateOnly exists on both declared targets | Compile/test both targets and verify a consumer assembly; only net10 validation completed here |
| Result invariants | Positional record allows Available/null and Unavailable/non-null, invalid enum and empty reason | Define validated construction/factories and exhaustively test invariants before release |
| Errors | Only Available/Unavailable and human text; fixture invalid input throws; post-dispose read unavailable, load throws | Define machine-readable reasons for no save, denied, unsupported, expired and failure; prohibit text parsing; agree exception boundary |
| Identity | Mock creates fresh SessionId on replacement; IDs are strings scoped to it | Define invalidation on selection/save replacement and distinguish stable identity from session token; never expose native pointers |
| Lifetime | Dispose clears mock and prevents reload; immutable old snapshots remain historical | Host-scoped reader must revoke access after unload/failure; serialized access contract and observer ownership required |
| Permissions | No IModContext exposure; no GameRead bypass added | Host must enforce GameRead before invoking reader; no direct adapter service injection into mods |
| Provenance | Mock IsSynthetic=true; real date source absent | Build/evidence provenance and current-session qualification; historical message dates cannot supply current date |
| Versioning | FmApiVersion.Current remains 0.1.0; host accepts matching major/minor, requested Build <= host Build, Revision <= 0 | This is actual current code, not universal SemVer. Define and test accepted version forms; breaking contracts require explicit version decision and migration notes |

## Validation versus design

Executed in preceding stage: 60 Core.Tests cases with cached dependency versions, existing offline CLI demo. Save-context coverage is one end-to-end fact covering unloaded state, date/IDs, synthetic provenance, replacement and shutdown. Missing coverage includes result construction invariants, Clear, invalid fixture arguments, exact reasons, concurrent access, permission-scoped reader integration and binary/source consumer compatibility. No claim that these are tested. No tests rerun for this documentation-only review.

Existing cached test versions differ from pinned project versions; full pinned restore remains blocked by NuGet TLS. net6 and game execution were not validated in this series. 28 Python self-tests and 38 normalized recovery hashes are offline research checks only.

## Agreed scope for the next review

Hold public contract shape as an experimental proposal while resolving result invariants, machine-readable error semantics, session identity and host revocation together. Do not expand domain fields, wire a real reader, publish packages or promise stability. Preserve existing experimental consumers; document any chosen breaking change before implementation. No main branch changes or Release.
