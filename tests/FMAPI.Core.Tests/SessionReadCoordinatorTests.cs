using FMAPI.Adapters.Windows;
using FMAPI.Sdk;

namespace FMAPI.Core.Tests;

public sealed class SessionReadCoordinatorTests
{
    private static readonly GameBuildInfo Build = new("FM", "owned-fixture", "Windows", "x64", "test", false);

    [Fact]
    public void UnavailableSessionDoesNotInvokeReader()
    {
        var gate = new ReadSessionGate(Build);
        var reader = new SessionReadCoordinator<string>(gate);
        var called = false;
        var result = reader.Read(0, () => { called = true; return "synthetic"; });
        Assert.False(result.Available);
        Assert.False(called);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void SessionChangeDuringCaptureDiscardsData(bool replace)
    {
        var gate = new ReadSessionGate(Build);
        var token = gate.Begin(Build, true, true);
        var reader = new SessionReadCoordinator<string>(gate);
        var result = reader.Read(token, () =>
        {
            if (replace) gate.Begin(Build, true, true);
            else gate.Invalidate("Selection changed.");
            return "synthetic value that must not escape";
        });
        Assert.False(result.Available);
        Assert.Null(result.Value);
    }

    [Fact]
    public void StableSessionReturnsOwnedFixture()
    {
        var gate = new ReadSessionGate(Build);
        var token = gate.Begin(Build, true, true);
        var result = new SessionReadCoordinator<string>(gate).Read(token, () => "synthetic");
        Assert.True(result.Available);
        Assert.Equal("synthetic", result.Value);
    }

    [Fact]
    public void CaptureFailureDoesNotReturnData()
    {
        var gate = new ReadSessionGate(Build);
        var token = gate.Begin(Build, true, true);
        Assert.Throws<InvalidOperationException>(() => new SessionReadCoordinator<string>(gate)
            .Read(token, () => throw new InvalidOperationException("synthetic failure")));
    }
}
