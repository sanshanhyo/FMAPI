> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property-to-entry evidence: messages-news

## Probe run (executed once)

Command (read-only, pinned binary, exact):

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'messages-news'
```

Result (verbatim, no save/private data):

```json
{"lane": "messages-news", "mode": "static-property-candidates", "matches": 11, "truncated": false, "liveRecordsRead": 0, "entries": [
  {"name": "HumanCanMarkSelectedPortalMessagesAsUnread", "literalIndex": 10136, "slotRvas": ["0x32dc628"], "semantics": "unverified-property-name"},
  {"name": "HumanPortalNewestUnreadMessage", "literalIndex": 10204, "slotRvas": ["0x32e0290"], "semantics": "unverified-property-name"},
  {"name": "HumanPortalNewestUnreadMessageIndex", "literalIndex": 10205, "slotRvas": ["0x32e0370"], "semantics": "unverified-property-name"},
  {"name": "HumanPortalNextUnreadMessage", "literalIndex": 10211, "slotRvas": ["0x32e08d0"], "semantics": "unverified-property-name"},
  {"name": "HumanPortalOldestUnreadMessage", "literalIndex": 10212, "slotRvas": ["0x32e09b8"], "semantics": "unverified-property-name"},
  {"name": "HumanPortalOldestUnreadMessagesIndex", "literalIndex": 10213, "slotRvas": ["0x32e0aa0"], "semantics": "unverified-property-name"},
  {"name": "HumanPortalPreviousUnreadMessage", "literalIndex": 10217, "slotRvas": ["0x32e0e10"], "semantics": "unverified-property-name"},
  {"name": "HumanPortalUnreadMessages", "literalIndex": 10219, "slotRvas": ["0x32e0fe8"], "semantics": "unverified-property-name"},
  {"name": "NewsBodyString", "literalIndex": 13657, "slotRvas": ["0x3309360"], "semantics": "unverified-property-name"},
  {"name": "NumberUnreadMessages", "literalIndex": 14030, "slotRvas": ["0x331e688"], "semantics": "unverified-property-name"},
  {"name": "ShortlistScoutingSendReportsToInbox", "literalIndex": 17503, "slotRvas": ["0x32acfd0"], "semantics": "unverified-property-name"}
]}
```

- `liveRecordsRead`: 0
- `truncated`: false
- `matches`: 11

## Source and pinned hash

- Primary pinned binary: `game_plugin.dll` SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`, image base `0x180000000`.
- Named-property/body context additionally references `GameAssembly.dll` SHA-256 `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A` (metadata signature `0xFAB11BAF`, version 39) from the position/native-entity evidence; it is not a messages-news compatibility claim.
- All slot RVAs are module-relative to the pinned `game_plugin.dll`. They are references only.

## Name surface: UI/news/operations versus business fields

The probe supplies property names only; names are unverified surface labels. Coordinator evidence shows a name can resolve a different context than its surface (NextFixture, literal 13696, slot `0x330B698`, native key `0x6E654669`, first resolves TEAM_BASE context via global `0x5703768`, not fixtures). Therefore classification below is a name-surface hypothesis, not a runtime referent.

| Property name | Surface group | Surface class | Read |
|---|---|---|---|
| `NewsBodyString` | business-field | business-field | Only candidate that names a business field; aligns with MSG-02 body route. |
| `NumberUnreadMessages` | ui-news-operations | ui-count | Count/operation surface, not a message body. |
| `HumanPortalUnreadMessages` | ui-news-operations | ui-portal | Portal collection/view candidate, not proven a business collection. |
| `HumanPortalNewestUnreadMessage` | ui-news-operations | ui-portal | Navigation surface. |
| `HumanPortalOldestUnreadMessage` | ui-news-operations | ui-portal | Navigation surface. |
| `HumanPortalNextUnreadMessage` | ui-news-operations | ui-portal | Navigation surface. |
| `HumanPortalPreviousUnreadMessage` | ui-news-operations | ui-portal | Navigation surface. |
| `HumanPortalNewestUnreadMessageIndex` | ui-news-operations | ui-portal | Index companion. |
| `HumanPortalOldestUnreadMessagesIndex` | ui-news-operations | ui-portal | Index companion. |
| `HumanCanMarkSelectedPortalMessagesAsUnread` | ui-news-operations | ui-operation | Mutation-style operation; inspect registration only, never invoke. |
| `ShortlistScoutingSendReportsToInbox` | ui-news-operations | scouting-operation | Inbox sink candidate; may be unrelated to messages-news business entries. |

No property name is treated as a proven entry point, native key, offset, or function.

## Ranked next registrations to inspect

1. `NewsBodyString` (literal 13657, slot `0x3309360`) — business field; inspect slot for entry registration.
2. `NumberUnreadMessages` (literal 14030, slot `0x331e688`) — count candidate for MSG-01 read state.
3. `HumanPortalUnreadMessages` (literal 10219, slot `0x32e0fe8`) — unread collection candidate.
4. `HumanPortalNewestUnreadMessage` (literal 10204, slot `0x32e0290`).
5. `HumanPortalOldestUnreadMessage` (literal 10212, slot `0x32e09b8`).
6. `HumanPortalNextUnreadMessage` (literal 10211, slot `0x32e08d0`).
7. `HumanPortalPreviousUnreadMessage` (literal 10217, slot `0x32e0e10`).
8. `HumanPortalNewestUnreadMessageIndex` (literal 10205, slot `0x32e0370`).
9. `HumanPortalOldestUnreadMessagesIndex` (literal 10213, slot `0x32e0aa0`).
10. `HumanCanMarkSelectedPortalMessagesAsUnread` (literal 10136, slot `0x32dc628`) — inspect only; do not invoke.
11. `ShortlistScoutingSendReportsToInbox` (literal 17503, slot `0x32acfd0`).

Native keys, entry offsets, and registration functions remain null for all entries.

## Next bounded live request

None is genuinely supported by current evidence. The property candidates are static name/slot references only; no constructed instance, offset, or context resolution has been proven for this lane, so a live read would require guessing entry structure. The supported next step is static: disassemble/inspect the 11 slot RVAs and their containing functions in the pinned `game_plugin.dll`, without invoking any function or reading process memory, to determine whether any slot is a constructor, factory, registration, or use site. Only after that static result should a coordinator consider a bounded live read.

Machine-readable manifest: `tools/research/property_entry_messages_news.py`.
