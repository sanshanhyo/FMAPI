using FMAPI.Core;
using FMAPI.Sdk;
using FMAPI.Adapters.Mock;
namespace FMAPI.Core.Tests;
public sealed class ScopedSaveContextTests
{
    [Theory]
    [InlineData(false, false)] [InlineData(false, true)] [InlineData(true, false)]
    public void DenialDoesNotInvokeSource(bool request, bool grant)
    {
        using var source = new Source(); using var host = new ModHost(new MockGameAdapter(), null, source);
        var mod = new Mod(request); host.Load(mod, new ModGrant(grant ? [ModCapability.GameRead] : []));
        Assert.Equal(SaveContextError.Denied, mod.Reader!.ReadCurrentSave().Error); Assert.Equal(0, source.Reads);
    }
    [Fact]
    public void UnloadAndSameIdReplacementNeverReviveOldReader()
    {
        using var source = new Source(); using var host = new ModHost(new MockGameAdapter(), null, source);
        var first = new Mod(true); host.Load(first, new ModGrant([ModCapability.GameRead]));
        Assert.True(first.Reader!.ReadCurrentSave().Snapshot!.IsSynthetic);
        host.Unload(first.Manifest.Id); var second = new Mod(true); host.Load(second, new ModGrant([ModCapability.GameRead]));
        Assert.Equal(SaveContextError.Expired, first.Reader.ReadCurrentSave().Error); Assert.Equal(1, source.Reads);
        Assert.Equal(SaveContextStatus.Available, second.Reader!.ReadCurrentSave().Status);
        host.Dispose(); Assert.Equal(SaveContextError.Expired, second.Reader.ReadCurrentSave().Error);
    }
    [Theory]
    [InlineData(false)] [InlineData(true)]
    public void RevocationOrSessionChangeDuringCaptureDiscardsResult(bool sessionChange)
    {
        using var source = new Source(); using var host = new ModHost(new MockGameAdapter(), null, source);
        var mod = new Mod(true); host.Load(mod, new ModGrant([ModCapability.GameRead]));
        source.DuringRead = () => { if (sessionChange) source.Fixture.LoadFixture("next", new(2026, 1, 2), "m", "t"); else host.Unload(mod.Manifest.Id); };
        var result = mod.Reader!.ReadCurrentSave(); Assert.Equal(SaveContextError.Expired, result.Error); Assert.Null(result.Snapshot);
    }
    [Fact]
    public void MissingSourceIsExplicitlyUnsupported()
    {
        using var host = new ModHost(new MockGameAdapter()); var mod = new Mod(true); host.Load(mod, new ModGrant([ModCapability.GameRead]));
        Assert.Equal(SaveContextError.Unsupported, mod.Reader!.ReadCurrentSave().Error);
    }
    private sealed class Mod(bool request) : IMod
    {
        public ModManifest Manifest { get; } = new("test.save", "fixture", new(0,1,0), FmApiVersion.Current, request ? [ModCapability.GameRead] : []);
        public ISaveContextReader? Reader;
        public void OnLoad(IModContext context) => Reader = ((IModSaveContext)context).SaveContext;
        public void OnUnload() { }
    }
    private sealed class Source : ISaveContextSessionSource, IDisposable
    {
        public MockSaveContextReader Fixture { get; } = new(); public int Reads; public Action? DuringRead;
        public long Generation => Fixture.Generation;
        public Source() => Fixture.LoadFixture("owned", new(2026,1,1), "m", "t");
        public SaveContextResult ReadCurrentSave() { Reads++; var result = Fixture.ReadCurrentSave(); DuringRead?.Invoke(); return result; }
        public void Dispose() => Fixture.Dispose();
    }
}
