> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property entry: manager-club

## Actual executed probe evidence

Command run once, read-only, static pinned metadata property probe, no process memory or live records:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'manager-club'
```

Returned result:

```json
{"lane":"manager-club","mode":"static-property-candidates","matches":4,"truncated":false,"liveRecordsRead":0,"entries":[
 {"name":"FirstTeamPlayers","literalIndex":8681,"slotRvas":["0x3324c50"],"semantics":"unverified-property-name"},
 {"name":"GameCurrentManager","literalIndex":9070,"slotRvas":["0x333ad88"],"semantics":"unverified-property-name"},
 {"name":"PlayerTeams","literalIndex":15141,"slotRvas":["0x32c2a90"],"semantics":"unverified-property-name"},
 {"name":"TeamType","literalIndex":19072,"slotRvas":["0x3306998"],"semantics":"unverified-property-name"}
]}
```

- Lane: `manager-club`
- Mode: `static-property-candidates`
- Matches: 4
- Truncated: false
- Live records read: 0
- Source binary hashes:
  - `game_plugin.dll`: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
  - `GameAssembly.dll`: `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`
  - metadata: `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`
- The probe printed property names, literal indices and encoded slots only. It did not prove property semantics, native keys, offsets, entries, or live availability.

## Property candidates and classification

| Rank | Name | Literal index | Slot RVA | Native key | Classification | Refers to |
|---|---|---:|---|---|---|---|
| 1 | GameCurrentManager | 9070 | 0x333AD88 | 0x4743754D (proven) | business-selection-field | business field: current selected human manager identity and employment chain |
| 2 | FirstTeamPlayers | 8681 | 0x3324C50 | 0x78754F31 (coordinator evidence) | ui-or-tactics-handler-candidate | operations/UI candidate: name suggests a roster, but dispatcher 0x628FC0 belongs to tactic UI handlers, so it is not a direct TEAM roster vector |
| 3 | TeamType | 19072 | 0x3306998 | null (unproven) | unverified-business-candidate | unverified candidate: name suggests team classification, but no key, offset, entry, or UI/news/operations evidence is established |
| 4 | PlayerTeams | 15141 | 0x32C2A90 | null (unproven) | unverified-business-candidate | unverified candidate: name suggests a player-to-teams relation, but no key, offset, entry, or UI/news/operations evidence is established |

Key interpretation notes:

- `GameCurrentManager` is a business field, not a UI/news/operations field. Its named-property registration is paired with native key `GCuM` (`0x4743754D`) at RVA `0x4F9DE0`, dispatches at `0x380020`, and controls selected-record global `0x56F32C8`. It remains current-selected-manager evidence only; it is not a general multiplayer/hotseat authority claim.
- `FirstTeamPlayers` sounds like a business roster field, but the available coordinator evidence says its dispatcher `0x628FC0` belongs to tactic UI handlers. Therefore it must be treated as a UI/operations candidate until a separate registration proof shows a direct TEAM roster vector. It must not be used as roster evidence.
- `TeamType` and `PlayerTeams` have no established classification. Their names alone do not establish business, UI, news, or operations meaning.
- `NextFixture` is not one of the four returned property candidates. Coordinator evidence for this wave says literal 13696 / slot `0x330B698` / key `0x6E654669` first resolves `TEAM_BASE` context through global `0x5703768`, not a fixture collection. Treat it as a team-context/operations candidate, not a fixture list. This sharpens the lane: team-context properties may masquerade as fixture or roster properties.

## Ranked next registrations to inspect

1. `GameCurrentManager` metadata literal 9070 / slot RVA `0x333AD88`; native dispatch `0x380020`; selected global `0x56F32C8`; getters `0x378FC0` and `0x3810B0`. Recheck only; no new property claim.
2. `FirstTeamPlayers` metadata literal 8681 / slot RVA `0x3324C50`; key `0x78754F31`; dispatcher `0x628FC0`. Classify the dispatcher before any roster or team-hierarchy claim.
3. Confirmed `TEAM` RTTI at `0x56A2A60` and vtable `0x4CE1108` as the comparison shape for any future roster/team-type property.
4. `TeamType` metadata literal 19072 / slot RVA `0x3306998`; find its registration block and any native key.
5. `PlayerTeams` metadata literal 15141 / slot RVA `0x32C2A90`; find its registration block and any native key.
6. `NextFixture` metadata literal 13696 / slot RVA `0x330B698`; key `0x6E654669`; global `0x5703768`; prove whether it exposes team context or any fixture relation.

## Exact missing semantics

- Native keys for `TeamType` and `PlayerTeams`.
- Field offsets for every property and every confirmed entry.
- Target RTTI/vtable entry for `GameCurrentManager`, `FirstTeamPlayers`, `TeamType` and `PlayerTeams`.
- Whether `FirstTeamPlayers` has any non-UI roster meaning.
- Whether `TeamType` or `PlayerTeams` are business, UI, news, or operations fields.
- Vtable slot semantics and method identities for all registration blocks.
- Live object availability, registry reference integrity, and snapshot consistency.

## Machine-readable manifest

`tools/research/property_entry_manager_club.py` emits the four-candidate manifest and validates candidate input. Unproven keys, offsets, target entries, functions and live values remain null or absent. Run:

```text
python tools/research/property_entry_manager_club.py --self-test
```

## One precise next bounded live request

Only `GameCurrentManager` already has a supported bounded live path. Run the existing minimal selection/employment capture in one stable loaded session with the 64 KiB capture budget and two fresh captures, rechecking global `0x56F32C8`, the matching `HUMAN_NON_PLAYER` PERSON RTTI, one owner match, person UID, contract kind and club UID token. Do not add live reads for `FirstTeamPlayers`, `TeamType`, or `PlayerTeams` until their registration blocks and native keys are proven. No UI, game call, network, private capture, write, or match/date advance is requested. If the selection is absent, unmatched, duplicated or changed, return unavailable rather than a substituted value.
## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
