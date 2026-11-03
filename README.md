# FMAPI

**Football Manager Modding API** is an independent, unofficial framework for building Football Manager mods and tools in C#.

[简体中文](README.zh-CN.md) · [Architecture](docs/architecture/overview.md) · [Roadmap](docs/roadmap.md) · [Contributing](CONTRIBUTING.md)

FMAPI aims to give mods a versioned API for lifecycle management, events, UI extensions, and controlled game commands. Game-specific integration belongs in adapters, so a mod can depend on public contracts without depending on a particular game's memory layout or a companion application.

## Current status

This repository contains the **Phase 0 offline foundation**, targeting .NET 10 and API version `0.1.0`. The API is experimental and may change before a stable release. No packages or real-game adapters have been released.

| Area | Available now | Planned integration |
| --- | --- | --- |
| Mods | Manifest/API compatibility checks and load/unload lifecycle | Discovery and packaging |
| Events | Typed subscriptions scoped to a loaded mod | Events from verified game adapters |
| UI extensions | Declaration registration and unload cleanup | Rendering inside supported game interfaces |
| Game access | Adapter contracts and synthetic in-memory state | Version-specific Football Manager adapters |
| Controlled writes | Default-deny dispatch, explicit grants, command allowlists, dry-run validation | Verified game commands with adapter-specific execution rules |

The offline demo changes synthetic data in memory. It does not connect to Football Manager. All real-game compatibility is [unverified](docs/compatibility.md).

## Quick start

Install the [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0), then run these commands from the repository root:

```sh
dotnet restore FMAPI.slnx
dotnet build FMAPI.slnx --configuration Release --no-restore
dotnet test FMAPI.slnx --configuration Release --no-build
dotnet run --project tools/FMAPI.Cli --configuration Release --no-build -- demo
```

The demo loads the sample mod, handles an event, registers a UI declaration, demonstrates a denied write, validates a dry-run, and explicitly authorizes a command against the mock adapter. It also shows resource cleanup when the mod unloads.

See [the sample mod](samples/FMAPI.SampleMod) for a small implementation of the SDK contracts. The CLI is an offline demonstration host; real-game installation and injection are outside this initialization.

## Project layout

```text
src/FMAPI.SDK/              Public contracts for mod authors and adapters
src/FMAPI.Core/             Host, lifecycle, events, UI registry, command policy
tests/FMAPI.Adapters.Mock/    Synthetic in-memory adapter
tools/FMAPI.Cli/              Offline demonstration host
samples/FMAPI.SampleMod/  Example mod using the public SDK
tests/FMAPI.Core.Tests/     Host behavior and policy tests
docs/                      Scope, architecture, compatibility, decisions
```

## Controlled commands

Writes are disabled by default. A command can execute only when the host enables writes, the mod requests the write capability, the host explicitly grants it, the host-wide and per-mod allowlists permit the command, and the adapter supports and validates it. Commands default to dry-run; validation never executes the command. Read [the architecture](docs/architecture/overview.md) for the policy boundary.

These checks coordinate cooperative mods through the FMAPI API. They do not isolate malicious code loaded into the same process. A real adapter must define game-thread scheduling, state validation, failure handling, and any recovery behavior before claiming write support.

## Development and licensing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing public contracts or adding an adapter. CI is configured to build, test, and run the offline demo on Linux, Windows, and macOS. This matrix concerns the framework; it does not establish game compatibility.

FMAPI is licensed under the [MIT License](LICENSE). Third-party dependencies keep their own licenses. Game binaries, databases, saves, and game-derived assemblies or metadata are not distributed here.

FMAPI is not affiliated with or endorsed by Sports Interactive or SEGA. Football Manager and associated marks belong to their respective owners.
