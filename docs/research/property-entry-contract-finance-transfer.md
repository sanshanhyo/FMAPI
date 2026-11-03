> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property entry: contract, finance and transfer

Status: **static property-candidate evidence only. No process memory was read.**

Lane: `contract-finance-transfer`. Probe mode: `static-property-candidates`,
`matches=6`, `liveRecordsRead=0`, `truncated=false`. Pinned `game_plugin.dll`
SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`,
image base `0x180000000`. Pinned `GameAssembly.dll` SHA-256:
`820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`. Metadata
signature/version: `0xFAB11BAF` / `39`.

## Actual executed evidence

Command:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'contract-finance-transfer'
```

Returned candidates:

| Name | Literal index | Slot RVA | Semantics |
| --- | --- | --- | --- |
| `DebugContractExpiryAnalysis` | 6679 | `0x32b2b68` | `unverified-property-name` |
| `DebugContractExpiryAnalysisAverage` | 6680 | `0x32b2c68` | `unverified-property-name` |
| `DebugContractExpiryAnalysisItem` | 6681 | `0x32b2d58` | `unverified-property-name` |
| `DebugContractExpiryAnalysisOverviewReference` | 6682 | `0x32b2e58` | `unverified-property-name` |
| `DebugContractExpiryAnalysisTableList` | 6683 | `0x32b2f68` | `unverified-property-name` |
| `LastContractWage` | 11871 | `0x32a3708` | `unverified-property-name` |

No native keys, entry RVAs, functions, or offsets were returned. These remain
`null` or `unknown` in `tools/research/property_entry_contract_finance_transfer.py`.

## UI/news/operations versus business fields

- `DebugContractExpiryAnalysis*`: names indicate debug contract-expiry analysis
  views. They are UI, news, operations, or debug surfaces until proven
  otherwise; they are not business fields.
- `LastContractWage`: the only candidate whose name suggests a wage value. It is
  a business-field candidate only. It is not proof of a wage field, unit,
  currency, scale, or pay period.
- None of the returned names establishes a contract date, status, wage, finance
  amount, budget, transfer, loan, offer, or negotiation field.

## Dependency sharpening

New coordinator evidence used for this lane:

- Current club2 TEAM pointers match their `TEAM_BASE` low 23-bit index entries
  2/2.
- `NextFixture` literal 13696, slot `0x330B698`, native key `0x6E654669` first
  resolves `TEAM_BASE` context via global `0x5703768`, not fixtures.

Consequence: a property registration or literal slot is not enough to identify a
business object. Context resolution must be proven before any entry or field
claim. This lane therefore keeps all native keys, entry RVAs, functions, and
offsets null/unknown.

## Ranked next registrations to inspect

1. `LastContractWage` (`11871`, `0x32a3708`) - only wage-named candidate.
2. `DebugContractExpiryAnalysisOverviewReference` (`6682`, `0x32b2e58`) - likely
   aggregate analysis view.
3. `DebugContractExpiryAnalysisTableList` (`6683`, `0x32b2f68`) - possible
   collection/view shape.
4. `DebugContractExpiryAnalysisItem` (`6681`, `0x32b2d58`) - item-level view.
5. `DebugContractExpiryAnalysisAverage` (`6680`, `0x32b2c68`) - derived display
   value.
6. `DebugContractExpiryAnalysis` (`6679`, `0x32b2b68`) - view/container root.

## Next bounded live request

One precise request is supported: inspect `LastContractWage` (literal index
`11871`, slot RVA `0x32a3708`) in a bounded static metadata/native-key
resolution pass against the pinned `GameAssembly.dll`, and record either its
resolved native key/context or `unavailable`. This is static file analysis only;
it must not open a process, read memory, claim a field offset, or execute a game
function.

## Machine-readable manifest

`tools/research/property_entry_contract_finance_transfer.py` contains the same
candidate evidence as a JSON manifest and validates supplied manifests against it.
Unresolved native keys and offsets remain `null` or `unknown`; no functions are
fabricated. Run `python tools/research/property_entry_contract_finance_transfer.py --self-test`.
