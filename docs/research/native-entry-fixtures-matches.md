> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry evidence: fixtures and matches

Task lane: FIX-01 / CMP-01 / MAT-01 / MAT-02 native-entry follow-up. This note records the coordinator-approved static probe result for the `fixtures-matches` lane and converts it into a narrow, fail-closed business-object entry hypothesis. It does not claim a fixture reader, match reader, competition reader, live read, or compatibility support.

## Executed probe

Command:

```text
& 'pwsh' -NoProfile -File '.../run-lane-probe.ps1' -Lane 'fixtures-matches'
```

Result:

```text
{"lane":"fixtures-matches","mode":"static-pinned-file","types":3,"vtables":1,"liveRecordsRead":0,"outputTruncated":false}
SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F ImageBase 0x180000000
TYPE 0x569DDB0 .?AVEXTERN_FIXTURE_RECORD@db@@
TYPE 0x56A1DB0 .?AVFIXTURE_RECORD@db@@
TYPE 0x56CE100 .?AV?$OBJECT_TRANSLATABLE@PEBVFIXTURE_RECORD@db@@@sitranslation@@
VTABLE 0x4CB2808 .?AVFIXTURE_RECORD@db@@ slots=0xDCEA10,0x2767D90,0xEF2630,0x414370,0x414380,0x414390,0x4143A0,0xDCEA70,0x2767A20,0xEF3880,0x4143D0,0x4143E0
RIP_CANDIDATE displacement=0xD6B6B0 function=0xD6B490 target=0x4CB2808 .?AVFIXTURE_RECORD@db@@
RIP_CANDIDATE displacement=0xD79196 function=0xD789B0 target=0x4CB2808 .?AVFIXTURE_RECORD@db@@
RIP_CANDIDATE displacement=0x2766FE1 function=0x2766FB0 target=0x4CB2808 .?AVFIXTURE_RECORD@db@@
RIP_CANDIDATE displacement=0x30F9EAF function=0x30E4F50 target=0x4CB2808 .?AVFIXTURE_RECORD@db@@
RIP_CANDIDATE displacement=0x310BB16 function=0x30E4F50 target=0x4CB2808 .?AVFIXTURE_RECORD@db@@
RIP_CANDIDATE displacement=0x3DCFFDB function=0x3DCFF00 target=0x4CB2808 .?AVFIXTURE_RECORD@db@@
```

All addresses are module-relative RVAs against image base `0x180000000`. The probe read no process memory and no fixture records.

## Confirmed type and vtable evidence

| Evidence | RVA | Meaning |
|---|---:|---|
| `.?AVEXTERN_FIXTURE_RECORD@db@@` | `0x569DDB0` | External fixture-record variant; confirms fixture is a DB record family. |
| `.?AVFIXTURE_RECORD@db@@` | `0x56A1DB0` | Core fixture record RTTI type. |
| `.?AV?$OBJECT_TRANSLATABLE@PEBVFIXTURE_RECORD@db@@@sitranslation@@` | `0x56CE100` | Translation wrapper around a pointer to a const fixture record; indicates a display/translation boundary, not a field layout. |
| `.?AVFIXTURE_RECORD@db@@` vtable | `0x4CB2808` | 12 slots: `0xDCEA10,0x2767D90,0xEF2630,0x414370,0x414380,0x414390,0x4143A0,0xDCEA70,0x2767A20,0xEF3880,0x4143D0,0x4143E0`. |
| RIP candidates | `0xD6B490`, `0xD789B0`, `0x2766FB0`, `0x30E4F50`, `0x30E4F50`, `0x3DCFF00` | Functions referencing the fixture-record vtable. Displacements: `0xD6B6B0`, `0xD79196`, `0x2766FE1`, `0x30F9EAF`, `0x310BB16`, `0x3DCFFDB`. |

No field offsets, collection offsets, UID offsets, vtable slot semantics, or record sizes were confirmed by this probe.

## Narrow business-object entry hypothesis

`FIXTURE_RECORD@db` is a native fixture business object / database record. The adjacent `EXTERN_FIXTURE_RECORD` and `OBJECT_TRANSLATABLE<...FIXTURE_RECORD...>` types suggest a fixture record can be represented as an external DB record and passed through a translation/display boundary, but they do not establish serialization, field layout, or ownership.

The six RIP candidates are candidate entry points into fixture-record lifetime or use because each references the fixture-record vtable. They are not classified as constructor, lookup, iterator, formatter, or reader entry points. Their exact roles require disassembly and, later, a coordinator-approved read-only capture.

This is an entry scaffold only. It is not an SDK contract, not a live reader, and not a field decoder.

## Exact missing semantics

- Fixture stable UID and fixture-versus-match identity.
- Home team, away team, and neutral-venue semantics.
- Competition, season, stage, round, and group references.
- Calendar date, kick-off time, timezone, and game-calendar meaning.
- Venue / stadium reference.
- Status enum and score entry, including extra time and penalties.
- Collection route and count bounds for fixture records.
- Relationship from fixture record to match result, appearance, and statistics records.
- Whether `EXTERN_FIXTURE_RECORD` differs in layout or ownership from `FIXTURE_RECORD`.
- Vtable slot meaning and any constructor/destructor or factory entry point.
- Competition, season, table, draw, result, appearance, rating, and statistic record types: no matching types were reported by this probe.

## No-match and proposed narrower names

The probe reported no match, competition, season, standing, appearance, rating, or statistics RTTI type. The following names are proposed search targets only; they are not confirmed and must not be treated as live readers or field layouts:

- `MATCH_RECORD` -> proposed narrower names: `MATCH_RESULT_RECORD`, `MATCH_REPORT_RECORD`, `MATCH_STATISTICS_RECORD`.
- `COMPETITION_RECORD` -> proposed narrower names: `COMPETITION_SEASON_RECORD`, `COMPETITION_STAGE_RECORD`, `COMPETITION_TABLE_RECORD`.
- `STANDING_RECORD` -> proposed narrower names: `LEAGUE_TABLE_ROW`, `GROUP_STANDING_ROW`.
- `APPEARANCE_RECORD` -> proposed narrower names: `MATCH_APPEARANCE_ROW`, `PLAYER_MATCH_ROW`.

## Next bounded read request

Request a later coordinator-approved, read-only process probe with these bounds:

- Start from the already validated current manager/club/team context.
- Locate at most one fixture collection edge and read at most 32 fixture entries.
- Read one upcoming fixture and one recent fixture if available.
- Record only candidate fields that can be cross-checked against the schedule UI: fixture UID, team references, competition reference, date/time, venue, home/away, status, and score.
- Aggregate capture budget: 64 KiB.
- Repeat the read twice and compare values; mark any field absent if it cannot be cross-checked.
- Do not advance the date, create or replay a match, invoke game functions, write memory, or read private samples.
- Do not attempt match, competition, table, or statistics reads until a fixture record type or collection route is independently confirmed.

## Limits

- This evidence is static and pinned to SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`.
- RTTI names and vtable addresses are structural evidence only. They are not field layouts, not call semantics, and not SDK APIs.
- The machine-readable companion is `tools/research/entry_fixtures_matches.py`.
- No live reader was created.

## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
