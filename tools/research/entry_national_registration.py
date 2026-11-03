"""Machine-readable native entry manifest and validator for national-registration.

This tool records only the static RTTI/type/vtable evidence returned by the
authorized lane probe. It is an offline scaffold, not a live reader or SDK
component. No process memory, offsets, instance layout, UID linkage, or
registration semantics are invented.
"""
import argparse
import json
from pathlib import Path

LANE = "national-registration"
GAME_PLUGIN_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = "0x180000000"
CONFIRMED_TYPE = ".?AVMANAGER_APPOINTED_COMPETITION_RULES_NEWS@@"
CONFIRMED_TYPE_RVA = "0x56BC920"
CONFIRMED_VTABLE_RVA = "0x4D5E108"
CONFIRMED_VTABLE_SLOTS = [
    "0x17837F0",
    "0x24D9C0",
    "0x24D9D0",
    "0x24D9E0",
    "0x24D9F0",
    "0x24DA00",
    "0x24DA10",
    "0x24DA20",
    "0x24DA30",
    "0x24DA40",
    "0x24DA50",
    "0x24DA60",
]
CONFIRMED_RIP_CANDIDATES = [
    {
        "displacement": "0x176062E",
        "function": "0x1750CC0",
        "target": "0x4D5E108",
        "targetType": CONFIRMED_TYPE,
    },
    {
        "displacement": "0x1C9085A",
        "function": "0x1C89D70",
        "target": "0x4D5E108",
        "targetType": CONFIRMED_TYPE,
    },
]
PROPOSED_NARROWER_NAMES = [
    "REGISTRATION",
    "NATIONAL",
    "NATIONAL_TEAM",
    "SQUAD",
    "ELIGIBILITY",
    "WORK_PERMIT",
    "COMPETITION_RULES",
]
MISSING_SEMANTICS = [
    "national-team entity, tier, age group, call-up status, report/return dates, squad membership, camp, club availability (NAT-01)",
    "nationality, eligibility, represented country, caps, selection status, multiple-nationality handling (NAT-02)",
    "national-team competition history, world ranking/coefficients, age-group qualification scope (NAT-03)",
    "next-match eligibility, registration status, suspension/discipline reason, applicable competition (REG-01)",
    "registration windows, squad-size/age/homegrown quotas, foreign-player limits, work permits, registration/loan limits (REG-02)",
    "promotion/relegation/competition format, cumulative card/suspension rules, financial compliance, transfer-window boundaries (REG-03)",
    "jurisdiction-specific rules and historical changes, rule-definition versus engine-result distinction (REG-04)",
    "instance layout, vtable slot semantics, UID linkage, collection traversal, and live capture validation for the confirmed type",
]
NEXT_BOUNDED_READ_REQUEST = {
    "step1": "Run static RTTI/name searches over the same pinned binary for narrower fragments: REGISTRATION, NATIONAL, NATIONAL_TEAM, SQUAD, ELIGIBILITY, WORK_PERMIT, COMPETITION_RULES.",
    "step2": "If a candidate type and vtable are specific to national registration, request coordinator approval for a bounded process probe recording only that type, vtable slots, and RIP/xref candidates. No instance reads yet.",
    "step3": "Only after a matching type and vtable are confirmed, request a separate bounded layout probe with explicitly supplied UIDs or fixture identities. Keep all outputs outside the repository and fail closed on fingerprint mismatch.",
    "currentStatus": "static evidence only; all NAT/REG fields remain unavailable",
}


def manifest():
    return {
        "schemaVersion": 1,
        "lane": LANE,
        "tool": "entry_national_registration",
        "status": "no_match",
        "mode": "static-pinned-file",
        "probe": {
            "lane": LANE,
            "types": 1,
            "vtables": 1,
            "liveRecordsRead": 0,
            "outputTruncated": False,
        },
        "binaryProfile": {
            "gamePluginSha256": GAME_PLUGIN_SHA256,
            "imageBase": IMAGE_BASE,
        },
        "confirmedType": {
            "rttiName": CONFIRMED_TYPE,
            "moduleRelativeRva": CONFIRMED_TYPE_RVA,
            "absoluteAddress": "0x1856BC920",
        },
        "confirmedVtable": {
            "moduleRelativeRva": CONFIRMED_VTABLE_RVA,
            "observedSlotCount": len(CONFIRMED_VTABLE_SLOTS),
            "slots": list(CONFIRMED_VTABLE_SLOTS),
            "slotRvas": list(CONFIRMED_VTABLE_SLOTS),
            "vtableSlots": list(CONFIRMED_VTABLE_SLOTS),
        },
        "ripCandidates": [dict(item) for item in CONFIRMED_RIP_CANDIDATES],
        "match": {
            "status": "no_match",
            "matchedType": None,
            "reason": (
                "The only confirmed RTTI type, MANAGER_APPOINTED_COMPETITION_RULES_NEWS, "
                "is a news item about a manager being appointed to competition rules. "
                "It is not a national-registration, national-team, squad-registration, "
                "eligibility, quota, work-permit, or competition-rule entity."
            ),
        },
        "entryHypothesis": {
            "status": "unverified",
            "text": (
                "The only verified native entry surface is a news type. It may be a "
                "downstream notification or presentation object rather than a data "
                "owner. No instance layout, collection pointer, field offset, UID "
                "relation, or registration state is confirmed, so this lane has no "
                "usable business-object entry."
            ),
        },
        "offsets": {},
        "missingSemantics": list(MISSING_SEMANTICS),
        "nextBoundedReadRequest": dict(NEXT_BOUNDED_READ_REQUEST),
        "proposedNarrowerNames": list(PROPOSED_NARROWER_NAMES),
        "safety": {
            "liveReader": False,
            "processRead": False,
            "sdk": False,
            "writesEnabled": False,
        },
    }


def _vtable_slots(candidate):
    vtable = candidate.get("confirmedVtable", candidate.get("vtable", {}))
    if not isinstance(vtable, dict):
        return None
    for key in ("slots", "slotRvas", "vtableSlots"):
        value = vtable.get(key)
        if isinstance(value, list):
            return [str(item).lower() for item in value]
    return None


def _rip_candidates(candidate):
    value = candidate.get("ripCandidates", candidate.get("rip_candidates", candidate.get("candidates")))
    if not isinstance(value, list):
        return None
    result = []
    for item in value:
        if not isinstance(item, dict):
            return None
        result.append(
            {
                "displacement": str(
                    item.get("displacement", item.get("displacementRva", item.get("displacement_rva", "")))
                ).lower(),
                "function": str(item.get("function", item.get("functionRva", item.get("function_rva", "")))).lower(),
                "target": str(item.get("target", item.get("targetRva", item.get("target_rva", "")))).lower(),
                "targetType": str(item.get("targetType", item.get("target_type", item.get("type", "")))),
            }
        )
    return result


def validate_manifest(candidate):
    if not isinstance(candidate, dict):
        raise ValueError("manifest must be a JSON object")

    if candidate.get("lane", candidate.get("laneId", candidate.get("lane_id"))) != LANE:
        raise ValueError("lane must be national-registration")

    status = candidate.get("status")
    if status != "no_match":
        raise ValueError("status must be no_match for this lane")

    match = candidate.get("match")
    if not isinstance(match, dict) or match.get("status") != "no_match":
        raise ValueError("match.status must be no_match")

    profile = candidate.get("binaryProfile", candidate.get("binary_profile", {}))
    if not isinstance(profile, dict):
        raise ValueError("binaryProfile must be an object")
    if str(profile.get("gamePluginSha256", profile.get("game_plugin_sha256", ""))).upper() != GAME_PLUGIN_SHA256:
        raise ValueError("game_plugin.dll SHA256 mismatch")

    type_info = candidate.get("confirmedType", candidate.get("confirmed_type", candidate.get("type", {})))
    if not isinstance(type_info, dict):
        raise ValueError("confirmedType must be an object")
    if type_info.get("rttiName", type_info.get("rtti_name", type_info.get("name"))) != CONFIRMED_TYPE:
        raise ValueError("confirmed RTTI type mismatch")

    type_rva = type_info.get("moduleRelativeRva", type_info.get("module_relative_rva", type_info.get("rva")))
    if str(type_rva).lower() != CONFIRMED_TYPE_RVA.lower():
        raise ValueError("confirmed type RVA mismatch")

    vtable = candidate.get("confirmedVtable", candidate.get("confirmed_vtable", candidate.get("vtable", {})))
    if not isinstance(vtable, dict):
        raise ValueError("confirmedVtable must be an object")
    vtable_rva = vtable.get("moduleRelativeRva", vtable.get("module_relative_rva", vtable.get("rva")))
    if str(vtable_rva).lower() != CONFIRMED_VTABLE_RVA.lower():
        raise ValueError("confirmed vtable RVA mismatch")

    slots = _vtable_slots(candidate)
    expected_slots = [item.lower() for item in CONFIRMED_VTABLE_SLOTS]
    if slots != expected_slots:
        raise ValueError("confirmed vtable slots mismatch")

    rips = _rip_candidates(candidate)
    expected_rips = [
        {
            "displacement": item["displacement"].lower(),
            "function": item["function"].lower(),
            "target": item["target"].lower(),
            "targetType": item["targetType"],
        }
        for item in CONFIRMED_RIP_CANDIDATES
    ]
    if rips != expected_rips:
        raise ValueError("confirmed RIP candidates mismatch")

    offsets = candidate.get("offsets", {})
    if offsets not in ({}, None):
        if not isinstance(offsets, dict) or any(value not in (None, "", "unknown", "unavailable") for value in offsets.values()):
            raise ValueError("unresolved offsets must be absent or unknown")
    for forbidden in ("entryOffset", "entry_offset", "instanceSize", "instance_size", "entryPoint", "entry_point"):
        if candidate.get(forbidden) not in (None, "", "unknown", "unavailable"):
            raise ValueError("invented entry offset or size is not allowed")

    proposed = candidate.get("proposedNarrowerNames", candidate.get("proposed_narrower_names", candidate.get("proposedNames")))
    if not isinstance(proposed, list) or not proposed:
        raise ValueError("proposedNarrowerNames must be a non-empty list")

    missing = candidate.get("missingSemantics", candidate.get("missing_semantics"))
    if not isinstance(missing, list) or not missing:
        raise ValueError("missingSemantics must be a non-empty list")

    next_request = candidate.get("nextBoundedReadRequest", candidate.get("next_bounded_read_request"))
    if not isinstance(next_request, dict) or not next_request:
        raise ValueError("nextBoundedReadRequest must be a non-empty object")

    safety = candidate.get("safety", {})
    if isinstance(safety, dict):
        if safety.get("liveReader") is True or safety.get("live_reader") is True:
            raise ValueError("this scaffold must not claim to be a live reader")
        if safety.get("sdk") is True:
            raise ValueError("this scaffold must not claim to be SDK")

    return {
        "status": "valid",
        "lane": LANE,
        "matchStatus": "no_match",
        "confirmedType": CONFIRMED_TYPE,
        "confirmedVtable": CONFIRMED_VTABLE_RVA,
    }


def self_test():
    good = manifest()
    result = validate_manifest(good)
    assert result["status"] == "valid"
    assert result["matchStatus"] == "no_match"

    bad_offset = dict(good)
    bad_offset["offsets"] = {"entryOffset": "0x10"}
    try:
        validate_manifest(bad_offset)
    except ValueError:
        pass
    else:
        raise AssertionError("invented offset was accepted")

    bad_match = dict(good)
    bad_match["status"] = "matched"
    bad_match["match"] = {"status": "matched"}
    try:
        validate_manifest(bad_match)
    except ValueError:
        pass
    else:
        raise AssertionError("false match was accepted")

    bad_type = dict(good)
    bad_type["confirmedType"] = dict(good["confirmedType"])
    bad_type["confirmedType"]["rttiName"] = ".?AVFAKE_TYPE@@"
    try:
        validate_manifest(bad_type)
    except ValueError:
        pass
    else:
        raise AssertionError("wrong RTTI type was accepted")

    bad_slot = dict(good)
    bad_slot["confirmedVtable"] = dict(good["confirmedVtable"])
    bad_slot["confirmedVtable"]["slots"] = list(good["confirmedVtable"]["slots"])
    bad_slot["confirmedVtable"]["slots"][0] = "0x0"
    bad_slot["confirmedVtable"]["slotRvas"] = list(bad_slot["confirmedVtable"]["slots"])
    bad_slot["confirmedVtable"]["vtableSlots"] = list(bad_slot["confirmedVtable"]["slots"])
    try:
        validate_manifest(bad_slot)
    except ValueError:
        pass
    else:
        raise AssertionError("changed vtable slot was accepted")

    assert good["offsets"] == {}

    print("PASS: no-match status, confirmed RTTI/vtable evidence, RIP candidates, empty offsets, and rejection of invented offsets/matches/types/slots")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="manifest JSON to validate")
    parser.add_argument("--output", type=Path, help="write canonical manifest JSON to this path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.input is not None:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = validate_manifest(data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    rendered = json.dumps(manifest(), ensure_ascii=False, indent=2)
    if args.output is not None:
        output = args.output.resolve()
        repo = Path(__file__).resolve().parents[2]
        if output.is_relative_to(repo):
            parser.error("private manifest output must remain outside repository")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Manifest written: {output}")
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
