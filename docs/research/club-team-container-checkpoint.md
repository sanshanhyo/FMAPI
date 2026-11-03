# Club team-container structural checkpoint

New bounded live evidence on 2026-11-03, PID33140. Existing pinned native BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F and GameAssembly820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A gates passed.

Static source of candidate: native helper0x11E2210, reached from GAME_TEAM virtualC0 implementation0x3147020, reads TEAM+0x30 and the resulting object's vector bounds at+0x18/+0x20. This is independent of UI text/instances. The generic TEAM accessor contains type-dependent branches; this does not establish every team's behavior.

The probe starts from exact GCuM manager ownership, validated FULL_CONTRACT -> TEAM -> CLUB, then inspects only this CLUB+0x18/20/28 vector, bounded at32 pointers with the existing aggregate64KiB budget. Every member must be exact TEAM RTTI and its +0x30 must point back to the validated CLUB. The vector/header is rechecked; snapshot atomicity is not guaranteed. No function is called.

Observed: count2, validatedTeamBacklinks2, currentEmploymentTeamFound=true. This proves a two-member current-club team container structure in this snapshot. It does not identify first/reserve/youth/national-team hierarchy, assign stable team UID semantics, reconstruct a player roster or prove membership completeness across saves. Output explicitly says candidate-structure, notPlayerRoster=true, teamHierarchySemanticsVerified=false. No names/UID lists or private records are published.

Code: EntityLinks.cs ReadClubTeamCandidates, now included in current-manager selection output. Release build succeeded. One focused live capture passed all new structural checks. Existing synthetic tests do not establish this layout. No writes, UI, injection, unknown function calls, or broad process scan. The read round ended; no process reader remains running.
