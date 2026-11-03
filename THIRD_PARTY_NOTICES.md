# Third-party notices

FMAPI's own code is licensed under [MIT](LICENSE). Third-party components retain their own licenses; FMAPI's license does not relicense them.

This structural initialization adds no dependencies and vendors no third-party code. Existing direct test dependencies are declared in [FMAPI.Core.Tests.csproj](tests/FMAPI.Core.Tests/FMAPI.Core.Tests.csproj): coverlet.collector, Microsoft.NET.Test.Sdk, xunit and xunit.runner.visualstudio. This is a tracking entry, not a complete transitive license audit or a distribution notice bundle.

Before adding or distributing a component, record its exact version, official source, license text/source, intended use, modifications, and any required redistribution notices. Review transitive dependencies and the actual distributed artifacts as well. Keep required notices alongside a distribution.

BepInEx is a planned integration point only; this initialization does not bundle it or assert redistribution permission. No game binaries, databases, saves, or extracted/generated game assemblies or metadata are included by this change.
