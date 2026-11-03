using FMAPI.Game;
using System.Runtime.InteropServices;
using FMAPI.SDK;

namespace FMAPI.Adapters.Mock;

// All values are synthetic. This adapter never connects to a game or reads game files.
public sealed class MockGameAdapter : IGameAdapter
{
    public const string RenameClubCommand = "mock.club.rename";
    public const string InitialClubName = "Synthetic FC";
    private readonly object gate = new();
    private string clubName = InitialClubName;

    public AdapterDescriptor Descriptor { get; } = new(
        "fmapi.mock",
        new GameBuildInfo("FMAPI offline fixture", "synthetic-1", "offline", RuntimeInformation.ProcessArchitecture.ToString(), "none", true),
        supportsReads: true,
        supportsWrites: true,
        supportedWriteCommands: [RenameClubCommand]);

    public GameSnapshot ReadSnapshot()
    {
        lock (gate)
        {
            return new(Descriptor.Build, new Dictionary<string, string>
            {
                ["club.id"] = "synthetic-club-001",
                ["club.name"] = clubName,
                ["data.source"] = "synthetic"
            });
        }
    }

    public CommandValidation ValidateCommand(GameCommand command)
    {
        if (command.Name != RenameClubCommand)
        {
            return new(false, "Unknown mock command.");
        }
        if (command.Arguments.Count != 1 || !command.Arguments.TryGetValue("name", out var name)
            || string.IsNullOrWhiteSpace(name) || name.Length > 80)
        {
            return new(false, "mock.club.rename requires only a nonblank 'name' of at most 80 characters.");
        }
        return new(true, "Valid synthetic club rename.");
    }

    public CommandResult ExecuteCommand(GameCommand command)
    {
        var validation = ValidateCommand(command);
        if (!validation.IsValid)
        {
            return new(CommandStatus.Invalid, validation.Message);
        }
        lock (gate)
        {
            clubName = command.Arguments["name"];
        }
        return new(CommandStatus.Applied, "Renamed the in-memory synthetic club.");
    }
}
