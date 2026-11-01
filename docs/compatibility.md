# Compatibility and evidence

This file separates framework validation from real-game adapter support. As of the initial repository foundation, **no real Football Manager adapter is implemented or verified**.

## Current support

| Component | Target | Status | What it establishes |
| --- | --- | --- | --- |
| Offline framework | .NET 10 | Implemented; use local checks and CI results for validation | Public contracts, host behavior, synthetic demo |
| SDK/Core/session runtime contracts | .NET 6.0.7, Windows x64 | Synthetic contracts exercised on an isolated copy of the BepInEx package runtime | Core/session execution only; no BepInEx chainloader, Unity or game access |
| BepInEx host bridge | BepInEx 6 Unity IL2CPP be.785+6abdba4 | Compiled offline against actual dependency DLLs; runtime loading unverified | Entry-point API compatibility only |
| CI matrix | Linux, Windows, macOS | Configured; remote runs depend on repository hosting | Offline framework portability only |
| Mock adapter | Synthetic in-memory state | Implemented | Adapter and command policy examples |
| Windows placeholder | Offline .NET 10 | Unavailable; no process or game access | Explicit unsupported reads/writes only |
| Football Manager 27 | Any game build/platform/storefront | Unverified; no adapter | No runtime support claim |
| Other Football Manager editions | Any | Unverified; no adapter | No runtime support claim |

The mock identity must remain visibly synthetic. A .NET build, unit test, existing external project, or previous private experiment does not establish an FMAPI real-game capability.

## Adding verified adapter support

Record all of the following with each adapter claim:

- Adapter name/version and FMAPI commit.
- Game edition, exact game build, preview/release channel, and storefront.
- Operating system/version and CPU architecture.
- Bootstrap/runtime prerequisites and lifecycle behavior.
- Each capability actually exercised, with source/provenance and known limitations.
- Reproduction steps, observed result, and verification date.
- Unsupported-version behavior and, for writes, validation, thread execution, and failure/recovery semantics.

Store owned or synthetic reproduction material in the repository. Do not attach game binaries, extracted game metadata, databases, or personal saves. When evidence cannot be shared, state what was checked and what remains independently unverified.

Game updates can invalidate an adapter. A known engine family or metadata format alone is insufficient to mark a game build as supported.

The active FA reader has reported user-checked match/player reads. The [shared-reader decision](adr/0003-share-verified-match-reader.md) records those reports separately from FMAPI runtime evidence and identifies reusable source boundaries. No FMAPI game capability is marked supported solely from that report.

A subsequent FA report adds one out-of-match player lookup by UID with exact type validation and user-checked attributes/profile fields, without match-cache input. This informs the future adapter boundary only. Global date, managed club and complete roster access remain unresolved; FMAPI has not implemented or runtime-verified this lookup.
