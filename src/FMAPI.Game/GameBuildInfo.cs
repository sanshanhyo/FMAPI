namespace FMAPI.Game;

public sealed record GameBuildInfo(
    string Title, string BuildId, string Platform, string Architecture, string Storefront, bool IsSynthetic);

