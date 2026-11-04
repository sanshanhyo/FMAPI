# Architecture

FMAPI keeps public mod contracts separate from host policy and game-build integration. SDK/Core target .NET 6 and .NET 10; the CLI and examples remain .NET 10. All current executable behavior is offline.

```text
Sample mod / future third-party mods
                |
                v
          FMAPI.Sdk contracts
                |
                v
          FMAPI.Core host
          |      |       |
       events   UI    command policy
                         |
                         v
                  IGameAdapter
                         |
                 Adapters.Mock
                 synthetic state
```

`FMAPI.Sdk` has no dependency on Core or a concrete adapter. `FMAPI.Core` consumes the SDK's contracts. The demo host composes Core, the mock adapter, and the sample mod. A future game adapter can implement the same contracts without exposing game-version details to mods.

## Mod lifecycle and resource ownership

A mod supplies `IMod.Manifest`, `OnLoad(IModContext)`, and `OnUnload()`. `ModHost.Load(mod, grant)` checks the manifest and API compatibility before calling the mod. The context provides `Events`, `Ui`, and `Game` services with the loaded mod's identity and grants.

The host owns the lifetime of context resources. Event subscriptions and UI registrations belong to one loaded mod and are cleaned up when it unloads. Failed loads must also clean up registrations made before the failure. A context from an unloaded mod must not remain an active route to host services.

This initial lifecycle is synchronous. Callers must serialize `Load`, `Unload`, and `Dispose`. It does not define game-thread scheduling or a general concurrent plugin runtime. Those concerns require explicit contracts before real game integration.

## Events

Events use typed subscriptions. The host can publish events; a mod can subscribe and publish through its scoped context when permitted. Subscription cleanup prevents unloaded mods from continuing to receive callbacks. The current event mechanism demonstrates host/mod communication using synthetic events. Event origins, game timing, delivery guarantees, and version-specific payloads must be specified by future adapters.

## UI extensions

The registry accepts declarative extension descriptions, associates them with their owner, rejects duplicate IDs within that mod, and removes them with the mod's resources. Different mods have separate ID namespaces. Declarations are a host-visible model; the current framework contains no game UI renderer. A renderer will need to define supported surfaces, placement rules, input routing, and game-version compatibility.

## Controlled commands

The host evaluates a command through these gates:

1. The mod context is active and the command is valid.
2. Host policy explicitly enables writes.
3. The manifest requests the write capability and the host explicitly grants it.
4. Both the host-wide command allowlist and the host's per-mod grant allowlist permit the command.
5. The adapter advertises support and validates the command against its state.
6. A dry-run returns the validation result without calling command execution.
7. An explicitly requested execution is handed to the adapter.

Commands default to dry-run. The host defaults to writes disabled. An unknown or unsupported command is not executed. The mock adapter executes only against its synthetic in-memory state.

The policy governs calls through FMAPI. It is not a security boundary against arbitrary code already executing in the same process. Real adapters must also enforce execution on an appropriate game thread, revalidate time-sensitive state, and document how partial failures are handled. A dry-run does not promise a later execution will succeed, and the core does not promise universal rollback.

## Version and compatibility boundaries

The SDK API version identifies framework contracts. Game identity and capabilities belong to the adapter. A compatible API version does not establish game compatibility, and a platform build does not establish successful runtime integration.

Keep game offsets, fingerprints, internal types, and private bootstrap details out of public SDK contracts. Record verified adapter support using the [compatibility evidence requirements](compatibility.md).

## Windows host direction

Reuse BepInEx for bootstrap and plugin loading; FMAPI owns domain APIs, scoped services and game adapters. See [the host boundary decision](adr/0002-bepinex-host-boundary.md) for the runtime-target prerequisite. Internal business objects/functions/lifecycle are the only allowed read/event sources; UI scraping and UI-driven fallbacks are excluded.

`Adapters.Windows` currently contains only an explicitly unavailable placeholder. It never reads a process or returns a snapshot. The CLI's `windows-status` command reports this without falling back to the mock; exit code 3 means integration is unavailable. Existing mock demonstration behavior is unchanged.

The opt-in `FMAPI.Host.BepInEx` project references the external BepInEx package and owns one default-deny Core host. Consumers register SDK mods through its thin wrapper API and dispose the returned registration on unload. Its session logic is checked offline; actual chainloader/Unity execution is unverified. See [bridge build instructions](bepinex-host.md).

## Experimental read-session prerequisite

The internal Windows `ReadSessionGate` rejects mismatched or synthetic builds, unverified sources and unavailable saves. Replacing or invalidating a session expires earlier tokens. Callers must serialize it and invalidate on selection/save changes and shutdown. This is an offline prerequisite implementation only: it is not wired into the placeholder adapter, detects no game lifecycle and provides no lock or atomic snapshot. No public SDK changes or new compatibility claims are introduced.

Current experimental interface status and unresolved lifecycle boundaries are tracked in [the closeout review](research/first-interface-closeout-review.md). Ordinary lifecycle calls remain caller-serialized; no general reentrant lifecycle guarantee is defined.
