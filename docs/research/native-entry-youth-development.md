> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Youth-development native entry

## Scope

Static, read-only evidence only. No process, game, UI, network, live read, write, or save access occurred for this document. All RVAs apply only to the pinned `game_plugin.dll` SHA-256 below.

## Probe execution

Command executed once, exactly as authorized:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-probe.ps1' -Lane 'youth-development'
```

Result:

```json
{"lane":"youth-development","mode":"static-pinned-file","types":1,"vtables":1,"liveRecordsRead":0,"outputTruncated":false}
```

## Pinned binary

- SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Mode: `static-pinned-file`
- Types reported: `1`
- Vtables reported: `1`
- Live records read: `0`
- Output truncated: `false`

## Actual probe evidence

```text
TYPE 0x56BF770 .?AVREGENERATION_YOUTH_INTAKE_NEWS@@
VTABLE 0x4D7A478 .?AVREGENERATION_YOUTH_INTAKE_NEWS@@ slots=0x1792CB0,0x24D9C0,0x24D9D0,0x24D9E0,0x24D9F0,0x24DA00,0x24DA10,0x24DA20,0x24DA30,0x24DA40,0x24DA50,0x24DA60
RIP_CANDIDATE displacement=0x1761423 function=0x1750CC0 target=0x4D7A478 .?AVREGENERATION_YOUTH_INTAKE_NEWS@@
RIP_CANDIDATE displacement=0x2FE2534 function=0x2FE2500 target=0x4D7A478 .?AVREGENERATION_YOUTH_INTAKE_NEWS@@
```

Confirmed RTTI/vtable facts:

- Type descriptor RVA: `0x56BF770`
- Type name: `.?AVREGENERATION_YOUTH_INTAKE_NEWS@@`
- Vtable RVA: `0x4D7A478` (absolute `0x184D7A478`)
- Reported vtable slot RVAs: `0x1792CB0`, `0x24D9C0`, `0x24D9D0`, `0x24D9E0`, `0x24D9F0`, `0x24DA00`, `0x24DA10`, `0x24DA20`, `0x24DA30`, `0x24DA40`, `0x24DA50`, `0x24DA60`
- Reported slot count: `12` (static scan limit; not proof of total table size)
- RIP-relative candidate 1: displacement RVA `0x1761423`, function RVA `0x1750CC0`, target RVA `0x4D7A478`
- RIP-relative candidate 2: displacement RVA `0x2FE2534`, function RVA `0x2FE2500`, target RVA `0x4D7A478`

The slot RVAs and RIP candidates are raw structural evidence only. No slot meaning, field offset, constructor, owner, collection, or instance layout is confirmed.

## Narrow business-object entry hypothesis

The only verified native entry for this lane is the RTTI type `.?AVREGENERATION_YOUTH_INTAKE_NEWS@@` with vtable RVA `0x4D7A478`. Its name suggests a news/notification business object associated with regeneration youth intake, not a squad roster, player record, academy container, or verified read path. The two RIP-relative candidates may be construction or vtable-assignment sites, but that remains unconfirmed because instruction boundaries and call context were not disassembled. Therefore this type is a candidate business-object entry surface only: it is enough to justify bounded static follow-up, but not enough to implement a reader, expose SDK behavior, or claim youth-development data access.

This evidence does not establish any of the following: youth/reserve squads, rosters, coaches, fixtures, promotion/loan state, intake batches, trials, assessments, mentors, development state, historical output, compensation records, or club/team/person linkage for this type.

## Exact missing semantics

- Whether the type is instantiated in an ordinary loaded save.
- Whether either RIP candidate is a real construction/factory path rather than a data artifact.
- Constructor signature and arguments.
- Vtable slot semantics, including destructor and virtual behavior.
- Field offsets, sizes, and types.
- Owning collection or owner object and its bounds.
- Relation to club, team, person, manager, or news collections.
- News content and localization linkage.
- Instance lifetime, count bounds, and mutation status.
- Game-state conditions required for instantiation.
- Whether the reported 12 slots are the complete vtable.

## Next bounded read request

1. Static-only, no process: disassemble the functions at RVA `0x1750CC0` and `0x2FE2500` with bounded length to confirm instruction boundaries, vtable stores, allocations, and call context.
2. If a constructor/factory is confirmed, request coordinator approval for a separate bounded process probe. That probe may read only RTTI type name, vtable RVA, and a small raw prefix from at most a few instances, with process recheck before and after, aggregate read budget no greater than 64 KiB, and no writes, UI, match advancement, or save changes.
3. Do not read private samples, saves, credentials, or arbitrary process memory outside the approved bounded request.

## Machine-readable companion

`tools/research/entry_youth_development.py` contains the same confirmed type/vtable evidence as a machine-readable manifest and validator. It does not include field offsets, slot semantics, or any live reader.
