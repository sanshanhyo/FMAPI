#!/usr/bin/env python3
"""Machine-readable manifest and validator for tactics native entries.

Offline static evidence only. This is not a live reader, SDK, adapter, or game
client. It records only RTTI type descriptors, vtables, and RIP-relative
references confirmed by the lane probe for the pinned game_plugin.dll profile.
No object field offsets are known; unresolved offsets are intentionally absent
and reported as unknown rather than invented.
"""
import argparse
import json
import sys
from pathlib import Path

PINNED_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = 0x180000000
MODULE = "game_plugin.dll"
LANE = "tactics"

CONFIRMED_TYPES = [
    {
        "rva": 0x567F2E0,
        "name": ".?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@",
        "module": MODULE,
        "kind": "rtti-type-descriptor",
    },
    {
        "rva": 0x568C850,
        "name": ".?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@",
        "module": MODULE,
        "kind": "rtti-type-descriptor",
    },
    {
        "rva": 0x56ED670,
        "name": ".?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@",
        "module": MODULE,
        "kind": "rtti-type-descriptor",
    },
]

CONFIRMED_VTABLES = [
    {
        "rva": 0x4B104C8,
        "rttiType": ".?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@",
        "rawSlotTokens": [
            "0x390B90", "0x6819C0", "0x6592D0", "0x7C7AB0", "0x7C7AC0",
            "0x65A700", "invalid", "invalid", "0x567F2DE80000000",
            "0x4B104FE84B10518", "invalid", "0x4B1052E80000004",
        ],
    },
    {
        "rva": 0x4B3D9E8,
        "rttiType": ".?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@",
        "rawSlotTokens": [
            "0x6818D0", "0x61DC80", "0x63C0F0", "0x6818C0", "0x78DAA0",
            "0x1EA320", "0x1EA330", "0x1EA340", "0x1EA350", "0x626610",
            "0x787D80", "0x61FBA0",
        ],
    },
    {
        "rva": 0x4B3DB98,
        "rttiType": ".?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@",
        "rawSlotTokens": [
            "0x681980", "0x61FA80", "invalid", "invalid", "0x568C84E80000000",
            "0x4B3DBAE84B3DBC8", "invalid", "0x4B3DBDE80000005", "invalid",
            "0x4AFE8AE84B3DC00", "0x4AE37FE84AE37C0", "invalid",
        ],
    },
    {
        "rva": 0x509E638,
        "rttiType": ".?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@",
        "rawSlotTokens": [
            "0x4AA7370", "0x4AA7290", "0x4AA72D0", "0x4AA71B0", "0x4AA7320",
            "invalid", "0x56ED66E80000000", "0x509E65E8509E678", "invalid",
            "0x509E68680000002", "0x4E52ACE8509E6A0", "invalid",
        ],
    },
]

RIP_CANDIDATES = [
    {
        "displacementRva": 0x388010,
        "functionRva": 0x387FC0,
        "targetVtableRva": 0x4B104C8,
        "rttiType": ".?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@",
    },
    {
        "displacementRva": 0x6816A0,
        "functionRva": 0x681690,
        "targetVtableRva": 0x4B3D9E8,
        "rttiType": ".?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@",
    },
    {
        "displacementRva": 0x6816AA,
        "functionRva": 0x681690,
        "targetVtableRva": 0x4B3DB98,
        "rttiType": ".?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@",
    },
    {
        "displacementRva": 0x29D7F9E,
        "functionRva": 0x29D7B10,
        "targetVtableRva": 0x509E638,
        "rttiType": ".?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@",
    },
    {
        "displacementRva": 0x4AA718C,
        "functionRva": 0x4AA7170,
        "targetVtableRva": 0x509E638,
        "rttiType": ".?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@",
    },
]

UNRESOLVED_SEMANTICS = [
    "active-tactic owner (team, manager, club, or separate tactic manager)",
    "whether a confirmed type is a controller/view or a business object",
    "active versus selected tactic slot",
    "tactic identity, scheme ordering, and formation representation",
    "starters, substitutes, unselected players, and player UID linkage",
    "role, duty, mentality, team, individual, and opposition instruction encodings",
    "set-piece routines, captain, and set-piece taker ordering",
    "tactical familiarity versus player positional familiarity",
    "object field offsets for every confirmed type",
    "vtable slot function semantics",
]

NEXT_BOUNDED_READ = {
    "static": {
        "inputs": "operator-provided pinned game_plugin.dll only",
        "functions": ["0x387FC0", "0x681690", "0x29D7B10", "0x4AA7170"],
        "actions": [
            "disassemble instruction boundaries",
            "trace referenced vtable use",
            "identify construction, return, storage, or dispatch patterns",
        ],
        "budget": "explicit functions only; no address-space scan; stop at 40 matches or 100 candidate types",
    },
    "live": {
        "status": "requires coordinator approval",
        "maxTotalBytes": 65536,
        "maxObjects": 32,
        "maxBytesPerRead": 8192,
        "maxPasses": 2,
        "maxPointerHops": 2,
        "requiredChecks": [
            "exact RTTI name",
            "exact vtable RVA",
            "pinned binary SHA256",
        ],
    },
}


def hx(value):
    return "0x%X" % value


def manifest():
    entries = [
        {
            "id": "tactics.ui-handler-server",
            "status": "confirmed-static-entry",
            "receiverType": ".?AVTEAM_TACTIC_UI_HANDLER_SERVER@game_plugin@@",
            "vtableRva": hx(0x4B104C8),
            "ripCandidate": {
                "functionRva": hx(0x387FC0),
                "displacementRva": hx(0x388010),
            },
            "businessObjectHypothesis": (
                "narrow: a tactic UI handler server is a confirmed native entry "
                "surface for tactic-related UI/controller code; it is not proven "
                "to be the business object that owns an active or selected tactic"
            ),
            "confirmedEvidence": [
                "RTTI type descriptor RVA 0x567F2E0",
                "validated vtable RVA 0x4B104C8",
                "RIP-relative reference at 0x388010 to function 0x387FC0",
            ],
            "objectFieldOffsets": {},
            "offsetStatus": "unknown",
            "unresolvedSemantics": UNRESOLVED_SEMANTICS,
        },
        {
            "id": "tactics.ui-handler",
            "status": "confirmed-static-entry",
            "receiverType": ".?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@",
            "vtableRva": hx(0x4B3D9E8),
            "ripCandidate": {
                "functionRva": hx(0x681690),
                "displacementRva": hx(0x6816A0),
            },
            "businessObjectHypothesis": (
                "narrow: a tactic UI handler is a confirmed native entry surface "
                "for tactic-related UI/controller code; it is not proven to be "
                "the business object that owns an active or selected tactic"
            ),
            "confirmedEvidence": [
                "RTTI type descriptor RVA 0x568C850",
                "validated vtable RVA 0x4B3D9E8",
                "RIP-relative reference at 0x6816A0 to function 0x681690",
            ],
            "objectFieldOffsets": {},
            "offsetStatus": "unknown",
            "unresolvedSemantics": UNRESOLVED_SEMANTICS,
        },
        {
            "id": "tactics.ui-handler-secondary-vtable",
            "status": "confirmed-static-entry",
            "receiverType": ".?AVTEAM_TACTIC_UI_HANDLER@game_plugin@@",
            "vtableRva": hx(0x4B3DB98),
            "ripCandidate": {
                "functionRva": hx(0x681690),
                "displacementRva": hx(0x6816AA),
            },
            "businessObjectHypothesis": (
                "narrow: a second vtable for the same tactic UI handler type is "
                "a confirmed native entry surface; its distinct construction or "
                "this-adjustment semantics are not yet known"
            ),
            "confirmedEvidence": [
                "RTTI type descriptor RVA 0x568C850",
                "validated vtable RVA 0x4B3DB98",
                "RIP-relative reference at 0x6816AA to function 0x681690",
            ],
            "objectFieldOffsets": {},
            "offsetStatus": "unknown",
            "unresolvedSemantics": UNRESOLVED_SEMANTICS,
        },
        {
            "id": "tactics.creator-change",
            "status": "confirmed-static-entry",
            "receiverType": ".?AVTEAM_TACTIC_CREATOR_CHANGE@simatch@@",
            "vtableRva": hx(0x509E638),
            "ripCandidate": {
                "functionRva": [hx(0x29D7B10), hx(0x4AA7170)],
                "displacementRva": [hx(0x29D7F9E), hx(0x4AA718C)],
            },
            "businessObjectHypothesis": (
                "narrow: a tactic creator-change object is a confirmed native "
                "type/vtable; whether it is a command, change record, or another "
                "tactic-related object is not established"
            ),
            "confirmedEvidence": [
                "RTTI type descriptor RVA 0x56ED670",
                "validated vtable RVA 0x509E638",
                "RIP-relative references at 0x29D7F9E and 0x4AA718C",
            ],
            "objectFieldOffsets": {},
            "offsetStatus": "unknown",
            "unresolvedSemantics": UNRESOLVED_SEMANTICS,
        },
    ]

    return {
        "schema": "fmapi.native-entry-tactics.v1",
        "lane": LANE,
        "status": "static-rtti-and-vtable-evidence-only",
        "binary": {
            "module": MODULE,
            "sha256": PINNED_SHA256,
            "imageBase": hx(IMAGE_BASE),
            "probeMode": "static-pinned-file",
            "liveRecordsRead": 0,
        },
        "counts": {
            "types": len(CONFIRMED_TYPES),
            "vtables": len(CONFIRMED_VTABLES),
            "ripCandidates": len(RIP_CANDIDATES),
            "liveRecordsRead": 0,
        },
        "confirmedTypes": [
            {
                "rva": hx(item["rva"]),
                "name": item["name"],
                "module": item["module"],
                "kind": item["kind"],
            }
            for item in CONFIRMED_TYPES
        ],
        "confirmedVtables": [
            {
                "rva": hx(item["rva"]),
                "rttiType": item["rttiType"],
                "rawSlotTokens": item["rawSlotTokens"],
                "slotTokenCount": len(item["rawSlotTokens"]),
            }
            for item in CONFIRMED_VTABLES
        ],
        "ripCandidates": [
            {
                "displacementRva": hx(item["displacementRva"]),
                "functionRva": hx(item["functionRva"]),
                "targetVtableRva": hx(item["targetVtableRva"]),
                "rttiType": item["rttiType"],
            }
            for item in RIP_CANDIDATES
        ],
        "entries": entries,
        "objectFieldOffsets": {},
        "offsetStatus": "unknown-for-all-confirmed-entries",
        "unresolvedOffsets": "absent-by-design",
        "unresolvedSemantics": UNRESOLVED_SEMANTICS,
        "nextBoundedReadRequest": NEXT_BOUNDED_READ,
    }


def validate_manifest(data):
    if not isinstance(data, dict):
        raise ValueError("manifest must be an object")
    required = {
        "schema", "lane", "status", "binary", "counts", "confirmedTypes",
        "confirmedVtables", "ripCandidates", "entries", "objectFieldOffsets",
        "offsetStatus", "unresolvedOffsets", "unresolvedSemantics",
        "nextBoundedReadRequest",
    }
    missing = required - set(data)
    if missing:
        raise ValueError("missing manifest keys: %s" % ", ".join(sorted(missing)))
    if data["schema"] != "fmapi.native-entry-tactics.v1":
        raise ValueError("unexpected schema")
    if data["lane"] != LANE:
        raise ValueError("unexpected lane")
    if data["binary"].get("sha256") != PINNED_SHA256:
        raise ValueError("unsupported binary fingerprint")
    if data["binary"].get("liveRecordsRead") != 0:
        raise ValueError("manifest must not claim live records")
    if data["counts"].get("liveRecordsRead") != 0:
        raise ValueError("manifest must not claim live records")
    if data["counts"].get("types") != len(CONFIRMED_TYPES):
        raise ValueError("type count mismatch")
    if data["counts"].get("vtables") != len(CONFIRMED_VTABLES):
        raise ValueError("vtable count mismatch")
    if data["counts"].get("ripCandidates") != len(RIP_CANDIDATES):
        raise ValueError("RIP candidate count mismatch")

    actual_types = [
        (item.get("rva"), item.get("name"))
        for item in data["confirmedTypes"]
    ]
    expected_types = [(hx(item["rva"]), item["name"]) for item in CONFIRMED_TYPES]
    if sorted(actual_types) != sorted(expected_types):
        raise ValueError("confirmed types do not match probe evidence")

    actual_vtables = [
        (item.get("rva"), item.get("rttiType")) for item in data["confirmedVtables"]
    ]
    expected_vtables = [(hx(item["rva"]), item["rttiType"]) for item in CONFIRMED_VTABLES]
    if sorted(actual_vtables) != sorted(expected_vtables):
        raise ValueError("confirmed vtables do not match probe evidence")

    actual_rips = [
        (item.get("displacementRva"), item.get("functionRva"), item.get("targetVtableRva"))
        for item in data["ripCandidates"]
    ]
    expected_rips = [
        (hx(item["displacementRva"]), hx(item["functionRva"]), hx(item["targetVtableRva"]))
        for item in RIP_CANDIDATES
    ]
    if sorted(actual_rips) != sorted(expected_rips):
        raise ValueError("RIP candidates do not match probe evidence")

    if data["objectFieldOffsets"] != {}:
        raise ValueError("top-level object field offsets must be empty")
    if data["unresolvedOffsets"] != "absent-by-design":
        raise ValueError("unresolvedOffsets must state absent-by-design")

    for entry in data["entries"]:
        if not isinstance(entry, dict):
            raise ValueError("entry must be an object")
        if entry.get("objectFieldOffsets") != {}:
            raise ValueError("entry objectFieldOffsets must be empty")
        if entry.get("offsetStatus") != "unknown":
            raise ValueError("entry offsetStatus must be unknown")
        if not isinstance(entry.get("unresolvedSemantics"), list) or not entry["unresolvedSemantics"]:
            raise ValueError("entry must list unresolved semantics")
    if not isinstance(data["unresolvedSemantics"], list) or not data["unresolvedSemantics"]:
        raise ValueError("manifest must list unresolved semantics")
    return True


def self_test():
    data = manifest()
    validate_manifest(data)
    assert data["counts"]["types"] == 3
    assert data["counts"]["vtables"] == 4
    assert data["counts"]["ripCandidates"] == 5
    assert len(data["entries"]) == 4
    assert all(entry["objectFieldOffsets"] == {} for entry in data["entries"])

    # Invented offsets must be rejected.
    invented = json.loads(json.dumps(data))
    invented["entries"][0]["objectFieldOffsets"] = {"activeTactic": 0x10}
    try:
        validate_manifest(invented)
    except ValueError:
        pass
    else:
        raise AssertionError("invented offset was accepted")

    # Missing confirmed evidence must be rejected.
    missing_type = json.loads(json.dumps(data))
    missing_type["confirmedTypes"].pop()
    missing_type["counts"]["types"] = len(missing_type["confirmedTypes"])
    try:
        validate_manifest(missing_type)
    except ValueError:
        pass
    else:
        raise AssertionError("missing confirmed type was accepted")

    print("PASS: tactics native-entry manifest, counts, no invented offsets, and evidence validation")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None, help="Write manifest JSON to this path")
    parser.add_argument("--validate", type=Path, default=None, help="Validate a manifest JSON file")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic checks")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if args.validate is not None:
        data = json.loads(args.validate.read_text(encoding="utf-8"))
        validate_manifest(data)
        print(json.dumps({"status": "valid", "schema": data.get("schema"), "lane": data.get("lane")}, indent=2))
        return 0

    data = manifest()
    validate_manifest(data)
    text = json.dumps(data, indent=2)
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
        print("Wrote tactics native-entry manifest")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"status": "unavailable", "reason": str(exc)}))
        sys.exit(3)
