using System.Collections;
using FMAPI.Core;
using FMAPI.Host.BepInEx;
using FMAPI.Sdk;

// Package-free runtime smoke contracts. These complement, not replace, the xUnit suite.
var checks = 0;
Check("Defensive permission sets", () =>
{
    var capabilities = new HashSet<ModCapability> { ModCapability.GameRead };
    var commands = new HashSet<string> { "test.write" };
    var grant = new ModGrant(capabilities, commands);
    var options = new ModHostOptions(true, commands);
    var manifest = new ModManifest("test", "Test", new(0, 1, 0), FmApiVersion.Current, capabilities);
    var descriptor = new AdapterDescriptor("test", Build(), true, true, commands);
    capabilities.Add(ModCapability.GameWrite);
    commands.Add("unexpected");
    Require(!grant.Capabilities.Contains(ModCapability.GameWrite), "Grant changed with caller input.");
    Require(!manifest.RequestedCapabilities.Contains(ModCapability.GameWrite), "Manifest changed with caller input.");
    foreach (var set in new[] { grant.AllowedWriteCommands, options.AllowedWriteCommands, descriptor.SupportedWriteCommands })
    {
        Require(set.SetEquals(new[] { "test.write" }), "Command allowlist changed.");
        Require(!set.Contains("TEST.WRITE"), "Command matching must be ordinal case-sensitive.");
        Require(set is not ICollection<string> && set is not ISet<string> && set is not IList,
            "Allowlist exposes a mutable collection interface.");
    }
    Require(grant.Capabilities is not ICollection<ModCapability>, "Capabilities expose mutation.");
    Require(manifest.RequestedCapabilities is not ICollection<ModCapability>, "Manifest exposes mutation.");
});
Check("Argument and enum validation", () =>
{
    Throws<ArgumentNullException>(() => new GameCommand(null!));
    Throws<ArgumentException>(() => new GameCommand(" "));
    Throws<FormatException>(() => ModManifest.Parse("""
        {"id":"test","name":"Test","version":"0.1.0","apiVersion":"0.1.0","requestedCapabilities":["3"]}
        """));
});
Check("Default deny and dry-run", () =>
{
    var adapter = new TestAdapter();
    using (var denied = new ModHost(adapter))
    {
        var mod = new TestMod("denied");
        denied.Load(mod);
        Require(mod.Context!.Game.Execute(new("test.write"), new(false)).Status == CommandStatus.Denied, "Default write allowed.");
    }
    using var host = new ModHost(adapter, new(true, ["test.write"]));
    var writer = new TestMod("writer");
    host.Load(writer, new(Enum.GetValues<ModCapability>(), ["test.write"]));
    Require(writer.Context!.Game.Execute(new("test.write")).Status == CommandStatus.DryRun, "Dry-run missing.");
    Require(adapter.Executions == 0, "Dry-run executed.");
    Require(writer.Context.Game.Execute(new("test.write"), new(false)).Status == CommandStatus.Applied, "Authorized write failed.");
    Require(adapter.Executions == 1, "Unexpected execution count.");
});
Check("Lifecycle cleanup, ordering and disposal", () =>
{
    var host = new ModHost(new TestAdapter());
    var mod = new TestMod("z");
    host.Load(mod);
    host.Load(new TestMod("a"));
    Require(host.LoadedModIds.SequenceEqual(new[] { "a", "z" }), "IDs are not ordered.");
    Require(host.Publish(1).Delivered == 2 && host.UiExtensions.Count == 2, "Registrations missing.");
    host.Unload("z");
    Require(host.Publish(1).Delivered == 1 && host.UiExtensions.Count == 1, "Unload leaked registrations.");
    Throws<InvalidOperationException>(() => mod.Context!.Game.ReadSnapshot());
    host.Dispose();
    Throws<ObjectDisposedException>(() => host.Load(new TestMod("late")));
    Throws<ObjectDisposedException>(() => host.Publish(1));
    Throws<ObjectDisposedException>(() => host.Unload("a"));
});
Check("Failed load cleanup and API rejection", () =>
{
    using var host = new ModHost(new TestAdapter());
    var failed = new TestMod("failed", fail: true);
    Throws<ModLoadException>(() => host.Load(failed));
    Require(host.LoadedModIds.Count == 0 && host.UiExtensions.Count == 0 && host.Publish(1).Delivered == 0,
        "Failed load leaked resources.");
    Require(failed.Unloads == 1, "Failed load was not cleaned up.");
    var incompatible = new TestMod("future", apiVersion: new(99, 0, 0));
    Throws<ModLoadException>(() => host.Load(incompatible));
    Require(incompatible.Context is null, "Incompatible mod was invoked.");
});
Check("Bridge registrations revoke contexts and tolerate stale tokens", () =>
{
    var session = new HostSession();
    var first = new TestMod("bridge");
    var token = session.Register(first);
    Require(first.Context!.Game.ReadSnapshot().Status == GameReadStatus.Unsupported, "Bridge fabricated a read.");
    Require(first.Context.Game.Execute(new("test.write"), new(false)).Status == CommandStatus.Denied, "Bridge enabled writes.");
    Throws<ModLoadException>(() => session.Register(new TestMod("bridge")));
    token.Dispose();
    Require(first.Unloads == 1, "Registration did not unload once.");
    Throws<InvalidOperationException>(() => first.Context.Game.ReadSnapshot());
    var second = new TestMod("bridge");
    var secondToken = session.Register(second);
    token.Dispose();
    Require(second.Unloads == 0, "Stale token unloaded replacement.");
    session.Dispose();
    Require(second.Unloads == 1, "Session shutdown did not unload mod.");
    secondToken.Dispose();
    session.Dispose();
    Throws<ObjectDisposedException>(() => session.Register(new TestMod("late")));
});
Check("Bridge load failures release IDs and registrations", () =>
{
    using var session = new HostSession();
    var failed = new TestMod("retry", fail: true);
    Throws<ModLoadException>(() => session.Register(failed));
    Require(failed.Unloads == 1, "Bridge did not clean failed registration.");
    Throws<InvalidOperationException>(() => failed.Context!.Events.Publish(1));
    using var retry = session.Register(new TestMod("retry"));
});
Check("Bridge shutdown attempts every cleanup even after failure", () =>
{
    var session = new HostSession();
    var broken = new TestMod("broken", throwOnUnload: true);
    var working = new TestMod("working");
    var first = session.Register(broken);
    var second = session.Register(working);
    Throws<AggregateException>(() => session.Dispose());
    Require(broken.Unloads == 1 && working.Unloads == 1, "Shutdown skipped cleanup.");
    Throws<InvalidOperationException>(() => working.Context!.Events.Publish(1));
    first.Dispose();
    second.Dispose();
    session.Dispose();
});
Console.WriteLine($"PASS: {checks} runtime contract groups on {System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription}. Synthetic fixtures only.");

void Check(string name, Action action) { action(); checks++; Console.WriteLine($"PASS: {name}"); }
static void Require(bool condition, string message) { if (!condition) throw new Exception(message); }
static void Throws<T>(Action action) where T : Exception
{
    try { action(); } catch (T) { return; }
    throw new Exception($"Expected {typeof(T).Name}.");
}
static GameBuildInfo Build() => new("Synthetic runtime contract", "test", "offline", "any", "none", true);

sealed class TestAdapter : IGameAdapter
{
    public int Executions { get; private set; }
    public AdapterDescriptor Descriptor { get; } = new("test", new("Synthetic", "test", "offline", "any", "none", true), true, true, ["test.write"]);
    public GameSnapshot ReadSnapshot() => new(Descriptor.Build, new Dictionary<string, string>());
    public CommandValidation ValidateCommand(GameCommand command) => new(true, "synthetic");
    public CommandResult ExecuteCommand(GameCommand command) { Executions++; return new(CommandStatus.Applied, "synthetic"); }
}

sealed class TestMod(string id, bool fail = false, Version? apiVersion = null, bool throwOnUnload = false) : IMod
{
    public ModManifest Manifest { get; } = new(id, "Test", new(0, 1, 0), apiVersion ?? FmApiVersion.Current, Enum.GetValues<ModCapability>());
    public IModContext? Context { get; private set; }
    public int Unloads { get; private set; }
    public void OnLoad(IModContext context)
    {
        Context = context;
        context.Events.Subscribe<int>(_ => { });
        context.Ui.Register(new("panel", UiExtensionKind.Panel, "Test", "offline"));
        if (fail) throw new Exception("Synthetic load failure.");
    }
    public void OnUnload()
    {
        Unloads++;
        if (throwOnUnload) throw new Exception("Synthetic cleanup failure.");
    }
}
