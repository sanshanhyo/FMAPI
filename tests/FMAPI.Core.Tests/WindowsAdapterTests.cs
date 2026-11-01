using FMAPI.Adapters.Windows;
using FMAPI.Core;
using FMAPI.Sdk;

namespace FMAPI.Core.Tests;

public sealed class WindowsAdapterTests
{
    [Fact]
    public void PlaceholderNeverReturnsSyntheticDataOrClaimsDetectedBuild()
    {
        var adapter = new UnavailableWindowsAdapter();
        Assert.False(adapter.Descriptor.Build.IsSynthetic);
        Assert.Equal("unknown", adapter.Descriptor.Build.BuildId);
        Assert.False(adapter.Descriptor.SupportsReads);
        Assert.False(adapter.Descriptor.SupportsWrites);
        Assert.Empty(adapter.Descriptor.SupportedWriteCommands);
        Assert.Throws<NotSupportedException>(() => adapter.ReadSnapshot());
    }

    [Fact]
    public void DirectCommandsCannotBypassUnavailableAdapter()
    {
        var adapter = new UnavailableWindowsAdapter();
        var command = new GameCommand("test.write");
        Assert.False(adapter.ValidateCommand(command).IsValid);
        Assert.Equal(CommandStatus.Unsupported, adapter.ExecuteCommand(command).Status);
    }

    [Fact]
    public void HostReportsUnsupportedWithoutDataEvenWithExplicitGrants()
    {
        using var host = new ModHost(new UnavailableWindowsAdapter(), new(true, ["test.write"]));
        var mod = new ReadWriteMod();
        host.Load(mod, new([ModCapability.GameRead, ModCapability.GameWrite], ["test.write"]));
        var read = mod.Context!.Game.ReadSnapshot();
        Assert.Equal(GameReadStatus.Unsupported, read.Status);
        Assert.Null(read.Snapshot);
        Assert.Equal(CommandStatus.Unsupported,
            mod.Context.Game.Execute(new("test.write"), new(DryRun: false)).Status);
    }

    private sealed class ReadWriteMod : IMod
    {
        public ModManifest Manifest { get; } = new("test.windows", "Windows contract test", new(0, 1, 0),
            FmApiVersion.Current, [ModCapability.GameRead, ModCapability.GameWrite]);
        public IModContext? Context { get; private set; }
        public void OnLoad(IModContext context) => Context = context;
        public void OnUnload() { }
    }
}
