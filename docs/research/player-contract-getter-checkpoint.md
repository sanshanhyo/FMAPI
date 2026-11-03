# Actual-player contract relation checkpoint

New static and live evidence, 2026-11-03. Native profile SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F. Source: EntityLinks.cs ReadPlayerEmployment; no SDK/provider integration.

The pinned actual-player PERSON vtable RVA 0x4D27758 slot +0x3C0 points to getter RVA 0x1634E50. Instruction-boundary decoding with existing Iced 1.21.0 confirms: subtract signed vtordisp at PERSON-4; read vbtable at adjusted PERSON-0x280; sign-extend vbtable+8; return pointer at adjusted PERSON+virtualOffset-0x200. Since the independently validated primary PLAYER is adjusted PERSON-0x288, this equals primary+0x88+virtualOffset. This is different from the human-manager getter. No native function was invoked.

The bounded probe checks the exact actual-player PERSON and primary RTTI/vtables, expected getter address, vbtable module range and offset bounds before following the pointer. It only interprets FULL_CONTRACT +0x10 as a TEAM when RTTI matches, then TEAM+0x30 as a CLUB when RTTI matches, with UID and pointer rechecks. Original 64 KiB capture budget, requested-UID bounds and process identity checks remain. Reads are not atomic.

Live: PID33140 started 2026-11-03T05:10:43.5722214Z. Exactly one current-session UID was requested and matched. The resulting types were FULL_CONTRACT, TEAM, CLUB; club UID present. The linked club differed from the GCuM manager's club. This is one global-index sample, NOT a managed-club roster and NOT proof of all player membership or employment semantics. Raw contract kind=1; its meaning, activation state and interpretation relative to the manager's kind16 remain unknown. Dates, wages, loans, national-team/dual contracts and contract-history scope remain unverified.

Validation: Release build passed, zero warnings/errors. Existing synthetic probe self-test passed; it does not test this new getter layout. One live relation traversal passed before a final additional identity recheck was added; that small recheck is subsequently built but must not be called a second live verification. Private capture and disassembly stay local, outside git. No UI, injection, game-function calls or writes.
