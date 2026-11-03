> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property-entry evidence: staff responsibilities

## Probe executed

Command:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'staff-responsibilities'
```

Result:

```json
{"lane": "staff-responsibilities", "mode": "static-property-candidates", "matches": 8, "truncated": false, "liveRecordsRead": 0, "entries": [{"name": "CoachingStaffDropdownList", "literalIndex": 5258, "slotRvas": ["0x32fd550"], "semantics": "unverified-property-name"}, {"name": "StaffAllList", "literalIndex": 18089, "slotRvas": ["0x32cefe8"], "semantics": "unverified-property-name"}, {"name": "StaffMeetingAllCategoriesSplitTopicList", "literalIndex": 18115, "slotRvas": ["0x32d0628"], "semantics": "unverified-property-name"}, {"name": "StaffMeetingSingleCategoryTopicList", "literalIndex": 18122, "slotRvas": ["0x32d0c40"], "semantics": "unverified-property-name"}, {"name": "StaffMeetingSplitTopicsList", "literalIndex": 18123, "slotRvas": ["0x32d0d40"], "semantics": "unverified-property-name"}, {"name": "StaffScoutList", "literalIndex": 18139, "slotRvas": ["0x32d1bd0"], "semantics": "unverified-property-name"}, {"name": "StaffSubGroupPersonList", "literalIndex": 18144, "slotRvas": ["0x32d2090"], "semantics": "unverified-property-name"}, {"name": "staffmeetingtopiclist", "literalIndex": 30039, "slotRvas": ["0x33091b8"], "semantics": "unverified-property-name"}]}
```

- Lane: `staff-responsibilities`
- Mode: `static-property-candidates`
- Matches: `8`
- Truncated: `false`
- Live records read: `0`

## Pinned sources and hashes

- Probe command source: `<research-workspace>/agent-tools/run-lane-property-probe.ps1`
- Native image: `game_plugin.dll`
- Native SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Metadata SHA-256: `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`
- Metadata sanity/version: `0xFAB11BAF` / `39`

This run was static only. It did not read process memory, game files, saves, UI, network resources, or private captures.

## Candidate classification

All eight returned names are property-name candidates. They are list, dropdown, or topic-list shaped and are not evidence of staff business fields, staff records, staff collections, posts, departments, responsibilities, contracts, or qualifications.

| Rank by slot RVA | Property name | Literal index | Slot RVA | Classification | Business field? |
|---:|---|---:|---|---|---|
| 1 | `StaffAllList` | 18089 | `0x32cefe8` | UI or operations list candidate | No |
| 2 | `StaffMeetingAllCategoriesSplitTopicList` | 18115 | `0x32d0628` | UI, news, or operations topic-list candidate | No |
| 3 | `StaffMeetingSingleCategoryTopicList` | 18122 | `0x32d0c40` | UI, news, or operations topic-list candidate | No |
| 4 | `StaffMeetingSplitTopicsList` | 18123 | `0x32d0d40` | UI, news, or operations topic-list candidate | No |
| 5 | `StaffScoutList` | 18139 | `0x32d1bd0` | UI or operations list candidate | No |
| 6 | `StaffSubGroupPersonList` | 18144 | `0x32d2090` | UI or operations list candidate | No |
| 7 | `CoachingStaffDropdownList` | 5258 | `0x32fd550` | UI dropdown candidate | No |
| 8 | `staffmeetingtopiclist` | 30039 | `0x33091b8` | UI, news, or operations topic-list candidate | No |

The coordinator evidence for `NextFixture` shows that a literal name alone does not establish the resolved business context. The same caution applies here: these names must be treated as registrations to inspect, not as staff business fields.

## Native keys and offsets

All native keys, offsets, and function names remain `null` in `tools/research/property_entry_staff_responsibilities.py`. No candidate has a confirmed entry point, registration function, or field layout.

## Next bounded request

No live request is genuinely supported by this evidence. The next step is a bounded static inspection of the eight slot RVAs above, using the same pinned native image and fail-closed profile. It must record only registration metadata that is directly observable at those slots. It must not call native functions, read process memory beyond the authorized static inspection budget, access UI, save data, network, or private captures, and it must not treat any list or topic name as a staff business field. No live request is authorized until a staff-specific type and collection entry are confirmed.

## Recovery qualification

The companion script named above failed recovery validation and is **not included** in this branch. Its original remains in the private recovery snapshots. Do not run the example commands or treat the validator as delivered.
