#!/usr/bin/env python3
"""Machine-readable bounded property-to-entry manifest for tactics property candidates.

Offline static evidence only. The only property candidate is the single result returned
by the reviewed fixed-file static property probe for lane "tactics". Property names are
not assumed to be business fields, and no native key, offset, function RVA, context
resolution, or field layout is invented. Unproven values are null or explicitly unknown.
"""
import argparse
import json
import sys
from pathlib import Path

SCHEMA = "fmapi.property-entry-tactics.v1"
LANE = "tactics"
STATUS = "static-property-candidate-evidence-only"

GAME_PLUGIN_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
GAME_ASSEMBLY_SHA256 = "820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A"
METADATA_SIGNATURE = "0xFAB11BAF"
METADATA_VERSION = 39
IMAGE_BASE = 0x180000000

PROBE_RESULT = {
    "lane": LANE,
    "mode": "static-property-candidates",
    "matches": 1,
    "truncated": False,
    "liveRecordsRead": 0,
    "entries": [
        {
            "name": "TacticRoleMenuModuleBindings",
            "literalIndex": 18799,
            "slotRvas": ["0x32f7040"],
            "semantics": "unverified-property-name",
        }
    ],
}

COORDINATOR_EVIDENCE = {
    "clubTeamBaseLow23BitMatch": {
        "status": "provided",
        "clubCount": 2,
        "matchedEntries": 2,
        "interpretation": (
            "Current club2 TEAM pointers match their TEAM_BASE low23-bit index entries. "
            "This is dependency evidence only; it does not establish a tactics property target."
        ),
    },
    "nextFixtureProperty": {
        "propertyName": "NextFixture",
        "literalIndex": 13696,
        "slotRva": "0x330B698",
        "nativeKey": "0x6E654669",
        "firstResolution": "TEAM_BASE context via global 0x5703768",
        "notResolution": "fixtures",
        "interpretation": (
            "A property name is not proof of its business target: NextFixture first resolves "
            "TEAM_BASE context, not fixtures. Use this as a comparator only."
        ),
    },
}

RANKED_REGISTRATIONS = [
    {
        "rank": 1,
        "id": "tactics.property.tactic-role-menu-module-bindings.registration",
        "source": "reviewed fixed-file static property probe",
        "propertyName": "TacticRoleMenuModuleBindings",
        "literalIndex": 18799,
        "slotRva": "0x32f7040",
        "classification": "candidate-property-name-only",
        "uiNewsOperationsAssessment": (
            "The name suggests a tactic role menu module binding. It is treated as a "
            "UI/module/operations candidate until registration disassembly proves a "
            "business tactic field or owner."
        ),
        "nativeKey": None,
        "nativeOffset": None,
        "nativeFunctionRva": None,
        "contextResolution": None,
        "status": "inspect-next",
        "nextInspection": [
            "disassemble the exact GameAssembly registration block at slot RVA 0x32f7040",
            "determine whether a native property key is constructed and how it is paired with literal index 18799",
            "compare the registration shape with the NextFixture comparator at slot RVA 0x330B698",
            "do not call game functions, read UI, or follow unvalidated pointers",
        ],
    },
    {
        "rank": 2,
        "id": "tactics.property.next-fixture.registration.comparator",
        "source": "coordinator evidence",
        "propertyName": "NextFixture",
        "literalIndex": 13696,
        "slotRva": "0x330B698",
        "classification": "proven-comparator-registration",
        "uiNewsOperationsAssessment": (
            "Comparator only. Its name is misleading with respect to fixtures; the proven "
            "first resolution is TEAM_BASE context."
        ),
        "nativeKey": "0x6E654669",
        "nativeOffset": None,
        "nativeFunctionRva": None,
        "contextResolution": "TEAM_BASE context via global 0x5703768, not fixtures",
        "status": "proven-comparator",
        "nextInspection": [
            "use only as a shape comparator for property registration blocks",
            "do not treat NextFixture as a tactics field or fixture reader",
        ],
    },
]

NEXT_BOUNDED_LIVE_REQUEST = {
    "status": "not-genuinely-supported",
    "reason": (
        "TacticRoleMenuModuleBindings has no proven native key, context resolution, owner, "
        "or pointer source. A live read cannot yet be bounded to a known object and would "
        "require executing or assuming an unverified property registration."
    ),
    "staticPrerequisite": (
        "Static disassembly of GameAssembly slot RVA 0x32f7040 must first establish a "
        "native key and its dispatch/context shape. Only then may a one-object, two-hop "
        "live read be proposed."
    ),
    "budgetIfLaterSupported": {
        "maxTotalBytes": 65536,
        "maxObjects": 32,
        "maxBytesPerRead": 8192,
        "maxPasses": 2,
        "maxPointerHops": 2,
    },
}


def hx(value):
    return "0x%X" % value


def manifest():
    entries = []
    for item in PROBE_RESULT["entries"]:
        for slot in item["slotRvas"]:
            entries.append(
                {
                    "id": "tactics.property.%s" % item["name"].lower().replace(" ", "-"),
                    "status": "returned-property-candidate",
                    "propertyName": item["name"],
                    "literalIndex": item["literalIndex"],
                    "slotRva": slot,
                    "semantics": item["semantics"],
                    "source": "reviewed fixed-file static property probe",
                    "uiNewsOperationsAssessment": (
                        "Returned property name only. It is not classified as a business "
                        "tactic field; it may name a UI, news, or operations surface."
                    ),
                    "businessFieldStatus": "not-established",
                    "nativeKey": None,
                    "nativeOffset": None,
                    "nativeFunctionRva": None,
                    "contextResolution": None,
                    "objectFieldOffsets": {},
                    "offsetStatus": "unknown",
                }
            )

    return {
        "schema": SCHEMA,
        "lane": LANE,
        "status": STATUS,
        "binary": {
            "gamePluginModule": "game_plugin.dll",
            "gamePluginSha256": GAME_PLUGIN_SHA256,
            "gameAssemblyModule": "GameAssembly.dll",
            "gameAssemblySha256": GAME_ASSEMBLY_SHA256,
            "metadataSignature": METADATA_SIGNATURE,
            "metadataVersion": METADATA_VERSION,
            "imageBase": hx(IMAGE_BASE),
            "probeMode": PROBE_RESULT["mode"],
            "liveRecordsRead": PROBE_RESULT["liveRecordsRead"],
        },
        "counts": {
            "propertyCandidates": len(PROBE_RESULT["entries"]),
            "encodedSlots": sum(len(item["slotRvas"]) for item in PROBE_RESULT["entries"]),
            "rankedRegistrations": len(RANKED_REGISTRATIONS),
            "liveRecordsRead": PROBE_RESULT["liveRecordsRead"],
        },
        "probeResult": PROBE_RESULT,
        "coordinatorEvidence": COORDINATOR_EVIDENCE,
        "propertyCandidates": [
            {
                "name": item["name"],
                "literalIndex": item["literalIndex"],
                "slotRvas": item["slotRvas"],
                "semantics": item["semantics"],
                "nativeKey": None,
                "nativeOffset": None,
                "contextResolution": None,
            }
            for item in PROBE_RESULT["entries"]
        ],
        "entries": entries,
        "rankedRegistrationsToInspect": RANKED_REGISTRATIONS,
        "objectFieldOffsets": {},
        "offsetStatus": "unknown-for-all-property-candidates",
        "nativeKeys": {},
        "nativeOffsets": {},
        "unresolvedSemantics": [
            "whether TacticRoleMenuModuleBindings names a business tactic field or only a UI/module/operations surface",
            "native property key for the tactics candidate",
            "registration block and dispatch shape at slot RVA 0x32f7040",
            "context resolution for the tactics candidate",
            "active versus selected tactic slot",
            "tactic identity, formation, lineup, roles, duties, instructions, set pieces, and familiarity",
            "object field offsets for any tactic property target",
        ],
        "nextBoundedLiveRequest": NEXT_BOUNDED_LIVE_REQUEST,
    }


def validate_manifest(data):
    if not isinstance(data, dict):
        raise ValueError("manifest must be an object")
    required = {
        "schema", "lane", "status", "binary", "counts", "probeResult",
        "coordinatorEvidence", "propertyCandidates", "entries",
        "rankedRegistrationsToInspect", "objectFieldOffsets", "offsetStatus",
        "nativeKeys", "nativeOffsets", "unresolvedSemantics", "nextBoundedLiveRequest",
    }
    missing = required - set(data)
    if missing:
        raise ValueError("missing manifest keys: %s" % ", ".join(sorted(missing)))
    if data["schema"] != SCHEMA:
        raise ValueError("unexpected schema")
    if data["lane"] != LANE:
        raise ValueError("unexpected lane")
    if data["binary"].get("gamePluginSha256") != GAME_PLUGIN_SHA256:
        raise ValueError("unsupported game_plugin fingerprint")
    if data["binary"].get("gameAssemblySha256") != GAME_ASSEMBLY_SHA256:
        raise ValueError("unsupported GameAssembly fingerprint")
    if data["binary"].get("liveRecordsRead") != 0:
        raise ValueError("manifest must not claim live records")
    if data["counts"].get("liveRecordsRead") != 0:
        raise ValueError("manifest must not claim live records")
    if data["counts"].get("propertyCandidates") != len(PROBE_RESULT["entries"]):
        raise ValueError("property candidate count mismatch")
    if data["counts"].get("encodedSlots") != sum(len(x["slotRvas"]) for x in PROBE_RESULT["entries"]):
        raise ValueError("encoded slot count mismatch")
    if data["counts"].get("rankedRegistrations") != len(RANKED_REGISTRATIONS):
        raise ValueError("ranked registration count mismatch")

    if data["probeResult"] != PROBE_RESULT:
        raise ValueError("probe result does not match actual executed evidence")
    if data["propertyCandidates"] != [
        {
            "name": item["name"],
            "literalIndex": item["literalIndex"],
            "slotRvas": item["slotRvas"],
            "semantics": item["semantics"],
            "nativeKey": None,
            "nativeOffset": None,
            "contextResolution": None,
        }
        for item in PROBE_RESULT["entries"]
    ]:
        raise ValueError("property candidates do not match probe evidence")

    expected_entries = [
        {
            "id": "tactics.property.%s" % item["name"].lower().replace(" ", "-"),
            "status": "returned-property-candidate",
            "propertyName": item["name"],
            "literalIndex": item["literalIndex"],
            "slotRva": slot,
            "semantics": item["semantics"],
            "source": "reviewed fixed-file static property probe",
            "uiNewsOperationsAssessment": (
                "Returned property name only. It is not classified as a business "
                "tactic field; it may name a UI, news, or operations surface."
            ),
            "businessFieldStatus": "not-established",
            "nativeKey": None,
            "nativeOffset": None,
            "nativeFunctionRva": None,
            "contextResolution": None,
            "objectFieldOffsets": {},
            "offsetStatus": "unknown",
        }
        for item in PROBE_RESULT["entries"]
        for slot in item["slotRvas"]
    ]
    if data["entries"] != expected_entries:
        raise ValueError("property entries do not match probe evidence")

    for entry in data["entries"]:
        if not isinstance(entry, dict):
            raise ValueError("entry must be an object")
        if entry.get("nativeKey") is not None:
            raise ValueError("unproven native key must be null")
        if entry.get("nativeOffset") is not None:
            raise ValueError("unproven native offset must be null")
        if entry.get("nativeFunctionRva") is not None:
            raise ValueError("unproven native function RVA must be null")
        if entry.get("contextResolution") is not None:
            raise ValueError("unproven context resolution must be null")
        if entry.get("objectFieldOffsets") != {}:
            raise ValueError("entry objectFieldOffsets must be empty")
        if entry.get("offsetStatus") != "unknown":
            raise ValueError("entry offsetStatus must be unknown")

    for candidate in data["propertyCandidates"]:
        if candidate.get("nativeKey") is not None or candidate.get("nativeOffset") is not None:
            raise ValueError("property candidate native values must be null")
        if candidate.get("contextResolution") is not None:
            raise ValueError("property candidate context resolution must be null")

    if data["objectFieldOffsets"] != {}:
        raise ValueError("top-level object field offsets must be empty")
    if data["nativeKeys"] != {}:
        raise ValueError("top-level nativeKeys must be empty until proven")
    if data["nativeOffsets"] != {}:
        raise ValueError("top-level nativeOffsets must be empty until proven")
    if not isinstance(data["unresolvedSemantics"], list) or not data["unresolvedSemantics"]:
        raise ValueError("manifest must list unresolved semantics")

    ranked = data["rankedRegistrationsToInspect"]
    if not isinstance(ranked, list) or not ranked:
        raise ValueError("ranked registrations must be a nonempty list")
    ranks = [item.get("rank") for item in ranked]
    if sorted(ranks) != list(range(1, len(ranked) + 1)):
        raise ValueError("ranked registrations must be contiguous from 1")
    if len(set(ranks)) != len(ranks):
        raise ValueError("ranked registration ranks must be unique")
    for item in ranked:
        if not isinstance(item, dict):
            raise ValueError("ranked registration must be an object")
        if item.get("nativeOffset") is not None:
            raise ValueError("ranked registration native offset must be null")
        if item.get("nativeFunctionRva") is not None:
            raise ValueError("ranked registration native function RVA must be null")
    candidate_ranked = ranked[0]
    if candidate_ranked.get("nativeKey") is not None:
        raise ValueError("rank 1 tactics candidate native key must be null")
    if candidate_ranked.get("contextResolution") is not None:
        raise ValueError("rank 1 tactics candidate context resolution must be null")
    return True


def self_test():
    data = manifest()
    validate_manifest(data)
    assert data["counts"]["propertyCandidates"] == 1
    assert data["counts"]["encodedSlots"] == 1
    assert data["counts"]["rankedRegistrations"] == 2
    assert len(data["entries"]) == 1
    assert data["entries"][0]["nativeKey"] is None
    assert data["entries"][0]["nativeOffset"] is None
    assert data["entries"][0]["nativeFunctionRva"] is None
    assert data["entries"][0]["contextResolution"] is None
    assert data["propertyCandidates"][0]["literalIndex"] == 18799
    assert data["propertyCandidates"][0]["slotRvas"] == ["0x32f7040"]
    assert data["rankedRegistrationsToInspect"][0]["slotRva"] == "0x32f7040"

    invented_key = json.loads(json.dumps(data))
    invented_key["entries"][0]["nativeKey"] = "0x1234"
    try:
        validate_manifest(invented_key)
    except ValueError:
        pass
    else:
        raise AssertionError("invented native key was accepted")

    invented_offset = json.loads(json.dumps(data))
    invented_offset["entries"][0]["objectFieldOffsets"] = {"tactic": 0x10}
    try:
        validate_manifest(invented_offset)
    except ValueError:
        pass
    else:
        raise AssertionError("invented offset was accepted")

    invented_function = json.loads(json.dumps(data))
    invented_function["entries"][0]["nativeFunctionRva"] = "0x4000"
    try:
        validate_manifest(invented_function)
    except ValueError:
        pass
    else:
        raise AssertionError("invented function RVA was accepted")

    missing_candidate = json.loads(json.dumps(data))
    missing_candidate["probeResult"]["entries"].pop()
    missing_candidate["counts"]["propertyCandidates"] = 0
    missing_candidate["counts"]["encodedSlots"] = 0
    missing_candidate["propertyCandidates"] = []
    missing_candidate["entries"] = []
    try:
        validate_manifest(missing_candidate)
    except ValueError:
        pass
    else:
        raise AssertionError("missing property candidate was accepted")

    print("PASS: tactics property-entry manifest, one actual candidate, null unproven keys/offsets, and evidence validation")
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
        print("Wrote tactics property-entry manifest")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"status": "unavailable", "reason": str(exc)}))
        sys.exit(3)
