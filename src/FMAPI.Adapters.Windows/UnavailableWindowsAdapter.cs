using FMAPI.Sdk;

namespace FMAPI.Adapters.Windows;

// Offline placeholder, not a BepInEx plugin or a game/process detector.
// Replace only after a specific game's business objects and lifecycle are verified.
public sealed class UnavailableWindowsAdapter : IGameAdapter
{
    public const string UnavailableReason =
        "Windows game integration is unavailable: bootstrap and game data sources are not implemented or verified.";

    public AdapterDescriptor Descriptor { get; } = new(
        "fmapi.windows.unavailable",
        new GameBuildInfo("Football Manager (not detected)", "unknown", "Windows", "unknown", "unknown", false),
        supportsReads: false, supportsWrites: false);

    public GameSnapshot ReadSnapshot() => throw new NotSupportedException(UnavailableReason);

    public CommandValidation ValidateCommand(GameCommand command) => new(false, UnavailableReason);

    public CommandResult ExecuteCommand(GameCommand command) => new(CommandStatus.Unsupported, UnavailableReason);
}
