# Roadmap

FMAPI develops in evidence-based stages. This roadmap records direction; it does not promise dates or game compatibility.

## Phase 0 — Offline foundation

The initial implementation provides:

- SDK contracts, manifest checks, and mod lifecycle.
- Typed events and mod-scoped UI declarations.
- Default-deny command dispatch with explicit grants, allowlists, and dry-run validation.
- A synthetic adapter, sample mod, offline demo, and behavior tests.
- MIT licensing, contributor guidance, architecture/compatibility records, and CI configuration.

## Phase 1 — First real adapter

Select one legally installed game build and one platform. Define the bootstrap mechanism and adapter lifecycle, verify read/event sources, and register capability-level evidence. Unsupported data must remain explicit. Establish thread scheduling and host failure behavior before introducing real writes.

Completion requires reproducible runtime results, documented compatibility boundaries, and a fixture strategy that does not redistribute game material.

## Phase 2 — Game UI and controlled writes

Implement a renderer for a small documented UI surface. Add a limited command set with validation, explicit grants, execution timing, audit information, and failure/recovery behavior. Evaluate preview and later game builds independently.

Completion requires runtime tests for every claimed surface and command, including unsupported-version behavior and failed/partial operations where applicable.

## Phase 3 — Mod distribution and stabilization

Define package discovery, dependency/API version rules, update policy, and host isolation expectations. Publish SDK packages only after package identity, ownership, and release automation are established. Stabilize contracts from real mod and host use cases.
