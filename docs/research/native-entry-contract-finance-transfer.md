> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry: contract, finance and transfer

Status: **static pinned-file probe evidence only. No process memory was read.**

Lane: `contract-finance-transfer`. Probe mode: `static-pinned-file`, `liveRecordsRead=0`,
`outputTruncated=true`. Pinned image SHA-256:
`BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`,
image base `0x180000000`.

## Actual probe evidence

Types returned by the probe:

| RTTI | RVA |
| --- | --- |
| `.?AVFULL_CONTRACT@db@@` | `0x567B9A0` |
| `.?AVEXTERN_FULL_CONTRACT@db@@` | `0x569DE60` |

Vtable returned by the probe:

| Owner | Vtable RVA | Slots |
| --- | --- | --- |
| `.?AVFULL_CONTRACT@db@@` | `0x4B00AE8` | `0x301930`, `0x23437E0`, `0x2342E00`, `0x2337DD0`, `0x2338F30`, `0x2339040`, `0x23390A0`, `0x23532F0`, `0x301960`, `0x2347930`, `0x301970`, `0x301980` |

The probe also returned 21 RIP candidates whose target is the confirmed
`FULL_CONTRACT` vtable `0x4B00AE8`. Their function/displacement pairs are
recorded in `tools/research/entry_contract_finance_transfer.py` as
`ripCandidates`; representative entries include function `0x3006D0`
(displacement `0x300ABF`), `0x574000` (`0x5741BC`), `0xB04930`
(`0xB04B90` and `0xB04E39`), and `0x1886B90` (`0x1886D15`).

No additional type, vtable, field, or collection evidence was returned. In
particular, no `PLAYER_CONTRACT`, finance, budget, transfer, loan, offer, or
negotiation type appeared.

## Narrow business-object entry hypothesis

`FULL_CONTRACT` is the only confirmed contract entry point in this evidence.
Consistent with the existing manager-employment chain, it is the narrowest
credible business object for a contract relation: `FULL_CONTRACT` vtable at
`0x4B00AE8`, with the previously established manager-only chain
`FULL_CONTRACT +0x10 -> TEAM`, `TEAM +0x30 -> CLUB`, and `CLUB +0x0C` UID.
That chain is manager employment only; it is not proof of player-contract,
finance, or transfer semantics.

`EXTERN_FULL_CONTRACT` is a second confirmed RTTI name, but this probe provides
no vtable, slot, field, or relation evidence for it. It is a type-only
candidate for an external/non-manager contract variant and must not be treated
as a confirmed entry until vtable and relation evidence exist.

Finance and transfer remain without an entry point. The only reusable anchor is
the `CLUB` object and its UID candidate from the manager chain. No balance,
budget, wage-budget, used-wage, transfer, loan, renewal, offer, party, stage, or
deadline object is confirmed.

## Exact missing semantics

- Contract start and expiry date fields/offsets.
- Contract status enum semantics beyond the raw `contract +0x26` kind byte.
- Wage raw value, scale, currency, and pay period.
- Whether `FULL_CONTRACT` covers player, free-agent, youth, or loan contracts.
- Player UID to contract instance entry point and multiplicity.
- Bonus, clause, option, signing-fee, promised-playing-time, and loan-share fields.
- Finance object entry point and ownership (club vs board).
- Balance, transfer budget, wage budget, and used wage fields/units.
- Transfer/loan/renewal/offer/negotiation object types, parties, stages, deadlines, and state.
- `EXTERN_FULL_CONTRACT` vtable and any field layout.
- Any field offset beyond the confirmed type/vtable evidence.

## Next bounded read request

1. Run a static metadata/binary inventory against the pinned `game_plugin.dll`
   and metadata for RTTI/type names among `CONTRACT`, `PLAYER_CONTRACT`,
   `WAGE`, `FINANCE`, `BUDGET`, `TRANSFER`, `LOAN`, `OFFER`, and
   `NEGOTIATION`, recording type tokens and RVAs only. No process read.
2. If `EXTERN_FULL_CONTRACT` is selected, obtain its vtable and relation
   evidence before any field read.
3. For `FULL_CONTRACT`, prove one date or money field statically, then read
   only that field from the already-resolved manager contract and recheck the
   selection, contract, team, club, and kind at capture end.
4. For finance, resolve one club through an already established index and read
   only statically proven finance offsets; otherwise return `unavailable`.
5. For transfers, prove a transfer object type and collection/relation anchor
   statically before reading at most eight bounded objects.

All future reads must remain read-only, fail closed, use the pinned hashes, and
publish only sanitized field names, types, units, and provenance.

## Machine-readable manifest

`tools/research/entry_contract_finance_transfer.py` contains the same confirmed
type/vtable evidence as a JSON manifest and validates supplied manifests against
it. Unresolved offsets remain absent/`unknown`; no offsets are invented.
Run `python tools/research/entry_contract_finance_transfer.py --self-test`.
