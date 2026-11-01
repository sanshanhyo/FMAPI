using BepInEx;
using BepInEx.Unity.IL2CPP;
using FMAPI.Adapters.Windows;
using FMAPI.Sdk;

namespace FMAPI.Host.BepInEx;

[BepInPlugin(PluginId, "FMAPI Host", "0.1.0")]
public sealed class FmApiPlugin : BasePlugin
{
    public const string PluginId = "org.fmapi.host";
    private static readonly object Gate = new();
    private static HostSession? current;
    private HostSession? owned;

    public override void Load()
    {
        lock (Gate)
        {
            if (current is not null || owned is not null)
                throw new InvalidOperationException("The FMAPI host is already loaded.");
            current = owned = new HostSession();
        }
        Log.LogWarning($"FMAPI host initialized; game access remains unavailable. {UnavailableWindowsAdapter.UnavailableReason}");
    }

    // Consumers declare a hard BepInDependency on PluginId, register in Load,
    // and dispose the returned registration in Unload. No DLL discovery occurs here.
    public static IDisposable RegisterMod(IMod mod)
    {
        HostSession session;
        lock (Gate)
        {
            session = current ?? throw new InvalidOperationException("The FMAPI host is not loaded.");
        }
        return session.Register(mod);
    }

    public override bool Unload()
    {
        HostSession? session;
        lock (Gate)
        {
            session = owned;
            owned = null;
            if (ReferenceEquals(current, session)) current = null;
        }
        try { session?.Dispose(); }
        catch (AggregateException error)
        {
            // Core already revoked all contexts and attempted every mod's cleanup.
            Log.LogError(error);
        }
        return true;
    }
}
