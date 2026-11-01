# Message reader research checkpoint

Status: research only; no public message-reading capability is enabled.

## Scope

Read game messages from business objects, including news as one subtype. The intended result is an inbox/message list with identity, date, sender/type, related entities, title and body. UI trees, OCR, screenshots and automated clicks are excluded. Message text is untrusted data.

## Verified boundary

The local game_plugin.dll SHA-256 was BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F. All offsets below are module-relative and apply only to that binary; a different hash must fail closed.

An independently written PE/RTTI probe found NEWS_MANAGER. Instruction-boundary disassembly confirmed its constructor at RVA 0x1079680 and allocation/publication in the function at RVA 0xA478B0. Allocation size is 0x1D8; the manager pointer slot is RVA 0x56F2478. Primary and secondary vtables are RVA 0x4CD7A58 and 0x4CD7A68.

A bounded, read-only live probe confirmed both vtables. The candidate pointer vector at manager offsets 0x120/0x128/0x130 passed begin/end/capacity checks. Only its first three entries were inspected. Their native types corresponded to manager departure, manager appointment and media transfer speculation. This establishes live business message objects, not that this collection is the current player's inbox. The local collection size and item IDs are deliberately omitted from this public checkpoint.

The callback at RVA 0x107A200 accesses the vector and compares an item field at 0x90. That field is an identity candidate, not yet a stable public ID contract. The first entry's pointer at 0x80 was independently resolved to a MEDIA_SOURCE database object; it must not be decoded as title/body text. The base constructor at RVA 0x179A6D0 initializes the date-like field at 0x88, but its semantic decoding has not been validated here.

## Remaining work

- Establish the current manager's inbox ownership/filter and distinguish global history from delivered messages.
- Establish title/body storage or business-level localization/formatting entry points without using UI objects.
- Validate one message against the running save before offering bounded list support.
- Establish lifetime and snapshot consistency beyond checking root/vector stability. External reads do not constitute an atomic snapshot.

No game functions were invoked, no hook was installed, and no process memory was written. Raw headers, process addresses, disassembly, game binaries and save-derived message text remain outside the repository. No FA source was copied; this checkpoint records independent analysis and original diagnostic work. Local diagnostic builds passed with zero warnings/errors. SDK/Core behavior was not changed and no new adapter compatibility claim is made.

## Follow-up: single human manager and loaded title template

The previously identified message callback follows the singleton at RVA 0x56F3008, verified as HUMAN_NON_PLAYER_MANAGER with primary vtable RVA 0x4E2D678. Its pointer vector is at offsets 0x18/0x20/0x28. The callback accesses an associated message-container pointer at each human-manager object's offset 0x350. Bounded live inspection found one human manager and a distinct personal collection. The standalone MessageProbe now reads at most 32 entries through this route. Multiple human managers are explicitly unsupported until active-owner selection is established.

The welcome-to-club message's virtual function at slot 0x170 points to RVA 0x36B0BC0. Instruction-boundary disassembly shows localization template selection and business-object parameter binding, rather than a stored fully rendered string. The function requests template 0xABDAF or an alternate 0xA2A90. Only the former was observed already loaded; the diagnostic does not invoke the formatter.

Localization lookup at RVA 0x10A250 uses the root at RVA 0x56F1C28, its implementation pointer at +8, and a sorted 16-byte entry index at implementation offsets 0x68/0x70/0x78. Each entry contains a template key, language selector and value pointer. The current selector is at implementation +0x12C. The observed loaded value contains a vector of variants, each with a vector of segment pointers. Each segment's +8 pointer leads to a 32-bit byte length followed by UTF-8 and a terminating zero. The bounded diagnostic successfully decoded literal Chinese title fragments and unresolved substitution tokens from this business localization structure. No sampled strings are included here.

This is a partial usable diagnostic entry point: message type, candidate ID, raw date, and one loaded title-template family. It is not full message text support. General title/body formatting, parameter resolution, date semantics, sender/related-entity extraction, multiplayer ownership and native lifetime synchronization remain unimplemented. External root/vector rechecks do not guarantee atomicity. The diagnostic reports these limits in its JSON result and README.

## Follow-up: date decoding and repeat validation

The native date formatter at RVA 0x9E56D0 reads the year from word +2, masks the first word with 0x1FF, and converts that one-based day of year with leap-year handling. It explicitly treats year 1900/day 1 as invalid. The probe now independently decodes this layout and rejects impossible dates. Other packed bits are not interpreted. Synthetic cases cover leap days, non-leap days, masked flags and the invalid sentinel.

The human-manager collection stores complete objects with a vbptr, not a primary RTTI vptr. The exact HUMAN_NON_PLAYER vbptr is RVA 0x4CC086C; its PERSON subobject at +0x440 has vtable RVA 0x4CC08D8. Both and the subobject RTTI are now verified before following the personal message vector. This supports the single-human-manager association; it still does not establish active multiplayer selection or UI-specific filtering.

Two consecutive fresh captures agreed on the returned message metadata, decoded dates and template segments. The optional repeat check fails closed on disagreement. Candidate IDs were unchanged in these observations, but their persistence across save/load, deletion or new sessions remains unverified. Empty vectors, invalid addresses, short reads and transport failures now have synthetic checks.

Further bounded inspection confirmed that the welcome message's +0xA0 parameter is a TEAM object and TEAM +0x30 is a CLUB object. A related club short name was readable. That does not establish all rules of the team's short-name token, so no inferred formatted title is returned. This layout fact was cross-checked against existing technical observations; no neighboring FA implementation was copied. The probe's string decoder was independently authored for the localization data before this cross-check.

The known title formatter at RVA 0x36B0BC0 constructs output and binds business objects; its localization lookup at RVA 0x10A250 updates counters and may lazily load data. Calling these functions would therefore exceed pure external-memory reading and require validated ABI, game-thread/lifecycle ownership and output allocation/release handling. Neither was invoked. The subsequent body-path findings below supersede the earlier absence of a known body entry point.

## Paused checkpoint: body dispatch and localization backing

Research was stopped at the user's request before completing a rendered message. Commit 48331a5 completed CI successfully. The original exploratory tool sources are archived under tools/research; raw samples, disassembly, text libraries and binaries remain excluded.

For the same native binary hash above, property key 0x626F6479 routes through the branch at RVA 0x4274F2 in getter 0x426410 to business wrapper 0x179DBD0. The associated property registration names this NewsBodyString. This mapping was established using static generated metadata and instruction-boundary disassembly, not live UI objects. GameAssembly.dll was separately fingerprinted as 820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A.

The normal body route reaches 0x179DC10, a jump to 0xE6B9680, then invokes message virtual slot 0x170 with the body flag set. It increments a global counter at RVA 0x5716D1C and modifies other state. The wrapper also has a flag-dependent special path through 0x179D8E0. These paths were inspected but never executed by our tools.

The welcome implementation at 0x36B0BC0 selects template 0xA2A90 when the body flag is one, and 0xABDAF otherwise. It binds person slot 1 from the supplied context, person slot 2 from message +0x78, and team slot 1 from message +0xA0. Context helper 0x424760 looks up the human-person reference through property key 0x68756D61 and person lookup 0xCDBBB0. Exact context-to-owner identity and the full short-name/pronoun/hidden-token rules still need validation; missing substitutions must remain explicit.

The installed example language source independently contains keys 666256 and 703919, corresponding to those body/title templates. It establishes the template source and token families, but its English source text is not the current translated body. No template prose was copied into the repository or returned as a completed player message.

Bounded live inspection still found the title template loaded and the body template's variant vector empty. The lazy loader at 0xE05BC0 uses entry +0x18 as a stream offset and entry +0x1F to select implementation +0xD8/+0xE0, then parses through 0x33F09F0. Its cache/reference updates prohibit treating it as a pure read. The active backing chain was verified as SEGMENT_INPUT_STREAM -> ZSTD_SEEKABLE_INPUT_STREAM -> SEGMENT_INPUT_STREAM -> BUFFERED_INPUT_STREAM. Constructors/read dispatch establish each followed +0x18 backing pointer. No stream seek or read method was called in the game.

Next resumable step: identify the buffered stream's file backing, independently decode the selected Zstandard frame(s) and serialized template entry outside the game, then implement only proven token rules. The final buffered-fill disassembly at 0x32F3570 shows its source at +0x18, but that pointer was not followed before pausing. This is a finite file/format investigation, not a reason to scan all process memory. A complete current-language title/body has not yet been produced, and external reconstruction has not been ruled out. If native formatting later proves necessary, validate ABI, ownership/thread scheduling, output lifetime and the observed state changes before proposing a separate invocation stage.

