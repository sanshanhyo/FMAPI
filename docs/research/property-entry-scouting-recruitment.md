> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property entry scouting: scouting-recruitment

Lane: `scouting-recruitment`
Probe mode: `static-property-candidates`
Probe command run once:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'scouting-recruitment'
```

Probe summary: `matches=8`, `truncated=false`, `liveRecordsRead=0`.

Pinned fingerprints:

- `game_plugin.dll`: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- `GameAssembly.dll`: `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`
- Image base: `0x180000000`

## Actual executed property candidates

| Property name | Literal index | Encoded slot RVAs | Probe semantics |
|---|---:|---|---|
| `CanViewCoachScoutReport` | 4398 | `0x32ccf50` | `unverified-property-name` |
| `MainSourceOfScoutKnowledgeClub` | 12508 | `0x32c8478` | `unverified-property-name` |
| `MainSourceOfScoutKnowledgePerson` | 12509 | `0x32c8558` | `unverified-property-name` |
| `MainSourceOfScoutKnowledgeType` | 12510 | `0x32c8648` | `unverified-property-name` |
| `ScoutReportSpeakTo` | 16786 | `0x331fd98` | `unverified-property-name` |
| `ScoutReportStrengths` | 16787 | `0x331fe70` | `unverified-property-name` |
| `ScoutReportWeaknesses` | 16788 | `0x331ff50` | `unverified-property-name` |
| `scoutnewssinglematchscoutreport` | 29528 | `0x32ec1a0` | `unverified-property-name` |

## Classification of names

| Property name | Classification | Interpretation |
|---|---|---|
| `CanViewCoachScoutReport` | view capability / UI permission | Capability gate; not a scout report business field. |
| `MainSourceOfScoutKnowledgeClub` | business field candidate | Possible source-club field; ownership, UID linkage, and offset are unproven. |
| `MainSourceOfScoutKnowledgePerson` | business field candidate | Possible source-person field; no staff/person UID or collection is proven. |
| `MainSourceOfScoutKnowledgeType` | business field candidate | Possible source-type discriminator; enum values are unproven. |
| `ScoutReportSpeakTo` | operation or message candidate | Likely action/recipient surface; do not treat as report content yet. |
| `ScoutReportStrengths` | business field candidate | Possible report-content field; storage shape and owner are unproven. |
| `ScoutReportWeaknesses` | business field candidate | Possible report-content field; storage shape and owner are unproven. |
| `scoutnewssinglematchscoutreport` | news presentation | Likely inbox/news surface; not proof of a standalone report entity. |

## Evidence limits

The probe returned metadata property names, literal indices, and encoded slot RVAs only. It did not read live records, invoke functions, resolve native property keys, establish owner types, or expose offsets. The slot RVAs are registration/encoded slots, not proven native keys, function RVAs, RTTI RVAs, vtable addresses, or field offsets. No collection owner, mount point, count, pagination, status transition, or business semantics is established.

`tools/research/property_entry_scouting_recruitment.py` keeps `nativeKey`, `nativeFunctionRva`, `rttiRva`, and `vtableAddress` null; `fields` and `offsets` empty; `semantics` unknown; and `liveReader` false. Its validator rejects fabricated keys, offsets, unknown candidates, and live-reader claims.

## Coordinator dependency sharpening

New coordinator evidence states that current club team pointers match their `TEAM_BASE` low 23-bit index entries (2/2), while `NextFixture` literal 13696 slot `0x330B698` with native key `0x6E654669` first resolves `TEAM_BASE` context through global `0x5703768`, not fixtures. Therefore, any future scouting property inspection must first establish the current club/team context through global `0x5703768`. The `NextFixture` literal must not be used as the context source. Property native keys remain null until a separate proof links them to that context.

## Next bounded request

No live request is currently supported. The returned property candidates do not yet have proven native keys, owner context, offsets, or collection boundaries, so reading them in a live process would be unsupported.

The next approved request is static only: perform a bounded xref scan of the eight slot RVAs and literal indices in `GameAssembly.dll`/`game_plugin.dll`, limited to the module and reporting referencing functions plus nearby string literals. No process memory, game functions, UI, writes, network, or private captures may be used.

If coordinator approval is later given for a live read, it must be a separate request with fail-closed fingerprint checks, a budget of at most 64 KiB, current club/team resolution through global `0x5703768`, raw and decoded values kept separate, and all unknowns retained as unknown. It still may not use offsets or native keys that are not yet proven.

This is research tooling, not an SDK. It does not claim game, platform, or SDK compatibility.

## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
