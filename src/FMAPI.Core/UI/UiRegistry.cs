using FMAPI.SDK;

namespace FMAPI.Core;

internal sealed class UiRegistry
{
    private readonly object gate = new();
    private readonly Dictionary<(string ModId, string Id), RegisteredUiExtension> extensions = [];

    public IDisposable Register(ModScope owner, UiExtension extension)
    {
        ArgumentNullException.ThrowIfNull(extension);
        ArgumentException.ThrowIfNullOrWhiteSpace(extension.Id);
        ArgumentException.ThrowIfNullOrWhiteSpace(extension.Title);
        ArgumentException.ThrowIfNullOrWhiteSpace(extension.Placement);
        if (!Enum.IsDefined(extension.Kind))
        {
            throw new ArgumentException("Unknown UI extension kind.", nameof(extension));
        }
        var key = (owner.Manifest.Id, extension.Id);
        var registered = new RegisteredUiExtension(owner.Manifest.Id, extension);
        lock (gate)
        {
            if (!extensions.TryAdd(key, registered))
            {
                throw new InvalidOperationException($"UI extension '{extension.Id}' is already registered by '{owner.Manifest.Id}'.");
            }
        }
        return new RegistrationToken(() =>
        {
            lock (gate)
            {
                // An old token must not remove a registration from a later reload.
                if (extensions.TryGetValue(key, out var current) && ReferenceEquals(current, registered))
                {
                    extensions.Remove(key);
                }
            }
        });
    }

    public IReadOnlyList<RegisteredUiExtension> Snapshot()
    {
        lock (gate)
        {
            return extensions.Values.OrderBy(value => value.ModId, StringComparer.Ordinal)
                .ThenBy(value => value.Extension.Id, StringComparer.Ordinal).ToArray();
        }
    }

    public void RemoveOwner(ModScope owner)
    {
        lock (gate)
        {
            foreach (var key in extensions.Keys.Where(key => key.ModId == owner.Manifest.Id).ToArray())
            {
                extensions.Remove(key);
            }
        }
    }
}
