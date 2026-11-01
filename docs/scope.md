# Project scope

FMAPI provides public contracts and host services for Football Manager mods and tools. It is an independent project that can be consumed by multiple hosts, mod authors, and companion applications.

## Product direction

The framework covers mod lifecycle, typed events, UI extension declarations, and controlled commands. Version-specific adapters translate between those contracts and a supported game build. A host chooses which mods to load and which capabilities to grant.

The initial API is `0.1.0`. During the `0.x` phase, contracts may change as adapter evidence and mod use cases develop. Compatibility checks must reject unsupported API versions rather than silently accepting them.

## Phase 0 implementation

- An SDK with mod manifests, lifecycle hooks, event/UI services, adapter identity/capabilities, and game command contracts.
- A host that validates manifests, manages loaded mods and owned resources, and applies command policy.
- Typed event subscriptions and declarative UI registrations that are removed on unload.
- Default-deny write dispatch, explicit grants and command allowlists, and validation without execution for dry-runs.
- A synthetic in-memory adapter, a sample mod, an offline CLI demo, and behavior tests.

The mock adapter is the only implemented adapter. UI declarations do not render inside a game. The sample is assembled by the demo host; automatic mod discovery and package installation are future work.

## Future adapter responsibilities

Real-game integration must establish source provenance, version/build detection, lifecycle and thread constraints, supported capabilities, and behavior when a capability is unavailable. Write support also needs command validation, execution timing, failure reporting, and explicit recovery semantics.

Game integration, injection/bootstrap mechanisms, editor interoperability, and native boundaries remain design and verification work. None is implied by the offline framework or by a successful build on a platform.

## Outside the initial scope

The initialization does not deliver a game runtime adapter, an in-game UI renderer, a mod marketplace, an assistant/LLM application, a save editor, or published packages. It does not distribute game-owned material or promise access to all Football Manager data.

The framework's permissions are a cooperative API policy. Loading untrusted code securely requires an isolation design beyond these same-process interfaces.
