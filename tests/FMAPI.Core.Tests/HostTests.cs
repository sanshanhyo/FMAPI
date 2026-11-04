using FMAPI.Adapters.Mock;
using FMAPI.Core;
using FMAPI.SampleMod;
using FMAPI.Sdk;
using OfflineSampleMod = FMAPI.SampleMod.SampleMod;

namespace FMAPI.Core.Tests;

public sealed class HostTests
{
    private const string WriteCommand = "test.write";

    [Theory]
    [InlineData("manifest", CommandStatus.Denied)]
    [InlineData("grant", CommandStatus.Denied)]
    [InlineData("host-disabled", CommandStatus.Denied)]
    [InlineData("host-allowlist", CommandStatus.Denied)]
    [InlineData("mod-allowlist", CommandStatus.Denied)]
    [InlineData("adapter-writes", CommandStatus.Unsupported)]
    [InlineData("adapter-command", CommandStatus.Unsupported)]
    public void EveryWriteGateMustPassBeforeAdapterIsCalled(string missingGate, CommandStatus expected)
    {
        var adapter = new SpyAdapter(supportsWrites: missingGate != "adapter-writes",
            commands: missingGate == "adapter-command" ? [] : [WriteCommand]);
        using var host = new ModHost(adapter, new ModHostOptions(
            enableWrites: missingGate != "host-disabled",
            allowedWriteCommands: missingGate == "host-allowlist" ? [] : [WriteCommand]));
        var mod = new TestMod(capabilities: missingGate == "manifest" ? [] : [ModCapability.GameWrite]);
        host.Load(mod, new ModGrant(missingGate == "grant" ? [] : [ModCapability.GameWrite],
            missingGate == "mod-allowlist" ? [] : [WriteCommand]));

        var result = mod.Context!.Game.Execute(new GameCommand(WriteCommand), new(DryRun: false));

        Assert.Equal(expected, result.Status);
        Assert.Equal(0, adapter.Validations);
        Assert.Equal(0, adapter.Executions);
    }

    [Fact]
    public void DefaultHostAndDefaultGrantDenyWrites()
    {
        var adapter = new SpyAdapter();
        using var host = new ModHost(adapter);
        var mod = new TestMod(capabilities: [ModCapability.GameWrite]);
        host.Load(mod);
        Assert.Equal(CommandStatus.Denied, mod.Context!.Game.Execute(new GameCommand(WriteCommand), new(false)).Status);
        Assert.Equal(0, adapter.Executions);
    }

    [Fact]
    public void AuthorizedCommandDefaultsToDryRunAndNeverCallsExecute()
    {
        var adapter = new SpyAdapter();
        using var host = WritableHost(adapter);
        var mod = LoadWriter(host);

        var result = mod.Context!.Game.Execute(new GameCommand(WriteCommand));

        Assert.Equal(CommandStatus.DryRun, result.Status);
        Assert.Equal(1, adapter.Validations);
        Assert.Equal(0, adapter.Executions);
    }

    [Fact]
    public void ExplicitAuthorizedWriteCallsAdapterExactlyOnce()
    {
        var adapter = new SpyAdapter();
        using var host = WritableHost(adapter);
        var mod = LoadWriter(host);
        Assert.Equal(CommandStatus.Applied, mod.Context!.Game.Execute(new GameCommand(WriteCommand), new(false)).Status);
        Assert.Equal(1, adapter.Validations);
        Assert.Equal(1, adapter.Executions);
    }

    [Fact]
    public void InvalidArgumentsDoNotExecute()
    {
        var adapter = new SpyAdapter { Validation = new(false, "invalid test input") };
        using var host = WritableHost(adapter);
        var mod = LoadWriter(host);
        Assert.Equal(CommandStatus.Invalid, mod.Context!.Game.Execute(new GameCommand(WriteCommand), new(false)).Status);
        Assert.Equal(0, adapter.Executions);
    }

    [Fact]
    public void AdapterValidationFailureIsReportedWithoutExecution()
    {
        var adapter = new SpyAdapter { ThrowOnValidation = true };
        using var host = WritableHost(adapter);
        var mod = LoadWriter(host);
        Assert.Equal(CommandStatus.Failed, mod.Context!.Game.Execute(new GameCommand(WriteCommand), new(false)).Status);
        Assert.Equal(0, adapter.Executions);
    }

    [Fact]
    public void UnknownCommandIsUnsupportedEvenIfHostAndModAllowIt()
    {
        var adapter = new SpyAdapter(commands: []);
        using var host = WritableHost(adapter);
        var mod = LoadWriter(host);
        Assert.Equal(CommandStatus.Unsupported, mod.Context!.Game.Execute(new GameCommand(WriteCommand), new(false)).Status);
        Assert.Equal(0, adapter.Executions);
    }

    [Fact]
    public void ReadRequiresManifestRequestAndHostGrant()
    {
        var adapter = new SpyAdapter();
        using var host = new ModHost(adapter);
        var noRequest = new TestMod("no.request", capabilities: []);
        var noGrant = new TestMod("no.grant", capabilities: [ModCapability.GameRead]);
        host.Load(noRequest);
        host.Load(noGrant, new ModGrant([]));
        Assert.Equal(GameReadStatus.Denied, noRequest.Context!.Game.ReadSnapshot().Status);
        Assert.Equal(GameReadStatus.Denied, noGrant.Context!.Game.ReadSnapshot().Status);
        Assert.Equal(0, adapter.Reads);
    }

    [Fact]
    public void UnsupportedReadDoesNotCallAdapter()
    {
        var adapter = new SpyAdapter(supportsReads: false);
        using var host = new ModHost(adapter);
        var mod = new TestMod(capabilities: [ModCapability.GameRead]);
        host.Load(mod);
        Assert.Equal(GameReadStatus.Unsupported, mod.Context!.Game.ReadSnapshot().Status);
        Assert.Equal(0, adapter.Reads);
    }

    [Theory]
    [InlineData("0.0.1")]
    [InlineData("0.2.0")]
    [InlineData("1.0.0")]
    [InlineData("0.1.1")]
    [InlineData("0.1.0.1")]
    public void IncompatibleApiIsRejectedBeforeModRuns(string apiVersion)
    {
        using var host = new ModHost(new SpyAdapter());
        var mod = new TestMod(apiVersion: Version.Parse(apiVersion));
        Assert.Throws<ModLoadException>(() => host.Load(mod));
        Assert.Null(mod.Context);
        Assert.Empty(host.LoadedModIds);
    }

    [Fact]
    public void UnknownCapabilityAndMalformedIdAreRejected()
    {
        using var host = new ModHost(new SpyAdapter());
        Assert.Throws<ModLoadException>(() => host.Load(new TestMod(capabilities: [(ModCapability)999])));
        Assert.Throws<ModLoadException>(() => host.Load(new TestMod("Not A Valid Id")));
        Assert.Empty(host.LoadedModIds);
    }

    [Theory]
    [InlineData("org.fmapi.test\n")]
    [InlineData("org.fmapi.test\r")]
    [InlineData("org.fmapi.test\r\n")]
    [InlineData("\norg.fmapi.test")]
    [InlineData("org.fmapi.\ntest")]
    public void ModIdRejectsLeadingEmbeddedAndTrailingLineBreaks(string id)
    {
        using var host = new ModHost(new SpyAdapter());
        var mod = new TestMod(id);

        Assert.Throws<ModLoadException>(() => host.Load(mod));

        Assert.Null(mod.Context);
        Assert.Empty(host.LoadedModIds);
    }

    [Fact]
    public void DuplicateModIdDoesNotReplaceOriginal()
    {
        using var host = new ModHost(new SpyAdapter());
        var original = new TestMod();
        host.Load(original);
        Assert.Throws<ModLoadException>(() => host.Load(new TestMod()));
        Assert.Single(host.LoadedModIds);
        Assert.Equal(0, original.Unloads);
    }

    [Fact]
    public void UnloadRemovesAllOwnedResourcesAndRevokesOldContext()
    {
        using var host = WritableHost(new SpyAdapter());
        var calls = 0;
        var mod = new TestMod(capabilities: Enum.GetValues<ModCapability>(), onLoad: context =>
        {
            context.Events.Subscribe<int>(_ => calls++);
            context.Ui.Register(Panel());
        });
        host.Load(mod, FullGrant());
        var oldContext = mod.Context!;
        Assert.Equal(1, host.Publish(1).Delivered);
        Assert.Single(host.UiExtensions);

        Assert.True(host.Unload(mod.Manifest.Id));

        Assert.Empty(host.UiExtensions);
        Assert.Equal(0, host.Publish(2).Delivered);
        Assert.Equal(1, calls);
        Assert.Throws<InvalidOperationException>(() => oldContext.Events.Subscribe<int>(_ => { }));
        Assert.Throws<InvalidOperationException>(() => oldContext.Events.Publish(3));
        Assert.Throws<InvalidOperationException>(() => oldContext.Ui.Register(Panel()));
        Assert.Throws<InvalidOperationException>(() => oldContext.Game.ReadSnapshot());
        Assert.Throws<InvalidOperationException>(() => oldContext.Game.Execute(new GameCommand(WriteCommand), new(false)));
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void FailedLoadCleansResourcesEvenIfCleanupAlsoThrows(bool throwOnUnload)
    {
        using var host = new ModHost(new SpyAdapter());
        var mod = new TestMod(onLoad: context =>
        {
            context.Events.Subscribe<int>(_ => { });
            context.Ui.Register(Panel());
            throw new InvalidOperationException("load failed");
        }, throwOnUnload: throwOnUnload);
        Assert.Throws<ModLoadException>(() => host.Load(mod));
        Assert.Empty(host.LoadedModIds);
        Assert.Empty(host.UiExtensions);
        Assert.Equal(0, host.Publish(1).Delivered);
        Assert.Equal(1, mod.Unloads);
        Assert.Throws<InvalidOperationException>(() => mod.Context!.Ui.Register(Panel()));
    }

    [Fact]
    public void UnloadFailureStillCleansResourcesAndAllowsReload()
    {
        using var host = new ModHost(new SpyAdapter());
        var mod = new TestMod(onLoad: context =>
        {
            context.Events.Subscribe<int>(_ => { });
            context.Ui.Register(Panel());
        }, throwOnUnload: true);
        host.Load(mod);
        Assert.Throws<InvalidOperationException>(() => host.Unload(mod.Manifest.Id));
        Assert.Empty(host.LoadedModIds);
        Assert.Empty(host.UiExtensions);
        Assert.Equal(0, host.Publish(1).Delivered);
        host.Load(new TestMod(mod.Manifest.Id));
        Assert.Single(host.LoadedModIds);
    }

    [Fact]
    public void DisposeAttemptsAllModCleanupWhenOneThrows()
    {
        var host = new ModHost(new SpyAdapter());
        var first = new TestMod("first", onLoad: context => context.Ui.Register(Panel()), throwOnUnload: true);
        var second = new TestMod("second", onLoad: context => context.Ui.Register(Panel()));
        host.Load(first);
        host.Load(second);
        Assert.Throws<AggregateException>(() => host.Dispose());
        Assert.Equal(1, first.Unloads);
        Assert.Equal(1, second.Unloads);
        Assert.Empty(host.LoadedModIds);
        Assert.Empty(host.UiExtensions);
        Assert.Throws<ObjectDisposedException>(() => host.Publish(1));
        host.Dispose();
    }

    [Fact]
    public void DuplicateUiIdsAreScopedToModAndOldTokensCannotRemoveReloadedUi()
    {
        using var host = new ModHost(new SpyAdapter());
        IDisposable? oldToken = null;
        var first = new TestMod("first", onLoad: context => oldToken = context.Ui.Register(Panel()));
        var second = new TestMod("second", onLoad: context => context.Ui.Register(Panel()));
        host.Load(first);
        host.Load(second);
        Assert.Equal(2, host.UiExtensions.Count);
        Assert.Throws<InvalidOperationException>(() => first.Context!.Ui.Register(Panel()));
        host.Unload(first.Manifest.Id);
        host.Load(new TestMod("first", onLoad: context => context.Ui.Register(Panel())));
        oldToken!.Dispose();
        Assert.Equal(2, host.UiExtensions.Count);
    }

    [Fact]
    public void EventFaultDoesNotPreventOtherSubscribersAndTypesAreExact()
    {
        using var host = new ModHost(new SpyAdapter());
        var calls = 0;
        host.Load(new TestMod("broken", onLoad: context => context.Events.Subscribe<int>(_ => throw new Exception("handler failed"))));
        host.Load(new TestMod("working", onLoad: context =>
        {
            context.Events.Subscribe<int>(_ => calls++);
            context.Events.Subscribe<string>(_ => calls += 100);
        }));
        var report = host.Publish(10);
        Assert.Equal(1, report.Delivered);
        Assert.Single(report.Failures);
        Assert.Equal("broken", report.Failures[0].ModId);
        Assert.Equal(1, calls);
    }

    [Fact]
    public void DisposingSubscriptionStopsFurtherDelivery()
    {
        using var host = new ModHost(new SpyAdapter());
        IDisposable? token = null;
        host.Load(new TestMod(onLoad: context => token = context.Events.Subscribe<int>(_ => { })));
        Assert.Equal(1, host.Publish(1).Delivered);
        token!.Dispose();
        token.Dispose();
        Assert.Equal(0, host.Publish(2).Delivered);
    }

    [Fact]
    public void EventsAndUiRequireBothRequestAndGrant()
    {
        using var host = new ModHost(new SpyAdapter());
        var noRequest = new TestMod("no.request", capabilities: []);
        var noGrant = new TestMod("no.grant");
        host.Load(noRequest);
        host.Load(noGrant, new ModGrant([]));
        foreach (var mod in new[] { noRequest, noGrant })
        {
            Assert.Throws<UnauthorizedAccessException>(() => mod.Context!.Events.Subscribe<int>(_ => { }));
            Assert.Throws<UnauthorizedAccessException>(() => mod.Context!.Events.Publish(1));
            Assert.Throws<UnauthorizedAccessException>(() => mod.Context!.Ui.Register(Panel()));
        }
    }

    [Theory]
    [InlineData("NotKnown")]
    [InlineData("3")]
    [InlineData("gamewrite")]
    public void ManifestParserRejectsUnknownOrNumericCapabilities(string capability)
    {
        var json = $$"""
            { "id": "test", "name": "test", "version": "0.1.0", "apiVersion": "0.1.0", "requestedCapabilities": ["{{capability}}"] }
            """;
        Assert.Throws<FormatException>(() => ModManifest.Parse(json));
    }

    [Fact]
    public void CommandArgumentsAndPermissionSetsAreDefensiveSnapshots()
    {
        var arguments = new Dictionary<string, string> { ["name"] = "original" };
        var command = new GameCommand(WriteCommand, arguments);
        arguments["name"] = "mutated";
        Assert.Equal("original", command.Arguments["name"]);
        var capabilities = new HashSet<ModCapability> { ModCapability.GameRead };
        var grant = new ModGrant(capabilities);
        capabilities.Add(ModCapability.GameWrite);
        Assert.DoesNotContain(ModCapability.GameWrite, grant.Capabilities);
    }

    [Fact]
    public void OfflineSampleExercisesDryRunAndExplicitWriteOnSyntheticData()
    {
        var adapter = new MockGameAdapter();
        using var host = new ModHost(adapter, new(true, [MockGameAdapter.RenameClubCommand]));
        var mod = new OfflineSampleMod();
        host.Load(mod, new(Enum.GetValues<ModCapability>(), [MockGameAdapter.RenameClubCommand]));
        host.Publish(new DemoTick(1));
        Assert.Equal(1, mod.ReceivedTicks);
        Assert.Single(host.UiExtensions);
        Assert.True(mod.ReadSnapshot().Snapshot!.Build.IsSynthetic);
        Assert.Equal(CommandStatus.DryRun, mod.RenameSyntheticClub("Changed FC").Status);
        Assert.Equal(MockGameAdapter.InitialClubName, mod.ReadSnapshot().Snapshot!.Values["club.name"]);
        Assert.Equal(CommandStatus.Applied, mod.RenameSyntheticClub("Changed FC", dryRun: false).Status);
        Assert.Equal("Changed FC", mod.ReadSnapshot().Snapshot!.Values["club.name"]);
        Assert.Equal(CommandStatus.Invalid, mod.RenameSyntheticClub(" ", dryRun: false).Status);
        Assert.Equal("Changed FC", mod.ReadSnapshot().Snapshot!.Values["club.name"]);
    }

    [Theory]
    [InlineData(false, false)]
    [InlineData(false, true)]
    [InlineData(true, false)]
    public void ReadRequiresBothManifestRequestAndHostGrantWithoutCallingAdapter(bool requested, bool granted)
    {
        var adapter = new SpyAdapter();
        using var host = new ModHost(adapter);
        var mod = new TestMod(capabilities: requested ? [ModCapability.GameRead] : []);
        host.Load(mod, new ModGrant(granted ? [ModCapability.GameRead] : []));
        Assert.Equal(GameReadStatus.Denied, mod.Context!.Game.ReadSnapshot().Status);
        Assert.Equal(0, adapter.Reads);
    }

    [Fact]
    public void OldReaderCannotAcquireReplacementRegistrationWithSameId()
    {
        var adapter = new SpyAdapter();
        using var host = new ModHost(adapter);
        var first = new TestMod(capabilities: [ModCapability.GameRead]);
        host.Load(first, new ModGrant([ModCapability.GameRead]));
        var old = first.Context!.Game;
        Assert.Equal(GameReadStatus.Available, old.ReadSnapshot().Status);
        host.Unload(first.Manifest.Id);
        var replacement = new TestMod(capabilities: [ModCapability.GameRead]);
        host.Load(replacement, new ModGrant([ModCapability.GameRead]));
        Assert.Throws<InvalidOperationException>(() => old.ReadSnapshot());
        Assert.Equal(1, adapter.Reads);
        Assert.Equal(GameReadStatus.Available, replacement.Context!.Game.ReadSnapshot().Status);
        Assert.Equal(2, adapter.Reads);
    }

    [Fact]
    public void FailedLoadRevokesCapturedReaderBeforeAnotherRegistration()
    {
        var adapter = new SpyAdapter();
        using var host = new ModHost(adapter);
        IModGame? captured = null;
        var mod = new TestMod(capabilities: [ModCapability.GameRead], onLoad: context =>
        {
            captured = context.Game;
            throw new InvalidOperationException("owned test failure");
        });
        Assert.Throws<ModLoadException>(() => host.Load(mod, new ModGrant([ModCapability.GameRead])));
        Assert.Throws<InvalidOperationException>(() => captured!.ReadSnapshot());
        Assert.Equal(0, adapter.Reads);
    }
    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void ReentrantRevocationDiscardsAdapterResult(bool shutdown)
    {
        var adapter = new SpyAdapter();
        using var host = new ModHost(adapter);
        var mod = new TestMod(capabilities: [ModCapability.GameRead]);
        host.Load(mod, new ModGrant([ModCapability.GameRead]));
        adapter.OnRead = () => { if (shutdown) host.Dispose(); else host.Unload(mod.Manifest.Id); };
        var result = mod.Context!.Game.ReadSnapshot();
        Assert.NotEqual(GameReadStatus.Available, result.Status);
        Assert.Null(result.Snapshot);
        Assert.Equal(1, adapter.Reads);
        Assert.Throws<InvalidOperationException>(() => mod.Context.Game.ReadSnapshot());
    }
    private static UiExtension Panel() => new("overview", UiExtensionKind.Panel, "Test panel", "test.location");
    private static ModHost WritableHost(IGameAdapter adapter) => new(adapter, new(true, [WriteCommand]));
    private static ModGrant FullGrant() => new(Enum.GetValues<ModCapability>(), [WriteCommand]);
    private static TestMod LoadWriter(ModHost host)
    {
        var mod = new TestMod(capabilities: [ModCapability.GameWrite]);
        host.Load(mod, FullGrant());
        return mod;
    }

    private sealed class TestMod : IMod
    {
        private readonly Action<IModContext>? onLoad;
        private readonly bool throwOnUnload;
        public ModManifest Manifest { get; }
        public IModContext? Context { get; private set; }
        public int Unloads { get; private set; }

        public TestMod(string id = "org.fmapi.test", IEnumerable<ModCapability>? capabilities = null,
            Version? apiVersion = null, Action<IModContext>? onLoad = null, bool throwOnUnload = false)
        {
            Manifest = new(id, "Test mod", new(0, 1, 0), apiVersion ?? FmApiVersion.Current,
                capabilities ?? [ModCapability.Events, ModCapability.UiExtensions]);
            this.onLoad = onLoad;
            this.throwOnUnload = throwOnUnload;
        }

        public void OnLoad(IModContext context)
        {
            Context = context;
            onLoad?.Invoke(context);
        }

        public void OnUnload()
        {
            Unloads++;
            if (throwOnUnload)
            {
                throw new InvalidOperationException("unload failed");
            }
        }
    }

    private sealed class SpyAdapter : IGameAdapter
    {
        public AdapterDescriptor Descriptor { get; }
        public Action? OnRead { get; set; }
        public int Reads { get; private set; }
        public int Validations { get; private set; }
        public int Executions { get; private set; }
        public bool ThrowOnValidation { get; init; }
        public CommandValidation Validation { get; init; } = new(true, "valid");

        public SpyAdapter(bool supportsReads = true, bool supportsWrites = true, IEnumerable<string>? commands = null)
        {
            Descriptor = new("test.adapter", new("Synthetic test", "test-1", "offline", "any", "none", true),
                supportsReads, supportsWrites, commands ?? [WriteCommand]);
        }

        public GameSnapshot ReadSnapshot()
        {
            Reads++;
            OnRead?.Invoke();
            return new(Descriptor.Build, new Dictionary<string, string> { ["test"] = "synthetic" });
        }

        public CommandValidation ValidateCommand(GameCommand command)
        {
            Validations++;
            if (ThrowOnValidation)
            {
                throw new InvalidOperationException("adapter validation failed");
            }
            return Validation;
        }

        public CommandResult ExecuteCommand(GameCommand command)
        {
            Executions++;
            return new(CommandStatus.Applied, "synthetic write");
        }
    }
}
