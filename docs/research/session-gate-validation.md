# Offline session-gate validation (2026-11-04)

Baseline: recovery/reviewed-20261103 at dfbae4d. Original worktrees preserved.

The Windows internal gate provides exact GameBuildInfo equality and source/save prerequisites, generation invalidation and terminal disposal. It does not perform fingerprint detection, subscribe to a game lifecycle or make any real adapter available. Callers must serialize access. A future verified observer must invalidate before save/selection replacement and host shutdown, and recheck tokens before returning results. This check cannot provide an atomic snapshot or a process lifetime lock. BuildId must eventually be populated by exact qualified fingerprint detection, not user-provided display versions. No public SDK additions.

Validation:
- net10.0 adapter build: passed, 0 warnings/errors.
- Existing package-free runtime contracts: 8 groups passed on .NET 10.0.14.
- All Core.Tests source files, including 3 session-gate facts: 47 tests passed, 0 failed/skipped, using an external temporary verification project and existing trusted local NuGet cache.
- Cached test dependencies differ from repository pins: Test.Sdk 17.11.1, xUnit 2.9.2, runner 2.8.2; no coverage collector. The checked-in project/dependency pins were not changed. This is supplementary offline validation, not a successful pinned full-solution test.
- Pinned full-solution restore failed: NuGet TLS authentication SEC_E_NO_CREDENTIALS. Git remote access succeeded with command-scoped OpenSSL backend; TLS verification remained enabled. No security settings were weakened.
- git diff --check passed.

No game process access, UI automation, installation, injection, save mutation, remote push or release. Alpha acceptance remains independent. Live lifecycle integration waits for coordinated exact-build observer evidence.
