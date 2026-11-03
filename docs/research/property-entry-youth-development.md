> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Youth-development property entry

## Scope

Offline static evidence only. No process, game, UI, network, live read, write, or save access occurred for this document. All RVAs apply only to the pinned `game_plugin.dll` SHA-256 below. This is a property-to-entry manifest for the actual candidates returned by the authorized property probe; it is not an SDK, adapter, or live reader.

## Probe execution

Command executed once, exactly as authorized:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'youth-development'
```

Result:

```json
{"lane":"youth-development","mode":"static-property-candidates","matches":15,"truncated":false,"liveRecordsRead":0,"entries":[{"name":"DaysUntilYouthIntake","literalIndex":6579,"slotRvas":["0x32ace90"],"semantics":"unverified-property-name"},{"name":"HighestLevelYouthTeam","literalIndex":9941,"slotRvas":["0x32d1650"],"semantics":"unverified-property-name"},{"name":"SecondHighestLevelYouthTeam","literalIndex":16963,"slotRvas":["0x3329d88"],"semantics":"unverified-property-name"},{"name":"YouthIntakeDescription","literalIndex":22257,"slotRvas":["0x33205e8"],"semantics":"unverified-property-name"},{"name":"YouthIntakeFeedbackString","literalIndex":22258,"slotRvas":["0x33206d0"],"semantics":"unverified-property-name"},{"name":"YouthIntakeGrade","literalIndex":22259,"slotRvas":["0x33207b8"],"semantics":"unverified-property-name"},{"name":"YouthIntakeLevel","literalIndex":22260,"slotRvas":["0x3320898"],"semantics":"unverified-property-name"},{"name":"YouthIntakePositionPreviews","literalIndex":22261,"slotRvas":["0x3320970"],"semantics":"unverified-property-name"},{"name":"YouthIntakeRating","literalIndex":22262,"slotRvas":["0x3320a50"],"semantics":"unverified-property-name"},{"name":"YouthIntakeStatus","literalIndex":22263,"slotRvas":["0x3320b30"],"semantics":"unverified-property-name"},{"name":"YouthTeam","literalIndex":22276,"slotRvas":["0x3321668"],"semantics":"unverified-property-name"},{"name":"YouthTeam3","literalIndex":22277,"slotRvas":["0x3321748"],"semantics":"unverified-property-name"},{"name":"YouthTeam4","literalIndex":22278,"slotRvas":["0x3321838"],"semantics":"unverified-property-name"},{"name":"YouthTeam5","literalIndex":22279,"slotRvas":["0x3321920"],"semantics":"unverified-property-name"},{"name":"YouthTeams","literalIndex":22280,"slotRvas":["0x3321a08"],"semantics":"unverified-property-name"}]}
```

Pinned binary:

- SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Mode: `static-property-candidates`
- Matches: `15`
- Truncated: `false`
- Live records read: `0`

## Candidate classification

The probe names are unverified strings. Based on names only, they split as follows; none has a proven native key, offset, function RVA, field type, or slot meaning.

| Property name | Literal index | Slot RVA | Classification |
|---|---:|---|---|
| YouthTeams | 22280 | 0x3321a08 | team-context-candidate |
| YouthTeam | 22276 | 0x3321668 | team-context-candidate |
| YouthTeam3 | 22277 | 0x3321748 | team-context-candidate |
| YouthTeam4 | 22278 | 0x3321838 | team-context-candidate |
| YouthTeam5 | 22279 | 0x3321920 | team-context-candidate |
| HighestLevelYouthTeam | 9941 | 0x32d1650 | team-context-candidate |
| SecondHighestLevelYouthTeam | 16963 | 0x3329d88 | team-context-candidate |
| YouthIntakeRating | 22262 | 0x3320a50 | business-field-candidate |
| YouthIntakeGrade | 22259 | 0x33207b8 | business-field-candidate |
| YouthIntakeLevel | 22260 | 0x3320898 | business-field-candidate |
| DaysUntilYouthIntake | 6579 | 0x32ace90 | operations-candidate |
| YouthIntakeStatus | 22263 | 0x3320b30 | operations-candidate |
| YouthIntakeDescription | 22257 | 0x33205e8 | ui-or-news-candidate |
| YouthIntakeFeedbackString | 22258 | 0x33206d0 | ui-or-news-candidate |
| YouthIntakePositionPreviews | 22261 | 0x3320970 | ui-or-news-candidate |

Interpretation:

- Team-named properties are treated as team-context candidates, not confirmed youth business objects.
- Grade/level/rating names are business-field candidates only by name; their value types and owners are unverified.
- Days/count/status names are operations/UI-facing candidates.
- Description/feedback/preview names are UI/news candidates, not business fields.

## Coordinator evidence used to sharpen this lane

- Current club's 2 TEAM pointers match their TEAM_BASE low 23-bit index entries: `2/2`.
- `NextFixture` (literal index `13696`, slot RVA `0x330B698`, native key `0x6E654669`) first resolves TEAM_BASE context via global `0x5703768`, not fixtures.
- Source: coordinator evidence; not independently verified in this worktree.

Implication: a property name containing "Team" or "Fixture" does not establish the returned business object. Youth team properties are ranked first for inspection so their registrations can be checked against the same TEAM_BASE context path before any field is decoded.

## Machine-readable companion

`tools/research/property_entry_youth_development.py` contains the same 15 candidates, classifications, ranked next registrations, coordinator evidence, manifest builder, and validator. It keeps native keys, offsets, function RVAs, and field types null.

## Ranked next registrations

1. YouthTeams
2. YouthTeam
3. YouthTeam3
4. YouthTeam4
5. YouthTeam5
6. HighestLevelYouthTeam
7. SecondHighestLevelYouthTeam
8. YouthIntakeRating
9. YouthIntakeGrade
10. YouthIntakeLevel
11. DaysUntilYouthIntake
12. YouthIntakeStatus
13. YouthIntakeDescription
14. YouthIntakeFeedbackString
15. YouthIntakePositionPreviews

## Next bounded live request

One precise request, subject to coordinator approval:

Read-only, bounded probe of global RVA `0x5703768` and the TEAM_BASE low 23-bit index entries for at most the two current-club TEAM pointers, plus a small raw prefix per entry. Requirements: process recheck before and after, aggregate read budget no greater than 64 KiB, no writes, no UI, no match advancement, no save changes, no native calls, no network, and no private capture access. Purpose: determine whether the ranked youth team properties resolve TEAM_BASE context like `NextFixture` or direct youth business data.

## Prohibited

Writes, game/UI/native calls, network access, private capture access, and save changes remain prohibited. No SDK or live reader is produced by this work.
