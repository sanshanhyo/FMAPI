# Host save-context boundary and compatibility acceptance

The checked-in package-free SaveContext.Consumer verifies retained constructor/property/deconstruction use. It does not exercise removed init setters. Current runtime contracts already test default deny, failed loads, stale registration tokens and shutdown revocation for existing host services; these are NOT save-reader host integration tests.

Proposed save-reader host boundary: enforce GameRead before calling the adapter; context wrapper belongs to one mod registration identity, never merely its string ID. Unload/failed load/shutdown must revoke before cleanup and discard in-flight results. A denied/revoked call must not invoke an adapter. Save generation identity and mod registration identity are independent. No wrapper, concurrency policy or observer has been implemented by this stage. Future tests must cover denial invocation counts, captured reader after unload, failed OnLoad, reload with same mod ID and in-flight invalidation. Existing host tests are evidence for reusable policy patterns only.

net6 acceptance uses existing 6.0.36 reference packs with SDK10, no install. SDK and runtime contracts build; 8 runtime contract groups pass on .NET6.0.36. Mock project has only net10 declared; supplemental net6 build required explicit TargetFramework/TargetFrameworks=net6.0 and LangVersion=12.0 and passed. This does not change its declared targets.

Pinned offline restore fails NU1100 for coverlet.collector6.0.4, Test.Sdk17.14.1, xunit2.9.3 and runner3.1.4. No packages.lock.json found; exact direct references are not a transitive dependency lock. No TLS/security settings weakened. Cached-version tests from earlier stages do not satisfy this gate.

Binary probe uses pre-hardening SaveContext.cs extracted from parent of5212561, compiled as FMAPI.Sdk. First run used incorrect assembly version1.0.0.0 and failed FileLoadException. Corrected baseline must use repository version0.1.0-alpha.1 (assembly0.1.0.0), rebuild consumer then replace only SDK DLL with current net6 SDK. Scope: retained constructors/properties/deconstruction only, not all binary compatibility or behavior. Failure logs retained as well as corrected output.

Raw acceptance logs and probe sources are in the external acceptance archive delivered with this review; local paths may appear but no game captures, save data, credentials or environment secrets were collected. No game access.

Final isolated binary consumer passed on .NET6.0.36. Source consumer output also reports PASS; final process completion recorded in delivered logs. Initial failure output/pipeline limitations are documented in FAILURES.txt. Failed consumer process cleanup remains uncertain after CIM access denial; no game process was targeted.
