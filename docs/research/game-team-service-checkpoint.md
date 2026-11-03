# Native team service, bounded live checkpoint

2026-11-03: PID33140, start2026-11-03T05:10:43Z. Pinned native SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F and GameAssembly820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A checked by existing probe. One bounded entity capture reported the service behind globalRVA0x57034A0 as RTTI GAME_TEAM, with root recheck and current-manager selection available. No service method was called. No UI instance was read.

The fixed global was selected from previously decoded TEAM accessor wrappers (e.g.0xB530250,0xB537DF0,0xB543ED0 forwarding to service virtualB8/C0/C8), not a process scan. New EntityLinks output teamServiceType records only RTTI; existing aggregate64KiB budget, pointer/type limits and process checks remain. It is diagnostic discovery, not an SDK capability or roster. The single explicit current-session player UID was reused to avoid broad indexing; raw capture stays private.

Static pinned-PE cross-check found GAME_TEAM type descriptor0x569ECA0 and candidate primary vtable0x4CA1348 (complete-object locators0x4CA14D0/0x4CA1590). Multiple subobjects must be distinguished before assigning virtual slots. This supplies a non-UI service-analysis route; it does not establish player-list filtering, fixture retrieval, name mapping, collection lifetime or safe function-call ABI. All native calls remain prohibited in this research mode.

Validation: Release build zero errors/warnings; one live capture confirmed RTTI and root stability. Existing synthetic tests do not cover service layout. No game writes, save writes, injection or UI operation. This round's process read ended before the static RTTI scan; no process reader remains running.

## Static interface follow-up

Pinned TEAM vtable0x4CE1108 virtualF8/100/108 enter native thunks0x1211900/0x1211950/0x1211980. Their unconditional jumps lead to wrappers0xB530250/0xB537DF0/0xB543ED0, which forward to GAME_TEAM virtualB8/C0/C8. Primary GAME_TEAM vtable0x4CA1348 maps these to0x3146F30/0x3147020/0x3148500. The primary table ends before its adjacent subobject table; virtual150 must not be read across that boundary as an interface member.

Static C0 implementation0x3147020 includes type-dependent TEAM input normalization via0x11E2210 and extensive context/eligibility filtering. It is not a simple pointer getter or a proven roster vector. Helper0x11E2210 supplies the CLUB team-container structural evidence recorded separately, but does not establish player-list semantics. No native function was invoked.

A bounded exact-byte search for trivial load/address-and-ret leaf getters in the TEAM vtable region0x4CE1108..0x4CE1380 found none; this negative pattern result does not prove no accessor exists. Decoding beyond unconditional thunks yields non-instruction padding/opaque bytes and was not used as semantic evidence. The remaining blocker is the independent business collection ownership and filtering path, not absence of a running game. No extra process read was justified by this follow-up; window remains free.
