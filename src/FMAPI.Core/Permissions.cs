using FMAPI.Internal;
using FMAPI.Sdk;

namespace FMAPI.Core;

public sealed class ModGrant
{
    public IReadOnlySet<ModCapability> Capabilities { get; }
    public IReadOnlySet<string> AllowedWriteCommands { get; }

    public static ModGrant ReadOnly { get; } = new([ModCapability.GameRead, ModCapability.Events, ModCapability.UiExtensions]);

    public ModGrant(IEnumerable<ModCapability> capabilities, IEnumerable<string>? allowedWriteCommands = null)
    {
        Capabilities = new SnapshotSet<ModCapability>(capabilities ?? throw new ArgumentNullException(nameof(capabilities)));
        AllowedWriteCommands = new SnapshotSet<string>(allowedWriteCommands ?? [], StringComparer.Ordinal);
    }
}

public sealed class ModHostOptions
{
    public bool EnableWrites { get; }
    public IReadOnlySet<string> AllowedWriteCommands { get; }

    public ModHostOptions(bool enableWrites = false, IEnumerable<string>? allowedWriteCommands = null)
    {
        EnableWrites = enableWrites;
        AllowedWriteCommands = new SnapshotSet<string>(allowedWriteCommands ?? [], StringComparer.Ordinal);
    }
}

public sealed class ModLoadException(string message, Exception? innerException = null) : Exception(message, innerException);
