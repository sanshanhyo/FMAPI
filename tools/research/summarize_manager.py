#!/usr/bin/env python3
"""Offline summarizer for manager-selection capture JSON.

Reads a capture produced by FMAPI.MessageProbe (--manager-selection or
--entity-links) and emits a sanitized JSON summary.  No raw UID, name,
pointer, process ID, or save path appears in the output.

Usage:
    python tools/research/summarize_manager.py capture.json
    python tools/research/summarize_manager.py capture.json --output summary.json
    python tools/research/summarize_manager.py --self-test
"""
import argparse
import json
import sys
from pathlib import Path

# Pinned hashes (must match tools/FMAPI.MessageProbe source).
PINNED_GAME_PLUGIN_HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
PINNED_GAME_ASSEMBLY_HASH = "820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A"
PINNED_METADATA_HASH = "A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C"

MAX_INPUT_BYTES = 10 * 1024 * 1024  # 10 MiB
MAX_MANAGERS = 16
MAX_POSITION_RECORDS = 32
MAX_UNSUPPORTED = 64


def _check_limits(capture):
    """Raise ValueError if input exceeds bounded limits."""
    managers = capture.get("managerCandidates")
    if isinstance(managers, list) and len(managers) > MAX_MANAGERS:
        raise ValueError(
            f"managerCandidates count {len(managers)} exceeds limit {MAX_MANAGERS}"
        )
    positions = capture.get("positions")
    if isinstance(positions, dict):
        records = positions.get("records")
        if isinstance(records, list) and len(records) > MAX_POSITION_RECORDS:
            raise ValueError(
                f"position records count {len(records)} exceeds limit "
                f"{MAX_POSITION_RECORDS}"
            )
    unsupported = capture.get("unsupported")
    if isinstance(unsupported, list) and len(unsupported) > MAX_UNSUPPORTED:
        raise ValueError(
            f"unsupported count {len(unsupported)} exceeds limit {MAX_UNSUPPORTED}"
        )


def _validate_hashes(capture):
    """Return a dict of hash validation results. Raise on mismatch."""
    result = {}
    for field, pinned in [
        ("binarySha256", PINNED_GAME_PLUGIN_HASH),
        ("gameAssemblySha256", PINNED_GAME_ASSEMBLY_HASH),
    ]:
        value = capture.get(field)
        if value is None:
            result[field] = "absent"
        elif isinstance(value, str) and value.upper() == pinned:
            result[field] = "match"
        else:
            raise ValueError(
                f"{field} mismatch: expected {pinned}, got {value!r}"
            )
    meta = capture.get("metadataSha256")
    if meta is None:
        result["metadataSha256"] = "absent"
    elif isinstance(meta, str) and meta.upper() == PINNED_METADATA_HASH:
        result["metadataSha256"] = "match"
    else:
        raise ValueError(
            f"metadataSha256 mismatch: expected {PINNED_METADATA_HASH}, "
            f"got {meta!r}"
        )
    return result


def _summarize_positions(positions):
    """Extract sanitized position/employment summary.

    Returns (status, record_count, employment_summary_or_None).
    """
    if positions is None:
        return None, 0, None
    if isinstance(positions, str):
        return positions, 0, None
    if not isinstance(positions, dict):
        return "unknown", 0, None
    status = positions.get("status", "unknown")
    records = positions.get("records")
    record_count = len(records) if isinstance(records, list) else 0
    emp_summary = None
    if isinstance(records, list) and records:
        with_contract = 0
        with_team = 0
        with_club = 0
        for rec in records:
            if not isinstance(rec, dict):
                continue
            emp = rec.get("employment")
            if not isinstance(emp, dict):
                continue
            if emp.get("contractType") is not None:
                with_contract += 1
            if emp.get("teamType") is not None:
                with_team += 1
            if emp.get("clubType") is not None:
                with_club += 1
        emp_summary = {
            "recordCount": record_count,
            "withContract": with_contract,
            "withTeam": with_team,
            "withClub": with_club,
        }
    return status, record_count, emp_summary


def _summarize_club_teams(active_manager):
    """Extract sanitized club-team container summary or None."""
    if not isinstance(active_manager, dict):
        return None
    ct = active_manager.get("clubTeams")
    if not isinstance(ct, dict):
        return None
    def _bool(v):
        return v if isinstance(v, bool) else None
    def _int(v):
        return v if isinstance(v, int) and not isinstance(v, bool) else None
    return {
        "status": ct.get("status") if isinstance(ct.get("status"), str) else None,
        "count": _int(ct.get("count")),
        "validatedTeamBacklinks": _int(ct.get("validatedTeamBacklinks")),
        "currentEmploymentTeamFound": _bool(ct.get("currentEmploymentTeamFound")),
        "notPlayerRoster": _bool(ct.get("notPlayerRoster")),
        "teamHierarchySemanticsVerified": _bool(
            ct.get("teamHierarchySemanticsVerified")
        ),
    }


def summarize(capture):
    """Produce a sanitized summary dict from a capture."""
    if not isinstance(capture, dict):
        raise ValueError("capture must be a JSON object")

    # Unwrap --verify-repeat output.
    if (
        "result" in capture
        and isinstance(capture.get("result"), dict)
        and "repeatVerified" in capture
    ):
        capture = capture["result"]

    _check_limits(capture)
    hash_validation = _validate_hashes(capture)

    selection = capture.get("selection")
    if not isinstance(selection, dict):
        selection = {}

    active_manager = capture.get("activeManager")
    if active_manager is not None and not isinstance(active_manager, dict):
        active_manager = None

    managers = capture.get("managerCandidates")
    manager_count = len(managers) if isinstance(managers, list) else 0

    # Contract/team/club availability.
    contract_available = False
    team_available = False
    club_available = False
    contract_kind_raw = None

    if isinstance(active_manager, dict):
        if active_manager.get("contractType") is not None:
            contract_available = True
        if active_manager.get("contractKind") is not None:
            contract_kind_raw = active_manager.get("contractKind")
        if active_manager.get("clubUid") is not None:
            club_available = True

    if isinstance(managers, list):
        for m in managers:
            if not isinstance(m, dict):
                continue
            if m.get("contractType") is not None:
                contract_available = True
            if contract_kind_raw is None and m.get("contractKind") is not None:
                contract_kind_raw = m.get("contractKind")
            if m.get("payloadType") == ".?AVTEAM@db@@":
                team_available = True
            if m.get("payloadField30Type") == ".?AVCLUB@db@@":
                club_available = True
            if m.get("clubUidCandidate") is not None:
                club_available = True

    positions = capture.get("positions")
    positions_status, position_record_count, emp_summary = _summarize_positions(
        positions
    )
    if emp_summary is not None:
        if emp_summary.get("withTeam", 0) > 0:
            team_available = True
        if emp_summary.get("withClub", 0) > 0:
            club_available = True

    club_teams = _summarize_club_teams(active_manager)
    if club_teams is not None and club_teams.get("currentEmploymentTeamFound") is True:
        team_available = True

    verified_current_manager = (
        selection.get("status") == "available"
        and selection.get("matchedHumanOwner") is True
        and isinstance(active_manager, dict)
        and active_manager.get("activeVerified") is True
    )

    team_service_type = capture.get("teamServiceType")
    if not isinstance(team_service_type, str):
        team_service_type = None

    atomic = capture.get("atomicSnapshot")
    if not isinstance(atomic, bool):
        atomic = None

    unsupported = capture.get("unsupported")
    if not isinstance(unsupported, list):
        unsupported = []

    result = {
        "captureStatus": capture.get("status"),
        "selectionStatus": selection.get("status"),
        "selectionSource": selection.get("sourcePropertyKey"),
        "verifiedCurrentManager": verified_current_manager,
        "selectionReason": selection.get("reason"),
        "managerCandidateCount": manager_count,
        "activeManagerPresent": isinstance(active_manager, dict),
        "activeManagerVerified": (
            isinstance(active_manager, dict)
            and active_manager.get("activeVerified") is True
        ),
        "contractAvailable": contract_available,
        "contractKindRaw": contract_kind_raw,
        "teamAvailable": team_available,
        "clubAvailable": club_available,
        "clubTeams": club_teams,
        "positionsStatus": positions_status,
        "positionRecordCount": position_record_count,
        "employmentSummary": emp_summary,
        "teamServiceType": team_service_type,
        "atomicSnapshot": atomic,
        "hashValidation": hash_validation,
        "unsupported": unsupported,
        "limitations": [
            "Summary is derived from a single capture; not an atomic snapshot.",
            "Empty manager collection does not imply an empty or unloaded save.",
            "Club-team container is candidate structure, not a roster.",
            "Contract kind raw value has unverified semantics.",
            "No UID, name, pointer, or process identity is included.",
        ],
    }
    return result


def _make_synthetic_capture(**overrides):
    """Build a minimal synthetic capture for self-test."""
    base = {
        "status": "partial",
        "selection": {
            "status": "available",
            "sourcePropertyKey": "GCuM",
            "selectedType": ".?AVHUMAN_NON_PLAYER@db@@",
            "matchedHumanOwner": True,
            "reason": None,
        },
        "binarySha256": PINNED_GAME_PLUGIN_HASH,
        "gameAssemblySha256": PINNED_GAME_ASSEMBLY_HASH,
        "atomicSnapshot": False,
        "managerCandidates": [
            {
                "personReferenceCandidate": 100,
                "personUidCandidate": 200,
                "flag422Raw": 1,
                "contractType": ".?AVFULL_CONTRACT@db@@",
                "contractKind": 16,
                "kindMethodRva": 0x301970,
                "payloadType": ".?AVTEAM@db@@",
                "payloadField30Type": ".?AVCLUB@db@@",
                "clubUidCandidate": 300,
                "activeVerified": True,
            }
        ],
        "activeManager": {
            "uid": 200,
            "clubUid": 300,
            "contractType": ".?AVFULL_CONTRACT@db@@",
            "contractKind": 16,
            "source": "native GameCurrentManager (GCuM) selection global",
            "activeVerified": True,
            "atomicSnapshot": False,
            "clubTeams": {
                "status": "candidate-structure",
                "count": 2,
                "validatedTeamBacklinks": 2,
                "currentEmploymentTeamFound": True,
                "notPlayerRoster": True,
                "teamHierarchySemanticsVerified": False,
            },
        },
        "positions": "not-requested",
        "unsupported": ["cross-session active-selection stability"],
    }
    base.update(overrides)
    return base


def self_test():
    """Synthetic checks for the summarizer."""
    # 1. Basic summary from a well-formed capture.
    cap = _make_synthetic_capture()
    s = summarize(cap)
    assert s["captureStatus"] == "partial"
    assert s["selectionStatus"] == "available"
    assert s["selectionSource"] == "GCuM"
    assert s["verifiedCurrentManager"] is True
    assert s["managerCandidateCount"] == 1
    assert s["activeManagerPresent"] is True
    assert s["activeManagerVerified"] is True
    assert s["contractAvailable"] is True
    assert s["teamAvailable"] is True
    assert s["clubAvailable"] is True
    assert s["contractKindRaw"] == 16
    assert s["clubTeams"]["count"] == 2
    assert s["clubTeams"]["validatedTeamBacklinks"] == 2
    assert s["clubTeams"]["currentEmploymentTeamFound"] is True
    assert s["hashValidation"]["binarySha256"] == "match"
    assert s["hashValidation"]["gameAssemblySha256"] == "match"
    assert s["hashValidation"]["metadataSha256"] == "absent"

    # 2. No raw field names leaked in output.
    output_text = json.dumps(s)
    for forbidden_key in [
        "personReferenceCandidate", "personUidCandidate", "personUid",
        "clubUidCandidate", "clubUid", "kindMethodRva",
        "processId", "processStartedAt",
    ]:
        assert forbidden_key not in output_text, (
            f"raw field {forbidden_key} leaked into output"
        )

    # 3. Empty manager collection does not imply loaded save.
    cap_empty = _make_synthetic_capture(
        managerCandidates=[], activeManager=None
    )
    cap_empty["selection"]["status"] = "unavailable"
    cap_empty["selection"]["matchedHumanOwner"] = False
    s_empty = summarize(cap_empty)
    assert s_empty["managerCandidateCount"] == 0
    assert s_empty["activeManagerPresent"] is False
    assert s_empty["verifiedCurrentManager"] is False
    # No claim about empty/unloaded save in any field value.
    for v in s_empty.values():
        if isinstance(v, str):
            assert "empty save" not in v.lower()
            assert "unloaded" not in v.lower()

    # 4. Hash mismatch raises.
    cap_bad = _make_synthetic_capture(binarySha256="0" * 64)
    try:
        summarize(cap_bad)
        raise AssertionError("game_plugin hash mismatch not detected")
    except ValueError:
        pass

    # 5. GameAssembly hash mismatch raises.
    cap_bad2 = _make_synthetic_capture(gameAssemblySha256="F" * 64)
    try:
        summarize(cap_bad2)
        raise AssertionError("game assembly hash mismatch not detected")
    except ValueError:
        pass

    # 6. Metadata hash mismatch raises.
    cap_bad3 = _make_synthetic_capture(metadataSha256="A" * 64)
    try:
        summarize(cap_bad3)
        raise AssertionError("metadata hash mismatch not detected")
    except ValueError:
        pass

    # 7. Too many managers raises.
    cap_many = _make_synthetic_capture(
        managerCandidates=[{"contractType": None}] * (MAX_MANAGERS + 1)
    )
    try:
        summarize(cap_many)
        raise AssertionError("manager limit not enforced")
    except ValueError:
        pass

    # 8. Positions with employment records.
    cap_pos = _make_synthetic_capture(
        positions={
            "status": "partial",
            "records": [
                {
                    "employment": {
                        "status": "available",
                        "contractType": "FULL",
                        "teamType": "TEAM",
                        "clubType": "CLUB",
                    }
                },
                {"employment": {"status": "available", "contractType": "FULL"}},
            ],
        }
    )
    s_pos = summarize(cap_pos)
    assert s_pos["positionsStatus"] == "partial"
    assert s_pos["positionRecordCount"] == 2
    assert s_pos["employmentSummary"]["recordCount"] == 2
    assert s_pos["employmentSummary"]["withContract"] == 2
    assert s_pos["employmentSummary"]["withTeam"] == 1
    assert s_pos["employmentSummary"]["withClub"] == 1
    assert s_pos["teamAvailable"] is True
    assert s_pos["clubAvailable"] is True

    # 9. verify-repeat wrapper unwrapping.
    cap_wrapped = {"repeatVerified": True, "result": _make_synthetic_capture()}
    s_wrapped = summarize(cap_wrapped)
    assert s_wrapped["verifiedCurrentManager"] is True

    # 10. Non-dict capture raises.
    try:
        summarize("not a dict")
        raise AssertionError("non-dict not rejected")
    except ValueError:
        pass

    # 11. Contract kind absent when no managers.
    cap_no_mgr = _make_synthetic_capture(
        managerCandidates=[], activeManager=None
    )
    cap_no_mgr["selection"]["status"] = "unavailable"
    cap_no_mgr["selection"]["matchedHumanOwner"] = False
    s_no_mgr = summarize(cap_no_mgr)
    assert s_no_mgr["contractKindRaw"] is None
    assert s_no_mgr["contractAvailable"] is False

    # 12. Team service type extraction.
    cap_svc = _make_synthetic_capture(teamServiceType="GAME_TEAM")
    s_svc = summarize(cap_svc)
    assert s_svc["teamServiceType"] == "GAME_TEAM"

    # 13. Positions as string.
    cap_str = _make_synthetic_capture(positions="not-requested")
    s_str = summarize(cap_str)
    assert s_str["positionsStatus"] == "not-requested"
    assert s_str["positionRecordCount"] == 0

    # 14. Club teams absent.
    cap_no_ct = _make_synthetic_capture()
    del cap_no_ct["activeManager"]["clubTeams"]
    s_no_ct = summarize(cap_no_ct)
    assert s_no_ct["clubTeams"] is None

    print("PASS: manager summarizer synthetic checks (14 cases)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--max-input-bytes", type=int, default=MAX_INPUT_BYTES)
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.input is None:
        parser.error("input JSON file required (or use --self-test)")

    input_path = args.input
    size = input_path.stat().st_size
    if size > args.max_input_bytes:
        raise ValueError(
            f"input size {size} exceeds limit {args.max_input_bytes}"
        )
    if size == 0:
        raise ValueError("input file is empty")

    raw = input_path.read_text(encoding="utf-8-sig")
    try:
        capture = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON: {e}")

    result = summarize(capture)
    output_text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"

    if args.output is not None:
        args.output.write_text(output_text, encoding="utf-8")
        print(f"Wrote sanitized summary to {args.output}")
    else:
        print(output_text, end="")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as e:
        print(
            json.dumps({"status": "error", "reason": str(e)}),
            file=sys.stderr,
        )
        sys.exit(3)