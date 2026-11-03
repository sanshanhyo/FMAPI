"""Sanitized capture evidence and coverage report for national registration research.

The report keeps five distinct concerns separate:
  * UID resolution
  * contract-club affiliation
  * player roster membership
  * registration status
  * match eligibility

Each is reported as verified / not_verified / unknown. A value is only
"verified" when the input carries explicit evidence and source text for it.
No game offsets, eligibility rules, roster semantics, or game data are
inferred here.
"""
import argparse
import json
from pathlib import Path

FIELDS = (
    "uidResolution",
    "contractClubAffiliation",
    "playerRosterMembership",
    "registration",
    "matchEligibility",
)

ALIASES = {
    "uidResolution": (
        "uidResolution", "uid_resolution", "uidResolved", "uid_resolved",
        "uidStatus", "uid_status", "personUid", "person_uid",
    ),
    "contractClubAffiliation": (
        "contractClubAffiliation", "contract_club_affiliation",
        "contractClub", "contract_club", "employment", "contractStatus",
        "contract_status",
    ),
    "playerRosterMembership": (
        "playerRosterMembership", "player_roster_membership",
        "rosterMembership", "roster_membership", "roster", "clubRoster",
        "club_roster",
    ),
    "registration": (
        "registration", "registrationStatus", "registration_status",
        "squadRegistration", "squad_registration",
    ),
    "matchEligibility": (
        "matchEligibility", "match_eligibility", "eligibility",
        "matchStatus", "match_status", "nextMatchEligibility",
        "next_match_eligibility",
    ),
}

EVIDENCE_KEYS = ("evidence", "evidenceRef", "evidence_ref", "proof", "basis")
SOURCE_KEYS = ("source", "sourcePath", "source_path", "sourceRef", "source_ref", "provenance")
RECORD_KEYS = ("records", "players", "persons", "items", "entries", "results", "roster")
JSON_LIMIT = 1024 * 1024


def read_json(path):
    raw = path.read_bytes()
    if len(raw) > JSON_LIMIT:
        raise ValueError("JSON input size limit exceeded")
    text = raw.decode("utf-8-sig")
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text = raw.decode("utf-16")
    return json.loads(text)


def _scalar_state(value):
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "verified" if value else "not_verified"
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {
            "verified", "supported", "available", "true", "yes", "present",
            "resolved", "matched", "observed", "validated",
        }:
            return "verified"
        if normalized in {
            "not_verified", "unsupported", "unavailable", "false", "no",
            "absent", "unresolved", "unmatched", "rejected", "failed",
        }:
            return "not_verified"
        if normalized in {
            "unknown", "null", "missing", "not_attempted", "not_checked",
            "not_applicable", "n/a", "none", "candidate", "partial",
        }:
            return "unknown"
        return "unknown"
    if isinstance(value, dict):
        for key in ("status", "value", "result", "state"):
            if key in value:
                return _scalar_state(value[key])
        for key in ("verified", "supported", "available", "resolved", "matched", "present"):
            if key in value:
                return _scalar_state(value[key])
        return "unknown"
    if isinstance(value, (int, float)):
        return "verified" if value else "not_verified"
    return "unknown"


def _first_present(mapping, keys):
    if not isinstance(mapping, dict):
        return None
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            value = mapping[key]
            if isinstance(value, str):
                return value
            return str(value)
    return None


def _record_evidence(record):
    return _first_present(record, EVIDENCE_KEYS)


def _record_source(record):
    return _first_present(record, SOURCE_KEYS)


def _field_specific(record, field, suffixes):
    if not isinstance(record, dict):
        return None
    variants = []
    for suffix in suffixes:
        variants.extend((
            field + suffix,
            field + "_" + suffix.lower(),
            field.lower() + suffix,
            field.lower() + "_" + suffix.lower(),
        ))
    for key in variants:
        if key in record and record[key] not in (None, ""):
            value = record[key]
            return value if isinstance(value, str) else str(value)
    return None


def _field_value(record, field):
    for alias in ALIASES[field]:
        if alias in record:
            return record[alias]
    nested = record.get("fields")
    if isinstance(nested, dict):
        for alias in ALIASES[field]:
            if alias in nested:
                return nested[alias]
    return None


def _normalize_value(value):
    if isinstance(value, dict):
        state = _scalar_state(value)
        evidence = _first_present(value, EVIDENCE_KEYS)
        source = _first_present(value, SOURCE_KEYS)
        return state, evidence, source
    return _scalar_state(value), None, None


def extract_records(data):
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        raise ValueError("input JSON must be an object or array")
    for key in RECORD_KEYS:
        value = data.get(key)
        if isinstance(value, list):
            return value
    sections = []
    for key in ("manager", "clubTeams", "activeManager", "employment", "positions"):
        value = data.get(key)
        if isinstance(value, dict):
            item = dict(value)
            item.setdefault("_section", key)
            sections.append(item)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    copied = dict(item)
                    copied.setdefault("_section", key)
                    sections.append(copied)
    if sections:
        return sections
    if any(_field_value(data, field) is not None for field in FIELDS):
        return [data]
    return [data]


def normalize_record(record, index, global_evidence, global_source):
    if not isinstance(record, dict):
        raise ValueError(f"record {index} is not an object")
    record_evidence = _record_evidence(record) or global_evidence
    record_source = _record_source(record) or global_source
    section = record.get("_section")
    record_id = record.get("recordId", record.get("id", record.get("index", index)))
    if record_id is None:
        record_id = index
    row = {"record": record_id}
    if section is not None:
        row["section"] = section

    rejected = []
    for field in FIELDS:
        value = _field_value(record, field)
        state, evidence, source = _normalize_value(value)
        if evidence is None:
            evidence = _field_specific(record, field, ("Evidence", "EvidenceRef", "Proof", "Basis")) or record_evidence
        if source is None:
            source = _field_specific(record, field, ("Source", "SourcePath", "SourceRef", "Provenance")) or record_source
        if state == "verified" and not (evidence and source):
            raise ValueError(
                f"record {record_id}: {field} verified claim requires explicit evidence and source"
            )
        row[field] = state
        row[field + "Evidence"] = evidence
        row[field + "Source"] = source
    return row, rejected


def build_report(data):
    global_evidence = _record_evidence(data) if isinstance(data, dict) else None
    global_source = _record_source(data) if isinstance(data, dict) else None
    records = extract_records(data)
    rows = []
    rejected = []
    for index, record in enumerate(records):
        row, row_rejected = normalize_record(record, index, global_evidence, global_source)
        rows.append(row)
        rejected.extend(row_rejected)

    counts = {field: {"verified": 0, "not_verified": 0, "unknown": 0} for field in FIELDS}
    for row in rows:
        for field in FIELDS:
            counts[field][row[field]] += 1

    all_verified = bool(rows) and all(
        row[field] == "verified" for row in rows for field in FIELDS
    )
    report = {
        "status": "complete" if all_verified else "partial",
        "recordCount": len(rows),
        "fieldCoverage": counts,
        "records": rows,
        "rejectedClaims": rejected,
        "limitations": [
            "verified means explicit evidence and source were present in the sanitized input",
            "not_verified means the claim was explicitly false or rejected for missing evidence/source",
            "unknown means the field was not attempted, missing, candidate, or unverified",
            "this tool does not infer offsets, rules, roster semantics, eligibility, or game state",
        ],
    }
    if rejected:
        report["status"] = "rejected_claims_present"
    return report


def self_test():
    valid = {
        "records": [
            {
                "uidResolution": True,
                "uidResolutionEvidence": "PERSON +0x0C UID lookup matched",
                "uidResolutionSource": "EntityLinks.cs:54",
                "contractClubAffiliation": {
                    "status": "verified",
                    "evidence": "FULL_CONTRACT -> TEAM -> CLUB pointers rechecked",
                    "source": "manager-player-links-checkpoint.md",
                },
                "playerRosterMembership": False,
                "registration": "unknown",
                "matchEligibility": None,
            }
        ]
    }
    report = build_report(valid)
    assert report["recordCount"] == 1
    assert report["records"][0]["uidResolution"] == "verified"
    assert report["records"][0]["contractClubAffiliation"] == "verified"
    assert report["records"][0]["playerRosterMembership"] == "not_verified"
    assert report["records"][0]["registration"] == "unknown"
    assert report["records"][0]["matchEligibility"] == "unknown"
    assert report["fieldCoverage"]["uidResolution"]["verified"] == 1
    assert report["rejectedClaims"] == []

    invalid = {"records": [{"uidResolution": True}]}
    try:
        build_report(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported true claim was accepted")

    candidate = {
        "records": [
            {
                "uidResolution": "candidate",
                "contractClubAffiliation": "candidate",
                "playerRosterMembership": "candidate",
                "registration": "candidate",
                "matchEligibility": "candidate",
            }
        ]
    }
    candidate_report = build_report(candidate)
    assert all(
        candidate_report["records"][0][field] == "unknown" for field in FIELDS
    )

    empty = build_report({"records": []})
    assert empty["recordCount"] == 0
    assert empty["status"] == "partial"

    print("PASS: tri-state separation, evidence/source rejection, candidate handling, empty input, and bounds")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="sanitized summary JSON input")
    parser.add_argument("--output", type=Path, help="write report JSON to this path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.input is None:
        parser.error("--input is required unless --self-test is used")

    data = read_json(args.input)
    report = build_report(data)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)

    if args.output is not None:
        output = args.output.resolve()
        repo = Path(__file__).resolve().parents[2]
        if output.is_relative_to(repo):
            parser.error("private report output must remain outside repository")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Report written: {output}")
    else:
        print(rendered)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "unavailable", "reason": str(error)}, ensure_ascii=False))
        raise SystemExit(3)
    except SystemExit:
        raise
    except Exception as error:
        print(json.dumps({"status": "unavailable", "reason": str(error)}, ensure_ascii=False))
        raise SystemExit(3)
