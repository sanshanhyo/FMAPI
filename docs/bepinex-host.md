# BepInEx host bridge (offline build only)

`src/FMAPI.Host.BepInEx` is an opt-in .NET 6 plugin entry point for BepInEx 6 Unity IL2CPP. It has compiled against the unmodified `6.0.0-be.785+6abdba4` package. It has **not** been loaded through BepInEx or tested inside Football Manager. Its only adapter is explicitly unavailable. No offsets, game objects, lifecycle hooks, UI scraping, or synthetic fallback are included.

## Build without a game installation

Use the pinned .NET 10 SDK and a separately extracted, trusted BepInEx package. Supply its root explicitly; there is no automatic download, installation or global configuration:

```sh
dotnet restore src/FMAPI.Host.BepInEx
dotnet build src/FMAPI.Host.BepInEx --configuration Release --no-restore -p:BepInExRoot="<extracted-package-root>"
```

`BepInExCoreDir` can alternatively identify the package's `BepInEx/core` directory. Missing reference files produce an actionable build error. The bridge is deliberately outside `FMAPI.slnx`, so normal offline framework builds do not require the external package. NuGet reference packs for .NET 6 may still be needed to build with a newer SDK.

Output is `src/FMAPI.Host.BepInEx/bin/Release/net6.0/`. The FMAPI assemblies are `FMAPI.Host.BepInEx.dll`, `FMAPI.Core.dll`, `FMAPI.Sdk.dll` and `FMAPI.Adapters.Windows.dll`. BepInEx references use `Private=false`; its DLLs are not copied into this output. Do not deploy the entire build directory or replace host runtime files. Actual installation requires a separately authorized game test and a compatibility record.

## Consumer contract

The plugin GUID is `org.fmapi.host`, plugin metadata version `0.1.0`; the SDK remains experimental API `0.1.0`. A consumer's BepInEx wrapper declares a hard dependency on that GUID, then calls `FmApiPlugin.RegisterMod(IMod)` from its `Load()` and retains the returned `IDisposable`. Dispose the registration from the consumer's `Unload()`. The domain mod itself can continue referencing only `FMAPI.Sdk`; its thin BepInEx wrapper also references the host bridge.

BepInEx owns discovery and dependency ordering. FMAPI does not scan DLLs or create another assembly loader. The bridge creates one `ModHost` with default grants and writes disabled. Calls before host startup or after shutdown fail explicitly. Duplicate IDs and incompatible manifests use Core validation; failed loads clean up. Disposing a registration revokes its context; a stale token cannot unload a replacement. Host unload revokes all contexts and attempts every mod's cleanup even if one throws. Callbacks are synchronous; this bridge does not yet define game-thread scheduling or hot-reload guarantees.

Successful plugin initialization logs that game access is unavailable. Read requests return `Unsupported` with no snapshot. Writes remain denied. Local mod events and UI declarations retain their existing offline meanings and are not game events or rendered game UI.

## Validation and source boundaries

The package-free runtime contracts link the bridge's exact `HostSession.cs` source and exercise registration/unregistration, stale tokens, failed loads, and shutdown failures on .NET 6.0.7 and .NET 10. They do not instantiate `BasePlugin`, execute BepInEx callbacks, or verify chainloader discovery. Compiling the bridge against actual BepInEx DLLs separately checks its entry-point signatures and attributes.

API reference: pinned upstream [BasePlugin](https://github.com/BepInEx/BepInEx/blob/6abdba4/Runtimes/Unity/BepInEx.Unity.IL2CPP/BasePlugin.cs) and [plugin/dependency attributes](https://github.com/BepInEx/BepInEx/blob/6abdba4/BepInEx.Core/Contract/Attributes.cs). FMAPI's bridge code is original MIT code calling these APIs. BepInEx remains separately licensed under its [LGPL 2.1 license](https://github.com/BepInEx/BepInEx/blob/6abdba4/LICENSE); no BepInEx source or binaries are vendored or relicensed. Any later distribution must preserve the relevant third-party notices and obligations.

Next runtime test, after authorization: prove BepInEx discovers the host and an owned consumer plugin, verifies registration/unload logging, and continues reporting unavailable reads. Only a later exact-build adapter test can establish a real internal business-object read and lifecycle event.

Before any binary distribution, record the pinned BepInEx version, its notices and corresponding-source provision/access arrangement, and keep compatible LGPL components replaceable. Inventory each bundled dependency's own license; FMMatchLens's MIT license does not cover unrelated dependencies or assets. No binary release or dependency bundling is authorized by this offline build work. These are packaging follow-ups, not a completed distribution review.
