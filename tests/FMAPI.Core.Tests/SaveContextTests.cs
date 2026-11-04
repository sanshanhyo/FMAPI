using FMAPI.Adapters.Mock;
using FMAPI.Sdk;

namespace FMAPI.Core.Tests;

public sealed class SaveContextTests
{
    [Fact]
    public void PublicReaderDeliversOnlySyntheticSessionScopedContext()
    {
        using var adapter = new MockSaveContextReader();
        ISaveContextReader reader = adapter;
        Assert.Equal(SaveContextStatus.Unavailable, reader.ReadCurrentSave().Status);
        adapter.LoadFixture("Owned fixture", new DateOnly(2026, 1, 1), "manager-1", "team-1");
        var first = reader.ReadCurrentSave().Snapshot!;
        Assert.True(first.IsSynthetic);
        Assert.Equal("manager-1", first.ManagerId);
        Assert.Equal("team-1", first.TeamId);
        Assert.Equal(new DateOnly(2026, 1, 1), first.Date);
        adapter.LoadFixture("Replacement", new DateOnly(2026, 1, 2), "manager-2", "team-2");
        Assert.NotEqual(first.SessionId, reader.ReadCurrentSave().Snapshot!.SessionId);
        adapter.Dispose();
        Assert.Null(reader.ReadCurrentSave().Snapshot);
        Assert.Throws<ObjectDisposedException>(() => adapter.LoadFixture("x", default, "m", "t"));
    }
}
