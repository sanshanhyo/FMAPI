# TEAM_BASE index correspondence: bounded live check

2026-11-03, PID33140. Native profile BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F; existing GameAssembly gate also passed. New CheckTeamIndexCandidate uses the independently identified TEAM_BASE root0x5703768 and exact DATABASE_TABLE<TEAM_BASE> RTTI.

Static source: resolver0xD789B0. Global mode0x5703DE0 zero selects table+0x60/+0x68 begin/end; nonzero selects indirect table+0x80 then indirect+0/+8. Native code masks input index to low23 bits and checks it against vector count. This differs from PERSON UID binary search.

Live input was limited to the two exact TEAM objects already obtained through current manager -> contract -> TEAM -> CLUB -> club-team vector. Their record+8 low23 bits were tested as candidate indices. Both selected table entries equalled the original TEAM pointers (2/2), and both TEAM+0x30 backlinks matched the same club. The current manager employment team was among them. No UID list, address, name or save record is published.

Probe bounds the table span at one million entries but reads only its16-byte header and at most two specifically selected entries; it does NOT enumerate that span. Root/mode/indirect pointer/header/reference fields are rechecked within the existing64KiB aggregate budget. Reads remain non-atomic. Out-of-range candidate indices produce no entry read or match. No sort, allocation, native getter call, UI access or game write is performed.

Output indexCandidatePointerMatches=2 is current-session structural correspondence, not proof that record+8 is a portable UID, registration state, hierarchy label or full roster membership. Both modes are implemented from native evidence; the live capture covers only the mode active in this instance, not both. No player roster or next-fixture values were obtained.

Release build succeeded and one focused live capture passed the new type/bounds/rechecks. Existing synthetic self-tests do not establish this layout. Raw capture remains private. This round ended with no reader command still running.
