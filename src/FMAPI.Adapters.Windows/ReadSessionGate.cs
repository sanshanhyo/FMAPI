using FMAPI.Sdk;

namespace FMAPI.Adapters.Windows;

// Adapter-internal prerequisite gate. It does not detect a process or prove a read.
internal sealed class ReadSessionGate(GameBuildInfo qualifiedBuild) : IDisposable
{
    private long generation;
    private bool active;
    private bool disposed;
    private string reason = "No observed session.";

    public long Begin(GameBuildInfo observedBuild, bool sourceVerified, bool saveReady)
    {
        if (disposed) throw new ObjectDisposedException(nameof(ReadSessionGate));
        Invalidate("Session replaced.");
        reason = observedBuild.IsSynthetic || qualifiedBuild.IsSynthetic || observedBuild != qualifiedBuild
            ? "Build is not qualified."
            : !sourceVerified ? "Internal data source is not verified."
            : !saveReady ? "Save is not ready."
            : "Ready for a bounded read; atomicity is not guaranteed.";
        active = observedBuild == qualifiedBuild && !observedBuild.IsSynthetic && !qualifiedBuild.IsSynthetic
            && sourceVerified && saveReady;
        return generation;
    }

    public void Invalidate(string unavailableReason)
    {
        generation = checked(generation + 1);
        active = false;
        reason = unavailableReason;
    }

    public void Dispose()
    {
        if (disposed) return;
        Invalidate("Host stopped.");
        disposed = true;
    }

    public (bool Available, string Reason) Check(long token) => token != generation
        ? (false, "Session expired.") : (active, reason);
}
