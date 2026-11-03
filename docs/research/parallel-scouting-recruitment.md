# Scouting audit: SCT-01/02/03

Coordinator-authored replacement: the model first claimed a missing report, then wrote test/tool-parameter fragments. Both deliveries were rejected; this is not a successful model finding.

Research source base: 99aba1d. Task definitions pinned to upstream 01b53c5a68a9b0602cf6e134f5a132a71ad857cf. No live read, game file analysis, UI, private capture or native function call was performed.

Evidence: tools/FMAPI.MessageProbe/EntityLinks.cs:37 implements supplied-UID player lookup, not scouting; :72 implements manager employment and optional player positions. src/FMAPI.Adapters.Windows/UnavailableWindowsAdapter.cs disables reads/writes. docs/research/native-entity-evidence.md records adjacent PERSON/manager/team/club prerequisites only. The native hash inherited by the probe is BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F; it does not establish a scouting layout.

SCT-01: no verified shortlist, assignment, recruitment-focus or knowledge fields. Depends on STF-01 staff identity and a proven scouting collection root.
SCT-02: no verified report target/date/confidence/grade/cost fields. Depends on SCT-01 and a pinned report getter/layout.
SCT-03: no verified candidate pool/history/global-knowledge index. Depends on SCT-02 and IDX-02 coverage.

Next: establish one named-property/type/getter chain through static analysis before scheduling any bounded process read. No offset or enum is guessed. After coordinator release, only a known header and bounded records may be read with budget, UID/type checks and root rechecks; unknown/dirty layouts fail closed. No blanket scanning, unknown function calls or raw sample upload.

Completed: coordinator source-boundary audit. Candidate: adjacent UID/relationship infrastructure only, not SCT coverage. Missing: all scouting-specific fields. New live reads: zero. Blockers: no proven scouting entry point in this source base, and invalid model artifact delivery.
