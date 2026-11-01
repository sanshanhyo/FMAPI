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

