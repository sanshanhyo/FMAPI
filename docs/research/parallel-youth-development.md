# Youth development research audit (YTH-01 / YTH-02 / YTH-03)

Status: offline research only; no SDK design, no live process read, no game writes.

## Scope and IDs

- IDs in scope: `YTH-01`, `YTH-02`, `YTH-03` (read-side only).
- Related write/event rows (`YTH-W01`, `YTH-E01`) are out of scope for this wave and remain unstarted.
- Task branch: `research/parallel-youth-development`.
- Pinned upstream FMAPI commit referenced by task: `01b53c5`.
- Local research base referenced by task: `research/alawell-message-reader` commits `10a5724`, `d1f5177`, `99aba1d` (not accessible in this worktree; treated as unavailable evidence, not re-invented).
- Prior CI commit referenced in repo: `48331a5`.

## Pinned runtime/profile hashes (from existing evidence)

- `game_plugin.dll` SHA-256: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- `GameAssembly.dll` SHA-256: `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`
- UnityPlayer product: `6000.3.18f1-custom` (`96cdb67fb884`), file `6000.3.18.9883062` (from `docs/research/message-reader-checkpoint.md`)
- Il2Cpp metadata signature/version: `0xFAB11BAF` / `39` (from `docs/research/native-entity-evidence.md`)
- All RVAs/offsets below apply only to the pinned `game_plugin.dll` hash; a different hash must fail closed.

## Audit method

Offline only. No process, game install, UI, private captures, credentials, account configuration, network or writes were accessed. No bash/subprocess, no scans, no injection, no native calls, no match advancement. Sources audited: repository documentation, research checkpoints, and the checked-in C# probe sources. No new memory reads were performed.

## Existing source locations audited

| Source | Relevant content | Youth-specific? |
|---|---|---|
| `docs/research/interface-inventory.md` (YTH-01..03, YTH-W01, YTH-E01 rows) | Task definitions and dependency declarations | No runtime evidence |
| `docs/research/data-discovery-todo.md` (YTH-01..03 rows, section 4 group B) | Discovery goals and acceptance criteria | No runtime evidence |
| `docs/research/native-entity-evidence.md` | Binary fingerprints, GCuM selection, PERSON registry, goalkeeper predicate, position masks | No youth/acadey/team-hierarchy evidence |
| `docs/research/manager-player-links-checkpoint.md` | Human manager -> `FULL_CONTRACT` -> `TEAM` -> `CLUB`; PERSON UID lookup; goalkeeper familiarity | Adjacent: proves club/team/contract/person linkage only |
| `docs/research/message-reader-checkpoint.md` | Welcome message `TEAM` -> `CLUB` short name, name overrides, person text service | Adjacent: club/team relation and short-name candidates only |
| `tools/FMAPI.MessageProbe/EntityLinks.cs` | `DATABASE_TABLE<PERSON>` UID lookup; club `+0x30` team link; club `+0x0C` UID; contract `+0x10` team | Adjacent: reusable UID/club/team relation |
| `tools/FMAPI.MessageProbe/Program.cs` | Welcome relations: `team +0x20` override, `club +0xC8` name, `club +0xBA` standalone flag, `club +0xD0` alternate names, `team +0x28` name-kind | Adjacent: club/team metadata candidates only |
| `src/FMAPI.Sdk/*`, `src/FMAPI.Core/*` | SDK/Core contracts and host policy | No youth domain model or native adapter |
| `src/FMAPI.Adapters.Mock/*` | Synthetic adapter | Not real game data; not evidence |
| `tools/research/*` | Legacy exploratory tools | No youth-specific offsets or RTTI fragments recorded |

## Reusable proven work (adjacent, not youth-specific)

- `HUMAN_NON_PLAYER_MANAGER` root at RVA `0x56F3008`, primary vtable RVA `0x4E2D678`; human owner vector at `+0x18/+0x20/+0x28` (single-owner requirement, active selection via GCuM).
- `GCuM` selection global at RVA `0x56F32C8`, key `0x4743754D`, with HUMAN_NON_PLAYER PERSON RTTI validation.
- Employment chain: PERSON virtual `+0x3C0` (RVA `0xF48D30`) -> vbtable signed offset -> virtual base `+0x80` `FULL_CONTRACT`; contract `+0x10` -> `TEAM`; team `+0x30` -> `CLUB`; club `+0x0C` UID.
- `FULL_CONTRACT` kind byte at `+0x26` (observed value `16`, raw only; native affiliation paths require `>=2`).
- `DATABASE_TABLE<PERSON>` at RVA `0x5703738`, vtable RVA `0x4CA5278`; UID lookup by `+0x0C`, ordered index, dirty-cache refusal.
- Club metadata candidates: `+0x0C` UID, `+0x20` team short override, `+0x28` name-kind, `+0xBA` standalone flag, `+0xC8` short name, `+0xD0` alternate-name vector.
- PERSON UID field at `+0x0C`; actual-player subobject conversion via PERSON virtual `+0x680` (RVA `0x16360E0`), displacement at `-4`, minus `0x288`.
- Position familiarity block at actual-player `+0x150..+0x15E` (15 bytes), goalkeeper business rule `>=15`, natural-position mask threshold `18`.

None of the above establishes youth/reserve/academy squads, age groups, intake, trials, assessments, mentors, promotion/loan state, or historical youth output.

## Field meaning audit (YTH-01)

Target: youth/reserve squads, rosters, coaches, fixtures, promotion/loan-out, current development state.

| Candidate field / relation | Source | Meaning status | Evidence strength |
|---|---|---|---|
| Club UID (`+0x0C`) | `EntityLinks.cs` club read | Club identity entry point | Observed (single club, one session) |
| Team UID (`+0x0C`) | contract->team read | Team identity entry point | Observed |
| Contract->team (`+0x10`) | `EntityLinks.cs` | Employment team linkage | Observed |
| Team->club (`+0x30`) | `EntityLinks.cs` | Team ownership linkage | Observed |
| Club short name (`+0xC8`) | `Program.cs` | Candidate club name | Candidate |
| Team short override (`+0x20`) | `Program.cs` | Candidate override text | Candidate |
| Team name-kind (`+0x28`) | `Program.cs` | Raw kind byte; semantics unknown | Raw only |
| Club standalone flag (`+0xBA`) | `Program.cs` | Raw flag; semantics unknown | Raw only |
| Club alternate names (`+0xD0`) | `Program.cs` | Candidate name records | Candidate |
| Manager employment club UID | `EntityLinks.cs` | Current human manager's club | Observed (single session) |
| Reserve/youth team membership | None | Unknown whether reserve/youth are separate TEAM/CLUB objects or attributes | Missing |
| Age group / squad type | None | Unknown | Missing |
| Promotion / loan-out state | None | Unknown | Missing |
| Current development state | None | Unknown; no training/development fields audited here | Missing |

## Field meaning audit (YTH-02)

Target: academy intake batches, trials, assessment reports, development, mentor links.

| Candidate dependency | Source | Status |
|---|---|---|
| Scouting reports / assessment (`SCT-02`) | Inventory | Unstarted; no implementation evidence |
| Person UID registry | `EntityLinks.cs` | Observed lookup only; no academy intake fields |
| Trials / intake batches | None | Missing |
| Mentor / development links | None | Missing |
| Assessment report content | None | Missing |

## Field meaning audit (YTH-03)

Target: historical youth output, compensation/joint-mechanism records, long-term queue.

| Candidate dependency | Source | Status |
|---|---|---|
| Registration rules / quotas (`REG-02`) | Inventory | Unstarted |
| Historical season data (`HIS-01`) | Inventory | Unstarted |
| Compensation / joint-mechanism records | None | Missing; no evidence any such record is readable |
| Long-term queue | None | Missing |

## Evidence strength summary

- Youth-specific implementation evidence: none.
- Adjacent reusable evidence (club/team/contract/person UID linkage): observed in one loaded session for one human manager; not validated across reload, multiple managers, or youth squads.
- No youth RTTI type names, offsets, or collection entry points were located in checked-in code.
- No runtime capture containing youth/reserve teams or players is present in the repository.
- Synthetic mock adapter data is not evidence of game behavior.

## Missing dependencies

- `CLB-01`: club/team hierarchy and reserve/youth distinction unverified.
- `PLY-01`: player UID/team/club observed but not youth-scoped.
- `SCT-02`: scouting/assessment reports unstarted (needed for YTH-02).
- `REG-02`: registration windows/quotas unstarted (needed for YTH-03).
- `TRA-02` / training development (referenced by TRA-03) unstarted.
- A coordinator-scheduled live capture of a loaded save containing visible youth/reserve teams and players.
- Access to the unpushed local commits `10a5724`, `d1f5177`, `99aba1d` to confirm no youth offsets were already discovered there (currently unavailable in this worktree).

## Unknown semantics

- Whether reserve/youth squads are separate `TEAM`/`CLUB` objects or attributes/flags on a club.
- How age groups and squad types are encoded.
- Whether youth players appear in the same `PERSON` registry and club roster vectors.
- Promotion, loan-out, intake, trial, assessment, mentor, and development-state representations.
- Historical youth output, compensation/joint-mechanism records, and long-term queue storage.
- Whether any of the above are loaded in a typical save or require specific game state.

## Minimal bounded follow-up read plan (future, coordinator-scheduled)

Offline/static (no process):
1. Use the pinned `game_plugin.dll` with the existing `PeProbe` style RTTI scan for fragments `YOUTH`, `RESERVE`, `ACADEMY`, `DEVELOPMENT`, `INTAKE`, `TRIAL` (read-only PE scan, no process). Record type names and vtables only; do not claim semantics.
2. Reuse the proven club/team UID relation to identify candidate child-team vectors on a club object (bounded field scan of already-known club offsets; no full memory scan).

Live (only when coordinator schedules; not this wave):
3. One bounded capture of a loaded save with visible youth/reserve teams: read the human manager's employment club, then a bounded child-team vector (if found) with at most 16 entries, and at most 8 player UIDs per team.
4. For each candidate, read only already-proven fields: UID (`+0x0C`), type name, and club/team linkage; record raw bytes for unknown fields without decoding.
5. Budget: aggregate read budget <= 64 KiB; at most 32 UIDs; process recheck before/after; fail closed on any change. No writes, no UI, no match advancement, no save changes.

Deliverables per `data-discovery-todo.md` section 4: `inventory.csv`, `findings.md`, `sample.sanitized.json`, `validation.md`, `handoff.md` in `docs/research/data/youth-development/` (or equivalent), sanitized, with exact source paths, build hash, and tested range.

## Completed / candidate / missing

- Completed (validated): 0 youth-specific fields.
- Candidate (reusable adjacent evidence): club/team/contract/person UID linkage and club metadata candidates listed above; none validated for youth semantics.
- Missing: all goals of YTH-01, YTH-02, YTH-03; all listed dependencies; all youth-specific RTTI/offsets/collections.

## Live read status

No live read performed. No process, game install, UI, private capture, credential, account configuration, network, scan, injection, native call, write, or match advancement occurred during this audit.
</content>
