# Session-bounded read delivery slice

Historical selected-manager evidence (native-entity-evidence.md) establishes a GCuM pointer, UID and employment relation with bounded identity rechecks. It does not establish safe cached pointers across selection/save changes. The new internal SessionReadCoordinator implements only the delivery portion of that integration: reject an unavailable token before calling a reader, call an explicitly supplied reader, and discard its entire result if the session changed during capture. Stable sessions may return owned synthetic data. Reader exceptions propagate; no partial value is returned.

The capture delegate is a trusted adapter implementation, not a public plugin API. It must implement exact-build fingerprint checks, native type/identity and byte bounds, copy values out of native storage, and recheck its source pointers. Callers serialize access and provide verified lifecycle invalidation. The coordinator does not supply locking, lifecycle detection, game-thread dispatch or a live reader. No real manager DTO is invented and the existing Windows placeholder remains unavailable.

Synthetic tests cover denied reads never invoking capture, replacement/invalidation discarding captured data, stable delivery, and capture exceptions. These tests do not promote historical observations to current-session support. Next integration step after Alpha coordination: wrap a qualified bounded selected-manager reader and observe save/selection invalidation; do not use property names as native semantics.

Validation: all 52 Core.Tests cases passed on net10.0 using the previously documented cached test dependencies (Test.Sdk 17.11.1, xUnit 2.9.2, runner 2.8.2). Pinned full-solution restore remains blocked by NuGet TLS; no live game access.
