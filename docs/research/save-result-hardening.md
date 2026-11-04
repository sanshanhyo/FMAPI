# Experimental save-result hardening

SaveContextResult now enforces: Available requires a snapshot and Error=None; Unavailable requires no snapshot and a non-None error. Unknown enum values, blank reasons and blank snapshot identities/labels are rejected. Read-only result properties prevent record with-expressions from bypassing validation. Snapshot itself remains a value record; any modified snapshot must pass validation when placed into a result.

SaveContextError provides None, Unknown (legacy unavailable construction), NoSave, Denied, Unsupported, Expired, Failed and Closed. Callers branch on Error, never parse Reason. Mock reader emits NoSave for unloaded/cleared and Closed after disposal; invalid fixture loading preserves existing state. Denied/Unsupported/Expired/Failed are vocabulary only, not implemented host behavior. Programmer misuse throws; operational host failure mapping remains a future design decision.

Compatibility: existing constructor signature, named arguments, three-value deconstruction and read properties remain. Potentially breaking: property setters/init and with { Status/Reason/Snapshot = ... } no longer compile; formerly contradictory construction now throws; record equality includes Error. Rebuild experimental consumers. No stable/binary compatibility promise, package release or version change is made. API version remains experimental 0.1.0; a release requires an explicit version/migration decision.

SessionId identifies one context generation, not a save filename or persistent manager/team identity. Replacement must generate a fresh session, and IDs cannot be joined across it. Snapshots are historical immutable values, not live handles. Callers serialize reader operations. A future host must enforce GameRead and revoke access after unload, failed load and shutdown; it must not infer readiness from UI. These mechanisms are not implemented by the public reader or mock and no new IModContext service is exposed.

New tests cover contradictory states, enum bounds, empty identity/reason, legacy construction/deconstruction, machine-readable clear/close and invalid-load preservation. net6, compiled binary consumers, concurrent access and real lifecycle remain unverified. Current live adapter stays unavailable; no game access.

Validation: 63 offline Core.Tests passed with documented cached dependency versions; CLI offline demo passed. Pinned full-solution restore and net6 remain unverified.
