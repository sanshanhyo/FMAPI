# Contributing to FMAPI

Start with the [project scope](docs/scope.md) and [architecture](docs/architecture/overview.md). FMAPI currently provides an offline framework foundation; real-game support requires separate evidence and implementation.

## Local checks

Use the .NET 10 SDK selected by `global.json`. From the repository root:

```sh
dotnet restore FMAPI.slnx
dotnet build FMAPI.slnx --configuration Release --no-restore
dotnet test FMAPI.slnx --configuration Release --no-build
dotnet run --project tools/FMAPI.Cli --configuration Release --no-build -- demo
```

Run checks relevant to your change. Add behavior tests for lifecycle, event cleanup, UI ownership, compatibility checks, and command policy when those behaviors change. Describe commands actually run and any remaining limitations in the pull request.

## Public API changes

- Keep `FMAPI.SDK` independent of host implementation, companion applications, and game-version internals.
- Describe the consumer impact of a changed contract, update the example and documentation, and add a decision record for substantial design changes.
- Treat `0.x` APIs as experimental, while making breaking changes visible in review.
- Preserve explicit unsupported or unknown results. Synthetic examples must remain clearly labeled.

## Adapter contributions

An adapter proposal must identify the game edition/build, release channel, storefront, operating system, architecture, and supported capabilities. Record reproduction steps and the evidence for each claimed capability in [compatibility](docs/compatibility.md).

Keep build-specific details within the adapter. Real write commands need validation, game-thread execution rules, failure behavior, and a description of any recovery guarantees or their absence. Core default-deny policy and dry-run behavior must remain testable without a game.

Do not commit game binaries, databases, saves, extracted/generated game assemblies or metadata, secrets, local install paths, or unreviewed third-party code. Use owned or synthetic fixtures and record dependency licenses. Any new dependency should have a concrete need.

## Reporting issues and proposing work

Use the repository's issue tracker once a remote is available. For a bug, include a minimal reproduction, expected and observed results, the framework commit, and relevant platform information. A proposed game adapter also needs the compatibility details above. Remove personal information from logs.

Keep pull requests focused and explain the resulting behavior. Contributions are provided under this repository's [MIT License](LICENSE); dependencies retain their own terms.
