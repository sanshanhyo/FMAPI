# Scoped save-context host integration

Experimental optional IModSaveContext extension exposes a host-owned ISaveContextReader. Existing IModContext implementations and original ModHost constructor remain unchanged; opt-in composition uses a three-argument overload (adapter, options, source), avoiding ambiguity in existing (adapter,null) calls. Source is caller-owned and is not disposed by ModHost. It must not be exposed directly to mods.

Source contract ISaveContextSessionSource requires a monotonic Generation, incremented whenever save/selection context changes. Caller serializes source changes and all host operations. Mock increments on load/clear/first disposal. Host requires both manifest GameRead and grant before invoking source, returns Unsupported if absent, and Expired for revoked registrations or generation changes during capture. Null results and exceptions map to Failed without source exception text. Snapshot is discarded on expiry. A new call on the same valid mod reader may observe a new session; old value snapshots remain historical data.

Generation reliability is a trusted adapter prerequisite, not detected by host. No counter can protect against a source that lies or misses lifecycle signals. No concurrent/atomic game snapshot guarantee, real Windows source, scheduler or process access is added. Denied sources are not called; source failures are not retried. Mod scope identity and save generation are independent.

Targeted synthetic tests cover all denied request/grant combinations, same-ID replacement, unload/shutdown, no-source status and reentrant unload/session replacement during capture. Failed-load save-reader-specific coverage, source exception/null result cases and net6/binary consumer revalidation remain follow-up gaps unless separately recorded. Existing broader host tests do not automatically validate this new route.

Compatibility: additive SDK interfaces and constructor overload only; default hosts now offer optional extension but return Unsupported without opt-in source. API remains experimental0.1.0, no stability/package release. Prior documents saying no wrapper exists are historical and superseded only for this owned synthetic route. Real lifecycle observation remains unimplemented.

Executed:83 cached-dependency tests passed (0 failed/skipped), ExitCode0; CLI offline demo passed ExitCode0. SDK10.0.403/net10.0. No pinned dependency or real-game acceptance.
