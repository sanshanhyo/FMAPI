# Parallel implementation-wave validation

Twelve original Python research tools are integrated. These are NOT twelve game-memory readers and do not add SDK contracts.

- Offline capture summaries: summarize_manager.py, summarize_positions.py, summarize_contract_links.py, summarize_messages.py, summarize_club_teams.py.
- Input/profile/evidence validation: bounded_capture_json.py, validate_capture_profile.py, coverage_report.py.
- Static pinned-file candidate locators: find_property_literals.py, find_literal_slots.py, locate_property_key.py, locate_vtable_function.py.

Coordinator executed all twelve `--self-test` entry points successfully against the integrated versions. These tests are synthetic, not live validation. Three summaries (manager, contract links, club-team container) were also executed against existing private captures, with outputs retained privately. No capture was committed or passed to a model.

Repairs after model delivery included unsigned metadata-header fixtures, a nine-field PE section tuple, null-byte escaping in a synthetic RTTI fixture, and valid JSON depth/size/node-limit test inputs. Validation rules were retained. The final integrated fixture/key, vtable and bounded-JSON tools passed their actual self-tests after coordinator corrections. Per-worker source copies may differ from this reviewed integration branch; use this branch as the delivery version.

The live interface remains tools/FMAPI.MessageProbe: manager selection and club-team container, explicit UID-linked positions/player contract relations, native service RTTI diagnostic, and bounded message/template capture. Existing known limitations remain, including no complete roster, no fixture-list reader, incomplete message formatting and non-atomic reads. Native calls, game writes, UI extraction and unbounded scans are not enabled.

No new FM memory reads occurred during this implementation-validation wave. No package or release was published.

## Actual-file qualification failure

Subsequent coordinator test of find_property_literals.py on the pinned real metadata failed closed with `section 0 size is not a whole literal-entry table`. The generated parser incorrectly assumed a six-integer header, 8-byte length/index entries and UTF16LE. This profile actually uses section offset/size/count triples, a section0 uint32 boundary-offset table and section1 UTF8 data, as independently recorded in roster-property-candidates.md. Its synthetic fixtures shared the wrong assumptions. Therefore this tool is NOT validated for the real build and must not be used to infer property indices until corrected and retested against GameCurrentManager9070/FirstTeamPlayers8681 controls. Other tools' synthetic passes also do not imply actual-file compatibility. A twelve-lane compatibility review wave was submitted; no runtime capability is promoted by it.
