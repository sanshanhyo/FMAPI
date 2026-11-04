# First-interface closeout review

Review scope: SDK result/identity surface, MockSaveContextReader, ModHost lifecycle/read path and BepInEx HostSession. This is an independent second source review by the same execution agent, not an external reviewer or another model.

Concurrency: lifecycle methods require caller serialization; locks do not promise arbitrary concurrent lifecycle/read/event safety. Mock reader and internal session gate likewise require serialization. Reentrant read revocation now discards results, but that does not ratify arbitrary reentrant Load/Unload callbacks. In particular, Load currently returns after OnLoad without rechecking that its registration remains active; a mod that unloads itself during OnLoad could make a successful Load return with no active mod. Treat this as an unresolved lifecycle design edge, not verified support. No such callbacks are used by examples.

Compatibility: public constructors and deconstruction retained for save results; init mutation removal and newly rejected contradictory values are intentional experimental changes. Source/net6 scoped binary consumer evidence covers selected calls only. Version remains experimental0.1.0, no stable package promised. Locked dependency graph absent; pinned restore blocked. Cached test versions are supplementary evidence.

Errors: SaveContextResult validates status/error/value relationships, but historical GameReadResult and other positional records remain externally constructible. Host must not emit Available/null even if a faulty adapter violates nullable contracts. Null adapter output is tested separately in this stage. Error text is diagnostic, not a machine protocol; no new enums introduced.

Documentation: earlier baseline reviews are historical findings. save-result-hardening.md supersedes their result-invariant/error gaps; reentrant-read-revocation.md supersedes the unchecked successful read-return finding in offline-host-read-boundary-review.md. Save-reader permissions, revocation wrapper, real observer and game-date source remain unimplemented. No game compatibility follows from mock/test success.

Pause gates after closeout: design general reentrant lifecycle semantics before further host exposure; restore official pinned dependencies before full dependency acceptance; coordinate exact-build game evidence before real adapter integration. Do not expand interfaces or claim these gates passed.

Null-output reproduction: before fix, targeted test failed Expected Failed / Actual Available (ExitCode1). Fix returns existing Failed with no snapshot for null adapter output after checking revocation. No public signatures changed; valid adapter behavior is unchanged. This is defensive handling of an implementation contract violation, not expansion of supported adapter behavior.

Final stage output: 71 cached-dependency tests passed (0 failed/skipped), ExitCode0; offline CLI demo passed, ExitCode0, SDK10.0.403/net10. Before-fix targeted test failed ExitCode1. No screenshots needed for this console-only acceptance; actual console output preserved.
