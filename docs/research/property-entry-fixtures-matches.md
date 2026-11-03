> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property-entry evidence: fixtures and matches

Task lane: FIX-01 / CMP-01 / MAT-01 / MAT-02 property-candidate follow-up. This note records the executed static property probe for the `fixtures-matches` lane and converts its two returned candidates into a bounded property-to-entry manifest. It does not claim a fixture reader, match reader, competition reader, live read, or compatibility support.

## Executed probe

Command:

```text
& 'pwsh' -NoProfile -File '.../run-lane-property-probe.ps1' -Lane 'fixtures-matches'
```

Result:

```json
{"lane":"fixtures-matches","mode":"static-property-candidates","matches":2,"truncated":false,"liveRecordsRead":0,"entries":[{"name":"FixtureDate","literalIndex":8701,"slotRvas":["0x3325e28"],"semantics":"unverified-property-name"},{"name":"NextFixture","literalIndex":13696,"slotRvas":["0x330b698"],"semantics":"unverified-property-name"}]}
```

The probe read no process memory and no fixture records. `liveRecordsRead` is 0.

## Source and hash

- Pinned binary: `game_plugin.dll`, SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`.
- Image base: `0x180000000`.
- Metadata signature/version used by related evidence: `0xFAB11BAF` / 39.
- Companion machine-readable manifest: `tools/research/property_entry_fixtures_matches.py`.
- Related native-entry evidence: `docs/research/native-entry-fixtures-matches.md`.

## Actual returned candidates

| Property | Literal index | Encoded slot RVA | Probe semantics |
|---|---:|---:|---|
| `FixtureDate` | 8701 | `0x3325e28` | `unverified-property-name` |
| `NextFixture` | 13696 | `0x330b698` | `unverified-property-name` |

Both are structural candidates only. Neither has a proven native key, field offset, registration function, record size, or collection route.

## UI/news/operations versus business fields

| Name | Hypothesis | Evidence |
|---|---|---|
| `FixtureDate` | Possible business field (fixture date), unverified | Name only. No registration context, native key, offset, or live comparison proves it. |
| `NextFixture` | Likely operations/UI/team-context candidate, not a proven fixture business field | Coordinator evidence: the reported native key for this slot first resolves `TEAM_BASE` context via global `0x5703768`, not a fixture record. |

The two names do not by themselves establish business fields. `FixtureDate` remains unclassified. `NextFixture` is sharpened by coordinator evidence toward team context and therefore should not be treated as a fixture-record entry point.

## Native keys and offsets

- Native keys remain `null` in the manifest.
- Field offsets remain `null` in the manifest.
- Coordinator-reported evidence for `NextFixture` records native key `0x6E654669` and global `0x5703768`, but that is attributed evidence only. It is not converted into a proven key, offset, or callable function in this repository.

## Ranked next registrations to inspect

1. `0x3325e28` (`FixtureDate`, literal 8701): inspect its GameAssembly registration and disassembly first to determine whether it is a business field or UI/news/operations.
2. `0x330b698` (`NextFixture`, literal 13696): inspect its registration second to confirm that it is team-context/UI/operations rather than a fixture business field.

No function RVAs are fabricated. The slot RVAs above are the only concrete registration locators.

## One precise next bounded live request

Only if coordinator-authorized and only for team-context confirmation, not for fixture data:

- Read only the pointer-sized value at global RVA `0x5703768` in the pinned binary.
- Maximum 8 bytes, repeated twice, with pointer and RTTI rechecks between reads.
- Verify that the resolved object has the `TEAM_BASE` RTTI expected by the coordinator evidence.
- Compare the result with the already validated current club/team backlinks; mark unavailable on any mismatch.
- Do not call game functions, advance dates, create or replay matches, read fixture records, read private samples, or access network/UI.

No additional live request is supported for `FixtureDate` until its registration is statically classified.

## Limits

- This evidence is static and pinned to SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`.
- Property names and slot RVAs are not field layouts, call semantics, or SDK APIs.
- No live reader was created and no process was accessed.
- Writes, game/UI/native calls, network, and private capture access remain prohibited.
