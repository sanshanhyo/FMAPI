# Minimal OnLoad completion invariant

Chosen minimal semantics: preserve existing callback-driven Unload/Dispose instead of introducing a broad transition guard. Load succeeds only if its original scope is still active when OnLoad returns. If already revoked, report ModLoadException without repeating cleanup or removing a same-ID replacement. If callback throws after revocation, likewise preserve completed cleanup/replacement and wrap original failure.

This intentionally changes only previously misleading load success and duplicate cleanup after reentrant revocation. No signature/version/enum changes; callers that deliberately self-unloaded in OnLoad must now handle load failure. General nested lifecycle ordering, concurrent calls and deferred shutdown remain undefined/caller-serialized. This narrow invariant supersedes only the relevant proposed matrix row; broad guard remains a proposal.

Reproduction: final before-fix run3 tests failed (ExitCode1). An earlier draft run retained old characterization assertions for2 cases (2 passed/1 failed); that output is retained as draft, not the final normative baseline. Final tests add an additional post-replacement callback exception branch.

Final after-fix:75 cached-dependency tests passed (0 failed/skipped), ExitCode0; CLI offline demo passed ExitCode0. SDK10.0.403/net10. No pinned dependency acceptance, net6 revalidation or game access claimed.
