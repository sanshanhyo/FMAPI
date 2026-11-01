using FMAPI.Adapters.Windows;
using FMAPI.Core;
using FMAPI.Sdk;

namespace FMAPI.Host.BepInEx;

// No BepInEx or Unity calls: the exact session source is linked into offline contracts.
internal sealed class HostSession : IDisposable
{
    private readonly object gate = new();
    private readonly ModHost host = new(new UnavailableWindowsAdapter());
    private bool disposed;

    public IDisposable Register(IMod mod)
    {
        ArgumentNullException.ThrowIfNull(mod);
        lock (gate)
        {
            if (disposed) throw new ObjectDisposedException(nameof(HostSession));
            var owned = new OwnedMod(mod);
            host.Load(owned); // Default grants; never enables writes.
            return new Registration(this, owned.Manifest.Id);
        }
    }

    public void Dispose()
    {
        lock (gate)
        {
            if (disposed) return;
            disposed = true;
            host.Dispose();
        }
    }

    private sealed class OwnedMod(IMod mod) : IMod
    {
        public ModManifest Manifest { get; } = mod.Manifest;
        public void OnLoad(IModContext context) => mod.OnLoad(context);
        public void OnUnload() => mod.OnUnload();
    }

    private sealed class Registration(HostSession session, string id) : IDisposable
    {
        private bool disposed;
        public void Dispose()
        {
            lock (session.gate)
            {
                if (disposed) return;
                disposed = true;
                if (!session.disposed) session.host.Unload(id);
            }
        }
    }
}
