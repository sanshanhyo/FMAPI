# FMAPI contributor instructions

## Scope and ownership

FMAPI is an independent, unofficial Football Manager modding framework under MIT. Its current implementation is an offline foundation. Read `README.md`, `docs/scope.md`, and `docs/architecture/overview.md` before changing framework behavior.

- `src/FMAPI.SDK` owns public contracts and must not reference Core, a concrete adapter, or a companion application.
- `src/FMAPI.Core` owns host policy and mod-scoped resources.
- `tests/FMAPI.Adapters.Mock` and example data are synthetic.
- Real-game support must live behind adapter contracts, with compatibility evidence documented per game build and platform.

## Development

Use .NET 10 and the checked-in `global.json`. Build and test with the commands in `CONTRIBUTING.md`. Run the offline demo when changing SDK/Core/example behavior. Do not describe unrun checks as passing.

Keep changes focused, preserve unrelated edits, and update documentation when public behavior changes. Add tests for meaningful behavior changes rather than tests that simply repeat implementation structure.

## Required boundaries

- Keep writes disabled by default and preserve explicit capability grants, command allowlists, adapter validation, and non-mutating dry-run behavior.
- Scope event subscriptions and UI declarations to mod lifetime; cleanup must also cover failed loads.
- Do not present declarative UI registration as game UI rendering or mock data as observed game data.
- Do not claim that cooperative API permissions isolate malicious in-process code.
- Do not add game binaries, databases, saves, generated game assemblies/metadata, secrets, fixed local install paths, or code copied without license review.
- Do not claim game/platform compatibility without reproducible evidence recorded in `docs/compatibility.md`.

Do not install into a game, inject a runtime, publish packages, or change a remote as part of routine build/test work. Those actions need task-specific scope. The normal verification path uses the offline adapter.
