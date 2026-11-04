# Reentrant read revocation reproduction

Scope: existing IModGame.ReadSnapshot, owned synthetic SpyAdapter only. A synchronous adapter callback unloads its own mod or disposes the host before returning a snapshot. A scope Monitor lock is reentrant on the same thread, so it cannot by itself prevent this transition.

Expected contract: no Available result or snapshot escapes after revocation; subsequent calls through captured context are rejected. This does not revoke historical values already delivered and does not provide a native game lifetime lock. No save-reader host integration or general concurrent lifecycle guarantee is introduced.

Before fix: 2 targeted tests failed, expected not Available but got Available for unload and shutdown. Fix rechecks the original scope after adapter capture and returns existing Failed with no snapshot when revoked. No public signatures or enum values changed. Intentional behavior change: a result previously returned after revocation is now rejected; adapter work already performed cannot be undone. Tests use cached dependency versions, not pinned restore.

After fix: all70 tests passed (0 failed/skipped), ExitCode0; offline CLI demo passed, ExitCode0. SDK10.0.403/net10; raw before/after/demo output retained and delivered with username paths redacted.
