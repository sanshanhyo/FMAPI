# Fixture type separation, static checkpoint

2026-11-03; offline pinned native PE analysis, SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F. No process scan or fixture read was performed. The existing PeProbe identified 81 matching RTTI names and 79 vtable candidates; counts are tool matches, not entity counts.

Relevant pinned type/vtable pairs:

- db::FIXTURE_RECORD: type descriptor RVA 0x56A1DB0, vtable 0x4CB2808.
- sicomps::FIXTURE: type descriptor 0x567B480, vtable 0x4CB69A8.
- simatchshared::BASE_FIXTURE: type descriptor 0x567B4B0, vtable 0x4DC2738.
- db::DATABASE_TABLE<db::FIXTURE_NAME>: type descriptor 0x56A0640, vtable 0x4CA4FD8; virtual slot+0x28 candidate 0xD16B00. This is a fixture-NAME table, not proven to be the scheduled fixtures collection.

Instruction-boundary decoding confirms 0xC716C3 loads the name-table vtable and 0xC716CA writes it to the newly initialized object. The nearby global 0x56F1AB0 is not established as the table root: a later store uses RBX rather than this RDI object. It must not be followed on a type-name assumption. Displacement xrefs alone are candidates, not proof of a valid instruction or owner relationship.

Missing: current-team fixture-list owner/getter, fixture UID/key semantics, exact dates/teams/competition/result field layouts, ordering and next-fixture selection. No FIX-01 field is newly readable from this checkpoint. Next work is static owner/getter mapping before any bounded live read. No binaries, disassembly payloads, names or save samples are committed.

Related live work during this window: the final player-contract identity-recheck implementation was executed against one explicit current-session sample UID; UID match, FULL_CONTRACT/TEAM/CLUB relation and final identity recheck passed. This closes the earlier build-only qualification for that extra check, not wider roster or contract semantics. No other process reads were running when this round completed.
