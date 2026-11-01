# Player installation and ZIP mod packages

Status: accepted long-term user-experience goal; design only. No installer, download runner or package importer is implemented by this decision.

## Goal and boundaries

A player should be able to install FMAPI with one command, then add a mod by dragging its ZIP package into a designated import surface. Ordinary players should not need the .NET SDK, a compiler, manual dependency assembly copying or developer configuration. The exact command name and drag/drop surface remain implementation choices; there is no installation command ready to run today.

FMAPI already separates Read, Event and Command APIs. Installation/package management serves those capabilities and does not require a new MCP layer. Protocol integrations can remain optional consumers. This goal does not change the immediate priority of verifying native reads, authorize running downloads or modifying a game installation, or promise support for every game build.

## One-command framework installation

The future installer should identify or accept the game location, verify the exact build/platform/architecture and any existing loader, then select a compatible pinned FMAPI/BepInEx combination. Unknown builds or incompatible existing installations must stop with a useful explanation rather than silently installing an approximate match. Automatic configuration should be minimal and scoped to this installation; ask only for unresolved choices that affect it.

Stage and verify release artifacts before changing the installation. Record artifact origin, version and integrity information. Back up files that would be changed and keep an installation receipt identifying owned files, previous versions and checksums. A failed installation should restore the prior installation where possible and report any incomplete recovery explicitly. Repair/uninstall should use that receipt and preserve unrelated mods, configuration and user data. Do not promise rollback of gameplay or save changes made after installation.

BepInEx remains an independent LGPL dependency. Before shipping an installer or bundle, complete version-specific notices, corresponding-source arrangements, component replacement and per-dependency licensing checks. Reusing its bootstrap/plugin loader does not require building another injector. SDK tooling is for developers; deliver only the runtime components actually required by a verified player installation.

## ZIP import contract

Dragging a ZIP is a request to inspect a package, not permission to execute arbitrary installation scripts. The initial importer should:

1. Stage the package without loading its assemblies or executing hooks/scripts.
2. Validate the manifest: stable mod ID/version, entry assembly, FMAPI compatibility, supported game/build capabilities, requested permissions and declared dependencies.
3. Resolve dependency versions/order against installed packages; report missing dependencies, conflicts, cycles and duplicate IDs. Do not silently fetch and run an undeclared dependency. A replacement/update must make the affected mod/version clear.
4. Extract safely within a dedicated staging directory: reject absolute/drive/UNC paths, traversal, links or reparse targets escaping the root, ambiguous/colliding names and unsupported archive entries. Enforce limits on entry count, expanded size and compression ratio before committing files.
5. Show the declared author/source, verified provenance or its absence, required dependencies and requested FMAPI capabilities. Author text inside a manifest is not authenticated identity. Preserve host capability grants and default-deny write policy; a mod's request does not grant itself permission.
6. Commit a validated package into its own owned directory with a receipt and recoverable previous version. An invalid ZIP leaves the active installation unchanged. Never overwrite another mod or the loader through a package's paths.

Manifest fields, package layout and dependency semantics need a focused specification and tests before implementation. Avoid adding broad empty SDK interfaces to represent this planned installer. Same-process mod code is not sandboxed by FMAPI's cooperative permissions; package validation and source display must not imply that it is.

## Initial activation model

The first version may require a normal game restart after adding, updating, disabling or removing mods. A successful import can remain pending until restart; it must not claim that the mod is already running. Do not overwrite assemblies used by a running process or require hot reload as an initial milestone. BepInEx owns assembly discovery/loading and dependency ordering; FMAPI validates its own contracts, grants and scoped resources.

## Acceptance before release

Use owned synthetic packages to test valid imports, incompatible manifests, dependency failures, duplicate/update behavior, malicious archive paths, expansion limits and interrupted installation/recovery. Separately verify a supported game install, one owned sample mod, restart activation and uninstall/restore on the exact supported build. Publish installation commands only after artifact hosting, provenance, licensing and recovery behavior are established. A passing framework build or a ZIP copied to disk does not establish these outcomes.

This ADR changes no runtime behavior, game files, README or roadmap. Native reader work and its current single-hook ownership remain unaffected.
