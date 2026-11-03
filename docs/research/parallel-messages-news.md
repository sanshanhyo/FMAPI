# Messages, news and localization parallel audit

IDs: MSG-01, MSG-02, MSG-03, MSG-04, LOC-02. Branch: `research/parallel-messages-news`.

This is an offline source and evidence audit. **No live read was performed for this wave.** No game process, game install, UI, private capture, credential/account configuration, network or out-of-worktree data was accessed. No process scan, injection, native call, write, match advance, subagent, push or release was used. Existing runtime observations below are quoted only from the checked-in research records; they are not new measurements.

## Provenance and pinned profile

- Worktree content audited at the stated local base `99aba1d`; upstream pin `01b53c5` as supplied by the task.
- Native message evidence is pinned to `game_plugin.dll` SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`. A different binary must fail closed.
- Named-property/body evidence additionally uses `GameAssembly.dll` SHA-256 `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`; metadata signature/version `0xFAB11BAF` / 39 is recorded in the position evidence and is not a message-layout guarantee.
- Observed Unity runtime in the prior message record: product `6000.3.18f1-custom` (`96cdb67fb884`), file `6000.3.18.9883062`. This identifies the observed environment only; it is not a compatibility claim.
- All offsets/RVAs are module-relative to the pinned binaries. They are not stable SDK contracts.

## MSG-01: inbox identity, date, sender, recipient, category, read state, related entities

### Exact source locations

- `tools/FMAPI.MessageProbe/Program.cs:152-161` — human-manager root, single-owner check, owner `+0x350` inbox pointer, vector begin/end/capacity bounds, 32768-entry cap, read at most 32 entries.
- `tools/FMAPI.MessageProbe/Program.cs:166-170` — per-entry RTTI type, `+0x88` date word, `+0x90` identity candidate, end-of-capture recheck.
- `tools/FMAPI.MessageProbe/Program.cs:79-87` — date decoding: high word year, low 9 bits one-based day-of-year, leap-year handling, invalid sentinel `1900/1`, other bits ignored.
- `tools/FMAPI.MessageProbe/Program.cs:137-148` — RTTI/vtable type-name resolution used as the native message type.
- `tools/research/StaticProbe/Program.cs:143-161` — archived exploratory `live-inbox` route with fewer guards; same owner `+0x350` collection and `+0x88`/`+0x90` fields.
- `docs/research/message-reader-checkpoint.md:13-17` — `NEWS_MANAGER`, candidate collection, callback `0x107A200`, `+0x90` identity candidate, `+0x88` date-like field.
- `docs/research/message-reader-checkpoint.md:30` — single human manager, `+0x350` personal collection, at most 32 entries, multiple managers unsupported.
- `docs/research/message-reader-checkpoint.md:38-44` — native date formatter `0x9E56D0`, repeat-capture agreement, persistence limits.

### What the source establishes

- There is a bounded, read-only route from one validated human-manager owner to a vector of business message objects. The scope is explicitly `single-human-manager-associated-messages`; it is not proven to be the current player's inbox under multiplayer/hotseat or UI filtering.
- Each returned entry has a native RTTI type, a raw `uint32` date at `+0x88`, and an `int32` identity candidate at `+0x90`.
- The date layout is observed and repeat-checked for the pinned binary. The identity candidate is only an observed object field; cross-save, deletion and new-session persistence are unverified.
- Observed native types include manager departure, manager appointment, media transfer speculation and welcome-to-club in prior records. The type name is a candidate category, not a decoded category enum.

### Field meaning and evidence strength

| Target field | Source evidence | Strength | Limits |
|---|---|---|---|
| Inbox collection | owner `+0x350` vector | observed, bounded | one human manager; not active-user/multiplayer inbox |
| Date | `+0x88`, native formatter `0x9E56D0` | observed, repeat-checked | other packed bits unknown; no timezone |
| Identity | `+0x90` int32 | candidate | not a stable public ID; persistence untested |
| Category | RTTI type name | candidate | no category enum or UI mapping |
| Title | only welcome template `0xABDAF` | partial, template-only | general title and formatting unavailable |
| Sender | only welcome `+0x78` person and `+0xA0` team | candidate, message-type-specific | not a general sender contract |
| Recipient manager | ownership by `+0x350` collection | inferred, not a field | no recipient field or active-user check |
| Read/unread | none found | missing | — |
| Related entities | welcome `+0x78`/`+0xA0`; `+0x80` media source in prior record | candidate | no general relation extraction |

### Missing dependencies and unknown semantics

- Depends on MGR-01 (current manager) and IDX-01 (entity references). MGR-01 has a pinned native current-selected source for one observed session but no multiplayer/reload proof; IDX-01 is partial.
- Unknown: read/unread flag, ordering key, category enumeration, general sender/recipient fields, stable message key, attachment links, general related-entity rules, UI inbox filter, deletion/archival semantics.

### Minimal bounded follow-up read plan

1. Offline: statically inspect the `0x107A200` callback and adjacent message subclasses for read/unread, sender, recipient and category fields; use RTTI/metadata only, no address-space scan.
2. Later live, only when the coordinator schedules it: one `--verify-repeat` capture with the existing 64 KiB budget and at most 32 entries on a loaded save with exactly one human manager.
3. Compare one or two entries against a user-supplied UI observation for date/type/read state; do not automate UI, click, mark read, delete or archive.
4. Keep any output outside the repository and omit raw identities/text from public notes.

## MSG-02: body path, template parameters, complete/partial/unresolved state

### Exact source locations

- `docs/research/message-reader-checkpoint.md:54-64` — body property key `0x626F6479` → `NewsBodyString`; wrapper `0x179DBD0`; normal route `0x179DC10` → `0xE6B9680` → message virtual slot `0x170` with body flag; welcome implementation `0x36B0BC0`; body/title templates `0xA2A90`/`0xABDAF`; slot binding and context helper `0x424760`.
- `docs/research/message-reader-checkpoint.md:75-83` — installed language archive route, FMF/LTC decoding, title match, body template available locally, unresolved substitutions.
- `docs/research/message-reader-checkpoint.md:85-107` — owner/person/team candidates, hidden-token zero-output rule, team-short branch, first-name limitation, synthetic-only parser validation.
- `tools/FMAPI.MessageProbe/Program.cs:173-174` — separate title/body template reads.
- `tools/FMAPI.MessageProbe/Program.cs:179-211` — bounded localization index lookup, language selector, loaded variants/segments, explicit unavailable for unloaded/multiple variants.
- `tools/research/decode_localization.py:20-64` — LTC template record decoding; `:67-129` — FMF archive entry extraction; `:132-145` — synthetic checks.
- `tools/research/render_welcome.py:13-43` — strict token renderer; `:46-72` — proven branch guards; `:82-107` — synthetic self-test.

### What the source establishes

- A static body route and property name exist for `NewsBodyString`; the welcome formatter selects different templates for title and body and binds person/team parameters from message fields and a supplied context.
- The template store can be decoded outside the game for the observed archive/language/key family. The observed title text matched loaded native segments after removing serialized token brackets; the body template was decoded but not fully formatted.
- The renderer emits text only when every token resolves. Person-hidden is established as zero visible output; an ordinary kind-zero team-short branch is guarded. Person-first, context person 1 and general token rules remain unresolved, so the complete body remains unavailable.
- The parser's new branch guards have synthetic validation only; the final real capture could not run because the process had exited. No end-to-end rendered body is claimed.

### Field meaning and evidence strength

| Target | Source evidence | Strength | Limits |
|---|---|---|---|
| Body property path | key `0x626F6479` → `NewsBodyString` | static, instruction-boundary | no callable formatter; no ABI/lifetime |
| Template IDs | `0xABDAF` title, `0xA2A90` body | observed/static | welcome family only |
| Template storage | LTC/FMF decoder | observed offline for selected entry | observed `0x1` key family, one language |
| Parameter binding | person 1 context, person 2 `+0x78`, team 1 `+0xA0` | static | context person 1 unconfirmed |
| Token rendering | hidden/team-short branches | partial, synthetic for new guards | first/pronoun/plural/rich text unresolved |
| Complete body | — | missing | all tokens must resolve; no fabrication |

### Missing dependencies and unknown semantics

- Depends on MSG-01 and LOC-02. Body rendering also depends on unresolved localization selector, token, name and context semantics.
- Unknown: context person-1 identity, first-name/common-name/locale output, general short-name and hidden-token rules, plural/pronoun handling, rich text, multiple variants, lazy-load behavior, native formatter ABI/lifetime. Lazy loading and formatter calls were deliberately not executed.

### Minimal bounded follow-up read plan

1. Offline: continue static branch analysis for the first-name/common-name path and the supplied-context helper; keep unknown tokens explicit.
2. Later live, only after coordinator scheduling: one bounded capture of a single known welcome message, no lazy load and no game formatter call; keep the 64 KiB budget and fail closed on multiple variants.
3. Produce text only if every token resolves under proven rules; otherwise return the partial/unresolved structure and no body text.

## MSG-03: pending reply, deadline, options, related read-only items

### Exact source locations

- No message-reply/deadline/option field is present in `tools/FMAPI.MessageProbe/Program.cs`.
- `tools/FMAPI.MessageProbe/Program.cs:177` lists only `formatted title`, `body` and `active owner in multiplayer` as unsupported; pending-reply structures are not implemented.
- The prior message checkpoints (`docs/research/message-reader-checkpoint.md`) describe identity/date/template/entity work only; no reply or deadline evidence is recorded.
- A repository-wide source search for reply/deadline/option fields found no implementation evidence for this ID.

### What the source establishes

Nothing beyond the shared MSG-01 message container. There is no established pending-reply flag, deadline field, option list, action target or related-item structure.

### Missing dependencies and unknown semantics

- Depends on MSG-01. Unknown: whether reply state is on the message, a separate task/decision object, or UI-only; deadline units; option ordering; consequences; read-only representation.
- This remains **not started**; the absence of a field is not proof that the game lacks the concept.

### Minimal bounded follow-up read plan

1. Offline: static RTTI/metadata search for reply, decision, deadline, option and task classes; inspect message subclasses and callbacks. No scan and no UI.
2. Later live, only with coordinator scheduling and a user-selected save state that already contains a pending decision: one bounded read of the known message and its related object, no click, no reply, no mark-read, no state change.
3. If no pending state is available, record the ID as blocked rather than inferring from titles.

## MSG-04: news, media interviews/press conferences, comments, social, subscriptions, attachments

### Exact source locations

- `docs/research/message-reader-checkpoint.md:13-15` — `NEWS_MANAGER` class and observed message types including media transfer speculation.
- `docs/research/message-reader-checkpoint.md:17` — first entry `+0x80` resolved to a `MEDIA_SOURCE` database object; explicitly not title/body text.
- `tools/FMAPI.MessageProbe/Program.cs:166-170` — only message type/date/identity are read; no news or media record fields.
- No checked-in code reads news archives, interviews, press conferences, comments, social feeds, subscription scope or attachments.

### What the source establishes

Only adjacent evidence: a news/message manager class exists, and one message type carries a media-source object pointer. This does not establish news records, media interview/press-conference records, comments, social dynamics, subscription ranges or attachments. `NEWS_MANAGER` must not be described as a news archive.

### Missing dependencies and unknown semantics

- Depends on MSG-01. Unknown: whether news is a separate collection, a message subtype, a media-source view or UI-derived; relationship between `MEDIA_SOURCE`, news items and messages; subscription/filter ownership; attachment representation.
- This remains **not started** for the target fields.

### Minimal bounded follow-up read plan

1. Offline: static inventory of news/media/interview/press/social/subscription/attachment RTTI and metadata; map `NEWS_MANAGER` and `MEDIA_SOURCE` relations. No process access.
2. Later live, only after coordinator scheduling: one bounded read of a single known news item and its media-source relation; no UI automation, no social/network access, no subscription changes.
3. Keep all prose and identities out of the repository; record only sanitized structural findings.

## LOC-02: text encoding, localization keys, templates/parameters, aliases, rich text

### Exact source locations

- `tools/FMAPI.MessageProbe/Program.cs:69-78` — strict length-prefixed UTF-8 with NUL terminator and bounds.
- `tools/FMAPI.MessageProbe/Program.cs:179-211` — localization root `0x56F1C28`, implementation `+8`, sorted 16-byte index entries at implementation `+0x68/+0x70/+0x78`, current language selector `+0x12C`, variant/segment structure, loaded-segment UTF-8 decoding.
- `tools/FMAPI.MessageProbe/Program.cs:212-232` — bounded name-override tree membership for observed record kinds.
- `tools/FMAPI.MessageProbe/Program.cs:273-304` — team custom-short candidate, club `+0xC8` short-name candidate, club alternate-name records kinds `0x18/0x19`.
- `tools/FMAPI.MessageProbe/Program.cs:305-311` — owner PERSON registry lookup used by the observed name path.
- `docs/research/message-reader-checkpoint.md:34` — localization root/index layout and UTF-8 segment structure.
- `docs/research/message-reader-checkpoint.md:75-83` — FMF/LTC archive layout, `0x1` key family, serialized template format, title/body observations.
- `docs/research/message-reader-checkpoint.md:97-107` — formatter labels, first/short rules, name-override and alternate-name evidence, parser limits.
- `tools/research/decode_localization.py:20-64`, `:67-129` — offline LTC/FMF decoding.
- `tools/research/render_welcome.py:9-43` — token syntax and opaque substitution handling.

### What the source establishes

- Localization text is length-prefixed UTF-8 with a terminating zero, decoded strictly; observed Chinese text validates the encoding.
- The loaded localization index is keyed by template ID and language selector; values contain variants and segment pointers.
- The observed FMF/LTC archive exposes keys with low-28-bit identity and high-nibble selector information; only the `0x1` family is selected. High-bit offsets are not decoded. Serialized templates use a one-byte variant count and length-prefixed UTF-8 strings.
- Title/body template IDs `0xABDAF`/`0xA2A90` and token syntax `[%...]` are established for the observed welcome family.
- Name aliases are partially mapped: team custom short `+0x20`, club short `+0xC8`, alternate club-name records, and bounded override-tree membership. These are observed branches, not general alias semantics.
- Rich text structure, general parameter/plural/pronoun rules, other key families, other languages and multiple variants are not established.

### Field meaning and evidence strength

| Target | Source evidence | Strength | Limits |
|---|---|---|---|
| Encoding | strict UTF-8 length-prefix | observed | observed language only |
| Localization index/key | root/index `+0x68` | observed | selector semantics partial |
| Archive format | FMF/LTC decoder | observed offline | only observed `0x1` family; high-bit offsets unsupported |
| Templates | IDs `0xABDAF`/`0xA2A90` | observed/static | welcome family only |
| Parameters/tokens | renderer branches | partial, synthetic for new guards | first/context/plural/rich text unresolved |
| Name aliases | override/alternate-name branches | partial, one focused observation | general alias rules unknown |
| Rich text | — | missing | — |

### Missing dependencies and unknown semantics

- Depends on IDX-01. Unknown: general selector semantics, other key families, high-bit offset meaning, multiple variant selection, rich text, plural/pronoun rules, general name alias/override rules, multi-language consistency and version-to-version changes.
- The lazy localization loader and native formatter were not invoked; treating them as pure reads would be incorrect.

### Minimal bounded follow-up read plan

1. Offline: continue static analysis of selector/key families and token/alias rules using already available metadata/disassembly; keep unsupported families fail-closed.
2. Later, with coordinator-provided authorized archive input only: decode additional selected language/key entries offline; do not call the lazy loader or formatter.
3. Validate any new branch against the pinned profile; keep unknown variants and tokens explicit and do not emit reconstructed prose.

## Single most concrete missing relationship

The strongest anchor in this lane is the MSG-02 welcome body parameter binding: the formatter binds person slot 1 from a supplied context, person slot 2 from message `+0x78`, and team slot 1 from message `+0xA0`. The message-side references are observed; the supplied-context person-1 identity is not. The next concrete question is whether the context helper at RVA `0x424760` resolves the same owner PERSON that the owner-registry lookup at module RVA `0x5703738` resolves for the observed owner. This is a pure static/relationship question with an existing bounded owner-lookup implementation; it does not require formatting, lazy loading, UI, or a live read in this wave.

Bounded read plan for a future scheduled live window (not now):
1. Reuse the existing `--manager-selection` owner record and owner PERSON registry lookup; no process scan.
2. Read only the context helper's property-key path (`0x68756D61`) and the masked 23-bit owner lookup result, with root/relation rechecks and the existing 64 KiB budget.
3. Compare the resolved owner PERSON to the already validated owner PERSON; record equality or mismatch only.
4. If mismatched or unavailable, keep `contextPerson1Confirmed=false`; do not render body text.
5. No game function, formatter, lazy loader, UI action, write, or state change is permitted.

If the owner PERSON cannot be independently revalidated in that window, the blocker is explicit: context person-1 identity remains unconfirmed and MSG-02 body rendering stays unavailable.

## Cross-ID status summary

- **Completed for this wave:** offline source/evidence audit and documentation only. None of MSG-01, MSG-02, MSG-03, MSG-04 or LOC-02 is fully completed against its aggregated task row.
- **Partial/candidate evidence:** MSG-01 (bounded owner collection, date, identity candidate, native type); MSG-02 (body/title template path, offline template decode, limited token branches); LOC-02 (UTF-8, index/key/template layout, FMF/LTC decoder, partial name aliases).
- **Missing:** MSG-01 title/sender/recipient/category/read state/stable ID/general relations; MSG-02 complete body and general parameters; MSG-03 entirely; MSG-04 entirely; LOC-02 rich text, general selectors, variants, parameters and aliases.
- **No live read, process access, UI access, game call, injection, write, scan, network access or subagent was performed in this wave.** Prior observations are cited from checked-in records only. Raw samples, names, UID lists, addresses, disassembly and game data remain outside the repository.
