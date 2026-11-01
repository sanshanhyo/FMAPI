# Archived message research tools

Original exploratory tools preserved when research was paused. They are not adapters, supported APIs, or part of the solution/CI. Prefer `FMAPI.MessageProbe` for its bounded, tested message diagnostic. No game data or third-party binaries are included.

- StaticProbe: PE/RTTI inspection, Iced disassembly, generated interop metadata/map inspection, and explicit read-only Windows live probes. Build with .NET 10 and `-p:IcedAssemblyPath=<absolute path to a separately obtained Iced.dll>`. Iced is an external MIT dependency; its source and license are at https://github.com/icedland/iced. The map layout was checked against BepInEx/Il2CppInterop's Common/Maps/MethodAddressToTokenMapBase.cs; no implementation was copied. Input binaries are opened as data, not loaded for execution.
- BundleProbe: exploratory UnityFS/LZ4 reader for one explicitly selected local archive. Modes: a search string, `bindings`, or `window:<hex offset>:<hex length>`. An optional third argument writes decompressed bytes. Do not commit any output. This is a resource-inspection aid, not a runtime dependency on game UI objects.

These prototypes can throw on invalid input and lack comprehensive parser tests. Live exploratory modes have fewer validation checks than MessageProbe, assume the analyzed object layouts, and print private raw data. They must not be automated against arbitrary processes or used as a production reader. No game functions are invoked. Run only with explicitly authorized local inputs and keep all output outside the repository.

The original prototypes built with zero warnings/errors. StaticProbe's final stream inspection succeeded before pausing. BundleProbe successfully inspected selected local archives earlier; this is not a malformed-input test suite. The existing MessageProbe synthetic self-test and framework tests passed in CI for commit 48331a5.
