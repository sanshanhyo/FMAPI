# Offline host read-boundary review

Existing IModGame path requires both manifest GameRead request and host grant before adapter invocation. ModScope identity owns context lifetime, distinct from manifest string ID. New tests check every denied request/grant combination with zero adapter reads, stale reader after same-ID replacement, and captured reader after failed load. These tests cover the existing GameSnapshot path only, not the experimental ISaveContextReader.

ReadSnapshot currently holds scope.Gate while invoking adapter.ReadSnapshot. This serializes ordinary external revocation on that scope, but Monitor locks are reentrant. There is no post-adapter scope activity check. Consequently this code review does not establish that a reentrant unload callback cannot produce an already-revoked result. No concurrency/reentrancy guarantee is claimed. Before save-reader exposure, explicitly specify whether callbacks/reentrancy are prohibited or implement/retest post-capture revocation; do not silently inherit lock semantics as an atomicity guarantee.

Future save-reader acceptance requires separate tests for host denial (no adapter call), failed load, same-ID replacement, shutdown, save-generation invalidation during capture and reentrant revocation. Registration identity and save generation must both be checked. Snapshot values retained by a mod cannot be erased by revocation; the contract revokes future service use, not knowledge of previously returned data. No sandbox against hostile in-process mods is implied.

This stage changes tests/documentation only. No save-reader wrapper, game observer, new permission, real read or network dependency is implemented. Cached-dependency test output is delivered separately; pinned restore remains blocked as documented.

Executed: 68 tests passed, 0 failed/skipped, net10.0, SDK10.0.403. Test dependencies are cached Test.Sdk17.11.1/xunit2.9.2/runner2.8.2; not the pinned project restore. ExitCode=0.
