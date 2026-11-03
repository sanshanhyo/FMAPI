#!/usr/bin/env python3
"""Machine-readable manifest for confirmed native entry evidence.

This tool reports only RTTI type and vtable evidence confirmed by the
staff-responsibilities static probe. It does not read a process, game file,
save, UI, or network resource, and it does not invent field offsets.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

NATIVE_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = 0x180000000
PROBE_LANE = "staff-responsibilities"
PROBE_MODE = "static-pinned-file"
PROBE_TYPES = 13
PROBE_VTABLES = 11
PROBE_LIVE_RECORDS_READ = 0

BUSINESS_OBJECT_CANDIDATES = [
    {
        "typeName": ".?AVHUMAN_NON_PLAYER@db@@",
        "typeInfoRva": 0x568A2E0,
        "vtables": [0x4CC0888, 0x4CC08D8],
    },
    {
        "typeName": ".?AVEXTERN_ACTUAL_NON_PLAYER@db@@",
        "typeInfoRva": 0x569D170,
        "vtables": [],
    },
    {
        "typeName": ".?AVEXTERN_HUMAN_NON_PLAYER@db@@",
        "typeInfoRva": 0x569DF90,
        "vtables": [],
    },
    {
        "typeName": ".?AVACTUAL_NON_PLAYER@db@@",
        "typeInfoRva": 0x56A6160,
        "vtables": [0x4D8BE28, 0x4D8BE78],
    },
    {
        "typeName": ".?AVACTUAL_PLAYER_AND_NON_PLAYER@db@@",
        "typeInfoRva": 0x56E1AD0,
        "vtables": [0x4F75A08, 0x4F75EE8, 0x4F75F38],
    },
]

IMPLEMENTATION_ARTIFACTS = [
    {
        "typeName": ".?AV?$_Func_impl_no_alloc@V<lambda_1>@?0??generate_past_match_chalkboard_data@MATCH_COORDINATOR@@QEAAXAEAVHUMAN_NON_PLAYER@db@@AEBVTEAM_BASE@5@AEBVSI_DATE@fmdate@@@Z@X$$V@std@@",
        "typeInfoRva": 0x56A4500,
        "vtables": [0x4CBC938],
    },
    {
        "typeName": ".?AV<lambda_1>@?0??generate_past_match_chalkboard_data@MATCH_COORDINATOR@@QEAAXAEAVHUMAN_NON_PLAYER@db@@AEBVTEAM_BASE@4@AEBVSI_DATE@fmdate@@@Z@",
        "typeInfoRva": 0x56A4620,
        "vtables": [],
    },
    {
        "typeName": ".?AV?$_Func_impl_no_alloc@V<lambda_0>@?0??generate_past_match_chalkboard_data@MATCH_COORDINATOR@@QEAAXAEAVHUMAN_NON_PLAYER@db@@AEBVTEAM_BASE@5@AEBVSI_DATE@fmdate@@@Z@_NAEBV56@@std@@",
        "typeInfoRva": 0x56A46C0,
        "vtables": [0x4CBCA68],
    },
    {
        "typeName": ".?AV?$_Func_impl_no_alloc@V<lambda_1>@?0???R<lambda_0>@?0??generate_past_match_chalkboard_data@MATCH_COORDINATOR@@QEAAXAEAVHUMAN_NON_PLAYER@db@@AEBVTEAM_BASE@6@AEBVSI_DATE@fmdate@@@Z@QEBA?A?<auto>@@XZ@X$$V@std@@",
        "typeInfoRva": 0x56A4790,
        "vtables": [0x4CBCB08],
    },
    {
        "typeName": ".?AV<lambda_1>@?0???R<lambda_0>@?0??generate_past_match_chalkboard_data@MATCH_COORDINATOR@@QEAAXAEAVHUMAN_NON_PLAYER@db@@AEBVTEAM_BASE@5@AEBVSI_DATE@fmdate@@@Z@QEBA?A?<auto>@@XZ@",
        "typeInfoRva": 0x56A4880,
        "vtables": [],
    },
    {
        "typeName": ".?AV<lambda_0>@?0??generate_past_match_chalkboard_data@MATCH_COORDINATOR@@QEAAXAEAVHUMAN_NON_PLAYER@db@@AEBVTEAM_BASE@4@AEBVSI_DATE@fmdate@@@Z@",
        "typeInfoRva": 0x56A4950,
        "vtables": [],
    },
    {
        "typeName": ".?AV?$_Func_impl_no_alloc@V<lambda_0>@?0??load@HUMAN_NON_PLAYER@db@@UEAA_NAEBV?$REFERENCE_COUNTER@$$CBVINPUT_STREAM@sicore@@@sicore@@_NPEAVDATABASE@4@W4DATABASE_TABLE_TYPE@@H1PEAVDATABASE_TABLE_BASE@4@@Z@_NAEBV56@@std@@",
        "typeInfoRva": 0x56A5F30,
        "vtables": [0x4CC11D8],
    },
    {
        "typeName": ".?AV<lambda_0>@?0??load@HUMAN_NON_PLAYER@db@@UEAA_NAEBV?$REFERENCE_COUNTER@$$CBVINPUT_STREAM@sicore@@@sicore@@_NPEAVDATABASE@3@W4DATABASE_TABLE_TYPE@@H1PEAVDATABASE_TABLE_BASE@3@@Z@",
        "typeInfoRva": 0x56A6090,
        "vtables": [],
    },
]

VTABLE_SLOTS = {
    0x4CBC938: ["0xE70FD0", "0xE70FF0", "0xE71010", "0xE712B0", "0xE712C0", "0xE712D0", "invalid", "invalid", "0x56A44FE80000000", "0x4CBC96E84CBC988", "invalid", "0x4CBC99680000002"],
    0x4CBCA68: ["0xE71410", "0xE71430", "0xE71450", "0xE71720", "0xE71730", "0xE71740", "invalid", "invalid", "0x56A46BE80000000", "0x4CBCA9E84CBCAB8", "invalid", "0x4CBCAC680000002"],
    0x4CBCB08: ["0xE71750", "0xE71770", "0xE71790", "0xE71880", "0xE71890", "0xE718A0", "invalid", "invalid", "0x56A478E80000000", "0x4CBCB3E84CBCB58", "invalid", "0x4CBCB6680000002"],
    0x4CC0888: ["0xF47460", "0x19260A0", "0xF2FCC0", "0xF2FDC0", "0xF47480", "0xF47490", "0xF474A0", "0xF474C0", "0xF474E0", "0x4CC11B0", "0xF474F0", "0xF29C90"],
    0x4CC08D8: ["0xF474F0", "0xF29C90", "0xF25BD0", "0xF47680", "0xF47710", "0xF47730", "0xF47760", "0x5E6920", "0xF80D60", "0xF75E90", "0x4143D0", "0xF6E0A0"],
    0x4CC11D8: ["0xF5ED10", "0xF5ED30", "0xF5ED50", "0xF5F270", "0xF5F280", "0xF5F290", "invalid", "invalid", "0x56A5F2E80000000", "0x4CC120E84CC1228", "invalid", "0x4CC123680000002"],
    0x4D8BE28: ["0x17DB6C0", "0x19260A0", "0x16336A0", "0x17ED170", "0x17EC7C0", "0x17EC7B0", "0x17EC9E0", "0x17EC790", "0x17EFE30", "0x4D8C600", "0x17EFE40", "0x17EB900"],
    0x4D8BE78: ["0x17EFE40", "0x17EB900", "0x17DFCA0", "0x17DB6D0", "0x17DD370", "0x17EFFD0", "0x17F0000", "0x5E6920", "0xF80D60", "0xF75E90", "0x4143D0", "0xF6E0A0"],
    0x4F75A08: ["0x16361F0", "0x15D4F70", "0x15F7060", "0x15F7070", "0x15D4F80", "0x15D4F60", "0x15D4F50", "0x15F7F00", "0x15EAF40", "0x15EB200", "0x15EAF30", "0x15E1760"],
    0x4F75EE8: ["0x3991BC0", "0x19260A0", "0x16336A0", "0x17ED170", "0x3991D80", "0x3991D70", "0x3991D90", "0x39920F0", "0x3992150", "0x4F76740", "0x3992170", "0x39920A0"],
    0x4F75F38: ["0x3992170", "0x39920A0", "0x3992030", "0x3991C50", "0x3991FF0", "0x3992310", "0x3992340", "0x5E6920", "0xF80D60", "0xF75E90", "0x4143D0", "0xF6E0A0"],
}

PROPOSED_NARROWER_NAMES = [
    "STAFF",
    "STAFF_MEMBER",
    "NON_PLAYER_STAFF",
    "HUMAN_STAFF",
    "ACTUAL_STAFF",
    "EXTERN_STAFF",
    "COACH",
    "SCOUT",
    "MEDICAL_STAFF",
    "ANALYST",
    "STAFF_RESPONSIBILITY",
]


class EntryError(Exception):
    """Raised for invalid manifest or evidence data."""


def build_type_entries(entries, category):
    result = []
    for item in entries:
        result.append(
            {
                "category": category,
                "typeName": item["typeName"],
                "typeInfoRva": item["typeInfoRva"],
                "vtables": [
                    {
                        "vtableRva": vtable,
                        "slots": VTABLE_SLOTS[vtable],
                    }
                    for vtable in item["vtables"]
                ],
                "offsets": "unknown",
            }
        )
    return result


def build_manifest():
    type_entries = build_type_entries(
        BUSINESS_OBJECT_CANDIDATES, "business-object-candidate"
    ) + build_type_entries(IMPLEMENTATION_ARTIFACTS, "implementation-artifact")

    vtable_entries = []
    for vtable, slots in VTABLE_SLOTS.items():
        owner = None
        for item in BUSINESS_OBJECT_CANDIDATES + IMPLEMENTATION_ARTIFACTS:
            if vtable in item["vtables"]:
                owner = item["typeName"]
                break
        vtable_entries.append(
            {
                "vtableRva": vtable,
                "typeName": owner,
                "slotCount": len(slots),
                "slots": slots,
            }
        )

    return {
        "schema": "fmapi.native-entry.manifest.v1",
        "lane": PROBE_LANE,
        "binary": {
            "name": "game_plugin.dll",
            "sha256": NATIVE_SHA256,
            "imageBase": IMAGE_BASE,
        },
        "probe": {
            "mode": PROBE_MODE,
            "typesReported": PROBE_TYPES,
            "vtablesReported": PROBE_VTABLES,
            "liveRecordsRead": PROBE_LIVE_RECORDS_READ,
        },
        "counts": {
            "types": len(type_entries),
            "vtables": len(vtable_entries),
            "businessObjectCandidates": len(BUSINESS_OBJECT_CANDIDATES),
            "implementationArtifacts": len(IMPLEMENTATION_ARTIFACTS),
        },
        "types": type_entries,
        "vtables": vtable_entries,
        "staffSpecific": {
            "confirmedType": None,
            "exactMatch": False,
            "proposedNarrowerNames": PROPOSED_NARROWER_NAMES,
        },
        "offsets": "unknown",
    }


def validate_manifest(manifest):
    if not isinstance(manifest, dict):
        raise EntryError("manifest must be an object")
    for key in ("schema", "lane", "binary", "probe", "counts", "types", "vtables", "staffSpecific", "offsets"):
        if key not in manifest:
            raise EntryError(f"missing manifest key: {key}")

    if manifest["binary"].get("sha256") != NATIVE_SHA256:
        raise EntryError("unsupported binary fingerprint")
    if manifest["lane"] != PROBE_LANE:
        raise EntryError("unsupported probe lane")
    if manifest["probe"].get("liveRecordsRead") != 0:
        raise EntryError("live records must not be claimed")
    if manifest["counts"].get("types") != len(manifest["types"]):
        raise EntryError("type count mismatch")
    if manifest["counts"].get("vtables") != len(manifest["vtables"]):
        raise EntryError("vtable count mismatch")
    if manifest["counts"].get("types") != PROBE_TYPES:
        raise EntryError("unexpected confirmed type count")
    if manifest["counts"].get("vtables") != PROBE_VTABLES:
        raise EntryError("unexpected confirmed vtable count")
    if manifest["staffSpecific"].get("confirmedType") is not None:
        raise EntryError("staff-specific type is not confirmed")
    if manifest["staffSpecific"].get("exactMatch") is not False:
        raise EntryError("staff-specific exact match must be false")
    if not manifest["staffSpecific"].get("proposedNarrowerNames"):
        raise EntryError("proposed narrower names are required")

    for entry in manifest["types"]:
        if entry.get("offsets") != "unknown":
            raise EntryError("unresolved offsets must be unknown")
        if not isinstance(entry.get("typeName"), str) or not entry["typeName"]:
            raise EntryError("invalid type name")
        if not isinstance(entry.get("typeInfoRva"), int):
            raise EntryError("invalid type RVA")
        for vtable in entry.get("vtables", []):
            if vtable["vtableRva"] not in VTABLE_SLOTS:
                raise EntryError("unconfirmed vtable")
            if vtable["slots"] != VTABLE_SLOTS[vtable["vtableRva"]]:
                raise EntryError("vtable slot mismatch")

    for entry in manifest["vtables"]:
        if entry["vtableRva"] not in VTABLE_SLOTS:
            raise EntryError("unconfirmed vtable")
        if entry["slots"] != VTABLE_SLOTS[entry["vtableRva"]]:
            raise EntryError("vtable slot mismatch")
        if entry["slotCount"] != len(entry["slots"]):
            raise EntryError("vtable slot count mismatch")


def self_test():
    manifest = build_manifest()
    validate_manifest(manifest)
    assert manifest["counts"]["types"] == 13
    assert manifest["counts"]["vtables"] == 11
    assert manifest["staffSpecific"]["confirmedType"] is None
    assert manifest["staffSpecific"]["exactMatch"] is False

    bad = json.loads(json.dumps(manifest))
    bad["counts"]["types"] = 12
    try:
        validate_manifest(bad)
    except EntryError:
        pass
    else:
        raise AssertionError("invalid manifest was accepted")

    bad_slots = json.loads(json.dumps(manifest))
    bad_slots["types"][0]["vtables"][0]["slots"][0] = "0x0"
    try:
        validate_manifest(bad_slots)
    except EntryError:
        pass
    else:
        raise AssertionError("corrupted vtable slots were accepted")

    print("PASS: confirmed RTTI manifest, vtable slots, no-match status, and fail-closed checks")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Machine-readable manifest for confirmed native entry RTTI evidence."
    )
    parser.add_argument("--output", help="write JSON manifest to this path")
    parser.add_argument("--validate", help="validate an existing manifest JSON file")
    parser.add_argument("--self-test", action="store_true", help="run synthetic checks only")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        return 0

    manifest = build_manifest()
    if args.validate:
        path = Path(args.validate)
        if not path.is_file():
            raise EntryError(f"manifest file not found: {path}")
        candidate = json.loads(path.read_text(encoding="utf-8"))
        validate_manifest(candidate)
        print(json.dumps({"status": "valid", "schema": candidate.get("schema")}, indent=2))
        return 0

    rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (EntryError, OSError, ValueError, json.JSONDecodeError) as error:
        sys.stderr.write(json.dumps({"status": "unavailable", "reason": str(error)}, ensure_ascii=False) + "\n")
        raise SystemExit(3)
