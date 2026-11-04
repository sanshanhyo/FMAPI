using FMAPI.Adapters.Mock;
using FMAPI.Sdk;

namespace FMAPI.Core.Tests;

public sealed class SaveContextInvariantTests
{
    private static readonly SaveContextSnapshot Snapshot = new("s", "fixture", new(2026, 1, 1), "m", "t", true);

    [Fact]
    public void ContradictoryResultsAndInvalidIdentitiesAreRejected()
    {
        Assert.Throws<ArgumentException>(() => new SaveContextResult(SaveContextStatus.Available, "x"));
        Assert.Throws<ArgumentException>(() => new SaveContextResult(SaveContextStatus.Unavailable, "x", Snapshot));
        Assert.Throws<ArgumentException>(() => new SaveContextResult(SaveContextStatus.Available, "x", Snapshot, SaveContextError.Failed));
        Assert.Throws<ArgumentException>(() => new SaveContextResult(SaveContextStatus.Unavailable, "x", null, SaveContextError.None));
        Assert.Throws<ArgumentException>(() => new SaveContextResult(SaveContextStatus.Available, "x", Snapshot with { ManagerId = " " }));
        Assert.Throws<ArgumentException>(() => new SaveContextResult(SaveContextStatus.Available, " ", Snapshot));
        Assert.Throws<ArgumentOutOfRangeException>(() => new SaveContextResult((SaveContextStatus)99, "x"));
        Assert.Throws<ArgumentOutOfRangeException>(() => new SaveContextResult(SaveContextStatus.Unavailable, "x", null, (SaveContextError)99));
    }

    [Fact]
    public void LegacyConstructionAndDeconstructionRemainValid()
    {
        var result = new SaveContextResult(SaveContextStatus.Available, "fixture", Snapshot);
        var (status, reason, snapshot) = result;
        Assert.Equal(SaveContextStatus.Available, status);
        Assert.Equal("fixture", reason);
        Assert.Same(Snapshot, snapshot);
        Assert.Equal(SaveContextError.None, result.Error);
        Assert.Equal(SaveContextError.Unknown, new SaveContextResult(SaveContextStatus.Unavailable, "legacy").Error);
    }

    [Fact]
    public void ClearAndCloseHaveMachineReadableReasonsAndInvalidLoadPreservesState()
    {
        using var reader = new MockSaveContextReader();
        reader.LoadFixture("fixture", new(2026, 1, 1), "m", "t");
        var first = reader.ReadCurrentSave().Snapshot;
        Assert.Throws<ArgumentException>(() => reader.LoadFixture(" ", default, "m", "t"));
        Assert.Same(first, reader.ReadCurrentSave().Snapshot);
        reader.Clear();
        Assert.Equal(SaveContextError.NoSave, reader.ReadCurrentSave().Error);
        reader.Dispose();
        Assert.Equal(SaveContextError.Closed, reader.ReadCurrentSave().Error);
    }
}
