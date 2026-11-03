# Contract/finance/transfer implementation note

This note covers the concrete artifact for the authorized FMAPI research wave:
`tools/research/summarize_contract_links.py`.

## Usage

Run the standalone summarizer against an existing bounded JSON capture. The
capture must contain 1 to 32 actual-player employment records under
`result.positions.records[].employment` (or a compatible top-level shape).

```text
python tools/research/summarize_contract_links.py --capture <private-capture.json>
python tools/research/summarize_contract_links.py --capture <private-capture.json> --output <private-summary.json>
python tools/research/summarize_contract_links.py --self-test
```

The output is counts only: record counts, employment status counts,
FULL_CONTRACT/TEAM/CLUB type-chain counts, raw kind counts, missing
date/wage field counts, and internal club-match counts. No UID values are
emitted. Contract affiliation is explicitly flagged as not registration or
loan eligibility.

## Evidence

- Historical evidence: `docs/research/manager-player-links-checkpoint.md` and
  `docs/research/native-entity-evidence.md` establish only the manager
  `FULL_CONTRACT -> TEAM -> CLUB` chain and the pinned binary profile.
- This-wave artifact: `tools/research/summarize_contract_links.py` plus this
  note. No capture, UID array, binary, or process output was created.
- New live reads this wave: zero.

## Limitations

- The script summarizes supplied capture JSON; it does not read any game
  process, file, network source, or external directory.
- Raw kind values are reported without semantic interpretation.
- Contract affiliation is not proof of registration, squad eligibility, loan
  terms, wage share, or availability.
- No date or wage fields are expected from current evidence; missing fields
  remain explicit.
- Synthetic self-test covers bounds and sanitization only; it is not a game
  runtime test.

## Synthetic edge-case expected outputs

These are expected JSON shapes for coordinator verification. They contain no
UIDs or game data.

Input A, one record with no employment object:

```json
{
  "recordCount": 1,
  "employmentRecordCount": 0,
  "employmentStatusCounts": {},
  "typeChain": {
    "fullContractCount": 0,
    "teamCount": 0,
    "clubCount": 0,
    "fullContractTeamClubCount": 0
  },
  "kindRawCounts": {},
  "kindRawCountsFullChain": {},
  "missingFields": {
    "recordsMissingDateFields": 0,
    "recordsMissingWageFields": 0,
    "dateFieldNamesFound": [],
    "wageFieldNamesFound": []
  },
  "clubComparison": {
    "recordsWithClubUid": 0,
    "distinctClubUidCount": 0,
    "clubsWithMultipleRecords": 0,
    "recordsSharingClubWithAnother": 0,
    "maxRecordsPerClub": 0
  },
  "eligibility": {
    "contractAffiliationIsRegistrationOrLoanEligibility": false,
    "registrationOrLoanEligibilityKnown": false
  },
  "status": "partial"
}
```

Input B, two records, one complete chain with kind 0 and one club UID, one
partial record with date and no wage:

```json
{
  "recordCount": 2,
  "employmentRecordCount": 2,
  "employmentStatusCounts": {
    "available": 1,
    "unavailable": 1
  },
  "typeChain": {
    "fullContractCount": 1,
    "teamCount": 1,
    "clubCount": 1,
    "fullContractTeamClubCount": 1
  },
  "kindRawCounts": {
    "0": 1,
    "<missing>": 1
  },
  "kindRawCountsFullChain": {
    "0": 1
  },
  "missingFields": {
    "recordsMissingDateFields": 1,
    "recordsMissingWageFields": 1,
    "dateFieldNamesFound": [
      "startDate"
    ],
    "wageFieldNamesFound": [
      "wage"
    ]
  },
  "clubComparison": {
    "recordsWithClubUid": 1,
    "distinctClubUidCount": 1,
    "clubsWithMultipleRecords": 0,
    "recordsSharingClubWithAnother": 0,
    "maxRecordsPerClub": 1
  },
  "eligibility": {
    "contractAffiliationIsRegistrationOrLoanEligibility": false,
    "registrationOrLoanEligibilityKnown": false
  },
  "status": "partial"
}
```
- Alpha.9 exclusive window is not released. No SDK, UI, persona, release, or
  remote change was made.