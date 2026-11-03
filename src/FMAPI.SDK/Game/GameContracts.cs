using FMAPI.Game;
using System.Collections.Frozen;
using System.Collections.ObjectModel;

namespace FMAPI.SDK;

public sealed class AdapterDescriptor
{
    public string Id { get; }
    public GameBuildInfo Build { get; }
    public bool SupportsReads { get; }
    public bool SupportsWrites { get; }
    public IReadOnlySet<string> SupportedWriteCommands { get; }

    public AdapterDescriptor(string id, GameBuildInfo build, bool supportsReads, bool supportsWrites,
        IEnumerable<string>? supportedWriteCommands = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);
        Id = id;
        Build = build ?? throw new ArgumentNullException(nameof(build));
        SupportsReads = supportsReads;
        SupportsWrites = supportsWrites;
        SupportedWriteCommands = (supportedWriteCommands ?? []).ToFrozenSet(StringComparer.Ordinal);
    }
}

public sealed class GameCommand
{
    public string Name { get; }
    public IReadOnlyDictionary<string, string> Arguments { get; }

    public GameCommand(string name, IReadOnlyDictionary<string, string>? arguments = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(name);
        Name = name;
        Arguments = new ReadOnlyDictionary<string, string>(new Dictionary<string, string>(arguments ?? new Dictionary<string, string>(), StringComparer.Ordinal));
    }
}

public enum GameReadStatus
{
    Available,
    Denied,
    Unsupported,
    Failed
}

public sealed record GameReadResult(GameReadStatus Status, string Message, GameSnapshot? Snapshot = null);

public enum CommandStatus
{
    Denied,
    Unsupported,
    Invalid,
    DryRun,
    Applied,
    Failed
}

public sealed record CommandResult(CommandStatus Status, string Message);

public sealed record CommandValidation(bool IsValid, string Message);

public sealed record CommandExecutionOptions(bool DryRun = true);

public interface IModGame
{
    AdapterDescriptor Adapter { get; }
    GameReadResult ReadSnapshot();
    CommandResult Execute(GameCommand command, CommandExecutionOptions? options = null);
}

// Implementations own platform/build compatibility and game-thread scheduling.
// ValidateCommand must not change game state. ExecuteCommand is called only after host checks.
public interface IGameAdapter
{
    AdapterDescriptor Descriptor { get; }
    GameSnapshot ReadSnapshot();
    CommandValidation ValidateCommand(GameCommand command);
    CommandResult ExecuteCommand(GameCommand command);
}
