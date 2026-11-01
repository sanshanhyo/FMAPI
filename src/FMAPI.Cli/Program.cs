using FMAPI.Adapters.Mock;
using FMAPI.Adapters.Windows;
using FMAPI.Core;
using FMAPI.SampleMod;
using FMAPI.Sdk;

if (args is ["windows-status"])
{
    var unavailable = new UnavailableWindowsAdapter();
    Console.WriteLine($"{unavailable.Descriptor.Id}: unavailable");
    Console.WriteLine(UnavailableWindowsAdapter.UnavailableReason);
    Console.WriteLine("No process was inspected; no game build or capabilities were detected. No synthetic fallback.");
    return 3;
}

if (args.Length != 1 || args[0] != "demo")
{
    Console.WriteLine("FMAPI 0.1.0-alpha.1 — Football Manager Modding API");
    Console.WriteLine("Usage: dotnet run --project src/FMAPI.Cli -- demo");
    Console.WriteLine("       dotnet run --project src/FMAPI.Cli -- windows-status (unavailable: exit 3)");
    Console.WriteLine("The demo uses synthetic in-memory data. No real-game adapter is available.");
    return args.Length == 0 || args is ["--help"] or ["-h"] ? 0 : 2;
}

Console.WriteLine("FMAPI OFFLINE DEMO — all club data is synthetic; no game is accessed.");
var adapter = new MockGameAdapter();
var sample = new SampleMod();
using (var host = new ModHost(adapter))
{
    host.Load(sample);
    host.Publish(new DemoTick(1));
    Console.WriteLine($"Event ticks received: {sample.ReceivedTicks}");
    Console.WriteLine($"Declared UI extensions: {host.UiExtensions.Count} (registration only; no game UI renderer)");
    Console.WriteLine($"Synthetic club: {sample.ReadSnapshot().Snapshot!.Values["club.name"]}");
    var denied = sample.RenameSyntheticClub("Should never apply", dryRun: false);
    Require(denied.Status == CommandStatus.Denied, "Default host must deny writes.");
    Console.WriteLine($"Default write: {denied.Status} — {denied.Message}");
    host.Unload(sample.Manifest.Id);
    Require(host.UiExtensions.Count == 0, "Unload must remove UI declarations.");
    Require(host.Publish(new DemoTick(2)).Delivered == 0, "Unload must remove subscriptions.");
    Console.WriteLine("Unload: event subscriptions and UI declarations removed.");
}

var grant = new ModGrant(
    [ModCapability.GameRead, ModCapability.Events, ModCapability.UiExtensions, ModCapability.GameWrite],
    [MockGameAdapter.RenameClubCommand]);
using (var host = new ModHost(adapter, new ModHostOptions(enableWrites: true, [MockGameAdapter.RenameClubCommand])))
{
    host.Load(sample, grant);
    var dryRun = sample.RenameSyntheticClub("Demo United");
    Require(dryRun.Status == CommandStatus.DryRun, "The default command must be a dry-run.");
    Require(sample.ReadSnapshot().Snapshot!.Values["club.name"] == MockGameAdapter.InitialClubName, "Dry-run must not mutate data.");
    Console.WriteLine($"Authorized dry-run: {dryRun.Status} — club remains {MockGameAdapter.InitialClubName}");
    var applied = sample.RenameSyntheticClub("Demo United", dryRun: false);
    Require(applied.Status == CommandStatus.Applied, "Explicit authorized write must update the mock.");
    Console.WriteLine($"Authorized mock write: {applied.Status} — {sample.ReadSnapshot().Snapshot!.Values["club.name"]}");
}
Console.WriteLine("Demo completed. Real Football Manager support: unsupported (adapter not implemented).");
return 0;

static void Require(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}
