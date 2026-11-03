> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry scouting: scouting-recruitment

Lane: `scouting-recruitment`
Probe mode: `static-pinned-file`
Probe command run once:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-probe.ps1' -Lane 'scouting-recruitment'
```

Probe summary: `types=10`, `vtables=9`, `liveRecordsRead=0`, `outputTruncated=true`.

Pinned native fingerprint:

- `game_plugin.dll`: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`

## Confirmed RTTI types

| RTTI RVA | Decorated type |
|---|---|
| `0x5674190` | `.?AVPERSON_KEEP_SCOUT_REPORT_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@` |
| `0x5674200` | `.?AVPERSON_DISCARD_SCOUT_REPORT_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@` |
| `0x5678B40` | `.?AVPERSON_KEEP_SCOUT_REPORT_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@` |
| `0x5678BB0` | `.?AVPERSON_DISCARD_SCOUT_REPORT_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@` |
| `0x5687D60` | `.?AVFMT_SCOUT_REPORT_NEWS_ITEM_UI@@` |
| `0x5687DA0` | `.?AV?$NEWS_ITEM_UI_SPECIFIC@VFMT_SCOUT_REPORT_NEWS@@@news_ui@@` |
| `0x56A81F0` | `.?AVDISCARD_SCOUT_REPORT_ACTION@@` |
| `0x56A8540` | `.?AVKEEP_SCOUT_REPORT_ACTION@@` |
| `0x56BBD10` | `.?AVFMT_SCOUT_REPORT_NEWS@@` |
| `0x56CD4E0` | `.?AVSCOUT_REPORT_ROUNDUP_ITEM@@` |

## Confirmed vtables

| Vtable address | Type | Slot RVAs |
|---|---|---|
| `0x4AED188` | `PERSON_KEEP_SCOUT_REPORT_ACTION_UI_HANDLER` | `0x1EB7B0, 0x1E3E70, 0x78A8C0, 0x1E3C80, 0x78DAA0, 0x1EA320, 0x1EA330, 0x1EA340, 0x1EA350, 0x1EA360, 0x787D80, 0x1E4140` |
| `0x4AED2F8` | `PERSON_DISCARD_SCOUT_REPORT_ACTION_UI_HANDLER` | `0x1EB7E0, 0x1E3E70, 0x78A8C0, 0x1E3C80, 0x78DAA0, 0x1EA320, 0x1EA330, 0x1EA340, 0x1EA350, 0x1EA360, 0x787D80, 0x1E4140` |
| `0x4AF80E8` | `PERSON_KEEP_SCOUT_REPORT_ACTION_UI_HANDLER_SERVER` | `0x1F1D10, 0x1EC5C0, 0x1EC6C0, 0x7C7AB0, 0x7C7AC0, 0x7C7A90, 0x1EF680, 0x4A8D30, 0x1F1D70, invalid, 0x5678B3E80000000, 0x4AF812E84AF8148` |
| `0x4AF81A8` | `PERSON_DISCARD_SCOUT_REPORT_ACTION_UI_HANDLER_SERVER` | `0x1F1D80, 0x1EC5C0, 0x1EC6C0, 0x7C7AB0, 0x7C7AC0, 0x7C7A90, 0x1EF680, 0x4A8DC0, 0x1F1DE0, invalid, 0x5678BAE80000000, 0x4AF81EE84AF8208` |
| `0x4B29468` | `FMT_SCOUT_REPORT_NEWS_ITEM_UI` | `0x473E70, 0x473E80, 0x473E90, 0x473EA0, 0x473ED0, 0x473EF0, 0x473F20, 0x473F50, 0x473F70, 0x473F80, 0x473F90, 0x473FB0` |
| `0x4CCA1F8` | `DISCARD_SCOUT_REPORT_ACTION` | `0x1051940, 0x1051970, 0xFE3620, 0x399B570, 0x399B640, 0x399B710, 0x399B940, 0xFDA500, 0x399B950, 0xFDAA60, 0xFE3740, invalid` |
| `0x4CCAC28` | `KEEP_SCOUT_REPORT_ACTION` | `0x1051C70, 0x1051CA0, 0x399B560, 0x399B570, 0x399B640, 0x399B710, 0x399B940, 0xFDA500, 0x399B950, 0xFDAA60, 0xFEBA20, invalid` |
| `0x4D56548` | `FMT_SCOUT_REPORT_NEWS` | `0x1780440, 0x24D9C0, 0x24D9D0, 0x24D9E0, 0x24D9F0, 0x24DA00, 0x24DA10, 0x24DA20, 0x24DA30, 0x24DA40, 0x24DA50, 0x24DA60` |
| `0x4E21A58` | `SCOUT_REPORT_ROUNDUP_ITEM` | `0x2698830, 0x4088430, 0x40884B0, 0x2698900, 0x4088580, 0x2698910, 0x2698920, 0x2698930, 0x2698940, 0x2698950, invalid, 0x4E21DB0` |

No vtable was listed for `NEWS_ITEM_UI_SPECIFIC<FMT_SCOUT_REPORT_NEWS>`; its RTTI name is confirmed, but no vtable/slot evidence is claimed for it.

## Visible RIP candidates

The probe output was truncated after these five candidates:

| Displacement | Function | Target vtable | Target type |
|---|---|---|---|
| `0x1E6C54` | `0x1E66D0` | `0x4AED188` | `PERSON_KEEP_SCOUT_REPORT_ACTION_UI_HANDLER` |
| `0x1E893B` | `0x1E66D0` | `0x4AED2F8` | `PERSON_DISCARD_SCOUT_REPORT_ACTION_UI_HANDLER` |
| `0x1EDB0A` | `0x1EC790` | `0x4AF81A8` | `PERSON_DISCARD_SCOUT_REPORT_ACTION_UI_HANDLER_SERVER` |
| `0x1EE43C` | `0x1EC790` | `0x4AF80E8` | `PERSON_KEEP_SCOUT_REPORT_ACTION_UI_HANDLER_SERVER` |
| `0x474330` | `0x474240` | `0x4B29468` | `FMT_SCOUT_REPORT_NEWS_ITEM_UI` |

## Interpretation

The confirmed names are scout-report UI handlers, keep/discard actions, scout-report news presentation, and a scout-report roundup item. They establish RTTI/vtable existence only. They do not establish any collection entry, object fields, offsets, UID linkage, status enum, ownership, count, pagination, update timing, or authority. The probe read no records and invoked no functions.

## Narrow business-object entry hypothesis

Primary candidate: `SCOUT_REPORT_ROUNDUP_ITEM` (`RTTI 0x56CD4E0`, vtable `0x4E21A58`) is the only confirmed type that resembles a domain item rather than an action or UI/news formatter. Hypothesis: it may be the item type used by a scout-report roundup/list surface, with `KEEP_SCOUT_REPORT_ACTION` and `DISCARD_SCOUT_REPORT_ACTION` representing state transitions on such an item. This is unvalidated. It may instead be a UI/news presentation item, and no collection mount point or item schema is known.

Secondary surfaces, not business-object proof:

- `PERSON_*_SCOUT_REPORT_ACTION_UI_HANDLER*`: UI adapter surfaces for keep/discard actions.
- `KEEP_SCOUT_REPORT_ACTION` / `DISCARD_SCOUT_REPORT_ACTION`: action/command entry surfaces.
- `FMT_SCOUT_REPORT_NEWS*`: inbox/news presentation surfaces.

No matching type was found for a scouting list, staff assignment, knowledge/region coverage, candidate pool, recruitment model, or report collection. The closest proposed narrower names for future static searches are `SCOUT_REPORT_ROUNDUP_ITEM`, `KEEP_SCOUT_REPORT_ACTION`, `DISCARD_SCOUT_REPORT_ACTION`, and their `PERSON_*_UI_HANDLER` variants. No fake live reader or invented offsets are created.

## Exact missing semantics

- Collection owner and mount point: club, department, manager, news feed, or roundup container.
- Item identity and foreign keys: report ID, player/person UID, club UID, staff UID, match/fixture UID, date.
- Item fields and offsets: recommendation, ability range, strengths/weaknesses, expected cost, confidence, report time, status.
- Status/state enum and transitions for keep/discard.
- Collection boundaries: loaded subset, pagination, counts, dedup keys, update/invalidation timing.
- Relationship to inbox/news presentation versus a standalone report entity.
- RTTI-to-instance discovery path and any safe collection traversal.
- Multi-manager/club scope and authority.

## Next bounded read request

1. Static-only xref scan of the pinned `game_plugin.dll` for the constants `0x56CD4E0`, `0x4E21A58`, `0x56A81F0`, `0x56A8540`, `0x4CCA1F8`, and `0x4CCAC28`, bounded to the module and reporting referencing functions plus nearby string literals. No process memory, no function calls.
2. If a collection factory or mount point is found, request coordinator approval for one bounded live read under the existing fail-closed fingerprint and `<=64 KiB` budget, using validated UID lookup only, with raw and decoded values kept separate and all unknowns explicit.
3. Until then, SCT-01/SCT-02/SCT-03 remain not started; no SDK or live reader is added.
## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
