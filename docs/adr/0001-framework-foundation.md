# ADR 0001: Independent SDK and adapter-based host

- Status: Accepted for the initial foundation
- Date: 2026-11-01

## Context

FMAPI is intended for multiple mods and consuming applications. Its requested scope includes events, UI extensions, and controlled writes. Game internals vary by build and platform, and the initial public repository has no independently verified real-game adapter.

## Decision

Use C#/.NET 10 for an offline, testable foundation. Separate public SDK contracts, host policy, and concrete adapters. Keep the sample mod dependent only on the SDK. Supply a synthetic adapter so contributors can build, test, and understand the contracts without a game installation.

Keep write execution disabled by default. Require explicit capability grants, command allowlists, adapter support, and validation. Commands default to dry-run. Represent UI extensions as owned declarations until a renderer has verified integration.

License newly authored project code under MIT. Review third-party code and dependency licenses before adding them. Do not import code or game-derived material from unrelated projects as part of initialization.

## Consequences

The framework can be developed independently of companion applications and game installations. Tests can exercise lifecycle and policy deterministically. The initial API is experimental; real adapter constraints may require contract changes before stabilization.

.NET 10 is the framework build target. It does not establish compatibility with any game's embedded runtime. Bootstrap, native interop, game-thread execution, UI rendering, and real write/recovery behavior remain adapter work. The same-process permission model coordinates cooperative mods and does not isolate malicious code.
