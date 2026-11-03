> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry evidence: tactics lane

Status: static RTTI/vtable evidence only. The lane probe opened the pinned `game_plugin.dll` as data; it did not open a process, read process memory, call game functions, use UI, or read private samples. `liveRecordsRead=0`.

## Executed probe

Command:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-probe.ps1' -Lane 'tactics'
```

Result summary:

- `lane`: `tactics`
- `mode`: `static-pinned-file`
- `types`: `3`
- `vtables`: `4`
- `liveRecordsRead`: `0`
- `outputTruncated`: `false`
- `SHA256`: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- `ImageBase`: `0x180000000`

Raw probe output:

```text
TYPE 0x567F2E0 .?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@
TYPE 0x568C850 .?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@
TYPE 0x56ED670 .?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@

VTABLE 0x4B104C8 .?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@ slots=0x390B90,0x6819C0,0x6592D0,0x7C7AB0,0x7C7AC0,0x65A700,invalid,invalid,0x567F2DE80000000,0x4B104FE84B10518,invalid,0x4B1052E80000004
VTABLE 0x4B3D9E8 .?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@ slots=0x6818D0,0x61DC80,0x63C0F0,0x6818C0,0x78DAA0,0x1EA320,0x1EA330,0x1EA340,0x1EA350,0x626610,0x787D80,0x61FBA0
VTABLE 0x4B3DB98 .?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@ slots=0x681980,0x61FA80,invalid,invalid,0x568C84E80000000,0x4B3DBAE84B3DBC8,invalid,0x4B3DBDE80000005,invalid,0x4AFE8AE84B3DC00,0x4AE37FE84AE37C0,invalid
VTABLE 0x509E638 .?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@ slots=0x4AA7370,0x4AA7290,0x4AA72D0,0x4AA71B0,0x4AA7320,invalid,0x56ED66E80000000,0x509E65E8509E678,invalid,0x509E68680000002,0x4E52ACE8509E6A0,invalid

RIP_CANDIDATE displacement=0x388010 function=0x387FC0 target=0x4B104C8 .?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@
RIP_CANDIDATE displacement=0x6816A0 function=0x681690 target=0x4B3D9E8 .?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@
RIP_CANDIDATE displacement=0x6816AA function=0x681690 target=0x4B3DB98 .?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@
RIP_CANDIDATE displacement=0x29D7F9E function=0x29D7B10 target=0x509E638 .?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@
RIP_CANDIDATE displacement=0x4AA718C function=0x4AA7170 target=0x509E638 .?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@
```

## Confirmed RTTI types

| Type RVA | RTTI name | Module |
|---|---|---|
| `0x567F2E0` | `.?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@` | `game_plugin.dll` |
| `0x568C850` | `.?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@` | `game_plugin.dll` |
| `0x56ED670` | `.?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@` | `game_plugin.dll` |

## Confirmed vtables

| Vtable RVA | RTTI name | Raw slot tokens from probe |
|---|---|---|
| `0x4B104C8` | `.?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@` | `0x390B90, 0x6819C0, 0x6592D0, 0x7C7AB0, 0x7C7AC0, 0x65A700, invalid, invalid, 0x567F2DE80000000, 0x4B104FE84B10518, invalid, 0x4B1052E80000004` |
| `0x4B3D9E8` | `.?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@` | `0x6818D0, 0x61DC80, 0x63C0F0, 0x6818C0, 0x78DAA0, 0x1EA320, 0x1EA330, 0x1EA340, 0x1EA350, 0x626610, 0x787D80, 0x61FBA0` |
| `0x4B3DB98` | `.?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@` | `0x681980, 0x61FA80, invalid, invalid, 0x568C84E80000000, 0x4B3DBAE84B3DBC8, invalid, 0x4B3DBDE80000005, invalid, 0x4AFE8AE84B3DC00, 0x4AE37FE84AE37C0, invalid` |
| `0x509E638` | `.?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@` | `0x4AA7370, 0x4AA7290, 0x4AA72D0, 0x4AA71B0, 0x4AA7320, invalid, 0x56ED66E80000000, 0x509E65E8509E678, invalid, 0x509E68680000002, 0x4E52ACE8509E6A0, invalid` |

The vtable slot tokens are the probe's raw 8-byte slot values. Tokens marked `invalid` are not module code pointers. Tokens that are not ordinary 32-bit RVAs are preserved as raw probe tokens and are not treated as executable RVAs.

## RIP-relative references

| Displacement RVA | Function RVA | Target vtable RVA | RTTI name |
|---|---|---|---|
| `0x388010` | `0x387FC0` | `0x4B104C8` | `.?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@` |
| `0x6816A0` | `0x681690` | `0x4B3D9E8` | `.?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@` |
| `0x6816AA` | `0x681690` | `0x4B3DB98` | `.?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@` |
| `0x29D7F9E` | `0x29D7B10` | `0x509E638` | `.?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@` |
| `0x4AA718C` | `0x4AA7170` | `0x509E638` | `.?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@` |

## Narrow business-object entry hypothesis

The confirmed names are RTTI/type names, not confirmed business-object layouts. The narrow hypothesis is:

- `TEAM_TACTIC_UI_HANDLER` and `TEAM_TACTIC_UI_HANDLER_SERVER` are native entry surfaces for tactic-related UI/controller behavior in `game_plugin.dll`.
- `TEAM_TACTIC_CREATOR_CHANGE` is a native entry surface for a tactic creator-change object in the `simatch` namespace.
- A function referencing one of the confirmed vtables (for example `0x681690` referencing both `0x4B3D9E8` and `0x4B3DB98`) is the smallest confirmed code entry point for disassembly in this lane.

This does not establish that any of these objects is the business object that owns an active or selected tactic. The types are UI handler / creator-change types. They may be view/controller, change-record, or adapter objects rather than tactic-slot owners. No field offset, collection root, UID linkage, or formation/lineup semantics is established.

Prior coordinator note: dispatcher `0x628FC0` belongs to tactic UI handlers; `FirstTeamPlayers` is not a direct `TEAM` roster vector. That note remains context only and is not converted into a field layout here.

## Exact missing semantics

- Which business object owns the active tactic: team, manager, club, or separate tactic manager.
- Whether the UI handler object is a controller/view or the tactic owner.
- Difference between active tactic slot and selected UI slot.
- Tactic identity/name/UID and scheme ordering.
- Formation representation and slot count.
- Starters, substitutes, unselected players, and player UID linkage.
- Role, duty, mentality, team instruction, individual instruction, and opposition instruction encodings.
- Set-piece routines, captain, and set-piece taker ordering.
- Tactical familiarity and its relationship to player positional familiarity.
- Lifetime/refresh behavior across edits, save/load, reload, manager change, and process restart.
- Object field offsets for all confirmed types. None are known.
- Slot-function semantics for every vtable slot. None are known beyond raw RVAs.
- Whether `TEAM_TACTIC_CREATOR_CHANGE` is a command/change record or another tactic-related object.

## Next bounded read request

1. Static, no process (operator-provided pinned binary only):
   - Disassemble instruction boundaries at `0x387FC0`, `0x681690`, `0x29D7B10`, and `0x4AA7170`.
   - Trace how each function uses its referenced vtable and whether it constructs, returns, stores, or dispatches a tactic handler/change object.
   - Use `tools/research/locate_vtable_function.py` only if an exact function RVA and slot index are already known; do not scan arbitrary address space.
   - Budget: explicit functions only, stop at 40 matches or 100 candidate types, no process memory.

2. Later coordinator-approved bounded process read, only after a static anchor exists:
   - Read one validated tactic UI handler or creator-change instance if a stable pointer source is identified statically.
   - Follow at most two already-analyzed pointer hops with exact expected RTTI/vtable checks.
   - Budget: 64 KiB total, 32 objects, 8 KiB per read, two passes; abort on any pointer, type, or state change.
   - Output sanitized structural JSON only: counts, RTTI names, module-relative offsets, raw enum values, and status. No names, UID lists, prose, or raw dumps.

3. If no static anchor is found, record `blocked`/`unavailable` rather than inventing an entry point.

Machine-readable manifest: `tools/research/entry_tactics.py`.
