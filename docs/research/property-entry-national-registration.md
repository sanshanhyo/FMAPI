> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property-entry lane: national-registration

## Authorized probe command

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'national-registration'
```

## Actual executed evidence

```text
{"lane": "national-registration", "mode": "static-property-candidates", "matches": 6, "truncated": false, "liveRecordsRead": 0, "entries": [{"name": "PlayersChangeRegistrationStatus", "literalIndex": 15167, "slotRvas": ["0x32c4398"], "semantics": "unverified-property-name"}, {"name": "PlayersChangeRegistrationStatusList", "literalIndex": 15168, "slotRvas": ["0x32c4488"], "semantics": "unverified-property-name"}, {"name": "RegisteredPlayers", "literalIndex": 16082, "slotRvas": ["0x32f7ce8"], "semantics": "unverified-property-name"}, {"name": "RegisteredPlayersCount", "literalIndex": 16083, "slotRvas": ["0x32f7de0"], "semantics": "unverified-property-name"}, {"name": "UnregisteredPlayers", "literalIndex": 21425, "slotRvas": ["0x32f0f48"], "semantics": "unverified-property-name"}, {"name": "UnregisteredPlayersCount", "literalIndex": 21426, "slotRvas": ["0x32f1038"], "semantics": "unverified-property-name"}]}
```

The probe read only the pinned static binary. It did not read process memory, records, UI, saves, or game state. `liveRecordsRead` is 0 and output was not truncated.

## Pinned source and hash

- Binary: `game_plugin.dll`
- SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- GameAssembly.dll SHA-256: `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`
- Metadata signature/version: `0xFAB11BAF` / v39
- PositionMask metadata SHA-256: `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`

## Property candidates

All six returned names are `unverified-property-name` values. They may refer to UI, news, operations, caches, views, or business state. None is proven to be a business field, and no native key, dispatch RVA, entry function, target, offset, instance layout, UID linkage, or live field has been recovered.

Ranked next registrations to inspect:

1. `RegisteredPlayersCount` (literal index 16083, slot `0x32f7de0`)
2. `UnregisteredPlayersCount` (literal index 21426, slot `0x32f1038`)
3. `RegisteredPlayers` (literal index 16082, slot `0x32f7ce8`)
4. `UnregisteredPlayers` (literal index 21425, slot `0x32f0f48`)
5. `PlayersChangeRegistrationStatus` (literal index 15167, slot `0x32c4398`)
6. `PlayersChangeRegistrationStatusList` (literal index 15168, slot `0x32c4488`)

The read-only count names are ranked first because they are the cheapest to compare against a known registration list. The collection names follow. The `PlayersChange...` names are ranked last because their names resemble commands or operation payloads rather than read-only fields.

## Coordinator evidence used to sharpen this lane

- Current club count 2: both TEAM pointers match their TEAM_BASE low23-bit index entries (`2/2`).
- `NextFixture` (literal index 13696, slot `0x330b698`, native key `0x6e654669`) first resolves TEAM_BASE context via global `0x5703768`, not a fixture object.

Implication: property names and apparent targets can resolve to a different context. The six national-registration property names therefore remain names only. No business field, native key, dispatch RVA, entry function, or target is inferred from them, and `NextFixture`'s proven key is not transferred to any candidate.

## UI/news/operations versus business fields

- `PlayersChangeRegistrationStatus` and `PlayersChangeRegistrationStatusList`: operation-like names; likely command or UI action inputs, not proven business fields.
- `RegisteredPlayers` and `UnregisteredPlayers`: collection-like names; may be views, caches, operation results, or UI lists, not proven business fields.
- `RegisteredPlayersCount` and `UnregisteredPlayersCount`: scalar-like names; may be derived counts, UI counters, or business state, not proven business fields.

No candidate is marked as a business field. All native keys, offsets, entry functions, dispatch RVAs, targets, contexts, layouts, and field semantics remain null or unavailable.

## Next bounded request

No live request is genuinely supported by the current evidence. Static inspection of the six slot RVAs in the pinned binary must come first to identify each property registration block, native key, dispatch RVA, and readable target. Only if one of those slots resolves to a documented readable scalar or collection target may a bounded read-only live capture of that target be requested for a loaded save with known registration counts. All outputs must remain outside the repository, and all fingerprint, bounds, and safety checks must fail closed.

No writes, game/UI access, native calls, network access, process reads, private capture access, or SDK behavior are involved. This document records research evidence only.

## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
