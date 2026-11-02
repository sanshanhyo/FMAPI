# Manager employment and player goalkeeper familiarity checkpoint

Status: external read-only research; no SDK/provider change and no active-manager contract.

## Build and process evidence

Observed on Windows on 2026-11-02. The new FM process was PID 25376, started at 21:21:41 local/UTC in this environment. It was independently checked instead of reusing the earlier PID. The installed/selected loaded game_plugin.dll matched SHA-256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F. All RVAs/offsets below are specific to that binary and must fail closed for another hash.

Raw output, UID input arrays, native disassembly and installed-reader output remain in a private local directory outside the repository. No game files, saves, raw names, message prose or process pointers are committed.

## Human candidate -> current contract -> team -> club

Reuse the validated HUMAN_NON_PLAYER_MANAGER at global RVA 0x56F3008, vtable 0x4E2D678, vector +0x18/+0x20/+0x28. Each human has vbtable 0x4CC086C and PERSON subobject +0x440 with vtable 0x4CC08D8. This remains an owner collection, not an active-user selector.

PERSON virtual +0x3C0 is RVA 0xF48D30. Instruction-boundary disassembly establishes the vtordisp at PERSON -4, complete human object's vbtable +8 signed offset and contract pointer at the resulting virtual base +0x80. Bounded emulation in the new EntityLinks probe found FULL_CONTRACT -> TEAM through contract +0x10 -> CLUB through team +0x30. FULL_CONTRACT virtual +0x50 is RVA 0x301970, which reads its kind byte +0x26. Native human-affiliation paths 0x281F030/0x281F820 check this kind before following the employer relation. No native methods were called.

The human PERSON UID field +0x0C and linked club UID field +0x0C both agreed with the installed external read-only OffseasonReader's manager candidate. Its producer manifest identified build 21bfd30 and the same game binary fingerprint. This is an independent consumer cross-check of current record linkage, not a claim of cross-save identity stability. No FA implementation was copied into FMAPI.

The observed human +0x422 flag was one. Native functions use it to filter human-owner processing, but its relation to foreground/local active-user selection has not been established. Exactly one human candidate, a nonzero flag or a valid employment relation must never be promoted to active=true. The probe continues to emit activeVerified=false and activeManager=null. Reliable current active-user selection remains missing.

## UID -> PERSON -> ACTUAL_PLAYER -> goalkeeper familiarity

Global RVA 0x5703738 is DATABASE_TABLE<PERSON>, validated vtable RVA 0x4CA5278. Native virtual +0x28 (0xCDBC30 -> 0xCF7960) looks up a signed positive UID by comparing record +0x0C in an ordered pointer index. If table +0x5C bit 0 is clear, it uses the vector behind +0x80. Otherwise it uses the inline +0x88/+0x90/+0x98 vector; +0xA0 is a dirty/sort-needed flag. The native routine can sort that cache. Our implementation never calls it and refuses the dirty-cache case. External binary search is bounded to 32 steps per UID and at most 32 explicitly supplied UIDs, under the existing aggregate 64 KiB capture budget. No full-registry/process scan is needed.

A matched actual player must have PERSON vtable 0x4D27758 and ACTUAL_PLAYER RTTI. PERSON virtual +0x680 is RVA 0x16360E0: subtract its vtordisp at -4 and 0x288 to obtain the actual player subobject, then require its primary vtable 0x4D27228 and the same RTTI. This is distinct from the abstract PLAYER base, whose methods include unsupported/null stubs.

PLAYER_IS_GOALKEEPER is a business rule with vtable 0x4D16C28 and evaluation 0x3C0EC90. It obtains the player through PERSON +0x680 and calls player virtual +0x348, then compares the returned byte against 15. That actual-player virtual getter is 0x16325D0 and reads player +0x150. The external probe therefore reports goalkeeperFamiliarity and businessRuleIsGoalkeeper = familiarity >= 15, requiring a value in 0..20. This rule is distinct from PLAYER_IS_CURRENTLY_PLAYING_AS_A_GOALKEEPER; it is not current match/tactic assignment.

Neighboring actual-player virtual getters independently read position-related bytes at +0x152 etc. The probe preserves the following 13 bytes as otherPositionSlotsRaw, with range checks, but does not assign outfield labels. Exact per-position names and aggregate/mask semantics remain unverified.

## Live result and limits

An initial fixed 64-slot PERSON registry window returned one exact player and a coherent goalkeeper familiarity. That exploratory sample was explicitly not the managed club roster and was not presented as one.

The installed reader supplied 27 exact-player records for the employment-linked club. Their UIDs were saved as a private input array. The new FMAPI probe then performed native-layout UID searches for exactly those 27 UIDs: all 27 matched, all had the exact actual-player types/subobjects, and all position blocks passed bounded reads/range/rechecks. Two matched the native goalkeeper business rule. No player names or UIDs are listed in this public checkpoint. Club-membership provenance comes from that separate roster input; this new probe does not independently rebuild club membership and says clubMembershipVerifiedHere=false.

The human contract kind is emitted as a raw field for the next current-state capture. The earlier observed FULL_CONTRACT/type/team/club relation and UID cross-check remain valid observations; a later-added field is not retroactively asserted to have been sampled.

External pointer/header/field rechecks do not provide a game lifetime lock or an atomic snapshot. No game call, injection, UI/OCR read, memory/save write, process control, installation change, release or push was performed.

## Reproduction

Build tools/FMAPI.MessageProbe with the checked-in .NET 10 SDK selection. Run its existing --self-test for common bounds/string primitives. For current explicitly authorized local research, invoke the built DLL with PID, absolute loaded game_plugin.dll path and --entity-links. An optional fourth argument is a private JSON array of 1-32 distinct positive signed-int UIDs. The file is limited to 4 KiB. Redirect output/error to a private directory outside this repository.

Without UID input, the diagnostic only inspects the first 64 PERSON-index slots and returns at most eight exact actual players. With UID input, it only searches the ordered UID index for those identifiers. Manager candidates and employment links remain separate from active-user identity. Check the running process and start time again before each new session.

## Follow-up: complete analyzed byte range and stronger relation rechecks

Static getter 0x15E7920 compares +0x15D/+0x15E, extending the analyzed byte range through player +0x15E. The diagnostic now reads 15 bytes at +0x150: the proven goalkeeper byte and 14 remaining raw slots. Direct getters additionally establish +0x156 (0x1632630), +0x157 (0x1632620), +0x158 (0x1632640), +0x159 (0x15E1990), +0x15A (0x1632650) and +0x15B (0x15E19A0). Aggregate accessors cover neighboring groups, but semantic outfield labels are still not assigned.

A focused current-instance capture with the added end byte succeeded for all 27 requested roster UIDs, again yielding two native-rule goalkeeper matches. The manager FULL_CONTRACT kind byte was actually observed as 16, which passes the analyzed affiliation path's >=2 check; no further meaning is assigned to that raw kind. Contract -> employer team -> club pointers, club UID and kind now receive additional end-of-capture rechecks. The raw-position output uses numeric arrays rather than System.Text.Json's default byte-array Base64 encoding; an existing private capture was losslessly decoded into that numeric shape without a redundant game capture. This changes presentation, not the measured values.

An active-user selector is still unverified. Static metadata mentions current-manager binding/controller fields, but no UI/controller instances or password/account fields were read. Such names alone do not establish a business-layer address or active-user identity. The +0x422 flag remains raw. Neither the unique human candidate nor an employment contract is treated as an active selection.

## Current selected human: native source established

This supersedes the earlier absence of an authoritative selection source for the observed session. Static metadata/literal registration binds GameCurrentManager to key GCuM (0x4743754D). Native selection dispatch at 0x380020 resolves the supplied record and stores it at global RVA 0x56F32C8; leaf getters 0x378FC0/0x3810B0 return that pointer and teardown clears it. See native-entity-evidence.md for the complete reproducible semantic chain and both binary fingerprints.

A new minimal --manager-selection mode reads this global and only enables activeVerified when it has HUMAN_NON_PLAYER PERSON RTTI and exactly matches one validated human-owner PERSON pointer. It never selects the first/only owner as a fallback. A focused capture returned an available matching selection and employment club in the current running session. The native selected manager identity and existing contract chain agreed. Null/unmatched selections stay unavailable; changes during the bounded read fail closed. GameAssembly is now separately fingerprinted because its named-property registration is part of the selection evidence.

This establishes the game's current-selected local human manager in the observed session, not a general multiplayer authority guarantee. Selection changes, multiple-human hotseat behavior, reloads and lifetime locking remain untested. Earlier captures' activeManager=null are historical observations from a probe without this source and must not be relabeled. No UI/controller instances or account/password fields were read; the diagnostic reads the fixed native business selection pointer.
