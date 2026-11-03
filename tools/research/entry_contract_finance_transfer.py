#!/usr/bin/env python3
"""Machine-readable native-entry manifest and validator for the contract-finance-transfer lane.

This is an offline scaffold only. It records confirmed RTTI type and vtable evidence
from the authorized static probe. It does not open a process, read memory, or claim
field offsets that are not established.
"""
import argparse
import json
from pathlib import Path

LANE = "contract-finance-transfer"
IMAGE_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = "0x180000000"
MODE = "static-pinned-file"

CONFIRMED_TYPES = [
    {
        "name": "FULL_CONTRACT",
        "namespace": "db",
        "rtti": ".?AVFULL_CONTRACT@db@@",
        "rttiRva": "0x567B9A0",
        "status": "confirmed-type",
        "source": "run-lane-probe contract-finance-transfer",
    },
    {
        "name": "EXTERN_FULL_CONTRACT",
        "namespace": "db",
        "rtti": ".?AVEXTERN_FULL_CONTRACT@db@@",
        "rttiRva": "0x569DE60",
        "status": "confirmed-type",
        "source": "run-lane-probe contract-finance-transfer",
    },
]

CONFIRMED_TYPE_MAP = {item["rtti"]: item for item in CONFIRMED_TYPES}

VTABLE_SLOTS = [
    0x301930,
    0x23437E0,
    0x2342E00,
    0x2337DD0,
    0x2338F30,
    0x2339040,
    0x23390A0,
    0x23532F0,
    0x301960,
    0x2347930,
    0x301970,
    0x301980,
]

CONFIRMED_VTABLES = [
    {
        "ownerType": "FULL_CONTRACT",
        "rtti": ".?AVFULL_CONTRACT@db@@",
        "vtableRva": "0x4B00AE8",
        "slotCount": len(VTABLE_SLOTS),
        "slots": [f"0x{value:x}" for value in VTABLE_SLOTS],
        "status": "confirmed-vtable",
        "source": "run-lane-probe contract-finance-transfer",
    }
]

CONFIRMED_VTABLE_MAP = {item["ownerType"]: item for item in CONFIRMED_VTABLES}

RIP_CANDIDATES = [
    {"displacement": "0x300ABF", "function": "0x3006D0"},
    {"displacement": "0x5741BC", "function": "0x574000"},
    {"displacement": "0xB04B90", "function": "0xB04930"},
    {"displacement": "0xB04E39", "function": "0xB04930"},
    {"displacement": "0xB1ADAC", "function": "0xB19E90"},
    {"displacement": "0xB4438A", "function": "0xB44280"},
    {"displacement": "0xB44679", "function": "0xB44280"},
    {"displacement": "0xB8A091", "function": "0xB89ED0"},
    {"displacement": "0xB8B913", "function": "0xB8AFA0"},
    {"displacement": "0xBA946D", "function": "0xBA7E10"},
    {"displacement": "0xBAC9F1", "function": "0xBAC8D0"},
    {"displacement": "0xBAEDCA", "function": "0xBADDE0"},
    {"displacement": "0xBC88C6", "function": "0xBC86C0"},
    {"displacement": "0xBD711D", "function": "0xBD6220"},
    {"displacement": "0xBE150C", "function": "0xBE1340"},
    {"displacement": "0x10C43AB", "function": "0x10C3910"},
    {"displacement": "0x10D88F7", "function": "0x10D8790"},
    {"displacement": "0x15499F0", "function": "0x1549840"},
    {"displacement": "0x157C58A", "function": "0x157C470"},
    {"displacement": "0x15CC9A2", "function": "0x15CC860"},
    {"displacement": "0x1886D15", "function": "0x1886B90"},
]

BUSINESS_OBJECTS = [
    {
        "id": "manager-employment-contract",
        "requestedType": "FULL_CONTRACT",
        "status": "confirmed-entry",
        "rtti": ".?AVFULL_CONTRACT@db@@",
        "vtableRva": "0x4B00AE8",
        "scope": "manager employment chain only",
        "semanticsKnown": False,
        "note": "Type and vtable are confirmed; no date, status, or money field is confirmed.",
    },
    {
        "id": "external-contract-variant",
        "requestedType": "EXTERN_FULL_CONTRACT",
        "status": "type-only",
        "rtti": ".?AVEXTERN_FULL_CONTRACT@db@@",
        "vtableRva": None,
        "semanticsKnown": False,
        "note": "Type RTTI is confirmed; no vtable, field layout, or relation evidence exists.",
    },
    {
        "id": "player-contract",
        "requestedType": "PLAYER_CONTRACT",
        "status": "no-match",
        "observedTypes": [item["rtti"] for item in CONFIRMED_TYPES],
        "proposedNarrowerNames": [item["rtti"] for item in CONFIRMED_TYPES],
        "semanticsKnown": False,
        "note": "No player-contract type appeared in the probe; player-contract coverage is unproven.",
    },
    {
        "id": "contract-dates",
        "requestedFields": ["start", "expiry"],
        "status": "no-match",
        "offsets": "unknown",
        "semanticsKnown": False,
        "note": "No date field or offset is established in checked-in source.",
    },
    {
        "id": "contract-wage",
        "requestedFields": ["wage", "salary", "currency", "period"],
        "status": "no-match",
        "offsets": "unknown",
        "semanticsKnown": False,
        "note": "No wage field, scale, currency, or pay period is established.",
    },
    {
        "id": "finance-budget",
        "requestedType": "FINANCE_OR_BUDGET",
        "status": "no-match",
        "observedTypes": [item["rtti"] for item in CONFIRMED_TYPES],
        "proposedNarrowerNames": [
            "CLUB",
            "FULL_CONTRACT",
            "EXTERN_FULL_CONTRACT",
        ],
        "semanticsKnown": False,
        "note": "Only a CLUB object and UID anchor are known; no finance object or amount field is confirmed.",
    },
    {
        "id": "transfer-negotiation",
        "requestedType": "TRANSFER_OR_NEGOTIATION",
        "status": "no-match",
        "observedTypes": [item["rtti"] for item in CONFIRMED_TYPES],
        "proposedNarrowerNames": [
            "FULL_CONTRACT",
            "EXTERN_FULL_CONTRACT",
        ],
        "semanticsKnown": False,
        "note": "No transfer, loan, offer, or negotiation type or field is confirmed.",
    },
]

STATIC_SEARCH_CANDIDATES = [
    "CONTRACT",
    "PLAYER_CONTRACT",
    "WAGE",
    "FINANCE",
    "BUDGET",
    "TRANSFER",
    "LOAN",
    "OFFER",
    "NEGOTIATION",
]

UNRESOLVED_OFFSETS = [
    "FULL_CONTRACT start date field",
    "FULL_CONTRACT expiry date field",
    "FULL_CONTRACT status or kind semantics",
    "FULL_CONTRACT wage raw value",
    "FULL_CONTRACT wage currency",
    "FULL_CONTRACT wage scale",
    "FULL_CONTRACT wage pay period",
    "EXTERN_FULL_CONTRACT vtable RVA",
    "EXTERN_FULL_CONTRACT field layout",
    "player-contract entry point",
    "finance object entry point",
    "finance amount fields",
    "transfer object entry point",
    "transfer party relations",
    "transfer stage or deadline fields",
]

MAX_INPUT_BYTES = 1024 * 1024


def manifest():
    return {
        "lane": LANE,
        "status": "static-probe-only",
        "binary": {
            "imageSha256": IMAGE_SHA256,
            "imageBase": IMAGE_BASE,
            "mode": MODE,
            "liveRecordsRead": 0,
            "outputTruncated": True,
        },
        "confirmedTypes": [dict(item) for item in CONFIRMED_TYPES],
        "confirmedVtables": [dict(item) for item in CONFIRMED_VTABLES],
        "ripCandidates": [dict(item) for item in RIP_CANDIDATES],
        "ripCandidateCount": len(RIP_CANDIDATES),
        "ripCandidateTarget": "0x4B00AE8",
        "businessObjects": [dict(item) for item in BUSINESS_OBJECTS],
        "staticSearchCandidates": list(STATIC_SEARCH_CANDIDATES),
        "offsets": {
            "status": "unknown",
            "confirmed": [],
            "unresolved": list(UNRESOLVED_OFFSETS),
            "values": {},
            "note": "No field offsets are confirmed by this probe; all remain unknown.",
        },
        "limits": {
            "maxInputBytes": MAX_INPUT_BYTES,
            "confirmedTypeCount": len(CONFIRMED_TYPES),
            "confirmedVtableCount": len(CONFIRMED_VTABLES),
        },
        "warnings": [
            "FULL_CONTRACT evidence covers manager employment only.",
            "No finance, transfer, date, or wage field is confirmed.",
            "EXTERN_FULL_CONTRACT has no vtable evidence in this probe.",
        ],
    }


def read_json(path):
    raw = path.read_bytes()
    if not (1 <= len(raw) <= MAX_INPUT_BYTES):
        raise ValueError("input size limit")
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("invalid JSON") from error
    if not isinstance(value, dict):
        raise ValueError("input must be an object")
    return value


def validate_manifest(data):
    errors = []
    warnings = []
    if not isinstance(data, dict):
        return {"valid": False, "errors": ["input must be an object"], "warnings": warnings}

    if "lane" in data and data["lane"] != LANE:
        errors.append(f"lane must be {LANE}")

    binary = data.get("binary", data)
    if isinstance(binary, dict):
        if "imageSha256" in binary and binary["imageSha256"] != IMAGE_SHA256:
            errors.append("imageSha256 does not match the pinned probe")
        if "imageBase" in binary and binary["imageBase"] not in (None, IMAGE_BASE):
            errors.append("imageBase does not match the pinned probe")
    elif isinstance(binary, str):
        if binary != IMAGE_SHA256:
            errors.append("image hash does not match the pinned probe")

    for item in data.get("confirmedTypes", []):
        if not isinstance(item, dict):
            errors.append("confirmed type entry must be an object")
            continue
        rtti = item.get("rtti")
        if rtti not in CONFIRMED_TYPE_MAP:
            errors.append(f"unconfirmed type: {rtti!r}")
            continue
        if "rttiRva" in item and item["rttiRva"] is not None:
            if item["rttiRva"] != CONFIRMED_TYPE_MAP[rtti]["rttiRva"]:
                errors.append(f"rttiRva mismatch for {rtti!r}")
        if "status" in item and item["status"] not in ("confirmed-type", "type-only"):
            warnings.append(f"unexpected type status: {item['status']!r}")

    for item in data.get("confirmedVtables", []):
        if not isinstance(item, dict):
            errors.append("confirmed vtable entry must be an object")
            continue
        owner = item.get("ownerType")
        match = CONFIRMED_VTABLE_MAP.get(owner)
        if match is None:
            errors.append(f"unconfirmed vtable owner: {owner!r}")
            continue
        if "rtti" in item and item["rtti"] != match["rtti"]:
            errors.append(f"rtti mismatch for vtable owner {owner!r}")
        if "vtableRva" in item and item["vtableRva"] is not None:
            if item["vtableRva"] != match["vtableRva"]:
                errors.append(f"vtableRva mismatch for {owner!r}")
        if "slotCount" in item and item["slotCount"] is not None:
            if item["slotCount"] != match["slotCount"]:
                errors.append(f"slotCount mismatch for {owner!r}")
        if "slots" in item and isinstance(item["slots"], list):
            if item["slots"] != match["slots"]:
                errors.append(f"slots mismatch for {owner!r}")

    offsets = data.get("offsets")
    if isinstance(offsets, dict):
        values = offsets.get("values")
        if values not in (None, {}):
            errors.append("offset values must remain empty or unknown")
        confirmed = offsets.get("confirmed")
        if isinstance(confirmed, list) and confirmed:
            errors.append("no field offset is confirmed by this probe")
        for key, value in offsets.items():
            if key in ("status", "confirmed", "unresolved", "values", "note"):
                continue
            if value not in (None, "unknown"):
                errors.append(f"unresolved offset field must not be populated: {key!r}")

    for item in data.get("businessObjects", []):
        if not isinstance(item, dict):
            errors.append("business object entry must be an object")
            continue
        status = item.get("status")
        if status not in ("confirmed-entry", "type-only", "no-match"):
            warnings.append(f"unexpected business object status: {status!r}")
        if "offsets" in item and item["offsets"] not in (None, "unknown"):
            errors.append(f"business object {item.get('id')!r} has an invented offset")
        if "vtableRva" in item and item["vtableRva"] is not None:
            if item["vtableRva"] not in {v["vtableRva"] for v in CONFIRMED_VTABLES}:
                errors.append(f"unconfirmed vtableRva in business object {item.get('id')!r}")

    if "ripCandidateTarget" in data and data["ripCandidateTarget"] != "0x4B00AE8":
        errors.append("ripCandidateTarget does not match the confirmed vtable")

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def self_test():
    result = manifest()
    assert len(result["confirmedTypes"]) == 2
    assert len(result["confirmedVtables"]) == 1
    assert result["confirmedVtables"][0]["slotCount"] == 12
    assert len(result["confirmedVtables"][0]["slots"]) == 12
    assert result["offsets"]["values"] == {}
    assert result["offsets"]["confirmed"] == []
    assert len(result["businessObjects"]) >= 6
    assert any(item["status"] == "no-match" for item in result["businessObjects"])
    assert result["ripCandidateCount"] == 21

    validation = validate_manifest(result)
    assert validation["valid"] is True, validation["errors"]

    bad_offset = json.loads(json.dumps(result))
    bad_offset["offsets"]["values"] = {"contractStart": 16}
    assert validate_manifest(bad_offset)["valid"] is False

    bad_type = json.loads(json.dumps(result))
    bad_type["confirmedTypes"].append({"rtti": ".?AVFAKE@db@@", "rttiRva": "0x1"})
    assert validate_manifest(bad_type)["valid"] is False

    bad_slot = json.loads(json.dumps(result))
    bad_slot["confirmedVtables"][0]["slots"][0] = "0x0"
    assert validate_manifest(bad_slot)["valid"] is False

    bad_vtable = json.loads(json.dumps(result))
    bad_vtable["businessObjects"][0]["vtableRva"] = "0x1234567"
    assert validate_manifest(bad_vtable)["valid"] is False

    assert validate_manifest({"lane": LANE})["valid"] is True
    print("PASS: confirmed type/vtable manifest, no-match records, empty offsets, validation guards")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.validate is not None:
        data = read_json(args.validate)
        print(json.dumps(validate_manifest(data), ensure_ascii=False, indent=2, sort_keys=True))
        return

    result = manifest()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is not None:
        output = args.output.resolve()
        repo = Path(__file__).resolve().parents[2]
        if output.is_relative_to(repo):
            raise ValueError("machine-readable output must remain outside repository")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
        print(f"Private manifest written: {output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
