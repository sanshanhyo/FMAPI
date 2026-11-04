using FMAPI.Internal;
using System.Text.RegularExpressions;
using FMAPI.Sdk;

namespace FMAPI.Core;

// Lifecycle calls are synchronous; callers must serialize Load, Unload and Dispose.
// Mod grants govern cooperative API use and do not isolate untrusted in-process code.
public sealed class ModHost : IDisposable
{
    private readonly IGameAdapter adapter;
    private readonly AdapterDescriptor descriptor;
    private readonly ModHostOptions options;
    private readonly Dictionary<string, ModScope> mods = new(StringComparer.Ordinal);
    private readonly EventRegistry events = new();
    private readonly UiRegistry ui = new();
    private bool disposed;
    private readonly ISaveContextSessionSource? saveContextSource;

    public ModHost(IGameAdapter adapter, ModHostOptions? options = null) : this(adapter, options, null) { }

    public ModHost(IGameAdapter adapter, ModHostOptions? options, ISaveContextSessionSource? saveContextSource)
    {
        this.adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
        descriptor = adapter.Descriptor ?? throw new ArgumentException("Adapter descriptor is required.", nameof(adapter));
        this.options = options ?? new ModHostOptions();
        this.saveContextSource = saveContextSource;
    }

    public IReadOnlyList<string> LoadedModIds => mods.Keys.OrderBy(id => id, StringComparer.Ordinal).ToArray();
    public IReadOnlyList<RegisteredUiExtension> UiExtensions => ui.Snapshot();

    public void Load(IMod mod, ModGrant? grant = null)
    {
        Guard.NotDisposed(disposed, this);
        ArgumentNullException.ThrowIfNull(mod);
        var manifest = mod.Manifest ?? throw new ModLoadException("Mod manifest is required.");
        ValidateManifest(manifest);
        if (mods.ContainsKey(manifest.Id))
        {
            throw new ModLoadException($"Mod '{manifest.Id}' is already loaded.");
        }

        var scope = new ModScope(mod, manifest, grant ?? ModGrant.ReadOnly);
        mods.Add(manifest.Id, scope);
        try
        {
            mod.OnLoad(new ModContext(this, scope));
        }
        catch (Exception error)
        {
            if (!scope.Active)
                throw new ModLoadException($"Mod '{manifest.Id}' failed after its registration was revoked.", error);
            RemoveScope(scope);
            // Give a partially initialized mod a chance to release its own resources.
            try
            {
                mod.OnUnload();
            }
            catch (Exception cleanupError)
            {
                throw new ModLoadException($"Mod '{manifest.Id}' failed to load and clean up.", new AggregateException(error, cleanupError));
            }
            throw new ModLoadException($"Mod '{manifest.Id}' failed to load.", error);
        }
        if (!scope.Active)
            throw new ModLoadException($"Mod '{manifest.Id}' was revoked during OnLoad.");
    }

    public bool Unload(string modId)
    {
        Guard.NotDisposed(disposed, this);
        if (!mods.TryGetValue(modId, out var scope))
        {
            return false;
        }
        RemoveScope(scope);
        scope.Mod.OnUnload();
        return true;
    }

    public EventDispatchReport Publish<TEvent>(TEvent value)
    {
        Guard.NotDisposed(disposed, this);
        return events.Publish(value);
    }

    public void Dispose()
    {
        if (disposed)
        {
            return;
        }
        disposed = true;
        List<Exception> errors = [];
        foreach (var scope in mods.Values.ToArray())
        {
            RemoveScope(scope);
            try
            {
                scope.Mod.OnUnload();
            }
            catch (Exception error)
            {
                errors.Add(error);
            }
        }
        if (errors.Count > 0)
        {
            throw new AggregateException("One or more mods failed to unload; host registrations were removed.", errors);
        }
    }

    private static void ValidateManifest(ModManifest manifest)
    {
        if (!Regex.IsMatch(manifest.Id, @"\A[a-z0-9]+(?:[.-][a-z0-9]+)*\z", RegexOptions.CultureInvariant))
        {
            throw new ModLoadException("Mod id must contain lowercase letters/digits separated by dots or hyphens.");
        }
        if (string.IsNullOrWhiteSpace(manifest.Name))
        {
            throw new ModLoadException("Mod name is required.");
        }
        // During 0.x, only this API's exact major/minor line is compatible.
        var expected = FmApiVersion.Current;
        if (manifest.ApiVersion.Major != expected.Major || manifest.ApiVersion.Minor != expected.Minor
            || manifest.ApiVersion.Build > expected.Build || manifest.ApiVersion.Revision > 0)
        {
            throw new ModLoadException($"API {manifest.ApiVersion} is unsupported; host API is {expected}.");
        }
        if (manifest.RequestedCapabilities.Any(capability => !Enum.IsDefined(typeof(ModCapability), capability)))
        {
            throw new ModLoadException("Manifest contains an unknown capability.");
        }
    }

    private void RemoveScope(ModScope scope)
    {
        lock (scope.Gate)
        {
            scope.Active = false;
            events.RemoveOwner(scope);
            ui.RemoveOwner(scope);
            mods.Remove(scope.Manifest.Id);
        }
    }

    private GameReadResult ReadSnapshot(ModScope scope)
    {
        lock (scope.Gate)
        {
            scope.EnsureActive();
            if (!scope.HasCapability(ModCapability.GameRead))
            {
                return new(GameReadStatus.Denied, "The mod did not request and receive GameRead.");
            }
            if (!descriptor.SupportsReads)
            {
                return new(GameReadStatus.Unsupported, "The adapter does not support reads.");
            }
            try
            {
                var snapshot = adapter.ReadSnapshot();
                // Adapter callbacks may reenter unload/dispose on this same monitor.
                if (!scope.Active)
                    return new(GameReadStatus.Failed, "Read scope was revoked during capture; snapshot discarded.");
                if (snapshot is null)
                    return new(GameReadStatus.Failed, "Adapter returned no snapshot.");
                return new(GameReadStatus.Available, "Snapshot available.", snapshot);
            }
            catch (Exception error)
            {
                return new(GameReadStatus.Failed, $"Adapter read failed: {error.Message}");
            }
        }
    }

    private CommandResult Execute(ModScope scope, GameCommand command, CommandExecutionOptions? executionOptions)
    {
        ArgumentNullException.ThrowIfNull(command);
        lock (scope.Gate)
        {
            scope.EnsureActive();
            if (!scope.HasCapability(ModCapability.GameWrite))
            {
                return new(CommandStatus.Denied, "The mod did not request and receive GameWrite.");
            }
            if (!options.EnableWrites)
            {
                return new(CommandStatus.Denied, "Host writes are disabled.");
            }
            if (!options.AllowedWriteCommands.Contains(command.Name)
                || !scope.Grant.AllowedWriteCommands.Contains(command.Name))
            {
                return new(CommandStatus.Denied, "The command is not in both host and mod allowlists.");
            }
            if (!descriptor.SupportsWrites || !descriptor.SupportedWriteCommands.Contains(command.Name))
            {
                return new(CommandStatus.Unsupported, "The adapter does not support this write command.");
            }
            try
            {
                var validation = adapter.ValidateCommand(command);
                if (!validation.IsValid)
                {
                    return new(CommandStatus.Invalid, validation.Message);
                }
                if ((executionOptions ?? new CommandExecutionOptions()).DryRun)
                {
                    return new(CommandStatus.DryRun, "Validation passed; no write was executed.");
                }
                return adapter.ExecuteCommand(command);
            }
            catch (Exception error)
            {
                return new(CommandStatus.Failed, $"Adapter command failed: {error.Message}");
            }
        }
    }

    private SaveContextResult ReadCurrentSave(ModScope scope)
    {
        lock (scope.Gate)
        {
            if (!scope.Active) return new(SaveContextStatus.Unavailable, "Mod registration expired.", null, SaveContextError.Expired);
            if (!scope.HasCapability(ModCapability.GameRead)) return new(SaveContextStatus.Unavailable, "GameRead denied.", null, SaveContextError.Denied);
            if (saveContextSource is null) return new(SaveContextStatus.Unavailable, "Save context source unavailable.", null, SaveContextError.Unsupported);
            try
            {
                var generation = saveContextSource.Generation;
                var result = saveContextSource.ReadCurrentSave();
                if (!scope.Active || generation != saveContextSource.Generation)
                    return new(SaveContextStatus.Unavailable, "Context changed during capture.", null, SaveContextError.Expired);
                return result ?? new(SaveContextStatus.Unavailable, "Source returned no result.", null, SaveContextError.Failed);
            }
            catch (Exception)
            {
                return new(SaveContextStatus.Unavailable, "Save context capture failed.", null, SaveContextError.Failed);
            }
        }
    }
    private sealed class ModContext : IModContext, IModEvents, IModUi, IModGame, IModSaveContext, ISaveContextReader
    {
        private readonly ModHost host;
        private readonly ModScope scope;
        public ModManifest Manifest => scope.Manifest;
        public IModEvents Events => this;
        public IModUi Ui => this;
        public IModGame Game => this;
        public ISaveContextReader SaveContext => this;
        public SaveContextResult ReadCurrentSave() => host.ReadCurrentSave(scope);
        public AdapterDescriptor Adapter => host.descriptor;

        public ModContext(ModHost host, ModScope scope) => (this.host, this.scope) = (host, scope);

        public IDisposable Subscribe<TEvent>(Action<TEvent> handler)
        {
            lock (scope.Gate)
            {
                scope.RequireCapability(ModCapability.Events);
                return host.events.Subscribe(scope, handler);
            }
        }

        public EventDispatchReport Publish<TEvent>(TEvent value)
        {
            lock (scope.Gate)
            {
                scope.RequireCapability(ModCapability.Events);
            }
            return host.events.Publish(value);
        }

        public IDisposable Register(UiExtension extension)
        {
            lock (scope.Gate)
            {
                scope.RequireCapability(ModCapability.UiExtensions);
                return host.ui.Register(scope, extension);
            }
        }

        public GameReadResult ReadSnapshot() => host.ReadSnapshot(scope);
        public CommandResult Execute(GameCommand command, CommandExecutionOptions? options = null) => host.Execute(scope, command, options);
    }
}

internal sealed class ModScope(IMod mod, ModManifest manifest, ModGrant grant)
{
    public object Gate { get; } = new();
    public bool Active { get; set; } = true;
    public IMod Mod { get; } = mod;
    public ModManifest Manifest { get; } = manifest;
    public ModGrant Grant { get; } = grant;

    public void EnsureActive()
    {
        if (!Active)
        {
            throw new InvalidOperationException("The mod context is no longer active.");
        }
    }

    public bool HasCapability(ModCapability capability) => Manifest.RequestedCapabilities.Contains(capability) && Grant.Capabilities.Contains(capability);

    public void RequireCapability(ModCapability capability)
    {
        EnsureActive();
        if (!HasCapability(capability))
        {
            throw new UnauthorizedAccessException($"The mod did not request and receive {capability}.");
        }
    }
}
