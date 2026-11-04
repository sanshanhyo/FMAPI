using FMAPI.Sdk;

namespace FMAPI.Adapters.Mock;

// Owned fixtures only. No game/save/process access.
public sealed class MockSaveContextReader : ISaveContextSessionSource, IDisposable
{
    private SaveContextSnapshot? current;
    private bool disposed;
    public long Generation { get; private set; }

    public void LoadFixture(string saveLabel, DateOnly date, string managerId, string teamId)
    {
        if (disposed) throw new ObjectDisposedException(nameof(MockSaveContextReader));
        if (new[] { saveLabel, managerId, teamId }.Any(string.IsNullOrWhiteSpace))
            throw new ArgumentException("Fixture labels and identities must be nonempty.");
        Generation = checked(Generation + 1);
        current = new(Guid.NewGuid().ToString("N"), saveLabel, date, managerId, teamId, true);
    }

    public void Clear() { Generation = checked(Generation + 1); current = null; }

    public SaveContextResult ReadCurrentSave() => disposed
        ? new(SaveContextStatus.Unavailable, "Reader is closed.", null, SaveContextError.Closed)
        : current is null
        ? new(SaveContextStatus.Unavailable, "No synthetic save fixture loaded.", null, SaveContextError.NoSave)
        : new(SaveContextStatus.Available, "Synthetic fixture only.", current);

    public void Dispose() { if (disposed) return; Clear(); disposed = true; }
}
