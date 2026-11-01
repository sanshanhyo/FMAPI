using FMAPI.Sdk;

namespace FMAPI.Core;

internal sealed class RegistrationToken(Action dispose) : IDisposable
{
    private Action? dispose = dispose;
    public void Dispose() => Interlocked.Exchange(ref dispose, null)?.Invoke();
}

internal sealed class EventRegistry
{
    private readonly object gate = new();
    private readonly List<Subscription> subscriptions = [];

    public IDisposable Subscribe<TEvent>(ModScope owner, Action<TEvent> handler)
    {
        ArgumentNullException.ThrowIfNull(handler);
        var subscription = new Subscription(owner, typeof(TEvent), value => handler((TEvent)value!));
        lock (gate)
        {
            subscriptions.Add(subscription);
        }
        return new RegistrationToken(() => Remove(subscription));
    }

    public EventDispatchReport Publish<TEvent>(TEvent value)
    {
        Subscription[] current;
        lock (gate)
        {
            current = subscriptions.Where(subscription => subscription.EventType == typeof(TEvent)).ToArray();
        }
        var delivered = 0;
        List<EventHandlerFailure> failures = [];
        foreach (var subscription in current)
        {
            lock (subscription.Owner.Gate)
            {
                if (!subscription.Owner.Active || !subscription.Active)
                {
                    continue;
                }
                try
                {
                    subscription.Handler(value);
                    delivered++;
                }
                catch (Exception error)
                {
                    failures.Add(new(subscription.Owner.Manifest.Id, error.Message));
                }
            }
        }
        return new(delivered, failures.AsReadOnly());
    }

    public void RemoveOwner(ModScope owner)
    {
        lock (gate)
        {
            foreach (var subscription in subscriptions.Where(subscription => subscription.Owner == owner))
            {
                subscription.Active = false;
            }
            subscriptions.RemoveAll(subscription => subscription.Owner == owner);
        }
    }

    private void Remove(Subscription subscription)
    {
        lock (subscription.Owner.Gate)
        {
            lock (gate)
            {
                subscription.Active = false;
                subscriptions.Remove(subscription);
            }
        }
    }

    private sealed class Subscription(ModScope owner, Type eventType, Action<object?> handler)
    {
        public ModScope Owner { get; } = owner;
        public Type EventType { get; } = eventType;
        public Action<object?> Handler { get; } = handler;
        public bool Active { get; set; } = true;
    }
}

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
