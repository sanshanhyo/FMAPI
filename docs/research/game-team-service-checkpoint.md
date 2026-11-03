# Native team service, bounded live checkpoint

2026-11-03: PID33140, start2026-11-03T05:10:43Z. Pinned native SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F and GameAssembly820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A checked by existing probe. One bounded entity capture reported the service behind globalRVA0x57034A0 as RTTI GAME_TEAM, with root recheck and current-manager selection available. No service method was called. No UI instance was read.

The fixed global was selected from previously decoded TEAM accessor wrappers (e.g.0xB530250,0xB537DF0,0xB543ED0 forwarding to service virtualB8/C0/C8), not a process scan. New EntityLinks output teamServiceType records only RTTI; existing aggregate64KiB budget, pointer/type limits and process checks remain. It is diagnostic discovery, not an SDK capability or roster. The single explicit current-session player UID was reused to avoid broad indexing; raw capture stays private.

Static pinned-PE cross-check found GAME_TEAM type descriptor0x569ECA0 and candidate primary vtable0x4CA1348 (complete-object locators0x4CA14D0/0x4CA1590). Multiple subobjects must be distinguished before assigning virtual slots. This supplies a non-UI service-analysis route; it does not establish player-list filtering, fixture retrieval, name mapping, collection lifetime or safe function-call ABI. All native calls remain prohibited in this research mode.

Validation: Release build zero errors/warnings; one live capture confirmed RTTI and root stability. Existing synthetic tests do not cover service layout. No game writes, save writes, injection or UI operation. This round's process read ended before the static RTTI scan; no process reader remains running.
