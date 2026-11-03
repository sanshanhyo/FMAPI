# Roster property candidates, static-only checkpoint

Metadata profile SHA256 A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C, signature/version 0xFAB11BAF/39. The literal index is a 4-byte boundary-offset table (section0), not 8-byte length/index records. Adjacent offsets bound strings in section1; GameCurrentManager literal9070 was used as a known control. No save/process data is involved.

Candidate literal IDs: AvailableFirstTeamPlayers3362, FirstTeamPlayers8681, PlayerTeams15141, PreviousMeetingsTeamFixtureList15501. These names do not establish a roster or next-fixture API. AvailableFirstTeamPlayers may be availability-filtered; previous-meetings fixtures are not future schedule entries.

GameAssembly profile SHA256 820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A. Correction: linear slot extrapolation was invalid. The earlier 0x333A160 slot contains encoded usage 0x2000D957, not the FirstTeamPlayers literal. Its static member+0x158 and helper0x1CA2530 must not be attributed to roster semantics.

Corrected slots were located by searching aligned on-disk encoded literal references (0xA0000000 | index*2 | 1), with GameCurrentManager9070 resolving to the known0x333AD88 control. FirstTeamPlayers8681 maps uniquely to0x3324C50; PlayerTeams15141 to0x32C2A90; PreviousMeetingsTeamFixtureList15501 to0x32D7088. Instruction decoding confirms FirstTeamPlayers slot loaded at0x570771, a stack-supplied key at+0x6EE0 and property registration call0x32EEE0. Its native key is still unresolved: the following immediate0x4670354C initializes the NEXT registration and must not be assigned to FirstTeamPlayers. PlayerTeams slot is loaded at0x359F45 and passed to helper0x1624F70; this is not yet a native player-to-team getter. PreviousMeetings slot displacement xref0x5845F6 still requires instruction-level confirmation.

No live read or new roster/fixture field was performed in this round. Next: recover the preceding FirstTeamPlayers key initialization and native dispatch, then identify collection ownership and filtering semantics before bounded process access. Existing player contract/team/club relation remains the supported narrow join; complete membership and collection coverage remain missing.

## Native key recovered

Later instruction-boundary decoding from the known managed function start0x4A49D0 confirms key0x78754F31 initialized at0x570718 via0x337E50, saved at stack+0x6EE0 and paired with the exact FirstTeamPlayers literal slot by call0x32EEE0 at0x570787. The following0x4670354C is a separate registration. The earlier unresolved-key qualification above is superseded by this evidence.

Searching this exact key in pinned native executable sections found two immediate occurrences, both in function0x628FC0. Sequential decoding from that function boundary confirms compare at0x62C3ED, branch to0x62C412, temporary container initialization, key-dependent flags and virtual+0x150 call at0x62C475. The dispatch receiver's type/owner has not been proven. The subsequent virtual+0x108 and other branches must not be interpreted as TEAM methods merely because the property contains Team in its name. Next work: establish receiver type and virtual+0x150 implementation, then container lifetime/filter semantics. No unknown native call or process collection traversal has been attempted.
