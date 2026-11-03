> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry evidence: messages-news

## Probe run

Command (run once, read-only, pinned binary):

```text
pwsh -NoProfile -File .../run-lane-probe.ps1 -Lane messages-news
```

Result:

```json
{"lane":"messages-news","mode":"static-pinned-file","types":3,"vtables":2,"liveRecordsRead":0,"outputTruncated":false}
SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F ImageBase 0x180000000
TYPE 0x5685680 .?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@
TYPE 0x56856C0 .?AV?$NEWS_ITEM_UI_SPECIFIC@VWELCOME_TO_THE_CLUB_NEWS@@@news_ui@@
TYPE 0x56C0AC0 .?AVWELCOME_TO_THE_CLUB_NEWS@@
VTABLE 0x4B234F8 .?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@ slots=0x4580F0,0x458100,0x458110,0x458120,0x458150,0x458170,0x4581A0,0x4581D0,0x4581F0,0x458200,0x458210,0x458230
VTABLE 0x4D86CF8 .?AVWELCOME_TO_THE_CLUB_NEWS@@ slots=0x179A080,0x24D9C0,0x24D9D0,0x24D9E0,0x24D9F0,0x24DA00,0x24DA10,0x24DA20,0x24DA30,0x24DA40,0x24DA50,0x24DA60
RIP_CANDIDATE displacement=0x4594B1 function=0x459460 target=0x4B234F8 .?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@
RIP_CANDIDATE displacement=0x175E275 function=0x1750CC0 target=0x4D86CF8 .?AVWELCOME_TO_THE_CLUB_NEWS@@
RIP_CANDIDATE displacement=0x1C8BAE1 function=0x1C89D70 target=0x4D86CF8 .?AVWELCOME_TO_THE_CLUB_NEWS@@
```

Evidence is static-only. No live records were read (`liveRecordsRead=0`). All RVAs are module-relative to the pinned `game_plugin.dll`.

## Confirmed type and vtable evidence

| Kind | RVA | Name / target |
|---|---|---|
| RTTI type | `0x5685680` | `.?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@` |
| RTTI type | `0x56856C0` | `.?AV?$NEWS_ITEM_UI_SPECIFIC@VWELCOME_TO_THE_CLUB_NEWS@@@news_ui@@` |
| RTTI type | `0x56C0AC0` | `.?AVWELCOME_TO_THE_CLUB_NEWS@@` |
| Vtable | `0x4B234F8` | `.?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@` |
| Vtable | `0x4D86CF8` | `.?AVWELCOME_TO_THE_CLUB_NEWS@@` |

The `NEWS_ITEM_UI_SPECIFIC` template type links the UI item to the business type `WELCOME_TO_THE_CLUB_NEWS`, but its vtable was not reported by this probe.

## Confirmed RIP candidates (code references to vtables)

| Displacement RVA | Containing function RVA | Target vtable RVA | Target type |
|---|---|---|---|
| `0x4594B1` | `0x459460` | `0x4B234F8` | `WELCOME_TO_THE_CLUB_NEWS_ITEM_UI` |
| `0x175E275` | `0x1750CC0` | `0x4D86CF8` | `WELCOME_TO_THE_CLUB_NEWS` |
| `0x1C8BAE1` | `0x1C89D70` | `0x4D86CF8` | `WELCOME_TO_THE_CLUB_NEWS` |

These are candidate references only. Instruction boundaries, constructor/factory role, and ownership have not been confirmed.

## Narrow business-object entry hypothesis

`WELCOME_TO_THE_CLUB_NEWS` (vtable `0x4D86CF8`) is the candidate business object, distinct from the UI item type `WELCOME_TO_THE_CLUB_NEWS_ITEM_UI` (vtable `0x4B234F8`). The two functions containing references to the business vtable, `0x1750CC0` and `0x1C89D70`, are the candidate business-object entry/constructor/factory sites. Function `0x459460` is the corresponding UI-side candidate.

This hypothesis is narrow: it claims only that these functions are static references to the confirmed vtables. It does not claim that either function constructs, registers, owns, or mutates a business object, and it does not map any vtable slot to a method.

## Exact missing semantics

- Which RIP candidate (if any) is a constructor, factory, registration, or use site for `WELCOME_TO_THE_CLUB_NEWS`.
- Vtable slot meaning for both vtables (12 slots each); no slot is mapped to a method.
- Field offsets, constructor ABI, object size, lifetime, ownership, and initialization order.
- Relationship between `WELCOME_TO_THE_CLUB_NEWS`, `NEWS_ITEM_UI_SPECIFIC<...>`, and `WELCOME_TO_THE_CLUB_NEWS_ITEM_UI`.
- Whether either business function is reachable for the pinned single-human-manager message route; no live read was performed.
- Whether `0x1750CC0` and `0x1C89D70` are distinct entry paths or one wrapper/delegate pair.
- All news/message fields outside the already documented MSG-01/MSG-02 welcome relation candidates.

Unresolved values are intentionally absent from `tools/research/entry_messages_news.py`; they are not invented as offsets.

## Next bounded read request

1. Offline only: disassemble functions `0x1750CC0` and `0x1C89D70` (and `0x459460` for comparison) at instruction boundaries using the pinned PE, without invoking any function or reading process memory. Identify whether either references the vtable as a constructor/factory/registration and which slot or field is touched.
2. If instruction-boundary analysis is inconclusive, request coordinator-approved static metadata/PE follow-up limited to those functions and their direct callees; no process scan.
3. Only after static results: request a coordinator-scheduled bounded live read of at most one constructed `WELCOME_TO_THE_CLUB_NEWS` instance with root/vector rechecks and the existing 64 KiB budget. No UI, game function call, lazy load, write, or state change.

## Machine-readable manifest

`tools/research/entry_messages_news.py` emits the confirmed type/vtable/RIP-candidate evidence as JSON and validates supplied manifests against that evidence. Run:

```text
python tools/research/entry_messages_news.py --self-test
python tools/research/entry_messages_news.py
```
