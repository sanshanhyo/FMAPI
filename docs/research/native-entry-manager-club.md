> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry: manager-club (lane manager-club)

## Probe execution record

Command (run once, read-only, static pinned binary, no process memory):

```
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-probe.ps1' -Lane 'manager-club'
```

Result header: `{"lane":"manager-club","mode":"static-pinned-file","types":19,"vtables":10,"liveRecordsRead":0,"outputTruncated":true}`

- Binary SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Live records read: `0` (no process memory, no native calls)
- Output truncated by the probe: full derived output stays private; only bounded structural RTTI evidence is reproduced here.

## Confirmed type evidence (19 RTTI nodes)

| RVA | RTTI name |
|---|---|
| 0x569E290 | .?AVEXTERN_NATIONAL_TEAM@db@@ |
| 0x569ECC0 | .?AVEXTERN_TEAM@db@@ |
| 0x56A0330 | .?AVSTARTING_RESERVE_TEAM@db@@ |
| 0x56A13F0 | .?AV?$DATABASE_TABLE@VSTARTING_RESERVE_TEAM@db@@@db@@ |
| 0x56A1A00 | .?AV?$_Func_base@XPEAVSTARTING_RESERVE_TEAM@db@@AEA_N@std@@ |
| 0x56A2A60 | .?AVTEAM@db@@ |
| 0x56A3910 | .?AV?$_Func_impl_no_alloc@VSETUP_STARTING_RESERVE_TEAM@db@@...@std@@ |
| 0x56A3990 | .?AVSETUP_STARTING_RESERVE_TEAM@db@@ |
| 0x56A39D0 | .?AV?$_Func_impl_no_alloc@VCOUNT_STARTING_RESERVE_TEAM@db@@...@std@@ |
| 0x56A3A50 | .?AVCOUNT_STARTING_RESERVE_TEAM@db@@ |
| 0x56AB010 | .?AV?$_Func_impl_no_alloc@V<lambda_0>...get_set_piece_candidates@TEAM...@std@@ |
| 0x56AB180 | .?AV<lambda_0>...get_set_piece_candidates@TEAM...@ |
| 0x56AB280 | .?AV?$_Func_impl_no_alloc@V<lambda_1>...get_penalty_candidates@TEAM...@std@@ |
| 0x56AB370 | .?AV<lambda_1>...get_penalty_candidates@TEAM...@ |
| 0x56C5D10 | .?AVNATIONAL_TEAM@db@@ |
| 0x56D38D0 | .?AV?$_Func_impl_no_alloc@V<lambda_3>...setup_implementation@SQUAD_PLANNER...@std@@ |
| 0x56D3A20 | .?AV<lambda_3>...setup_implementation@SQUAD_PLANNER...@ |
| 0x56D3B00 | .?AV?$_Func_impl_no_alloc@V<lambda_4>...setup_implementation@SQUAD_PLANNER...@std@@ |
| 0x56D3C30 | .?AV<lambda_4>...setup_implementation@SQUAD_PLANNER...@ |

## Confirmed vtable evidence (5 of 10 printed)

| Vtable RVA | RTTI name | Slot RVAs |
|---|---|---|
| 0x4CA63F8 | .?AV?$DATABASE_TABLE@VSTARTING_RESERVE_TEAM@db@@@db@@ | 0xD94D00,0xD5AD00,0xD5B210,0xD5B230,0xD5B710,0xD5B5E0,0xD5AD50,0xD5B890,0xD5B8A0,0xD5AD70,0xC92770,0xD5BD80 |
| 0x4CB1E28 | .?AVSTARTING_RESERVE_TEAM@db@@ | 0xDA1530,0x389AC40,0x389B530,0x414370,0x414380,0x414390,0x4143A0,0x4144C0,0x4143C0,0xEF3880,0x4143D0,0x4143E0 |
| 0x4CBAC38 | .?AV?$_Func_impl_no_alloc@VSETUP_STARTING_RESERVE_TEAM...@std@@ | 0xE3ED80,0xE3EDA0,0xE3EDC0,0xE3EDD0,0xE3EDE0,0xE3EDF0,invalid,invalid,0x56A390E80000000,0x4CBAC6E84CBAC88,invalid,0x4CBAC9680000002 |
| 0x4CBACF8 | .?AV?$_Func_impl_no_alloc@VCOUNT_STARTING_RESERVE_TEAM...@std@@ | 0xE3EE00,0xE3EE20,0xE3EE40,0xE3EE50,0xE3EE60,0xE3EE70,invalid,invalid,0x56A39CE80000000,0x4CBAD2E84CBAD48,invalid,0x4CBAD5680000002 |
| 0x4CE1108 | .?AVTEAM@db@@ | 0x121AC10,0x11FDA20,0x1202320,0x11DDD90,0x414380,0x414390,0x4143A0,0xDA0AA0,0x120E480,0x1185810,0x4143D0,0x117A4C0 |

The remaining 5 vtable nodes are in the truncated/private probe output and are not reproduced here. Slot RVAs are raw code pointers; their method semantics are not established by this probe.

## Exact no-match records

The following requested entry types were **not** printed by this probe. They are recorded as no-match, not as confirmed absence in the binary:

| Requested | Status | Proposed narrower names / next search |
|---|---|---|
| .?AVCLUB@db@@ | no-match-in-this-probe | .?AVCLUB@db@@; team+0x30 club pointer (prior docs only, not this probe); EXTERN_TEAM / STARTING_RESERVE_TEAM hierarchy nodes |
| .?AVHUMAN_NON_PLAYER_MANAGER@db@@ | no-match-in-this-probe | .?AVHUMAN_NON_PLAYER_MANAGER@db@@; .?AVHUMAN_NON_PLAYER@db@@; GameCurrentManager / GCuM selected record RTTI (prior native-entity evidence) |
| .?AVPERSON@db@@ | no-match-in-this-probe | .?AVPERSON@db@@; .?AVACTUAL_PLAYER@db@@; DATABASE_TABLE<PERSON> vtable 0x4CA5278 (prior doc) |
| .?AVFULL_CONTRACT@db@@ | no-match-in-this-probe | .?AVFULL_CONTRACT@db@@; .?AVCONTRACT@db@@ |
| .?AVFIXTURE@db@@ | no-match-in-this-probe | .?AVFIXTURE@db@@; .?AVMATCH@db@@ |

No fake live reader, club reader, or manager reader is created from this probe. Prior GCuM/employment-chain evidence is separate and is not re-attributed to this probe.

## Narrow business-object entry hypothesis

Supported by this probe only:

- `TEAM@db` (RTTI 0x56A2A60, vtable 0x4CE1108) is a confirmed native business-object type entry for the manager-club lane.
- `STARTING_RESERVE_TEAM@db` (RTTI 0x56A0330, vtable 0x4CB1E28) is a confirmed specialization distinct from `TEAM@db`.
- `DATABASE_TABLE<STARTING_RESERVE_TEAM>` (RTTI 0x56A13F0, vtable 0x4CA63F8) is a confirmed table/index container for reserve teams.
- `EXTERN_TEAM`, `EXTERN_NATIONAL_TEAM`, and `NATIONAL_TEAM` are confirmed type nodes, but no vtable slot list was captured for them in this bounded output.
- `SETUP_STARTING_RESERVE_TEAM` and `COUNT_STARTING_RESERVE_TEAM` are confirmed operation types around reserve teams.

Hypothesis: a managed club's team hierarchy enters through `TEAM@db` instances, with `STARTING_RESERVE_TEAM` as a reserve specialization and `EXTERN_*`/`NATIONAL_TEAM` as separate specializations. This is a type/vtable-level claim only; no object instance, field offset, or method identity is claimed.

## Exact missing semantics

- No `CLUB`, manager/human, person, contract, or fixture RTTI/vtable in this probe; all club/manager-level fields remain unconfirmed here.
- No field offsets for any confirmed type. Prior documented offsets (team UID +0x0C, name candidates, club pointer +0x30, etc.) are not attributed to this probe.
- Vtable slot semantics unknown; slot RVAs are not validated as methods.
- 5 of 10 vtables not captured (truncated/private).
- No live read, no process memory, no native call, no UI/game access was performed.
- Reserve/youth/national team hierarchy and team-type classification are not established.

## Next bounded read request (coordinator-scheduled only)

1. Static: a later bounded RTTI scan for `.?AVCLUB@db@@` and `.?AVHUMAN_NON_PLAYER_MANAGER@db@@` (or narrower names above) under the same pinned binary fingerprint, recording type RVA + vtable RVA + slot list. Budget: type-node walk only, no process memory, no disassembly beyond instruction boundaries.
2. Static: if `CLUB`/manager nodes are found, capture their vtable slot lists and compare against the `TEAM`/`STARTING_RESERVE_TEAM` shapes already recorded.
3. Live (separate authorization): only after a confirmed type/vtable, read at most one object instance's vtable pointer (8 bytes) plus recheck; no field offsets until statically proven.
4. All requests must fail closed on fingerprint mismatch and stop at the stated bound.

## Machine-readable manifest

`tools/research/entry_manager_club.py` emits the confirmed type/vtable manifest and validates candidate entries against it. Unresolved offsets are absent in the manifest and rejected when supplied as input. Run `python tools/research/entry_manager_club.py --self-test`.
