> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native-entry evidence: staff responsibilities

## Probe

- Lane: `staff-responsibilities`
- Mode: `static-pinned-file`
- Image: `game_plugin.dll`
- SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- Image base: `0x180000000`
- Types reported: `13`
- Vtables reported: `11`
- Live records read: `0`
- Output truncated: `true`

This evidence is static RTTI only. It does not read process memory, game files, saves, UI, or network resources.

## Confirmed RTTI types

| RTTI type | Type RVA | Category |
|---|---:|---|
| `.?AVHUMAN_NON_PLAYER@db@@` | `0x568A2E0` | business-object candidate |
| `.?AVEXTERN_ACTUAL_NON_PLAYER@db@@` | `0x569D170` | business-object candidate |
| `.?AVEXTERN_HUMAN_NON_PLAYER@db@@` | `0x569DF90` | business-object candidate |
| `.?AV?$_Func_impl_no_alloc@...generate_past_match_chalkboard_data...lambda_1...@std@@` | `0x56A4500` | implementation artifact |
| `.?AV<lambda_1>@...generate_past_match_chalkboard_data...` | `0x56A4620` | implementation artifact |
| `.?AV?$_Func_impl_no_alloc@...generate_past_match_chalkboard_data...lambda_0...@std@@` | `0x56A46C0` | implementation artifact |
| `.?AV?$_Func_impl_no_alloc@...lambda_1 inner...@std@@` | `0x56A4790` | implementation artifact |
| `.?AV<lambda_1>@...lambda_0 inner...` | `0x56A4880` | implementation artifact |
| `.?AV<lambda_0>@...generate_past_match_chalkboard_data...` | `0x56A4950` | implementation artifact |
| `.?AV?$_Func_impl_no_alloc@...load@HUMAN_NON_PLAYER...lambda_0...@std@@` | `0x56A5F30` | implementation artifact |
| `.?AV<lambda_0>@...load@HUMAN_NON_PLAYER...` | `0x56A6090` | implementation artifact |
| `.?AVACTUAL_NON_PLAYER@db@@` | `0x56A6160` | business-object candidate |
| `.?AVACTUAL_PLAYER_AND_NON_PLAYER@db@@` | `0x56E1AD0` | business-object candidate |

## Confirmed vtables

| Vtable RVA | RTTI type | Slots |
|---:|---|---|
| `0x4CBC938` | lambda_1, chalkboard | `0xE70FD0, 0xE70FF0, 0xE71010, 0xE712B0, 0xE712C0, 0xE712D0, invalid, invalid, 0x56A44FE80000000, 0x4CBC96E84CBC988, invalid, 0x4CBC99680000002` |
| `0x4CBCA68` | lambda_0, chalkboard | `0xE71410, 0xE71430, 0xE71450, 0xE71720, 0xE71730, 0xE71740, invalid, invalid, 0x56A46BE80000000, 0x4CBCA9E84CBCAB8, invalid, 0x4CBCAC680000002` |
| `0x4CBCB08` | lambda_1, inner chalkboard | `0xE71750, 0xE71770, 0xE71790, 0xE71880, 0xE71890, 0xE718A0, invalid, invalid, 0x56A478E80000000, 0x4CBCB3E84CBCB58, invalid, 0x4CBCB6680000002` |
| `0x4CC0888` | `HUMAN_NON_PLAYER` | `0xF47460, 0x19260A0, 0xF2FCC0, 0xF2FDC0, 0xF47480, 0xF47490, 0xF474A0, 0xF474C0, 0xF474E0, 0x4CC11B0, 0xF474F0, 0xF29C90` |
| `0x4CC08D8` | `HUMAN_NON_PLAYER` | `0xF474F0, 0xF29C90, 0xF25BD0, 0xF47680, 0xF47710, 0xF47730, 0xF47760, 0x5E6920, 0xF80D60, 0xF75E90, 0x4143D0, 0xF6E0A0` |
| `0x4CC11D8` | lambda_0, load | `0xF5ED10, 0xF5ED30, 0xF5ED50, 0xF5F270, 0xF5F280, 0xF5F290, invalid, invalid, 0x56A5F2E80000000, 0x4CC120E84CC1228, invalid, 0x4CC123680000002` |
| `0x4D8BE28` | `ACTUAL_NON_PLAYER` | `0x17DB6C0, 0x19260A0, 0x16336A0, 0x17ED170, 0x17EC7C0, 0x17EC7B0, 0x17EC9E0, 0x17EC790, 0x17EFE30, 0x4D8C600, 0x17EFE40, 0x17EB900` |
| `0x4D8BE78` | `ACTUAL_NON_PLAYER` | `0x17EFE40, 0x17EB900, 0x17DFCA0, 0x17DB6D0, 0x17DD370, 0x17EFFD0, 0x17F0000, 0x5E6920, 0xF80D60, 0xF75E90, 0x4143D0, 0xF6E0A0` |
| `0x4F75A08` | `ACTUAL_PLAYER_AND_NON_PLAYER` | `0x16361F0, 0x15D4F70, 0x15F7060, 0x15F7070, 0x15D4F80, 0x15D4F60, 0x15D4F50, 0x15F7F00, 0x15EAF40, 0x15EB200, 0x15EAF30, 0x15E1760` |
| `0x4F75EE8` | `ACTUAL_PLAYER_AND_NON_PLAYER` | `0x3991BC0, 0x19260A0, 0x16336A0, 0x17ED170, 0x3991D80, 0x3991D70, 0x3991D90, 0x39920F0, 0x3992150, 0x4F76740, 0x3992170, 0x39920A0` |
| `0x4F75F38` | `ACTUAL_PLAYER_AND_NON_PLAYER` | `0x3992170, 0x39920A0, 0x3992030, 0x3991C50, 0x3991FF0, 0x3992310, 0x3992340, 0x5E6920, 0xF80D60, 0xF75E90, 0x4143D0, 0xF6E0A0` |

Note: `EXTERN_ACTUAL_NON_PLAYER` and `EXTERN_HUMAN_NON_PLAYER` appeared as RTTI types but no vtable was reported for them in this probe.

## Staff-specific type match

No staff-specific RTTI type was reported. The probe found only generic non-player types and implementation lambdas. This is an exact no-match for staff-specific names, not evidence that such types do not exist elsewhere.

Proposed narrower names for the next bounded probe:

- `STAFF`
- `STAFF_MEMBER`
- `NON_PLAYER_STAFF`
- `HUMAN_STAFF`
- `ACTUAL_STAFF`
- `EXTERN_STAFF`
- `COACH`
- `SCOUT`
- `MEDICAL_STAFF`
- `ANALYST`
- `STAFF_RESPONSIBILITY`

## Narrow business-object entry hypothesis

The only confirmed business-object entry candidates are the generic non-player types above. `HUMAN_NON_PLAYER` is the narrowest confirmed human non-player entry and has two confirmed vtables. It can support a future candidate read path for human non-player identity, but it is not proof of a staff record, staff collection, staff post, department, or responsibility assignment.

`ACTUAL_NON_PLAYER` and `ACTUAL_PLAYER_AND_NON_PLAYER` are related confirmed non-player entries. `EXTERN_*_NON_PLAYER` types are confirmed as type names only; no vtable or layout is confirmed. The lambda types and vtables are implementation artifacts for chalkboard generation and loading, not business-object entries.

## Exact missing semantics

- Staff-specific RTTI type and vtable.
- Staff collection entry point, enumeration, pagination, and loaded range.
- Staff UID identity and whether it uses `PERSON` UID, non-player UID, or another key.
- Post, department, role, responsibility, workload, and vacancy semantics.
- Staff contract linkage and whether it follows the manager `FULL_CONTRACT -> TEAM -> CLUB` candidate chain.
- Qualifications, technical/mental attributes, knowledge scope, career history, and recruitment records.
- Field offsets, sizes, enums, null representations, and all live validation.
- Any live read, game call, UI access, save access, or mutation.

## Next bounded read request

Authorize only a static RTTI follow-up for the proposed narrower names, with the same pinned binary hash and fail-closed profile. If a name matches, record its type RVA and any vtables only. Do not read records, fields, offsets, or process memory beyond the existing static RTTI scan budget. No live reader should be created until a staff-specific type and collection entry are confirmed.
