# net6 harness resolution repair

Root cause confirmed by MSBuild ResolveReferences diagnostic: an external validation project at workspace root had default None item collection enabled. CandidateAssemblyFiles resolved FMAPI.SampleMod to its net10 output and FMAPI.Sdk to the pre-hardening consumer-baseline assembly despite explicit current net6 HintPaths. This explains both System.Runtime6/10 conflict and missing current SDK symbols. It is a validation-harness resolution bug, not evidence that current net6 SDK references net10.

PE metadata inspection of current SDK/Core/Mock/Sample net6 outputs shows System.Runtime6.0.0.0 references. A new isolated-directory harness ran all86 source tests on .NET6 successfully. Minimal repair to old external harness: EnableDefaultNoneItems=false and EnableDefaultEmbeddedResourceItems=false (Compile inputs already explicit), preventing unrelated DLL candidates. No repository runtime, dependency version or target framework declarations changed.

Tests use existing cached Test.Sdk17.11.1/xunit2.9.2/runner2.8.2 and installed reference packs6.0.36 with SDK10.0.403; supplementary only. Mock/Sample net6 outputs are explicit target overrides, not newly declared production support. Official pinned restore remains unavailable and no packages.lock.json exists. TLS was not altered; no downloads or installations performed.

Evidence: original failing output, PE references, relevant ResolveReferences extract, isolated and repaired-root test logs plus reproducible external harness files. Full verbose diagnostic stays local because recursive candidate inventory includes unrelated local paths; only relevant sanitized extract is delivered. No game/private captures. Prior failed net6 acceptance is superseded only for this scoped harness repair.

Final results: isolated harness86 passed ExitCode0; repaired original harness86 passed ExitCode0; 0 failed/skipped, .NET6. Original failing evidence retained. No production changes or broader compatibility claim.
