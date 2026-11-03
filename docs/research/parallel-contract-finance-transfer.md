# Contract, finance and transfer: offline source audit

Status: **offline source audit only. No live process read was performed in this wave.**

This note covers task IDs CON-01, CON-02, FIN-01 and TRN-01 on branch
`research/parallel-contract-finance-transfer`, local base `99aba1d`. It records
what the checked-in source actually proves, reuses the already-committed
research instead of repeating discovery, and does not design an SDK. No game
process, install, UI, capture, credential, account setting, network or any input
outside this worktree was accessed. No scan, injection, native call, memory or
save write, or match advance was performed.

The repository contains no product code for these domains: `src/FMAPI.Sdk` has
no contract/finance/transfer types, and `src/FMAPI.Adapters.Windows` is an
explicitly unavailable placeholder. The only auditable native evidence for these
four domains is the read-only diagnostic under `tools/FMAPI.MessageProbe`.

## Pinned profile

All offsets below are module-relative and valid only for the pinned binaries.
The diagnostic refuses any other fingerprint before opening a process.

| Item | Value | Source |
| --- | --- | --- |
| `game_plugin.dll` SHA-256 | `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F` | `native-entity-evidence.md:7`, `tools/FMAPI.MessageProbe/Program.cs:100` |
| `GameAssembly.dll` SHA-256 | `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A` | `native-entity-evidence.md:8`, `tools/FMAPI.MessageProbe/EntityLinks.cs:75` |
| Metadata | signature `0xFAB11BAF`, version 39 (position work only; not re-audited here) | `native-entity-evidence.md:9` |
| Environment context | Unity `6000.3.18f1-custom` (`96cdb67fb884`) noted in the message checkpoint | `message-reader-checkpoint.md:69` |

Observed session date for the underlying research: 2026-11-02. The result was
single-session evidence and was never validated across reloads or saves.

## Shared anchors

These are the only reusable object anchors for the four IDs. None of them is a
finance or transfer reader.

- Current selected manager: global `moduleBase+0x56F32C8`; source property key
  `GCuM` (`0x4743754D`). See `native-entity-evidence.md:15-31` and
  `tools/FMAPI.MessageProbe/EntityLinks.cs:78,107-113`.
- Manager employment contract: the selected/human person's PERSON virtual base
  `+0x80` points at a FULL_CONTRACT (`EntityLinks.cs:96`). The exact type name
  `.?AVFULL_CONTRACT@db@@` is required (`EntityLinks.cs:98`).
- Contract kind: byte at `contract+0x26` (`EntityLinks.cs:100`); the native
  kind getter is FULL_CONTRACT virtual `+0x50`, RVA `0x301970`
  (`manager-player-links-checkpoint.md:15`, `EntityLinks.cs:101-102`). The raw
  value `16` was observed once; only the `>=2` affiliation check is interpreted
  (`manager-player-links-checkpoint.md:51`).
- Contract → employer team: pointer at `contract+0x10`, required to be TEAM
  (`EntityLinks.cs:103`).
- Team → club: pointer at `team+0x30`, required to be CLUB; club UID candidate
  at `club+0x0C` (`EntityLinks.cs:104`).
- End-of-capture rechecks for person identity, contract pointer, contract → team,
  team → club, club UID and kind byte (`EntityLinks.cs:114`).
- PERSON lookup/index used by the same probe: `DATABASE_TABLE<PERSON>` at
  `moduleBase+0x5703738`, ordered signed-UID index through `table+0x5C/+0x80`
  (`EntityLinks.cs:39-70`, `manager-player-links-checkpoint.md:23`).

## CON-01 — contract relation, dates, status, wage

**Evidence strength: observed, partial (relationship/type only). The task row is
not complete.**

Auditable source:

- `tools/FMAPI.MessageProbe/EntityLinks.cs:96-105,114` establishes that the
  current manager's employment record is a FULL_CONTRACT, reaches an employer
  TEAM and then a CLUB, and yields a raw kind byte.
- `docs/research/manager-player-links-checkpoint.md:15` records the native
  virtual getter RVA and the affiliation checks.
- `docs/research/manager-player-links-checkpoint.md:17` records an independent
  UID cross-check against an external read-only reader (producer manifest build
  `21bfd30`). That is a consumer cross-check, not cross-save UID stability.

Field meaning established here:

| Field | Location | Meaning | Strength |
| --- | --- | --- | --- |
| contract type | `contract` vtable RTTI | FULL_CONTRACT | observed |
| kind byte | `contract+0x26` | raw; value 16 observed | observed, semantics unknown |
| employer team | `contract+0x10` | TEAM pointer | observed |
| club | `team+0x30` | CLUB pointer | observed |
| club UID | `club+0x0C` | UID candidate | observed, same-session only |
| manager UID | person `+0x0C` | UID candidate | observed, same-session only |

Missing from this ID (no in-worktree evidence):

- Contract start date and expiry date offsets. No date field is read anywhere in
  the contract path.
- Contract status/enum semantics beyond the raw kind byte.
- Wage raw value, scale, currency and pay period. No wage field exists in the
  probe.
- Player-contract entry point. The audited chain is manager employment only; it
  is not proof that player contracts share this object, link direction or kind.
- Contract list/collection entry point and multiplicity (one contract pointer is
  read from the person virtual base).

Important provenance distinction: `docs/research/data-discovery-todo.md:191,303`
and `interface-inventory.md:42` state that an external FA reader has contract
dates and a raw-wage relation. That claim is **not reproducible from this
worktree**: no FA source, offsets, samples or tests for dates/wage are present.
It must remain a downstream user report, not upgraded by this audit.

## CON-02 — bonuses, clauses, options, loan share

**Evidence strength: missing.**

No checked-in source reads bonuses, signing fees, release clauses, renewal or
extension options, promised playing time, loan wage share, or special terms.
FULL_CONTRACT is the only contract type named in the diagnostics
(`EntityLinks.cs:98`), and only the kind byte, the contract→team pointer and the
team→club pointer are touched. There is no field-layout evidence for this task
and therefore no basis to name any clause field.

Dependency: CON-01 must first locate the contract field layout and prove the
applicable contract type(s). The task remains `not_started`.

## FIN-01 — balance, transfer budget, wage budget, used wage

**Evidence strength: missing. One indirect anchor only, not a finance read.**

No checked-in source reads any money value, budget, balance or accounting
object. The only relevant fact is that a CLUB object is reachable and its UID
candidate is at `club+0x0C` (`EntityLinks.cs:104`). That gives a potential club
anchor for a future Finance read but does not establish where finance data lives,
whether it is on CLUB or a separate object, or whether any of the target amounts
exist as readable fields.

No evidence in this worktree distinguishes:

- cash balance vs transfer budget vs wage budget vs used wage;
- raw scale, currency, or conversion to a display currency;
- club-level vs board-level ownership of a budget.

Dependencies CLB-01 and CON-01 are not complete for this purpose. LOC-01
(currency/scale/period dictionary) also remains unstarted. The task remains
`not_started`.

## TRN-01 — existing transfer/loan/renewal matters, parties, stage, deadline, offer state

**Evidence strength: missing.**

No checked-in source reads a transfer, loan, negotiation, offer or renewal
object. There is no established entry point, type name, party relation, stage
enum or deadline. The task remains `not_started`.

Explicit non-evidence: `message-reader-checkpoint.md:15` describes live message
types that include "manager departure", "manager appointment" and "media
transfer speculation". These are inbox/news message subtypes, not transfer
negotiation records. They must not be cited as TRN-01 evidence. The message
reader also has no transfer object link.

TRN-02 (valuation/offers) depends on TRN-01 and is out of scope here; TRN-01
must wait for a real transfer object entry point.

## Unknown semantics to keep explicit

- `contract+0x26` kind `16` is a raw observation. The only interpreted use is a
  `>=2` affiliation gate; the numeric value has no established meaning.
- `contract+0x10 → team+0x30 → club` is the manager's employer relation. It is
  not necessarily the counterparty club in any hypothetical transfer.
- FULL_CONTRACT coverage of player contracts, free agents, youth or loan
  contracts is unproven.
- No date, wage, currency, period, budget or offer field has been located.
- The existing external FA reader claims about dates and raw wage were not
  re-audited and remain unverified inside this repository.

## Minimal bounded follow-up plan (not executed here)

This plan is for a later coordinator-scheduled stage. It is deliberately small,
read-only and fail-closed, and reuses the existing 64 KiB aggregate capture
budget, per-read ≤8192 bytes and ≤32 requested objects. It does not authorize
scans, injection, native calls or writes.

1. **Offline static field inventory first (no process).** Using the already
   available `tools/research/StaticProbe` managed/map modes against the pinned
   binaries, enumerate metadata fields/methods whose names relate to
   `CONTRACT`, `PLAYER_CONTRACT`, `WAGE`, `FINANCE`, `BUDGET`, `TRANSFER`,
   `LOAN`, `OFFER` and `NEGOTIATION`. Record type tokens and RVAs only. This is
   static file analysis, not a process read, and needs a later execution stage.
2. **CON-01 bounded read.** Once a contract field offset is proven statically,
   read only that field from the already-resolved manager FULL_CONTRACT and, if
   a player-contract entry point is proven, from one explicitly supplied player
   UID. Recheck the selection pointer, contract pointer, type, team and club at
   the end of the capture. Do not scan for contracts.
3. **FIN-01 anchor check.** From the proven `club+0x0C` club UID, resolve one
   club through an already established index, then read only statically proven
   finance offsets. If no offset is proven, return `unavailable` rather than
   publishing a guessed amount.
4. **TRN-01 entry point search.** First prove a transfer object type and a
   collection/relation anchor statically. Only then read a bounded set (≤8
   objects) and report raw fields with unknown semantics. No message-derived
   speculation is accepted as a transfer record.
5. **Isolation / evidence.** Run only in a coordinator-scheduled live session
   with the pinned hashes; capture to a private path outside the repository;
   publish only sanitized field names, types, units and provenance. Every
   unsupported or absent field must remain `unavailable`.

## Provenance classification

- Historical evidence (pre-existing, not re-run this wave): local research commits through `99aba1d`, `docs/research/manager-player-links-checkpoint.md`, `native-entity-evidence.md`, `message-reader-checkpoint.md`, and `tools/FMAPI.MessageProbe` source. It supports only the manager employment chain and position decoding, not dates/wages/finance/transfers.
- This-wave offline artifacts: `docs/research/parallel-contract-finance-transfer.md` and the four narrowly relevant evidence notes in `docs/research/interface-inventory.md`. No capture, binary, UID array or process output was created.
- New live reads this wave: zero. No process, game install, UI, capture, credential, account setting, network, subprocess or out-of-worktree source was accessed.

## Evidence corrections (this wave)

- Metadata signature/version citation corrected to `native-entity-evidence.md:9` (line 8 is the `GameAssembly.dll` hash).
- Static field inventory step 1 was clarified: `tools/research/StaticProbe` can only run against the separately obtained pinned `game_plugin.dll` and metadata, which are not in this repository and were not accessed in this wave. It is a future execution-stage prerequisite, not an available offline artifact.
- No FA reader date/wage claim was upgraded. `interface-inventory.md:42` and `data-discovery-todo.md:191,303` remain downstream user reports with no in-repository offsets, samples or tests.
- No SDK, adapter, UI, persona, release or remote change was made.

## Single most concrete missing entry/property relationship

The most concrete missing relationship is **FULL_CONTRACT instance → its date and money fields** (start/expiry, status, wage raw/currency/scale/period). We know the exact object type and three pointers, but no field offset for any date or amount is established in checked-in source. The next most concrete is **player UID → contract instance**, because no player-contract entry point or collection anchor is established.

No safe pure decoder is supported by current source evidence: there is no checked-in game binary, metadata, capture JSON or field layout to decode. The bounded plan above is therefore the only honest artifact. The specific blocker is the absence of a pinned game binary/metadata or sanitized capture exposing contract fields; without it, any decoder would be invented.

## Completion summary

| ID | State after this audit | Auditable in-worktree evidence | Missing |
| --- | --- | --- | --- |
| CON-01 | partial / observed (relationship only) | FULL_CONTRACT type, kind byte, contract→team→club, UIDs | start/expiry dates, status semantics, wage raw/currency/scale/period, player-contract entry point |
| CON-02 | missing | none beyond the FULL_CONTRACT type | all clause/bonus/option/loan-share fields |
| FIN-01 | missing | only a CLUB object/UID anchor | all balance/budget/used-wage fields and units |
| TRN-01 | missing | none | all transfer/loan/renewal/offer objects and stages |

No live read, process access, scan, injection, native call, game/save write,
match advance, network access or push was performed. This audit only reads the
checked-in source and documentation in this worktree.
