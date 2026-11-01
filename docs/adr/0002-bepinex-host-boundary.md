# BepInEx host boundary

Status: accepted direction; minimal host bridge compiled offline, runtime integration unverified.

## Decision

Use BepInEx 6 as the candidate Windows bootstrap and plugin-loading foundation. Do not implement a competing injector, assembly scanner, dependency resolver, or remote installer. FMAPI supplies Football Manager domain contracts, scoped API services, game events, and build-specific adapters. FA is a consumer, not an owner of the public API.

BepInEx discovering a plugin and FMAPI registering that plugin's `IMod` are different operations. The thin BepInEx host bridge passes already loaded, explicitly trusted mod instances to `ModHost`; Core retains API-version checks, grants and resource cleanup. The offline CLI remains a development tool. No dynamic DLL loader is added in this change. See [bridge build and consumer contracts](../bepinex-host.md).

Game reads and events must come from verified internal business objects, functions and lifecycle hooks. UI nodes, active pages, screenshots, OCR and automated clicks are not data sources or fallbacks. Existing UI declarations are optional output metadata and do not establish game access.

Prioritize one current Windows game build that actually works. An update may require a new adapter. Unknown/unverified builds must be refused; a general cross-version abstraction is not a prerequisite for the first verified read.

## Read, Event and Command API scope

FMAPI's long-term scope includes both observing and modifying supported game state. Keep three domain-facing surfaces:

- **Read API:** validated, owned snapshots with explicit unavailable/unknown fields and build provenance.
- **Event API:** typed notifications from verified game business lifecycle sources, with defined ordering, thread delivery and subscription lifetime.
- **Command API:** named, narrowly scoped game operations with typed/validated inputs, explicit capability grants and observable outcomes. It is not a generic arbitrary-address memory-write interface.

For future commands, prefer verified game business functions on the correct game thread and at a valid lifecycle point so that the game's own invariants and dependent updates can be honored. Direct field writes require separate evidence for each field/operation, including affected invariants, dependent caches, object lifetime and save persistence. Reading a field successfully does not establish that writing it is safe or correct.

Keep existing host writes disabled by default, capability grants, host/mod command allowlists, adapter validation and non-mutating dry-run behavior. Revalidate state at execution; a successful dry-run does not guarantee later success. Report unsupported, denied, invalid and failed outcomes explicitly, including partial effects where relevant. Recovery or compensation must be specified per command; do not promise universal transactions or rollback.

This is scope/design only. It authorizes no native write implementation, arbitrary-memory API, game deployment or live mutation test. Current work remains focused on read evidence. Real commands require a separately scoped implementation and runtime validation before the adapter can advertise them.

## Runtime evidence and next implementation

The downloaded `BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.785+6abdba4.zip` package's `dotnet/Microsoft.NETCore.App.runtimeconfig.json` declares `net6.0`; `.version` and `coreclr.dll` identify .NET 6.0.7, runtime commit `0ec02c8c96e2eda06dc5b5edfdbdba0f36415082`. A recent build SDK does not establish compatibility with an older hosted runtime.

SDK/Core and the Windows placeholder now target both `net6.0` and `net10.0`, built using the .NET 10 SDK and explicit C# 12 syntax support. CLI, examples and mock remain .NET 10; the opt-in BepInEx bridge targets .NET 6. No BepInEx dependency enters the SDK. Internal defensive set wrappers replace frozen collections without exposing mutable grant/manifest sets. Compatible argument/enum/disposal checks preserve the public contract.

The package-free `FMAPI.Runtime.Contracts` executable exercises synthetic core contracts and links the bridge session source for registration/cleanup checks on .NET 10.0.0 and a task-local copy of the package's .NET 6.0.7 runtime. The .NET 6 runtime is launched with a copied .NET CLI host, not through BepInEx/Unity; this establishes core/session runtime execution only. Local xUnit restore lacked external packages; [CI for commit c85fc001](https://github.com/sanshanhyo/FMAPI/actions/runs/41332797590) subsequently passed 44/44 xUnit tests, the offline demo and eight .NET 10 contract groups on Windows, Linux and macOS. Do not replace the game's runtime to accommodate FMAPI.

Then verify bootstrap, exact game build identity, one internal read source and one lifecycle event. Record thread/lifetime requirements, behavior before/after save load, and repeated results while changing pages. Loading successfully alone is not evidence that reads work. Keep writes disabled and unsupported until separately verified.

`UnavailableWindowsAdapter` is an offline placeholder with no supported capabilities, no detected build, no process access, and no synthetic fallback. It is not a BepInEx plugin. `windows-status` reports this state and exits with code 3, including on non-Windows hosts.

## Sources

- [BepInEx plugin setup](https://docs.bepinex.dev/master/articles/dev_guide/plugin_tutorial/1_setup.html) distinguishes SDK tooling from plugin runtime targets.
- [BepInEx IL2CPP installation](https://docs.bepinex.dev/master/articles/user_guide/installation/unity_il2cpp.html) identifies platform-specific IL2CPP distributions. Its installation steps were not executed for this task.

FMAPI remains MIT. BepInEx's pinned [upstream license](https://github.com/BepInEx/BepInEx/blob/6abdba4/LICENSE) is LGPL 2.1; that license and other bundled dependencies remain separate from FMAPI. No BepInEx binary or source is included in this repository change. Local runtime copies are test inputs outside the repository, not deliverables. Review dependency notices and distribution requirements when packaging a bridge. This decision does not claim compatibility with any game build.
