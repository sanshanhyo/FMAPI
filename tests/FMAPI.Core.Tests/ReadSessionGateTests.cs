using FMAPI.Adapters.Windows;
using FMAPI.Sdk;

namespace FMAPI.Core.Tests;

public sealed class ReadSessionGateTests
{
    private static readonly GameBuildInfo Build = new("FM", "owned-fixture", "Windows", "x64", "test", false);

    [Fact]
    public void UnknownBuildAndUnverifiedSourceFailClosed()
    {
        var gate = new ReadSessionGate(Build);
        Assert.False(gate.Check(gate.Begin(Build with { BuildId = "unknown" }, true, true)).Available);
        Assert.False(gate.Check(gate.Begin(Build, false, true)).Available);
        Assert.False(gate.Check(gate.Begin(Build, true, false)).Available);
        Assert.False(gate.Check(gate.Begin(Build with { IsSynthetic = true }, true, true)).Available);
    }

    [Fact]
    public void SelectionChangeAndReplacementRevokeOldTokens()
    {
        var gate = new ReadSessionGate(Build);
        var first = gate.Begin(Build, true, true);
        Assert.True(gate.Check(first).Available);
        gate.Invalidate("Selection changed.");
        Assert.False(gate.Check(first).Available);
        var second = gate.Begin(Build, true, true);
        Assert.True(gate.Check(second).Available);
        Assert.False(gate.Check(first).Available);
    }
    [Fact]
    public void ShutdownCannotBeReopened()
    {
        var gate = new ReadSessionGate(Build);
        var token = gate.Begin(Build, true, true);
        gate.Dispose();
        gate.Dispose();
        Assert.False(gate.Check(token).Available);
        Assert.Throws<ObjectDisposedException>(() => gate.Begin(Build, true, true));
    }
}
