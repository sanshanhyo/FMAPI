#!/usr/bin/env python3
"""Sanitized summary of a captured manager.clubTeams container.

Reads one explicitly supplied sanitized JSON capture and emits only the
club-team-container summary fields. It never reads processes, game files, UI,
network, credentials, or raw player samples. Absent fields are reported as
"unknown"; they are never converted to zero teams or a completed roster.
"""
import argparse
import json
from pathlib import Path

MAX_INPUT_BYTES = 1024 * 1024
UNKNOWN = "unknown"


def _as_int(value):
    # bool is a subclass of int in Python; exclude it explicitly.
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return None


def find_club_teams(capture):
    """Return the first clubTeams dict found, in priority order, or None."""
    if not isinstance(capture, dict):
        return None
    paths = []
    active = capture.get("activeManager")
    if isinstance(active, dict):
        paths.append(active.get("clubTeams"))
    result = capture.get("result")
    if isinstance(result, dict):
        active_result = result.get("activeManager")
        if isinstance(active_result, dict):
            paths.append(active_result.get("clubTeams"))
        paths.append(result.get("clubTeams"))
    paths.append(capture.get("clubTeams"))
    for candidate in paths:
        if isinstance(candidate, dict):
            return candidate
    for candidate in paths:
        if candidate is not None:
            return candidate
    return None


def summarize_club_teams(capture):
    club_teams = find_club_teams(capture)
    if not isinstance(club_teams, dict):
        raw = {}
        present = False
    else:
        raw = club_teams
        present = True

    status = raw.get("status")
    if not isinstance(status, str) or not status:
        status = UNKNOWN

    count = _as_int(raw.get("count"))
    count_out = count if count is not None else UNKNOWN

    backlinks = _as_int(raw.get("validatedTeamBacklinks"))
    backlinks_out = backlinks if backlinks is not None else UNKNOWN

    employment_found = _as_bool(raw.get("currentEmploymentTeamFound"))
    employment_out = employment_found if employment_found is not None else UNKNOWN

    not_roster = _as_bool(raw.get("notPlayerRoster"))
    not_roster_out = not_roster if not_roster is not None else UNKNOWN

    hierarchy_verified = _as_bool(raw.get("teamHierarchySemanticsVerified"))
    hierarchy_verified_out = hierarchy_verified if hierarchy_verified is not None else UNKNOWN

    # Hierarchy is explicitly unverified unless positively verified.
    hierarchy_unverified = hierarchy_verified is not True

    return {
        "present": present,
        "status": status,
        "count": count_out,
        "validatedTeamBacklinks": backlinks_out,
        "currentEmploymentTeamFound": employment_out,
        "notPlayerRoster": not_roster_out,
        "teamHierarchySemanticsVerified": hierarchy_verified_out,
        "hierarchyUnverified": hierarchy_unverified,
    }


def build_output(capture, source_name):
    summary = summarize_club_teams(capture)
    return {
        "source": source_name,
        "clubTeams": {
            "status": summary["status"],
            "count": summary["count"],
            "validatedTeamBacklinks": summary["validatedTeamBacklinks"],
            "currentEmploymentTeamFound": summary["currentEmploymentTeamFound"],
            "notPlayerRoster": summary["notPlayerRoster"],
            "teamHierarchySemanticsVerified": summary["teamHierarchySemanticsVerified"],
        },
        "summary": {
            "teamCount": summary["count"],
            "validatedTeamBacklinks": summary["validatedTeamBacklinks"],
            "employmentTeamPresent": summary["currentEmploymentTeamFound"],
            "hierarchyUnverified": summary["hierarchyUnverified"],
            "notPlayerRoster": summary["notPlayerRoster"],
        },
        "limitations": [
            "count and validatedTeamBacklinks are candidate-structure values from the captured container; not independently verified here.",
            "teamHierarchySemanticsVerified is false or unknown; team hierarchy semantics remain unverified.",
            "notPlayerRoster is not a youth, reserve, or development roster claim.",
            "absent fields are reported as unknown, never as zero teams or a completed roster.",
            "no process, game, UI, network, credential, or raw sample access occurred.",
        ],
    }


def self_test():
    full = {
        "activeManager": {
            "clubTeams": {
                "status": "candidate-structure",
                "count": 2,
                "validatedTeamBacklinks": 2,
                "currentEmploymentTeamFound": True,
                "notPlayerRoster": True,
                "teamHierarchySemanticsVerified": False,
            }
        }
    }
    out = summarize_club_teams(full)
    assert out["present"] is True
    assert out["status"] == "candidate-structure"
    assert out["count"] == 2
    assert out["validatedTeamBacklinks"] == 2
    assert out["currentEmploymentTeamFound"] is True
    assert out["notPlayerRoster"] is True
    assert out["teamHierarchySemanticsVerified"] is False
    assert out["hierarchyUnverified"] is True

    missing_container = {"activeManager": {"uid": 123}}
    out2 = summarize_club_teams(missing_container)
    assert out2["present"] is False
    assert out2["status"] == UNKNOWN
    assert out2["count"] == UNKNOWN
    assert out2["validatedTeamBacklinks"] == UNKNOWN
    assert out2["currentEmploymentTeamFound"] == UNKNOWN
    assert out2["notPlayerRoster"] == UNKNOWN
    assert out2["teamHierarchySemanticsVerified"] == UNKNOWN
    assert out2["hierarchyUnverified"] is True

    partial = {"clubTeams": {"count": 0}}
    out3 = summarize_club_teams(partial)
    assert out3["count"] == 0
    assert out3["validatedTeamBacklinks"] == UNKNOWN
    assert out3["currentEmploymentTeamFound"] == UNKNOWN
    assert out3["notPlayerRoster"] == UNKNOWN
    assert out3["hierarchyUnverified"] is True

    bool_count = {"clubTeams": {"count": True}}
    out4 = summarize_club_teams(bool_count)
    assert out4["count"] == UNKNOWN

    verified = {"clubTeams": {"teamHierarchySemanticsVerified": True}}
    out5 = summarize_club_teams(verified)
    assert out5["hierarchyUnverified"] is False

    priority = {
        "clubTeams": {"count": 99},
        "activeManager": {"clubTeams": {"count": 2}},
    }
    out6 = summarize_club_teams(priority)
    assert out6["count"] == 2

    nested = {"result": {"activeManager": {"clubTeams": {"count": 3}}}}
    out7 = summarize_club_teams(nested)
    assert out7["count"] == 3

    print("PASS: club-team-container summary synthetic checks")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.input is None:
        parser.error("input JSON path required (or use --self-test)")

    try:
        info = args.input.stat()
    except OSError as error:
        raise SystemExit(f"invalid input: {error}")
    if info.st_size == 0 or info.st_size > MAX_INPUT_BYTES:
        raise SystemExit("input missing or outside 1..1048576 bytes")

    try:
        capture = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SystemExit(f"invalid input: {error}")

    output = build_output(capture, args.input.name)
    rendered = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote sanitized club-team summary to {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
