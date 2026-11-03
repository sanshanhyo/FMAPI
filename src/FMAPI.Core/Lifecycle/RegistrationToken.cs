using FMAPI.SDK;

namespace FMAPI.Core;

internal sealed class RegistrationToken(Action dispose) : IDisposable
{
    private Action? dispose = dispose;
    public void Dispose() => Interlocked.Exchange(ref dispose, null)?.Invoke();
}

