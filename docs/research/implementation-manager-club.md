# Manager-selection capture summarizer

## Purpose

Offline Python CLI that reads a manager-selection capture JSON (produced by
`FMAPI.MessageProbe --manager-selection` or `--entity-links`) and emits a
sanitized summary. No raw UID, name, pointer, process ID, or save path
appears in the output.

## File

`tools/research/summarize_manager.py`

## Usage

```sh
# Summarize a capture to stdout
python tools/research/summarize_manager.py capture.json

# Write summary to a file
python tools/research/summarize_manager.py capture.json --output summary.json

# Run synthetic self-tests
python tools/research/summarize_manager.py --self-test
```

## Output fields

| Field | Meaning |
|---|---|
| `captureStatus` | Top-level capture status |
| `selectionStatus` | Selection subsystem status |
| `selectionSource` | Selection source key (e.g. `GCuM`) |
| `verifiedCurrentManager` | True only when selection available, `matchedHumanOwner` true, and `activeManager.activeVerified` true |
| `selectionReason` | Reason string or null |
| `managerCandidateCount` | Count only; no UIDs |
| `activeManagerPresent` | Boolean |
| `activeManagerVerified` | Boolean |
| `contractAvailable` | Boolean |
| `contractKindRaw` | Raw kind byte or null (semantics unverified) |
| `teamAvailable` | Boolean |
| `clubAvailable` | Boolean |
| `clubTeams` | Sanitized container summary or null |
| `positionsStatus` | Position subsystem status |
| `positionRecordCount` | Count only |
| `employmentSummary` | Aggregate counts (`withContract`, `withTeam`, `withClub`) |
| `teamServiceType` | Service type string or null |
| `atomicSnapshot` | Boolean or null |
| `hashValidation` | Per-hash `match`/`mismatch`/`absent` |
| `unsupported` | List from capture |
| `limitations` | Static limitations of the summary |

### clubTeams sub-fields

| Field | Meaning |
|---|---|
| `status` | Container status (e.g. `candidate-structure`) |
| `count` | Team count in container |
| `validatedTeamBacklinks` | Number of validated backlinks |
| `currentEmploymentTeamFound` | Boolean |
| `notPlayerRoster` | Boolean (always true; container is not a player roster) |
| `teamHierarchySemanticsVerified` | Boolean (currently false) |

## Pinned hashes enforced

- `game_plugin.dll`: `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
- `GameAssembly.dll`: `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`
- Metadata: `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`

A hash present in the capture must match its pinned value or the summarizer
exits with code 3. An absent hash is reported as `absent`, not an error.

## Input limits

| Limit | Default |
|---|---|
| File size | 10 MiB (configurable via `--max-input-bytes`) |
| `managerCandidates` | 16 |
| Position records | 32 |
| `unsupported` items | 64 |

## Evidence basis

All field mappings are derived from:

- `tools/FMAPI.MessageProbe/EntityLinks.cs` (capture schema)
- `docs/research/implementation-wave-input.md` (coordinator-confirmed additions)

No live game data was read in this wave. No SDK, UI, or adapter changes
are included.

## Limitations

- Summary is from a single capture; not an atomic snapshot.
- Empty manager collection does not imply an empty or unloaded save.
- Club-team container is candidate structure, not a roster.
- Contract kind raw value has unverified semantics.
- No UID, name, pointer, or process identity is included in output.
- Synthetic self-tests only; no real capture was processed in this wave.
- The summarizer does not invoke any game function, read any process, or
  access any network or external directory.
