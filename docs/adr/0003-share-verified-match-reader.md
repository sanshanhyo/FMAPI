# Share the current match reader findings

Status: technical boundary recorded; code extraction paused pending provenance and license review. No reader port or second hook installed by this change.

## Evidence and its limits

The active FA task reports an installed native match hook reading team identities, score updates, ticks, 50 player identities/names/positions, and 22 players on the pitch. The user confirmed agreement for score, shots, shots on target, xG and corners, plus four attributes, height and birth date for the same player. These are reported observations from the current FA session, not tests run by FMAPI. Counts describe that observation, not a universal squad size or invariant.

The inspected source is FA's `modules/game-bridge/match-reader`. Its vendored reader identifies upstream FMMatchLens commit `276d17ff677f90a0f13a75565c7af7d855756768` and carries `Copyright (c) 2026 osnsyc` under MIT in `vendor/LICENSE`. That notice establishes neither the license of FA as a whole nor permission to copy FA-added or modified code into MIT FMAPI. FA may be GPLv3; its exact revision/license and rights in each modification are still being checked. FA's README still describes an unverified candidate and only one local hook change; do not use it as a complete provenance or modification inventory.

No private snapshot, save, live game memory, game binary or generated assembly was read or copied for this review. The source's build catalog contains an accepted fingerprint; it was not independently matched to the running game in this task. FMAPI still advertises no real-game read/event capability. A later, narrowly scoped FA out-of-match observation is recorded below; it does not establish general world/save access.

## Reported out-of-match player lookup

The active FA task subsequently reports locating one user-selected player by UID through a candidate personnel-table fallback in 16 bounded probes, with a matching name and an exact player-type check before decoding fields. Four raw attribute values `60/55/55/75` decoded to `12/11/11/15`; the user also confirmed height and birth date against the selected player. The report states that this used the current out-of-match save, not a match cache. Player identity and private snapshots are intentionally not reproduced here.

This supports a proposed native-adapter operation that resolves a player by UID independently of an active match or UI page. It does not establish unrestricted enumeration, a stable table root, lookup performance for every player, or compatibility across saves/builds. Global date, the human manager's club and the complete squad/roster remain unresolved. Candidate probing must remain bounded; a UID/name match alone is insufficient without type validation, readable-object checks and explicit unknown results for failed fields. Addresses and object validity must be reacquired or invalidated across save/lifecycle changes.

These are attributed FA/user observations, not FMAPI runtime tests. The user has indicated rights to their own code, but FA's licensing/dependency cleanup (including the `rfc3987` dependency chain) remains a separate task. No new FA lookup implementation is copied under this update. Reuse code only after its provenance and applicable licensing are confirmed; directly sourced, verified MIT upstream material remains the preferred starting point. The reported scaling is restricted to the explicitly identified attribute encoding, not all player fields.

## One implementation, separate consumers

The intended technical boundary is a small independent Windows match-reading component that both the eventual FMAPI adapter and FA can consume. This does not authorize extracting FA implementation. Prefer obtaining any reusable code directly from the pinned MIT FMMatchLens upstream, verifying its own notices and provenance. Separately identify FA changes and their applicable rights before considering reuse; unresolved material must stay out of MIT FMAPI. No project license change or publication is part of this decision. FMAPI must not reference the FA product, its routes, environment variables or JSON schema. The SDK must not expose native addresses, offsets, pooled buffers, or BepInEx types.

| Existing source responsibility | Shared adapter boundary | Kept outside the shared component |
| --- | --- | --- |
| `GamePluginBuildCatalog`, `Offsets` | Exact binary fingerprint, build-specific layout and source identity | Product UI and broad cross-version promises |
| `MemoryReader`, `VirtualMemory`, UID readers/caches | Checked reads, readable-region validation, object identity and lifetime | FA endpoints and file output |
| `GameMatchTickHook`, tick/frame buffers | One owner of the detour, capture and bounded delivery | Third-party mod callbacks inside the native hook |
| `Domain` records and metadata decoding | Minimal pointer-free match/team/player values with explicit unknowns | Unverified rating/momentum/season fields unless separately justified |
| `RealtimeMatchTimeline` sink methods | Small internal capture sink for begin/frame/metadata/end, with owned snapshots | FA `fa-match-snapshot/0.1` serialization, timers, file replacement and freshness routes |
| `Plugin.cs`, `PluginLogger` | Host-provided lifecycle/logging boundary | FA plugin identity, configuration and `FOOTBALL_ASSISTANT_MATCH_FILE` |

The table describes responsibilities, not a copy list. Do not import FA's vendored tree or local modifications on the assumption that an upstream MIT file licenses every change. After provenance is resolved, scope any permitted implementation to the user-checked match/stat/player subset and keep the rest explicitly unverified. UI nodes, active pages, screenshot/OCR and automated clicks are never data sources or fallbacks. Manual user comparison is validation evidence, not an implementation dependency or a copyright license.

## Technical observations to validate, not authorization to copy fixes

- `Start` rejects unknown `game_plugin.dll` hashes before detouring. Although the catalog constructs a fallback record, its false result must never authorize using the fallback RVA.
- The current source uses BepInEx `INativeDetour.CreateAndApply` and a permanent native trampoline. It identifies the older undo/call/redo trampoline path as unsafe with concurrent simulation calls. This records a technical concern; copying the FA fix requires resolving its provenance and license first.
- Current candidate pairing uses a 720-tick expected lead with tolerance and confirmation, not the older 360-tick assumption. This is build-specific evidence, not a global FM rule.
- The selected animated instance serializes original-call plus capture. Memory read scopes are refreshed after the original call. Keep native callback exception containment, bounded buffers and deferred diagnostics.
- The sink copies pooled player arrays before returning them. Public snapshots/events must own their data; neither cached pointers nor pooled arrays can escape their valid lifetime.
- Keep match epochs, end/reset behavior, duplicate/out-of-order/gap accounting and player identity invalidation. A missing frame or field must remain missing, not be fabricated or silently replaced by old data.
- Attribute decoding is field-specific: the inspected `ReadAttribute` returns a raw byte only when readable and at most 100, otherwise zero. For fields explicitly documented with the confirmed attribute scale, positive raw values are divided by 5, rounded and clamped to 1..20; zero/read failure maps to unknown. Preserve raw provenance and do not apply that transform to every numeric field, ability, money, height, dates or match statistics. Four checked attributes do not establish all attributes.

## Next extraction and runtime acceptance

First resolve the exact FA revision/license, compare any candidate code with the directly obtained upstream revision, and identify the rights for every local modification. Keep FA-source extraction paused until that review determines an authorized route; technical observation alone is insufficient. Retain original notices for any permitted reuse. Pure decoder fixtures must be owned/synthetic; do not copy FA test implementation or data under an assumed MIT license. A later authorized shared component may introduce the internal sink boundary without changing the FA product contract. Obtain a single hook ownership/lifecycle plan before replacing the active reader; never install a second competing hook alongside it.

Then run a separately authorized FMAPI adapter test against the same exact build: prove the host/adapter loads, the shared reader supplies a fresh internal match snapshot, checked values agree, and unload/reload or match changes do not retain stale pointers or callbacks. Record binary fingerprint, platform/storefront, reproduction steps and capability-level evidence in compatibility documentation. Until then the current BepInEx bridge remains an unavailable adapter host, even though FA has reported working reads.

The active FA task now owns out-of-match date/team-roster research. FMAPI does not take over that game process or repeat that investigation; its independent next work is source reconciliation and offline shared-decoder tests. BepInEx remains LGPL 2.1, separately from FMAPI and the reviewed FMMatchLens MIT code. Preserve each component's original notices and review packaging/source-access obligations before any distribution; no game assets or binary release are included here.

## Audit of this local FMAPI change

No FA reader implementation has been copied into the current FMAPI patch. SDK/Core compatibility edits, the unavailable adapter, BepInEx host/session and synthetic contracts were authored in this task before the FA source inspection. The host calls APIs checked against pinned official BepInEx source and external reference DLLs; it does not derive its implementation from FA's plugin. FA-derived content in this patch is limited to this document's attributed technical observations, source identifiers/hashes and reported validation findings, plus roadmap/compatibility links. No FA source files, reader implementation fragments, private snapshots or fixtures are included. This provenance review does not claim a comprehensive legal audit of the pre-existing FMAPI repository.

## Source snapshot identifiers

Read-only inspection hashes (SHA256), for reconciling later FA edits; these identify source files, not game binaries:

```text
GameMatchTickHook.cs      6D9CBEF1BD0951868C1993984377ADDC32842C6230FD5C143975F800D8EDF552
GamePluginBuildCatalog.cs 4D2218C8E9C388361F18DBFA894F1928D4491068467091F3A9817A6836C6F05B
MemoryReader.cs           0A8062906078986A7FAE5E771C6D7455F85051A81CFFD1E160A65DF5F59CE7F8
Offsets.cs                86582598D4C4358C5862422C3950B1B375D255458AD5C18660E37F20D3092737
PlayerUidReader.cs        E0E2B56A99F521C0FAFAE1140848738D059CB9B6071D367B48D4735EEF8F98EF
```
