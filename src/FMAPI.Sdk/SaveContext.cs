namespace FMAPI.Sdk;

// Experimental value-only contract. IDs are scoped to SessionId, never native pointers.
public sealed record SaveContextSnapshot(
    string SessionId, string SaveLabel, DateOnly Date, string ManagerId,
    string TeamId, bool IsSynthetic);

public enum SaveContextStatus { Available, Unavailable }

public sealed record SaveContextResult(SaveContextStatus Status, string Reason, SaveContextSnapshot? Snapshot = null);

public interface ISaveContextReader
{
    SaveContextResult ReadCurrentSave();
}
