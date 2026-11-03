> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property-entry evidence: player-position-state

Status: offline static evidence only. The only executed probe is the coordinator-approved
read-only command recorded below. No process, game file, native function, UI, network
access, match advance, save mutation or private capture read was performed.

## 1. Executed probe evidence

Command (run once, exactly as authorized):

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'player-position-state'
```

Result:

```json
{"lane":"player-position-state","mode":"static-property-candidates","matches":7,"truncated":false,"liveRecordsRead":0,"entries":[{"name":"Fatigue","literalIndex":8408,"slotRvas":["0x3315580"],"semantics":"unverified-property-name"},{"name":"PlayerConditionsList","literalIndex":14998,"slotRvas":["0x32ba2e8"],"semantics":"unverified-property-name"},{"name":"Sharpness","literalIndex":17463,"slotRvas":["0x32aace8"],"semantics":"unverified-property-name"},{"name":"SharpnessStatusDescription","literalIndex":17464,"slotRvas":["0x32aadb8"],"semantics":"unverified-property-name"},{"name":"_DirectionalBrightnessSharpness","literalIndex":22863,"slotRvas":["0x32a76c8"],"semantics":"unverified-property-name"},{"name":"_Sharpness","literalIndex":23449,"slotRvas":["0x32c9568"],"semantics":"unverified-property-name"},{"name":"_SunRaysSharpness","literalIndex":23582,"slotRvas":["0x32d0af8"],"semantics":"unverified-property-name"}]}
```

Source and hash:

- Native profile: `game_plugin.dll` SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Probe mode: `static-property-candidates`
- Returned candidates: 7
- `truncated`: false
- `liveRecordsRead`: 0
- Related native-entry evidence: `docs/research/native-entry-player-position-state.md`
- Related player-position evidence: `docs/research/native-entity-evidence.md`

## 2. Returned candidates

| Rank | Name | Literal index | Slot RVA | Semantics |
|---:|---|---:|---|---|
| 1 | `Fatigue` | 8408 | `0x3315580` | `unverified-property-name` |
| 2 | `PlayerConditionsList` | 14998 | `0x32ba2e8` | `unverified-property-name` |
| 3 | `Sharpness` | 17463 | `0x32aace8` | `unverified-property-name` |
| 4 | `SharpnessStatusDescription` | 17464 | `0x32aadb8` | `unverified-property-name` |
| 5 | `_DirectionalBrightnessSharpness` | 22863 | `0x32a76c8` | `unverified-property-name` |
| 6 | `_Sharpness` | 23449 | `0x32c9568` | `unverified-property-name` |
| 7 | `_SunRaysSharpness` | 23582 | `0x32d0af8` | `unverified-property-name` |

These are property-name/literal/slot candidates only. No getter, native key, offset, function, enum, or object layout is established.

## 3. UI/news/operations versus business fields

Classification is by name and probe context only. It is not a proven field classification.

| Name | Tentative domain | Why |
|---|---|---|
| `Fatigue` | business-field candidate | Could name a player condition, but it may also be a UI/news/operations label. No offset, key, getter or UI comparison exists. |
| `PlayerConditionsList` | ui/news/operations | List-shaped name; likely an aggregate, list or UI surface rather than one scalar business field. |
| `Sharpness` | business-field candidate | Could name match sharpness, but the word is also used by rendering properties. Unproven. |
| `SharpnessStatusDescription` | ui/news/operations | `Description` suffix indicates text/status UI, not a numeric business field. |
| `_DirectionalBrightnessSharpness` | ui/news/operations | Leading underscore and rendering words indicate a graphics property. |
| `_Sharpness` | ui/news/operations | Underscore-prefixed `Sharpness` is more likely a rendering control than player sharpness. |
| `_SunRaysSharpness` | ui/news/operations | Sun-rays wording indicates lighting/rendering, not a business field. |

Coordinator evidence used to sharpen this lane:

- Current club 2 TEAM pointers match their TEAM_BASE low 23-bit index entries 2/2.
- `NextFixture` (literal 13696, slot `0x330B698`, native key `0x6E654669`) first resolves TEAM_BASE context through global `0x5703768`, not fixtures.

This shows that property names can mislead. Therefore every returned name above remains a candidate. `Fatigue` and `Sharpness` are ranked first only because they are the most plausible condition-related business names, not because they are validated.

## 4. Native keys and offsets

All of the following are intentionally null or unproven:

- native property key
- property getter RVA
- entry function RVA
- object offset
- field semantics
- UI/news/operations/business classification beyond name-based candidate status

`tools/research/property_entry_player_position_state.py` rejects manifests that populate any native key, offset, getter or function field.

## 5. Ranked next registrations to inspect

1. `Fatigue` (literal 8408, slot `0x3315580`) - most plausible player-condition candidate.
2. `Sharpness` (literal 17463, slot `0x32aace8`) - second plausible condition candidate, but confusable with rendering sharpness.
3. `PlayerConditionsList` (literal 14998, slot `0x32ba2e8`) - may expose condition aggregation or UI list structure.
4. `SharpnessStatusDescription` (literal 17464, slot `0x32aadb8`) - useful for UI text mapping only after the numeric field is proven.
5. `_Sharpness` (literal 23449, slot `0x32c9568`) - likely rendering; inspect only to rule out confusion with match sharpness.
6. `_DirectionalBrightnessSharpness` (literal 22863, slot `0x32a76c8`) - rendering property.
7. `_SunRaysSharpness` (literal 23582, slot `0x32d0af8`) - rendering property.

## 6. Exact missing semantics

- Whether any candidate is a real property registration or merely a literal/slot reference.
- Native property key for each candidate.
- Registration/dispatch path and function role.
- Getter RVA and calling convention.
- Object offset and value type.
- Whether `Fatigue` and `Sharpness` refer to player condition, UI label, news text or another concept.
- Whether `PlayerConditionsList` is business state or a UI/news/operations list.
- Value range, scaling, update timing and display semantics.
- Relationship to roster, team, club, match, tactic, availability, injury and UI.

## 7. Next bounded request

No live request is genuinely supported by the current evidence. The next request should remain offline and bounded:

1. Offline static inspection of the property registrations for `Fatigue` and `Sharpness` using the pinned `game_plugin.dll`, including instruction boundaries and direct call targets.
2. Only if that inspection proves a safe getter/offset path, request a later bounded live read of at most 32 already validated `ACTUAL_PLAYER` entries under the existing 64 KiB capture budget.
3. Validate each candidate separately against the same-save UI. Keep unknown where no comparison exists; do not map one value onto another concept.

## 8. Machine-readable scaffold

`tools/research/property_entry_player_position_state.py` implements the manifest and validator for this evidence. It contains only the seven returned candidate names, literal indices and slot RVAs. It rejects unsupported native hashes, invented offsets, invented native keys, unreturned property names, unconfirmed classifications and fabricated functions. Run:

```text
python tools/research/property_entry_player_position_state.py --self-test
```

## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
