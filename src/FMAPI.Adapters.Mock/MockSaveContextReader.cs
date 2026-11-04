using FMAPI.Sdk;

namespace FMAPI.Adapters.Mock;

// Owned fixtures only. No game/save/process access.
public sealed class MockSaveContextReader : ISaveContextReader, IDisposable
{
    private SaveContextSnapshot? current;
    private bool disposed;

    public void LoadFixture(string saveLabel, DateOnly date, string managerId, string teamId)
    {
        if (disposed) throw new ObjectDisposedException(nameof(MockSaveContextReader));
        if (new[] { saveLabel, managerId, teamId }.Any(string.IsNullOrWhiteSpace))
            throw new ArgumentException("Fixture labels and identities must be nonempty.");
        current = new(Guid.NewGuid().ToString("N"), saveLabel, date, managerId, teamId, true);
    }

    public void Clear() => current = null;

    public SaveContextResult ReadCurrentSave() => current is null
        ? new(SaveContextStatus.Unavailable, "No synthetic save fixture loaded.")
        : new(SaveContextStatus.Available, "Synthetic fixture only.", current);

    public void Dispose() { Clear(); disposed = true; }
}
