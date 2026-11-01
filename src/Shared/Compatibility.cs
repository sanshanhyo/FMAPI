using System.Collections;
using System.Runtime.CompilerServices;

namespace FMAPI.Internal;

// Copy input and expose no mutation interface, on both runtime targets.
// Returning a HashSet as IReadOnlySet alone would let callers cast and change grants.
internal sealed class SnapshotSet<T> : IReadOnlySet<T>
{
    private readonly HashSet<T> items;

    public SnapshotSet(IEnumerable<T> values, IEqualityComparer<T>? comparer = null)
        => items = new HashSet<T>(values, comparer);

    public int Count => items.Count;
    public bool Contains(T item) => items.Contains(item);
    public bool IsProperSubsetOf(IEnumerable<T> other) => items.IsProperSubsetOf(other);
    public bool IsProperSupersetOf(IEnumerable<T> other) => items.IsProperSupersetOf(other);
    public bool IsSubsetOf(IEnumerable<T> other) => items.IsSubsetOf(other);
    public bool IsSupersetOf(IEnumerable<T> other) => items.IsSupersetOf(other);
    public bool Overlaps(IEnumerable<T> other) => items.Overlaps(other);
    public bool SetEquals(IEnumerable<T> other) => items.SetEquals(other);
    public IEnumerator<T> GetEnumerator() => items.GetEnumerator();
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}

internal static class Guard
{
    public static void NotBlank(string? value, [CallerArgumentExpression("value")] string? parameter = null)
    {
        ArgumentNullException.ThrowIfNull(value, parameter);
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("The value cannot be empty or whitespace.", parameter);
        }
    }

    public static void NotDisposed(bool disposed, object instance)
    {
        if (disposed)
        {
            throw new ObjectDisposedException(instance.GetType().FullName);
        }
    }
}
