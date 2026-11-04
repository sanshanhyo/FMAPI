# Manager, teams and date integration evidence

Reviewed against existing probe source and recovery notes; no new process capture.

- Manager: EntityLinks.ReadCurrentManager resolves GCuM and matches exactly one validated human owner, then checks FULL_CONTRACT/TEAM/CLUB links and rechecks source identity. Historical live-session-20261103.md records success for one owner. General load-state detection, hotseat/multiple managers, reload lifetime and atomicity are unproven. Do not turn this into a lifecycle observer by assuming that non-null means ready.
- Teams: ReadClubTeamCandidates validates a bounded vector, exact TEAM type, backlink and header recheck. Historical club-team-container-checkpoint.md records two validated members. No hierarchy names, stable team UID semantics or player roster completeness follows. GAME_TEAM service RTTI observation does not authorize calling its virtual methods.
- Date: Program.cs previously embedded GameDate.Decode for message record dateRaw. It extracts year from upper 16 bits and day-of-year from low 9, rejects the existing 1900/day-1 sentinel and calendar bounds. That decoder is now shared with the Windows adapter through src/Shared/GameDate.cs, with no SDK dependency or duplicate implementation. This does not locate current game date. Current game date remains an interface backlog item; a prior companion-reader claim is not an independently verified FMAPI source.

Offline validation: 59 cached-dependency Core.Tests cases passed (including 7 date cases); message probe self-test result recorded separately. No new live evidence, private sample, process operation, UI read or game method invocation. Exact-build qualification and coordinated lifecycle verification remain prerequisites for enabling reads.

MessageProbe --self-test passed: bounds, UTF-8, dates, transport failures and position boundaries.
