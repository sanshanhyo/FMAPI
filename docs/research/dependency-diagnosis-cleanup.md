# Dependency restore diagnosis and failed-probe cleanup

Read-only dependency diagnosis, no installs/security changes/game access. Official nuget.org v3 source is enabled. Direct HTTPS service-index probe fails HttpRequestException -> AuthenticationException -> Win32Exception (security package has no credentials). Earlier restore reported SEC_E_NO_CREDENTIALS. This locates failure in the Windows TLS authentication path; it does not identify a missing root certificate or prove proxy interference. Do not bypass validation or replace feeds with untrusted mirrors.

Offline failure is separate: cache has Test.Sdk17.11.1/xunit2.9.2/runner2.8.2, lacks coverlet and pinned versions. No packages.lock.json exists. Clearing caches cannot provide missing packages and would destroy useful offline evidence, so no caches cleared.

Safe recovery options for user/administrator review: reproduce HTTPS/restore in an authorized interactive Windows session; inspect Windows/network policy and trusted certificate/proxy configuration through approved administration; once verified TLS to official NuGet works, restore pinned project versions. Alternatively supply officially obtained, integrity-verified packages and full transitive closure through an approved local source using normal NuGet verification. No package transfer/install or certificate changes performed here. Generate/review a real packages.lock.json only after a successful resolved graph, then use locked-mode restore in CI. Existing direct versions do not equal a transitive lock.

Official references:
- https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-restore
- https://learn.microsoft.com/en-us/nuget/consume-packages/managing-the-global-packages-and-cache-folders
- https://learn.microsoft.com/en-us/nuget/reference/msbuild-targets

Cleanup: before interrupt, two failed probe log files remained exclusively locked. Sent Ctrl-C only to known execution sessions85677 and99720; both returned exit1. Afterward both files could be exclusively opened. Thus those session/file-lock blockers are cleared; no arbitrary dotnet process was killed and no game process targeted. Remaining dotnet processes were not identified or changed. Prior CIM access refusal was respected.

Evidence includes UTC inventory, enabled source output, TLS exception chain, before/after lock probes and process snapshots. No tests rerun. Two initial diagnostic commands had PowerShell parser errors before execution; corrected commands generated the delivered logs. No claim of pinned restore recovery.
