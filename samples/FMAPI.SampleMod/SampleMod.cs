using FMAPI.SDK;

namespace FMAPI.SampleMod;

public sealed record DemoTick(int Number);

public sealed class SampleMod : IMod
{
    private IModContext? context;
    private IDisposable? subscription;
    private IDisposable? panel;

    public ModManifest Manifest { get; } = ReadManifest();
    public int ReceivedTicks { get; private set; }

    public void OnLoad(IModContext context)
    {
        this.context = context;
        subscription = context.Events.Subscribe<DemoTick>(_ => ReceivedTicks++);
        panel = context.Ui.Register(new UiExtension("overview", UiExtensionKind.Panel, "Offline sample overview", "club.overview"));
    }

    public GameReadResult ReadSnapshot() => ActiveContext.Game.ReadSnapshot();

    public CommandResult RenameSyntheticClub(string name, bool dryRun = true) => ActiveContext.Game.Execute(
        new GameCommand("mock.club.rename", new Dictionary<string, string> { ["name"] = name }),
        new CommandExecutionOptions(dryRun));

    public void OnUnload()
    {
        panel?.Dispose();
        subscription?.Dispose();
        context = null;
    }

    private IModContext ActiveContext => context ?? throw new InvalidOperationException("Sample mod is not loaded.");

    private static ModManifest ReadManifest()
    {
        using var stream = typeof(SampleMod).Assembly.GetManifestResourceStream("FMAPI.SampleMod.mod.json")
            ?? throw new InvalidOperationException("Embedded sample manifest is missing.");
        using var reader = new StreamReader(stream);
        return ModManifest.Parse(reader.ReadToEnd());
    }
}
