using System.Collections.ObjectModel;

namespace FMAPI.Game;

public sealed class GameSnapshot
{
    public GameBuildInfo Build { get; }
    public IReadOnlyDictionary<string, string> Values { get; }

    public GameSnapshot(GameBuildInfo build, IReadOnlyDictionary<string, string> values)
    {
        Build = build ?? throw new ArgumentNullException(nameof(build));
        Values = new ReadOnlyDictionary<string, string>(new Dictionary<string, string>(values, StringComparer.Ordinal));
    }
}

