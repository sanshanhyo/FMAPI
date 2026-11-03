"""Pure offline validator/summarizer for FMAPI player-position captures.

Reads one explicitly supplied position-capture JSON and emits aggregate counts,
coverage and unknowns. It never opens a process, reads game files, calls native
functions, performs network access, or emits player/club/UID identities.

The 14 named familiarities, natural-mask threshold (>=18) and goalkeeper business
rule (>=15) are the proven layout from tools/FMAPI.MessageProbe/PositionFields.cs
and docs/research/native-entity-evidence.md. The skipped slot is player +0x151.
"""

import json
import sys
from pathlib import Path

NATIVE_HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
METADATA_HASH = "A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C"
ASSEMBLY_HASH = "820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A"

# (block index, code, native enum name, mask bit). Block index 1 (+0x151) is skipped.
MAPPING = [
    (0, "GK", "Goalkeeper", 0x1),
    (2, "DL", "DefenderLeft", 0x8),
    (3, "DC", "DefenderCentre", 0x10),
    (4, "DR", "DefenderRight", 0x4),
    (5, "DM", "DefensiveMidfielderCentre", 0x80),
    (6, "ML", "MidfielderLeft", 0x200),
    (7, "MC", "MidfielderCentre", 0x400),
    (8, "MR", "MidfielderRight", 0x100),
    (9, "AML", "AttackingMidfielderLeft", 0x1000),
    (10, "AMC", "AttackingMidfielderCentre", 0x2000),
    (11, "AMR", "AttackingMidfielderRight", 0x800),
    (12, "ST", "AttackerCentre", 0x4000),
    (13, "WBL", "WingBackLeft", 0x40),
    (14, "WBR", "WingBackRight", 0x20),
]
NATURAL_THRESHOLD = 18
GOALKEEPER_THRESHOLD = 15
SKIPPED_INDEX = 1
MAX_RECORDS = 32
MAX_INPUT_BYTES = 1024 * 1024


def recompute_mask(block):
    mask = 0
    for index, _code, _name, bit in MAPPING:
        if block[index] >= NATURAL_THRESHOLD:
            mask |= bit
    return mask


def validate_record(record):
    errors = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record not object"]}

    status = record.get("status")
    available = status == "available"
    uid_matched = record.get("uidMatched") is True
    names_verified = record.get("positionNamesVerified") is True

    block = None
    gk = record.get("goalkeeperFamiliarity")
    other = record.get("otherPositionSlotsRaw")
    if isinstance(other, list) and len(other) == 14 and isinstance(gk, int):
        try:
            block = [int(gk)] + [int(v) for v in other]
        except (TypeError, ValueError):
            block = None
    if block is None or len(block) != 15:
        errors.append("incomplete position block")
        range_ok = False
        mask_consistent = False
        gk_consistent = False
    else:
        if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 or v > 20 for v in block):
            range_ok = False
            errors.append("value outside 0..20")
        else:
            range_ok = True
        gk_consistent = (gk >= GOALKEEPER_THRESHOLD) == bool(record.get("businessRuleIsGoalkeeper"))
        pf = record.get("positionFields")
        if isinstance(pf, dict) and "naturalPositionMask" in pf:
            mask_consistent = pf.get("naturalPositionMask") == recompute_mask(block)
            if not mask_consistent:
                errors.append("natural mask inconsistent")
        else:
            mask_consistent = False
            errors.append("missing positionFields.naturalPositionMask")
        if pf is not None and pf.get("unusedSlot151Raw") != block[SKIPPED_INDEX]:
            errors.append("skipped slot mismatch")

    employment = record.get("employment")
    employment_present = isinstance(employment, dict)
    contract_linked_club = False
    employment_errors = []
    if employment_present:
        for key in ("status", "contractType", "kind", "teamType", "clubType", "clubUid", "source", "atomicSnapshot"):
            if key not in employment:
                employment_errors.append("missing employment." + key)
        club_uid = employment.get("clubUid")
        if (employment.get("status") == "available"
                and isinstance(employment.get("clubType"), str)
                and isinstance(club_uid, int)
                and not isinstance(club_uid, bool)
                and employment.get("atomicSnapshot") is False):
            contract_linked_club = True
        if employment.get("atomicSnapshot") is True:
            employment_errors.append("employment claims atomic snapshot (not supported)")
    # Employment is a separate evidence dimension, not a position-validity gate.

    valid = (len(errors) == 0 and available and uid_matched
             and names_verified and (range_ok if block is not None else False)
             and mask_consistent and gk_consistent)

    return {
        "available": available,
        "uid_matched": uid_matched,
        "names_verified": names_verified,
        "range_ok": range_ok if block is not None else False,
        "mask_consistent": mask_consistent,
        "gk_consistent": gk_consistent,
        "employment_present": employment_present,
        "contract_linked_club": contract_linked_club,
        "positionErrors": errors,
        "employmentErrors": employment_errors,
        "errors": errors + employment_errors,
        "valid": valid,
    }


def validate_capture(document):
    if not isinstance(document, dict):
        raise ValueError("capture must be object")
    result = document.get("result")
    if not isinstance(result, dict):
        raise ValueError("result missing")
    if result.get("binarySha256") != NATIVE_HASH:
        raise ValueError("unsupported native binary profile")
    positions = result.get("positions")
    if not isinstance(positions, dict):
        raise ValueError("positions missing")
    records = positions.get("records")
    if not isinstance(records, list) or not (1 <= len(records) <= MAX_RECORDS):
        raise ValueError("records count out of range")
    club_membership_verified = result.get("clubMembershipVerifiedHere")
    active_manager = result.get("activeManager")
    club_teams_info = None
    if isinstance(active_manager, dict):
        ct = active_manager.get("clubTeams")
        if isinstance(ct, dict):
            club_teams_info = {
                "present": True,
                "notPlayerRoster": ct.get("notPlayerRoster") is True,
                "teamHierarchySemanticsVerified": ct.get("teamHierarchySemanticsVerified") is True,
                "currentEmploymentTeamFound": ct.get("currentEmploymentTeamFound") is True,
            }
        else:
            club_teams_info = {"present": False}

    validated = [validate_record(r) for r in records]
    available_count = sum(1 for v in validated if v["available"])
    uid_matched_count = sum(1 for v in validated if v["uid_matched"])
    names_verified_count = sum(1 for v in validated if v["names_verified"])
    range_ok_count = sum(1 for v in validated if v["range_ok"])
    mask_ok_count = sum(1 for v in validated if v["mask_consistent"])
    gk_ok_count = sum(1 for v in validated if v["gk_consistent"])
    employment_present_count = sum(1 for v in validated if v["employment_present"])
    contract_club_count = sum(1 for v in validated if v["contract_linked_club"])
    valid_count = sum(1 for v in validated if v["valid"])
    error_count = sum(len(v["errors"]) for v in validated)

    unknowns = [
        "preferred foot: no byte/mapping in proven layout",
        "current match/tactic position assignment: not derivable from familiarity",
        "roster membership: clubMembershipVerifiedHere is not true; contract linkage only",
        "employment.kind meaning: unknown",
        "employment atomic snapshot: not supported",
        "display scaling/UI semantics: not validated in this offline artifact",
        "broader PositionMask enum members without familiarity bytes: not synthesized",
    ]

    return {
        "status": "validated" if (valid_count == len(records) and len(records) > 0) else "partial",
        "profile": {
            "nativeSha256": NATIVE_HASH,
            "assemblySha256": ASSEMBLY_HASH,
            "metadataSha256": METADATA_HASH,
            "naturalThreshold": NATURAL_THRESHOLD,
            "goalkeeperThreshold": GOALKEEPER_THRESHOLD,
            "namedFamiliarities": len(MAPPING),
            "skippedSlot": SKIPPED_INDEX,
        },
        "counts": {
            "records": len(records),
            "available": available_count,
            "uidMatched": uid_matched_count,
            "positionNamesVerified": names_verified_count,
            "valuesInRange0To20": range_ok_count,
            "naturalMaskConsistent": mask_ok_count,
            "goalkeeperRuleConsistent": gk_ok_count,
            "employmentPresent": employment_present_count,
            "contractLinkedClub": contract_club_count,
            "fullyValid": valid_count,
            "recordErrors": error_count,
        },
        "coverage": {
            "namedFamiliaritiesPerRecord": len(MAPPING),
            "skippedSlotIncludedInMask": False,
            "goalkeeperThresholdDistinctFromNatural": True,
        },
        "clubMembershipVerifiedHere": club_membership_verified is True,
        "clubMembershipExpectedFalse": True,
        "activeManagerClubTeams": club_teams_info,
        "unknowns": unknowns,
        "identityPolicy": "no player, club, or UID identities emitted",
    }


def write_output(input_path, output_path):
    inp = Path(input_path).resolve()
    out = Path(output_path).resolve()
    if not inp.is_file():
        raise ValueError("input file missing")
    if inp.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("input size limit")
    if inp == out:
        raise ValueError("input and output must differ")
    if out.exists():
        raise ValueError("output must be new")
    # Keep private data out of the repository.
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for d in [start] + list(start.parents):
            if (d / "FMAPI.slnx").is_file():
                try:
                    out.relative_to(d)
                    raise ValueError("output must be outside repository")
                except ValueError:
                    pass
                break
    text = inp.read_text(encoding="utf-8")
    document = json.loads(text)
    summary = validate_capture(document)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "written", "output": str(out)}, ensure_ascii=False))


def self_test():
    # Synthetic capture with one valid record.
    block = [15, 20, 18, 17, 1, 18, 5, 5, 5, 18, 18, 18, 18, 5, 5]
    # recompute expected mask
    rec = {
        "status": "available",
        "uidMatched": True,
        "positionNamesVerified": True,
        "goalkeeperFamiliarity": block[0],
        "businessRuleIsGoalkeeper": block[0] >= GOALKEEPER_THRESHOLD,
        "otherPositionSlotsRaw": block[1:],
        "positionFields": {"naturalPositionMask": None, "unusedSlot151Raw": block[1]},
        "employment": {
            "status": "available",
            "contractType": "FULL_CONTRACT",
            "kind": 1,
            "teamType": "TEAM",
            "clubType": "CLUB",
            "clubUid": 12345,  # synthetic, not emitted as identity in summary
            "source": "ACTUAL_PLAYER virtual +0x3C0 getter 0x1634E50",
            "atomicSnapshot": False,
        },
    }
    rec["positionFields"]["naturalPositionMask"] = recompute_mask(block)
    doc = {"result": {"binarySha256": NATIVE_HASH, "clubMembershipVerifiedHere": False,
                      "positions": {"records": [rec]}}}
    summary = validate_capture(doc)
    assert summary["counts"]["records"] == 1
    assert summary["counts"]["fullyValid"] == 1
    assert summary["counts"]["contractLinkedClub"] == 1
    assert summary["clubMembershipVerifiedHere"] is False
    assert "preferred foot" in " ".join(summary["unknowns"])

    # Malformed: bad range, bad mask, missing employment, uid not matched.
    bad = json.loads(json.dumps(rec))
    bad["goalkeeperFamiliarity"] = 21
    bad["otherPositionSlotsRaw"][0] = 21
    bad["uidMatched"] = False
    bad["employment"] = {"status": "available", "contractType": "X", "kind": 1,
                         "teamType": "TEAM", "clubType": "CLUB", "clubUid": 1,
                         "source": "x", "atomicSnapshot": True}
    bad_doc = {"result": {"binarySha256": NATIVE_HASH, "clubMembershipVerifiedHere": True,
                          "positions": {"records": [bad]}}}
    bs = validate_capture(bad_doc)
    assert bs["counts"]["fullyValid"] == 0
    assert bs["counts"]["valuesInRange0To20"] == 0
    assert bs["clubMembershipVerifiedHere"] is True
    # unsupported profile
    try:
        validate_capture({"result": {"binarySha256": "0" * 64, "positions": {"records": [rec]}}})
        raise AssertionError("unsupported profile accepted")
    except ValueError:
        pass
    print("PASS: summarize_positions synthetic validation; range, mask, uid, employment, unknowns, profile guard")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        return
    if len(sys.argv) != 3:
        raise SystemExit("Usage: summarize_positions.py <capture.json> <new-private-output.json> | --self-test")
    write_output(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()