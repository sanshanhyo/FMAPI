# Lifecycle state machine proposal and characterization

Status: design proposal, not implemented behavior or stabilized public contract. Scope is synchronous host lifecycle, not game/save lifecycle. Existing caller-serialization requirement remains.

## Proposed states and transitions

| Host state | Request | Proposed result |
| --- | --- | --- |
| Ready | Load | Loading -> Ready on success or after failure cleanup |
| Ready | Unload | Unloading -> Ready even if cleanup throws |
| Ready | Dispose | Stopping -> Stopped; attempt every cleanup; aggregate errors |
| Loading / Unloading | nested Load or Unload | Reject before touching registration dictionary or invoking callback |
| Loading / Unloading | Dispose | Reject before changing state; no implicit deferred shutdown queue |
| Stopping / Stopped | Dispose | Idempotent no-op |
| Stopping / Stopped | Load / Unload | Reject |

Mod states: Absent -> Loading -> Active; failed loading -> Revoked -> CleanupAttempted -> Absent. Unload revokes services before callback; callback failure cannot restore active state. A cleanup callback is attempted once per registration. Replacement with the same manifest ID receives a distinct registration identity. Completed Load must never report success for an already-revoked scope.

Reads/events during OnLoad are currently possible through the initializing context. This proposal does not remove them; permission checks still apply. Their failure semantics must be tested if lifecycle transitions are rejected. Lifecycle operations requested from ordinary adapter reads/events outside a transition are a separate path: existing read-result revocation check remains required. Never hold this up as arbitrary callback/concurrency safety.

## Concurrency boundary

Do not silently convert caller-serialized lifecycle into a general concurrent API. A future transition guard must define whether overlapping calls reject or serialize and avoid host/scope lock inversion. A plain unsynchronized bool cannot claim cross-thread exclusion. Callback exception handling must reset transition state in finally. Event callbacks and adapter callbacks must not wait on other threads calling lifecycle while holding scope locks. This is a design constraint, not enforced scheduling.

## Reproducible probes and future acceptance

Two checked-in characterization cases run OnLoad -> self Unload and OnLoad -> host Dispose. They assert observed old behavior only: Load returns normally, active count0, cleanup1, captured context revoked. Passing these cases demonstrates the current surprising behavior, NOT approval of it. A future guard implementation must replace these expectations with explicit rejection/failure semantics and migration notes.

Before implementation add failing normative tests for all nested transition pairs, caught versus uncaught nested rejection, cleanup exceptions, same-ID replacement, guard reset after failed load and double Dispose during shutdown. Include adapter-read initiated unload to preserve existing result-discard behavior. General multi-thread stress does not replace a defined synchronization contract.

Decision: do not implement a broad guard in this stage. Rejecting nested lifecycle calls changes callback behavior and shutdown semantics; the matrix is proposed for review. No package/API stability claim, real game access or dependency recovery. Existing characterization evidence is sufficient to confirm the gap, not to declare it fixed.

Executed: targeted2 characterization cases passed, ExitCode0, SDK10.0.403/net10 using documented cached dependency versions. Actual OBSERVED lines retained. No full-suite rerun or pinned dependency acceptance claimed for this test/documentation-only stage.
