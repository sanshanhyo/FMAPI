namespace FMAPI.Sdk;

// Experimental value-only contract. IDs are scoped to SessionId, never native pointers.
public sealed record SaveContextSnapshot(
    string SessionId, string SaveLabel, DateOnly Date, string ManagerId,
    string TeamId, bool IsSynthetic);

public enum SaveContextStatus { Available, Unavailable }

public enum SaveContextError { None, Unknown, NoSave, Denied, Unsupported, Expired, Failed, Closed }

public sealed record SaveContextResult
{
    public SaveContextStatus Status { get; }
    public string Reason { get; }
    public SaveContextSnapshot? Snapshot { get; }
    public SaveContextError Error { get; }

    // Existing valid three-argument construction remains source-compatible.
    public SaveContextResult(SaveContextStatus Status, string Reason, SaveContextSnapshot? Snapshot = null)
        : this(Status, Reason, Snapshot, Status == SaveContextStatus.Available ? SaveContextError.None : SaveContextError.Unknown) { }

    public SaveContextResult(SaveContextStatus status, string reason, SaveContextSnapshot? snapshot, SaveContextError error)
    {
        if (!Enum.IsDefined(typeof(SaveContextStatus), status)) throw new ArgumentOutOfRangeException(nameof(status));
        if (!Enum.IsDefined(typeof(SaveContextError), error)) throw new ArgumentOutOfRangeException(nameof(error));
        if (string.IsNullOrWhiteSpace(reason)) throw new ArgumentException("Reason must be nonempty.", nameof(reason));
        if ((status == SaveContextStatus.Available) != (snapshot is not null)
            || (status == SaveContextStatus.Available) != (error == SaveContextError.None))
            throw new ArgumentException("Status, snapshot and error disagree.");
        if (snapshot is not null && new[] { snapshot.SessionId, snapshot.SaveLabel, snapshot.ManagerId, snapshot.TeamId }.Any(string.IsNullOrWhiteSpace))
            throw new ArgumentException("Snapshot identity and label must be nonempty.", nameof(snapshot));
        Status = status; Reason = reason; Snapshot = snapshot; Error = error;
    }

    public void Deconstruct(out SaveContextStatus status, out string reason, out SaveContextSnapshot? snapshot)
    { status = Status; reason = Reason; snapshot = Snapshot; }
}

public interface ISaveContextReader
{
    SaveContextResult ReadCurrentSave();
}

// Optional context extension; existing IModContext implementations remain valid.
public interface IModSaveContext
{
    ISaveContextReader SaveContext { get; }
}

// Trusted adapter contract, serialized with capture. Increment on every context change.
public interface ISaveContextSessionSource : ISaveContextReader
{
    long Generation { get; }
}
