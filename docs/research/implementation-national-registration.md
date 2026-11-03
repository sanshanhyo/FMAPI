# Implementation note: national registration coverage report

File: `tools/research/coverage_report.py`

## Usage

```text
python tools/research/coverage_report.py --self-test
python tools/research/coverage_report.py --input sanitized-summary.json
python tools/research/coverage_report.py --input sanitized-summary.json --output C:\private\report.json
```

Input is a sanitized summary JSON object or array. The report is JSON. Private report output must remain outside the repository.

## Evidence model

The report keeps five concerns as separate tri-state fields:

- `uidResolution`
- `contractClubAffiliation`
- `playerRosterMembership`
- `registration`
- `matchEligibility`

Each field is `verified`, `not_verified`, or `unknown`. `verified` requires explicit non-empty evidence and source text in the sanitized input. A positive claim without evidence/source is rejected and reported as `not_verified` with a `rejectedClaims` entry. Candidate, partial, or missing values become `unknown`; they are not upgraded to verified.

The tool performs no UID resolution, roster inference, eligibility inference, offset discovery, native calls, or game reads. It only normalizes and counts evidence already present in the sanitized input.

## Limitations

- Field aliases are accepted for common sanitized summary shapes, but no live capture schema is assumed.
- No real samples, names, UIDs, credentials, or process data are included.
- Synthetic self-test is included in the file; it was not executed in this offline implementation wave.
- Coordinator execution/build/verification and any later bounded live read remain separate steps.
