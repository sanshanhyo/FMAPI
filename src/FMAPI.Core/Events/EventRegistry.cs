using FMAPI.SDK;

namespace FMAPI.Core;

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

