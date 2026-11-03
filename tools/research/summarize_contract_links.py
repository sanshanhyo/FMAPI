#!/usr/bin/env python3
"""Bounded summarizer for sanitized actual-player employment capture output.

This reads a JSON capture produced by the existing read-only EntityLinks diagnostic
and emits counts only. It never prints UIDs, raw capture bodies, or kind guesses.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

MAX_INPUT_BYTES = 1024 * 1024
MAX_RECORDS = 32
MAX_TEXT = 256

FULL_CONTRACT = ".?AVFULL_CONTRACT@db@@"
TEAM = ".?AVTEAM@db@@"
CLUB = ".?AVCLUB@db@@"

DATE_FIELDS = {
    "contractStart", "contractStartDate", "startDate", "contractExpiry",
    "expiryDate", "contractEnd", "endDate", "fromDate", "toDate", "date",
}
WAGE_FIELDS = {
    "wage", "wageRaw", "salary", "weeklyWage", "monthlyWage", "yearlyWage",
    "wageAmount", "amount", "salaryRaw",
}


def read_json(path):
    raw = path.read_bytes()
    if not (1 <= len(raw) <= MAX_INPUT_BYTES):
        raise ValueError("capture size limit")
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("invalid capture JSON") from error
    if not isinstance(value, dict):
        raise ValueError("capture must be an object")
    return value


def employment_records(capture):
    root = capture.get("result", capture)
    if not isinstance(root, dict):
        raise ValueError("capture result must be an object")
    positions = root.get("positions", root.get("records"))
    if isinstance(positions, dict):
        records = positions.get("records")
    elif isinstance(positions, list):
        records = positions
    else:
        records = root.get("records")
    if not isinstance(records, list) or not (1 <= len(records) <= MAX_RECORDS):
        raise ValueError("capture must contain 1 to 32 records")
    normalized = []
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise ValueError(f"record {index} must be an object")
        employment = item.get("employment")
        if employment is not None and not isinstance(employment, dict):
            raise ValueError(f"record {index} employment must be an object")
        normalized.append(employment)
    return normalized


def text_or_none(value):
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > MAX_TEXT:
        raise ValueError("capture text field bounds")
    return value


def summarize(capture):
    records = employment_records(capture)
    status_counts = Counter()
    type_counts = Counter()
    kind_counts = Counter()
    kind_counts_full_chain = Counter()
    full_contract = team = club = full_chain = 0
    with_employment = 0
    missing_dates = 0
    missing_wages = 0
    date_names = set()
    wage_names = set()
    club_uids = []

    for employment in records:
        if employment is None:
            continue
        with_employment += 1
        status = text_or_none(employment.get("status"))
        status_counts[status if status is not None else "<missing>"] += 1
        contract_type = text_or_none(employment.get("contractType"))
        team_type = text_or_none(employment.get("teamType"))
        club_type = text_or_none(employment.get("clubType"))
        if contract_type == FULL_CONTRACT:
            full_contract += 1
        if team_type == TEAM:
            team += 1
        if club_type == CLUB:
            club += 1
        chain = contract_type == FULL_CONTRACT and team_type == TEAM and club_type == CLUB
        if chain:
            full_chain += 1
        kind = employment.get("kind")
        kind_key = "<missing>" if kind is None else str(kind)
        if len(kind_key) > MAX_TEXT:
            raise ValueError("kind value bounds")
        kind_counts[kind_key] += 1
        if chain:
            kind_counts_full_chain[kind_key] += 1
        found_date = False
        found_wage = False
        for key, value in employment.items():
            if not isinstance(key, str) or len(key) > MAX_TEXT:
                raise ValueError("employment key bounds")
            if key in DATE_FIELDS and value is not None:
                found_date = True
                date_names.add(key)
            if key in WAGE_FIELDS and value is not None:
                found_wage = True
                wage_names.add(key)
        if not found_date:
            missing_dates += 1
        if not found_wage:
            missing_wages += 1
        club_uid = employment.get("clubUid")
        if club_uid is not None:
            if not isinstance(club_uid, (str, int)):
                raise ValueError("club UID type bounds")
            club_uids.append(str(club_uid))

    club_groups = Counter(club_uids)
    multi_clubs = {value for value, count in club_groups.items() if count > 1}
    return {
        "status": "partial",
        "recordCount": len(records),
        "employmentRecordCount": with_employment,
        "employmentStatusCounts": dict(sorted(status_counts.items())),
        "typeChain": {
            "fullContractCount": full_contract,
            "teamCount": team,
            "clubCount": club,
            "fullContractTeamClubCount": full_chain,
        },
        "kindRawCounts": dict(sorted(kind_counts.items())),
        "kindRawCountsFullChain": dict(sorted(kind_counts_full_chain.items())),
        "missingFields": {
            "recordsMissingDateFields": missing_dates,
            "recordsMissingWageFields": missing_wages,
            "dateFieldNamesFound": sorted(date_names),
            "wageFieldNamesFound": sorted(wage_names),
        },
        "clubComparison": {
            "recordsWithClubUid": len(club_uids),
            "distinctClubUidCount": len(club_groups),
            "clubsWithMultipleRecords": len(multi_clubs),
            "recordsSharingClubWithAnother": sum(
                count for count in club_groups.values() if count > 1
            ),
            "maxRecordsPerClub": max(club_groups.values(), default=0),
        },
        "eligibility": {
            "contractAffiliationIsRegistrationOrLoanEligibility": False,
            "registrationOrLoanEligibilityKnown": False,
            "note": (
                "A FULL_CONTRACT/TEAM/CLUB employment chain is contract affiliation "
                "evidence only. It is not proof of registration, squad eligibility, "
                "loan terms, wage share, or availability."
            ),
        },
        "limits": {
            "maxRecords": MAX_RECORDS,
            "maxInputBytes": MAX_INPUT_BYTES,
        },
        "warnings": [
            "clubMembershipVerifiedHere remains false in source evidence",
            "No date or wage field was found in the supplied employment objects",
            "Raw kind values are reported without semantic interpretation",
        ],
    }


def self_test():
    capture = {
        "result": {
            "positions": {
                "records": [
                    {
                        "employment": {
                            "status": "available",
                            "contractType": FULL_CONTRACT,
                            "kind": 16,
                            "teamType": TEAM,
                            "clubType": CLUB,
                            "clubUid": "club-a",
                        }
                    },
                    {
                        "employment": {
                            "status": "available",
                            "contractType": FULL_CONTRACT,
                            "kind": 2,
                            "teamType": TEAM,
                            "clubType": CLUB,
                            "clubUid": "club-a",
                        }
                    },
                    {
                        "employment": {
                            "status": "unavailable",
                            "contractType": "OTHER",
                            "kind": None,
                            "teamType": None,
                            "clubType": None,
                        }
                    },
                ]
            }
        }
    }
    result = summarize(capture)
    assert result["recordCount"] == 3
    assert result["employmentRecordCount"] == 3
    assert result["typeChain"]["fullContractTeamClubCount"] == 2
    assert result["kindRawCounts"] == {"16": 1, "2": 1, "<missing>": 1}
    assert result["missingFields"]["recordsMissingDateFields"] == 3
    assert result["missingFields"]["recordsMissingWageFields"] == 3
    assert result["clubComparison"]["distinctClubUidCount"] == 1
    assert result["clubComparison"]["recordsSharingClubWithAnother"] == 2
    assert result["eligibility"]["contractAffiliationIsRegistrationOrLoanEligibility"] is False
    assert "clubUid" not in json.dumps(result)
    assert "club-a" not in json.dumps(result)
    try:
        employment_records({"result": {"positions": {"records": []}}})
    except ValueError:
        pass
    else:
        raise AssertionError("empty record set accepted")
    print("PASS: bounded counts, raw kind counts, missing fields, internal club matching, no UID leakage, eligibility flag")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.capture is None:
        parser.error("--capture is required")
    capture = read_json(args.capture)
    result = summarize(capture)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is not None:
        repo = Path(__file__).resolve().parents[2]
        output = args.output.resolve()
        if output.is_relative_to(repo):
            raise ValueError("sanitized output must remain outside repository")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
        print(f"Private summary written: {output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
