using System.Collections.Frozen;
using System.Text.Json;

namespace FMAPI.Sdk;

public static class FmApiVersion
{
    public static Version Current { get; } = new(0, 1, 0);
}

public enum ModCapability
{
    GameRead,
    Events,
    UiExtensions,
    GameWrite
}

public sealed class ModManifest
{
    public string Id { get; }
    public string Name { get; }
    public Version Version { get; }
    public Version ApiVersion { get; }
    public IReadOnlySet<ModCapability> RequestedCapabilities { get; }

    public ModManifest(string id, string name, Version version, Version apiVersion,
        IEnumerable<ModCapability> requestedCapabilities)
    {
        Id = id ?? throw new ArgumentNullException(nameof(id));
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Version = version ?? throw new ArgumentNullException(nameof(version));
        ApiVersion = apiVersion ?? throw new ArgumentNullException(nameof(apiVersion));
        RequestedCapabilities = (requestedCapabilities ?? throw new ArgumentNullException(nameof(requestedCapabilities)))
            .ToFrozenSet();
    }

    public static ModManifest Parse(string json)
    {
        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;
        var capabilities = root.GetProperty("requestedCapabilities").EnumerateArray()
            .Select(element => element.GetString() is { } value
                && Enum.TryParse<ModCapability>(value, ignoreCase: false, out var capability)
                && Enum.IsDefined(capability)
                && capability.ToString() == value
                    ? capability
                    : throw new FormatException("Unknown mod capability."));
        return new ModManifest(
            root.GetProperty("id").GetString() ?? throw new FormatException("Missing mod id."),
            root.GetProperty("name").GetString() ?? throw new FormatException("Missing mod name."),
            System.Version.Parse(root.GetProperty("version").GetString() ?? ""),
            System.Version.Parse(root.GetProperty("apiVersion").GetString() ?? ""),
            capabilities);
    }
}

public interface IMod
{
    ModManifest Manifest { get; }
    void OnLoad(IModContext context);
    void OnUnload();
}

public interface IModContext
{
    ModManifest Manifest { get; }
    IModEvents Events { get; }
    IModUi Ui { get; }
    IModGame Game { get; }
}

public interface IModEvents
{
    IDisposable Subscribe<TEvent>(Action<TEvent> handler);
    EventDispatchReport Publish<TEvent>(TEvent value);
}

public sealed record EventHandlerFailure(string ModId, string Message);

public sealed record EventDispatchReport(int Delivered, IReadOnlyList<EventHandlerFailure> Failures);

public enum UiExtensionKind
{
    Panel,
    MenuItem
}

// Declarative metadata only. A future platform adapter is responsible for rendering.
public sealed record UiExtension(string Id, UiExtensionKind Kind, string Title, string Placement);

public sealed record RegisteredUiExtension(string ModId, UiExtension Extension);

public interface IModUi
{
    IDisposable Register(UiExtension extension);
}
