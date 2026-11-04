namespace FMAPI.Adapters.Windows;

// Coordinates an already-qualified reader. It neither discovers nor calls game objects.
internal sealed class SessionReadCoordinator<T>(ReadSessionGate session) where T : class
{
    public SessionReadResult<T> Read(long token, Func<T> capture)
    {
        ArgumentNullException.ThrowIfNull(capture);
        var before = session.Check(token);
        if (!before.Available) return new(null, before.Reason);

        var value = capture(); // Caller owns bounds, source identity and thread safety.
        var after = session.Check(token);
        if (!after.Available) return new(null, after.Reason);
        return value is null
            ? new(null, "Reader returned no data.")
            : new(value, "Captured within the same observed session; atomicity is not guaranteed.");
    }
}

internal sealed record SessionReadResult<T>(T? Value, string Reason) where T : class
{
    public bool Available => Value is not null;
}
