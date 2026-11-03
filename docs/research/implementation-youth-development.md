# Youth development implementation note

## Artifact

- File: `tools/research/summarize_club_teams.py`
- Purpose: sanitize a captured `manager.clubTeams` container into a bounded summary.
- No SDK, Core, adapter, inventory, or other implementation files were changed.

## Usage

```text
python tools/research/summarize_club_teams.py <sanitized-capture.json>
python tools/research/summarize_club_teams.py <sanitized-capture.json> --output <private-summary.json>
python tools/research/summarize_club_teams.py --self-test
```

Input must be 1..1,048,576 bytes and valid JSON. The script locates `clubTeams` under `activeManager`, `result.activeManager`, `result`, or top level, in that priority order. It emits only summary fields; it does not echo the source capture.

## Output fields

- `status`: captured status string, or `unknown` if absent/invalid.
- `count`: integer team count, or `unknown` if absent/not an integer.
- `validatedTeamBacklinks`: integer, or `unknown`.
- `currentEmploymentTeamFound`: boolean, or `unknown`.
- `notPlayerRoster`: boolean, or `unknown`.
- `teamHierarchySemanticsVerified`: boolean, or `unknown`.
- `hierarchyUnverified`: true unless `teamHierarchySemanticsVerified` is explicitly true.

## Evidence basis

- Coordinator-attributed schema from `docs/research/implementation-wave-input.md`: `activeManager.clubTeams` has `status=candidate-structure`, `count`, `validatedTeamBacklinks`, `currentEmploymentTeamFound`, `notPlayerRoster=true`, `teamHierarchySemanticsVerified=false`.
- One current club had 2 TEAM backlinks including the employment team. This is attributed coordinator evidence, not a live result from this task.
- `clubMembershipVerifiedHere` remains false; contract linkage is not registration or roster completeness.

## Limitations

- This tool summarizes captured JSON only; it performs no game, process, UI, native, network, or capture work.
- Absent fields are `unknown`, never zero teams or a completed youth roster.
- `notPlayerRoster` is not a youth/reserve/development roster claim.
- `teamHierarchySemanticsVerified` stays false/unknown; hierarchy remains unverified.
- Synthetic self-test checks presence, absence, partial input, bool/int separation, verification flag, and path priority only.
- Coordinator must execute/build/verify; no tests were run in this environment.
