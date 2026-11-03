# Parallel player position/state audit (PLY-01, PLY-02, PLY-03, PST-01, MED-01)

Status: offline source/evidence audit only. Branch `research/parallel-player-position-state`.
No live process read, game install access, UI access, memory/save write, injection, native
call, match advance, network access or subprocess was used for this document.

## Task pin and evidence base

- Task-supplied documentation pin: upstream `01b53c5`.
- Task-supplied local evidence base: `99aba1d`.
- This audit did not execute git, so it does not independently re-verify either identifier.
  It records the pins supplied with the task rather than claiming a new commit link.
- Files inspected are the checked-out worktree at `tools/FMAPI.MessageProbe`,
  `tools/research`, `docs/research` and `src`. No raw capture, UID list, player name or
  private save output is reproduced here.
- All conclusions below are either (a) static source reading in this worktree,
  (b) synthetic self-tests present in source, or (c) documented prior live observations
  explicitly attributed to another checkpoint. They are not new runtime results.

## Evidence grades used here

| Grade | Meaning in this audit |
|---|---|
| `code+static` | Pinned-hash code path plus native/metadata cross-reference or an independent static decoder in the tree. |
| `code+synthetic` | The code path exists and has a synthetic test; no live comparison in this wave. |
| `observed (documented)` | A prior live observation is written in a repository checkpoint, but this audit cannot reproduce it offline. |
| `documented-external` | Only a prose claim about an external FA reader exists; no reader source/code is present in this worktree. |
| `not started` | No source path, candidate field or documented observation for the target was found. |

## Summary

| ID | Goal | Current grade | Repository evidence | Remaining gap |
|---|---|---|---|---|
| PLY-01 | Person UID, name, DOB, age basis, nationality, team/club, height, body info | `observed (documented)` for UID; `documented-external` for name/DOB/height; `not started` for nationality/age basis/player team-club | `EntityLinks.cs` UID match and manager employment chain | No player identity decoder or roster relation in this tree |
| PLY-02 | Position familiarity, natural mask, GK/outfield codes, preferred foot, verified semantics | `code+static` / `observed (documented)` for 14 familiarities and mask; `not started` for preferred foot and current match assignment | `PositionFields.cs`, `EntityLinks.cs`, `PositionCaptureDecoder.cs`, `position_layout_probe.py` | Foot, UI semantic comparison, current match/tactic assignment, broader enum members |
| PLY-03 | Technical/mental/physical/GK attributes with raw, display, scale and unknown fields | `documented-external` only in this worktree | No implementation; prose names four raw fields | Reader source/artifact, display scaling, full attribute coverage |
| PST-01 | Condition, match sharpness, fatigue, morale, happiness, availability reasons | `not started` | No implementation or candidate path | All target fields; depends on PLY-01 roster baseline and MED-01/REG-01 for availability |
| MED-01 | Injury type, date, expected return, training restriction, condition and injury risk | `not started` | No implementation or candidate path | All target fields; healthy/injured comparison and date semantics |

Partial evidence for one subfield is not completion of the whole task row.

## Pinned fingerprints and profiles

The player-position code fails closed unless these exact profiles match. They are reproduced
from existing repository source only.

| Artifact | SHA-256 / version | Source |
|---|---|---|
| `game_plugin.dll` | `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F` | `tools/FMAPI.MessageProbe/Program.cs:100`, `PositionFields.cs:6` |
| `GameAssembly.dll` | `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A` | `PositionFields.cs:7`, `EntityLinks.cs:75` |
| Installed metadata | `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`, signature `0xFAB11BAF`, version 39 | `PositionFields.cs:8`, `position_layout_probe.py:10-11,41` |

These are build-specific research profiles, not compatibility claims for another build,
platform, save or game mode.

## PLY-01 — identity and body basics

### Target decomposition

| Subfield | Status | Source | Evidence strength and limit |
|---|---|---|---|
| Person UID | observed (documented) | `tools/FMAPI.MessageProbe/EntityLinks.cs:47-67`; UID compared at `person+0x0C` | Requested 1-32 positive signed-int UIDs are binary-searched in the loaded ordered PERSON index; observed live 27/27 match is documented in `manager-player-links-checkpoint.md:31-35`. Cross-save stability is unverified (`EntityLinks.cs:122`). |
| Name | documented-external | `docs/research/data-discovery-todo.md:191` | Prose says the packaged external FA reader can read person names. No player-name implementation or reproducible sample is in this worktree. |
| Date of birth | documented-external | `docs/research/data-discovery-todo.md:191` | Only the prose claim `dob` exists. No getter, offset, type or validation in this tree. |
| Age basis | not started | — | No game-date/age-basis field or calculation was found. Age cannot be derived reliably from the external `dob` claim alone without a validated game date. |
| Nationality | not started | — | No source or documentation claim for player nationality was found in this worktree. |
| Player team/club | not started | — | Only the manager `FULL_CONTRACT -> TEAM -> CLUB` chain exists (`EntityLinks.cs:96-105`). Player roster membership is not rebuilt; `clubMembershipVerifiedHere=false` at `EntityLinks.cs:70`. The 27 UIDs came from an external roster input. |
| Height | documented-external | `docs/research/data-discovery-todo.md:191` | Prose claim `heightCm` only; no unit/scale/source location in this tree. |
| Other body info | not started | — | No weight, preferred foot data, or other physical fields found. Preferred foot also belongs to PLY-02 and is absent there. |

### What the current code actually proves

- The probe validates the `DATABASE_TABLE<PERSON>` root and type, then performs a bounded
  binary search over at most 32 sorted index steps per requested UID
  (`EntityLinks.cs:39-58`). It refuses a dirty sort cache instead of calling a game sort
  function.
- A matched record must be an exact `ACTUAL_PLAYER` PERSON subobject with the pinned vtable
  and RTTI, and the UID is re-read after the player block
  (`EntityLinks.cs:60-66`). This is a strong type/identity check for the observed build.
- The 27/27 live match is an observation recorded in
  `docs/research/manager-player-links-checkpoint.md:31-35`; this audit did not repeat it.
- UID is a candidate persistence key, not yet a cross-save stable public ID.

### Missing dependencies

- A verified player roster/team membership path (CLB-01/IDX-02), because the current probe
  accepts roster UIDs from outside and does not prove club membership.
- A validated game-date snapshot (ENV-01) before any age calculation.
- Recovery of the external FA reader source or a sanitized field sample for name/DOB/height.
  That artifact is not available in this worktree.

### Unknown semantics

- Which person name components (first/common/second, overrides, localized names) the
  external reader reports.
- DOB storage type and epoch, and whether the external `dob` is a calendar date or packed
  value.
- Height unit, scaling, rounding and whether it is current or historical.
- Whether person UID values persist across reloads and new saves.

### Minimal bounded follow-up read plan (not executed)

1. Recover or obtain the external FA reader's exact field paths for name/DOB/height; keep
   its source/licence review separate from this FMAPI worktree.
2. After coordinator scheduling, reuse `--entity-links` with at most 32 already validated
   UIDs and the existing 64 KiB budget. Add only new bounded reads for the recovered
   fields; do not add a registry-wide scan.
3. Compare values against the external reader or UI for the same save and game date.
   Record `capture_id`, build, game date and load epoch. Do not commit raw values.
4. Treat nationality, age basis and player team/club as unavailable until a dedicated
   entry point is found.

## PLY-02 — position familiarity and natural mask

### Proven field map

The mapping below is static evidence, not a sample of any player. Offsets are relative to
the actual-player object; values are 0..20 familiarity bytes. The natural mask uses
threshold `>=18`; the goalkeeper business rule uses threshold `>=15`.

| Offset | Code | Native enum | Mask bit |
|---|---|---|---|
| `+0x150` | GK | Goalkeeper | `0x1` |
| `+0x152` | DL | DefenderLeft | `0x8` |
| `+0x153` | DC | DefenderCentre | `0x10` |
| `+0x154` | DR | DefenderRight | `0x4` |
| `+0x155` | DM | DefensiveMidfielderCentre | `0x80` |
| `+0x156` | ML | MidfielderLeft | `0x200` |
| `+0x157` | MC | MidfielderCentre | `0x400` |
| `+0x158` | MR | MidfielderRight | `0x100` |
| `+0x159` | AML | AttackingMidfielderLeft | `0x1000` |
| `+0x15A` | AMC | AttackingMidfielderCentre | `0x2000` |
| `+0x15B` | AMR | AttackingMidfielderRight | `0x800` |
| `+0x15C` | ST | AttackerCentre | `0x4000` |
| `+0x15D` | WBL | WingBackLeft | `0x40` |
| `+0x15E` | WBR | WingBackRight | `0x20` |
| `+0x151` | — | `SweeperCentreNotInUse` | skipped; retained only as `unusedSlot151Raw` |

Sources: `PositionFields.cs:11-18`; independent static recovery
`tools/research/position_layout_probe.py:102-112`; native loop/table and metadata pairing
`docs/research/native-entity-evidence.md:58-83`; prior observed sample summary
`docs/research/native-entity-evidence.md:85-87` and
`docs/research/manager-player-links-checkpoint.md:63-65`.

### Code path

- `EntityLinks.cs:37-71` reads 15 bytes at `player+0x150`, requires every value in 0..20,
  re-reads the UID and block, then calls `PositionFields.Decode`. It reports
  `positionNamesVerified=true` only after decoding under the pinned profile.
- `EntityLinks.cs:12-36` is an exploratory first-64-slots mode, capped at eight actual
  players. It is explicitly not a club roster (`notClubRoster=true`).
- `PositionFields.cs:19-25` computes 14 named familiarities, the natural mask and natural
  codes, preserves `+0x151`, and keeps `businessRuleIsGoalkeeper` separate.
- `PositionCaptureDecoder.cs:6-33` decodes an existing private capture offline; it requires
  the pinned native hash, 1-32 records, a complete 14-byte tail and a new output path
  outside the repository. It does not open a process.
- Synthetic coverage is in `PositionFields.cs:26-36`: left/right mapping, reserved slot,
  17/18 natural boundary, 14/15 goalkeeper boundary, and malformed block sizes. CI runs
  this self-test at `.github/workflows/ci.yml:39-40`.

### Evidence strength

- The 14 name/offset/bit mappings are `code+static`: native table and loop plus independently
  paired metadata enum. The static script and C# decoder agree.
- The 27 requested-UID live result, two goalkeeper matches and nonempty natural masks are
  `observed (documented)` in the checkpoint, not re-run in this wave.
- This is interpretation under a proven layout and synthetic tests, not a UI comparison.

### Missing and unknown

- Preferred foot: no byte, getter, enum or metadata mapping was found. `not started`.
- Current match/tactic position assignment: explicitly unsupported
  (`EntityLinks.cs:122`). Familiarity is not current assignment.
- `AttackerRight` / `AttackerLeft` and other `PositionMask` members have no corresponding
  familiarity byte in the analyzed loop; the code correctly does not synthesize them.
- Whether all 14 bytes remain in 0..20 for every player state, and whether any position
  field changes with training/development, is not established.
- Natural-mask semantics are not yet compared with the game UI for GK and multiple outfield
  players in the same state.
- The static script needs separately supplied pinned binaries; those binaries are not in
  the repository and were not accessed in this wave.
- UID-to-roster provenance is external, so position values are player-linked only for the
  supplied UID set.

### Minimal bounded follow-up read plan (not executed)

1. Offline: re-run `position_layout_probe.py` only if the coordinator supplies the pinned
   binaries; compare its 14 rows with `PositionFields.cs`. No player records are read.
2. Static: locate a preferred-foot candidate from the pinned metadata/GameAssembly before
   adding any read. If none is proven, keep foot `not_started` rather than guessing a byte.
3. Live, later scheduling: one `--entity-links` capture with at most 32 known UIDs and the
   existing 64 KiB budget, including at least one goalkeeper and several outfield players.
4. Validation: compare position names/natural status against the same-save UI. Record
   only pass/fail and aggregate counts; keep raw bytes and names outside the repository.
5. Do not claim current lineup position, role or tactic slot from this field family.

## PLY-03 — attribute coverage

### Target decomposition

| Subfield | Status | Source | Limit |
|---|---|---|---|
| GK raw fields `reflexesRaw`, `handlingRaw` | documented-external | `docs/research/data-discovery-todo.md:191` | No attribute reader in this worktree; raw meaning/scale unverified here |
| Mental raw field `anticipationRaw` | documented-external | same | Only a prose name; no getter/offset |
| Physical raw field `jumpingRaw` | documented-external | same | Only a prose name; no getter/offset |
| Technical attributes | not started | — | No evidence |
| Remaining mental/body attributes | not started | — | No evidence |
| Display value and scaling | not started | — | No formula, UI comparison or raw-to-display mapping |
| Unknown fields | not started | — | No field catalog |

The inventory row says "partial implementation" because an external packaged FA reader is
reported to expose four raw fields. In this worktree the claim is documentation-only: there
is no `reflexesRaw`/`handlingRaw`/`anticipationRaw`/`jumpingRaw` source line, test or sample.
That is not enough to validate semantics, units or scaling, let alone "all attributes".

### Missing dependencies

- External FA reader source/artifact and provenance review; it is not present here.
- A pinned metadata/GameAssembly property audit to tie names to getters and offsets.
- At least one same-save display comparison for each claimed raw field.
- PLY-01 UID/roster baseline for joining attributes to players.

### Unknown semantics

- Whether each raw value is a 1..20 ability, a 0..100 internal value, or another scale.
- Rounding and display visibility rules, including masking by staff knowledge.
- Whether the four names are complete, correctly ordered, or current for this build.
- Attribute changes over time and training; none observed here.

### Minimal bounded follow-up read plan (not executed)

1. Recover the external reader's field list and offsets, with licence/provenance review.
2. Offline static audit of the pinned binaries: map each claimed name to a getter and
   object offset; record unknowns instead of inferring from value ranges.
3. Later live capture: read only the proven offsets for at most 32 known UIDs under the
   64 KiB budget; include synthetic boundary checks before any live run.
4. Compare raw and displayed values for the same player/save. Do not call range heuristics
   validation.

## PST-01 — condition, sharpness, fatigue, morale, happiness, availability

No implementation, candidate offset, field name or documented observation was found in this
worktree. The only related statements are broad dependencies in the inventory and the
availability acceptance criteria in `data-discovery-todo.md` (B package, line 288). Those
do not identify a field or prove readability.

### Missing dependencies

- PLY-01 UID and roster/team membership.
- MED-01 for injury/restriction reasons.
- REG-01 for suspension/registration reasons.
- ENV-01 for a game-date/phase baseline, because condition and sharpness are stateful.

### Unknown semantics

- Whether condition, match sharpness, fatigue, jadedness, morale and happiness are distinct
  fields or derived values.
- Update timing (daily, match, training) and whether values change without a new snapshot.
- Scaling and display rounding; no field is assumed to be 0..100 or 1..20.
- Availability is a composition of medical, registration, suspension and selection states;
  no single field may substitute for it.

### Minimal bounded follow-up read plan (not executed)

1. Offline static candidate audit only: search pinned metadata/property registrations for
   the distinct concepts and record candidate names/RVAs. A name alone is `candidate`, not
   a field.
2. Require an independent getter/offset path and range check before adding a read.
3. Later live capture of at most 32 known UIDs under the 64 KiB budget, with a healthy,
   tired and (if available) injured player in the same state.
4. Validate each concept separately against the same-save UI. Keep unknown where no UI
   comparison exists; never map one value onto another concept.
5. Availability output must remain `unknown` unless every contributing check is known.

## MED-01 — injury and medical availability

No implementation, candidate offset, field name or documented observation was found in this
worktree. No prose claim in this tree says the external FA reader exposes injury type, injury
date, expected return, training restriction or injury risk.

### Missing dependencies

- PLY-01 UID/roster baseline.
- ENV-01 game date for injury date and expected-return intervals.
- REG-01 to separate injury unavailability from suspension/registration unavailability.
- Later access to at least one injured and one healthy player in the same save and state.

### Unknown semantics

- Injury type representation (enum, localized key or record reference).
- Whether the injury date is a calendar date, day-of-year, or duration.
- Expected return as a date, a day count, a range, or a UI-derived estimate.
- Training restriction and injury-risk fields; none are named in this tree.
- Recurrence, severity and medical-staff knowledge effects; no evidence.
- Whether a missing injury field means healthy or merely unreadable; must stay `unknown`.

### Minimal bounded follow-up read plan (not executed)

1. Offline static audit of pinned metadata/property registrations for distinct injury,
   recovery and restriction concepts; retain only candidates with a getter/offset path.
2. Later live capture of at most 32 known UIDs under the 64 KiB budget, deliberately
   including a healthy player and, if the coordinator can schedule it, an injured player.
3. Re-read the same state to test stability and, separately, after a scheduled game-date
   change to test date/return semantics. Do not advance matches in this research wave.
4. Validate against the same-save medical UI. Report `unknown` for every subfield without a
   comparison; do not infer injury type from text or from expected return.

## Cross-cutting unknowns and constraints

- No player names, UIDs, raw slot arrays or capture contents are included in this document.
- UID persistence is unproven across reloads; the current evidence is one session and one
  supplied roster set.
- External reads are non-atomic and have no native lifetime lock; this restricts any future
  multi-field snapshot claim.
- Player roster membership is not rebuilt by the current probe. All player-position results
  inherit the external UID input provenance.
- Position familiarity, current match assignment, tactical role and preferred foot are four
  different concepts and must not be substituted for each other.
- Condition, sharpness, fatigue, morale and happiness are treated as distinct targets until
  separate evidence exists.
- Availability must not be inferred from absence of an injury read or from one boolean.
- No SDK design, adapter contract, compatibility claim or write capability is introduced.

## Historical evidence vs this-wave offline artifacts

Historical evidence (prior live or documented work, not reproduced in this wave):

- `manager-player-links-checkpoint.md`: 27/27 requested UID matches, two goalkeeper-rule matches,
  nonempty natural masks, contract/team/club chain for the manager, FULL_CONTRACT kind 16.
- `native-entity-evidence.md`: GCuM current-selected manager pointer and named familiarity
  static decoding.
- `data-discovery-todo.md:191`: external FA reader names for uid/name/dob/heightCm and
  reflexesRaw/handlingRaw/anticipationRaw/jumpingRaw.
- `message-reader-checkpoint.md`: message/template/localization route work, unrelated to this lane.

This-wave offline artifacts (new, no live reads):

- `docs/research/parallel-player-position-state.md` (this note).
- Narrow inventory row evidence corrections in `docs/research/interface-inventory.md`.
- No new code, SDK, adapter, decoder, capture or private sample.

No live read was performed in either category during this wave.

## Single most concrete missing relationship and bounded plan

The most concrete missing entry/property relationship in this lane is the **player person
to current team/club employment chain** (analogous to the proven manager chain
`FULL_CONTRACT -> TEAM -> CLUB` in `EntityLinks.cs:96-105`). The current probe only
validates person UID and actual-player type; it does not resolve a player's contract,
team or club, and it accepts roster UIDs from external provenance
(`clubMembershipVerifiedHere=false`, `EntityLinks.cs:70`).

No safe pure decoder can be added from source evidence alone: there is no proven player
contract offset, virtual getter, RTTI path or metadata property for player employment in
this tree. Inventing one would violate the no-invention constraint. This is the explicit
blocker for PLY-01 team/club membership and for any roster-level position/condition join.

Bounded read plan for a later scheduled live/static wave (not executed now):

1. Static first: audit pinned `game_plugin.dll`/`GameAssembly.dll` metadata for player
   employment/contract/team/club properties and getters, mirroring the manager chain proof
   in `native-entity-evidence.md`. Retain only candidates with a getter/offset path.
2. If and only if a getter path is proven, extend `--entity-links` to read that path for
   at most 32 known UIDs within the existing 64 KiB budget, with root/vector rechecks and
   no native calls or sorting.
3. Validate against the same-save UI/external reader for at least one player. Report
   `unknown` for any subfield without a comparison.
4. Preferred foot, condition/sharpness and injury fields remain blocked on their own
   static anchors and are not folded into this relationship.

## Completion summary

### Completed (audit work, not full interface delivery)

- PLY-01: exact UID lookup path, person/actual-player type validation, manager contract chain
  and documented 27/27 observation consolidated with source locations.
- PLY-02: all 14 named position familiarities, natural-mask threshold `>=18`, goalkeeper
  business threshold `>=15`, skipped `+0x151`, offline decoder and synthetic checks
  consolidated with source locations.
- PLY-03: documentation-only status and the four external raw-field claims are now bounded
  and separated from validated capability.

### Candidate

- PLY-02 preferred foot: no candidate byte yet; only a follow-up static audit is proposed.
- PLY-03 full attribute set: four externally reported raw names are candidates pending
  source recovery and getter/offset evidence.
- PLY-01 name/DOB/height: external apparatus is a candidate source, not a reproducible
  in-tree capability.

### Missing

- PLY-01: nationality, age basis, player team/club membership in this tree, and in-tree
  name/DOB/height implementation.
- PLY-02: preferred foot, current match/tactic position assignment, UI semantic validation,
  and broader enum members without bytes.
- PLY-03: technical/mental/body/GK complete coverage, display scaling and unknown fields.
- PST-01: all target fields and any candidate entry point.
- MED-01: all target fields and any candidate entry point.

These missing items mean PLY-01, PLY-02 and PLY-03 remain partial, and PST-01/MED-01 remain
not started. No task row is fully complete.

## Live-read statement

No live read was performed for this document. No process was opened, no game install, UI,
save or private capture was accessed, and no runtime result is claimed.
