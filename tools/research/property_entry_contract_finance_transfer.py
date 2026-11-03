#!/usr/bin/env python3
"""Machine-readable property-to-entry manifest and validator for contract-finance-transfer.

This is an offline scaffold only. It records the actual candidates returned by the
authorized static property probe. It does not open a process, read memory, claim a
native key, or invent a function or field offset.
"""
import argparse
import json
from pathlib import Path

LANE = "contract-finance-transfer"
IMAGE_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
GAME_ASSEMBLY_SHA256 = "820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A"
METADATA_SIGNATURE = "0xFAB11BAF"
METADATA_VERSION = 39
IMAGE_BASE = "0x180000000"
MODE = "static-property-candidates"
SOURCE_PROBE = "run-lane-property-probe.ps1 -Lane contract-finance-transfer"

PROPERTY_CANDIDATES = [
    {
        "name": "DebugContractExpiryAnalysis",
        "literalIndex": 6679,
        "slotRvas": ["0x32b2b68"],
        "semantics": "unverified-property-name",
        "surfaceClassification": "debug-contract-expiry-analysis view (UI/operations/debug; unverified)",
        "uiOrOperations": True,
        "businessFieldCandidate": False,
        "nativeKey": None,
        "entryRva": None,
        "resolvedContext": None,
        "function": None,
        "offsets": "unknown",
        "status": "candidate",
    },
    {
        "name": "DebugContractExpiryAnalysisAverage",
        "literalIndex": 6680,
        "slotRvas": ["0x32b2c68"],
        "semantics": "unverified-property-name",
        "surfaceClassification": "debug-contract-expiry-analysis view (UI/operations/debug; unverified)",
        "uiOrOperations": True,
        "businessFieldCandidate": False,
        "nativeKey": None,
        "entryRva": None,
        "resolvedContext": None,
        "function": None,
        "offsets": "unknown",
        "status": "candidate",
    },
    {
        "name": "DebugContractExpiryAnalysisItem",
        "literalIndex": 6681,
        "slotRvas": ["0x32b2d58"],
        "semantics": "unverified-property-name",
        "surfaceClassification": "debug-contract-expiry-analysis view (UI/operations/debug; unverified)",
        "uiOrOperations": True,
        "businessFieldCandidate": False,
        "nativeKey": None,
        "entryRva": None,
        "resolvedContext": None,
        "function": None,
        "offsets": "unknown",
        "status": "candidate",
    },
    {
        "name": "DebugContractExpiryAnalysisOverviewReference",
        "literalIndex": 6682,
        "slotRvas": ["0x32b2e58"],
        "semantics": "unverified-property-name",
        "surfaceClassification": "debug-contract-expiry-analysis view (UI/operations/debug; unverified)",
        "uiOrOperations": True,
        "businessFieldCandidate": False,
        "nativeKey": None,
        "entryRva": None,
        "resolvedContext": None,
        "function": None,
        "offsets": "unknown",
        "status": "candidate",
    },
    {
        "name": "DebugContractExpiryAnalysisTableList",
        "literalIndex": 6683,
        "slotRvas": ["0x32b2f68"],
        "semantics": "unverified-property-name",
        "surfaceClassification": "debug-contract-expiry-analysis view (UI/operations/debug; unverified)",
        "uiOrOperations": True,
        "businessFieldCandidate": False,
        "nativeKey": None,
        "entryRva": None,
        "resolvedContext": None,
        "function": None,
        "offsets": "unknown",
        "status": "candidate",
    },
    {
        "name": "LastContractWage",
        "literalIndex": 11871,
        "slotRvas": ["0x32a3708"],
        "semantics": "unverified-property-name",
        "surfaceClassification": "possible wage display or business field (unverified)",
        "uiOrOperations": None,
        "businessFieldCandidate": True,
        "nativeKey": None,
        "entryRva": None,
        "resolvedContext": None,
        "function": None,
        "offsets": "unknown",
        "status": "candidate",
    },
]

KNOWN_CANDIDATES = {item["name"]: item for item in PROPERTY_CANDIDATES}

RANKED_REGISTRATIONS = [
    {
        "rank": 1,
        "name": "LastContractWage",
        "literalIndex": 11871,
        "slotRvas": ["0x32a3708"],
        "priority": "high",
        "reason": "Only candidate whose name suggests a wage value rather than a debug view.",
    },
    {
        "rank": 2,
        "name": "DebugContractExpiryAnalysisOverviewReference",
        "literalIndex": 6682,
        "slotRvas": ["0x32b2e58"],
        "priority": "medium",
        "reason": "Overview reference is the most likely aggregate contract-expiry analysis registration.",
    },
    {
        "rank": 3,
        "name": "DebugContractExpiryAnalysisTableList",
        "literalIndex": 6683,
        "slotRvas": ["0x32b2f68"],
        "priority": "medium",
        "reason": "Table list registration may expose collection shape, but likely view-level data.",
    },
    {
        "rank": 4,
        "name": "DebugContractExpiryAnalysisItem",
        "literalIndex": 6681,
        "slotRvas": ["0x32b2d58"],
        "priority": "low",
        "reason": "Item-level registration depends on an already proven collection entry.",
    },
    {
        "rank": 5,
        "name": "DebugContractExpiryAnalysisAverage",
        "literalIndex": 6680,
        "slotRvas": ["0x32b2c68"],
        "priority": "low",
        "reason": "Average is likely a derived display value, not a business field.",
    },
    {
        "rank": 6,
        "name": "DebugContractExpiryAnalysis",
        "literalIndex": 6679,
        "slotRvas": ["0x32b2b68"],
        "priority": "low",
        "reason": "Base registration is likely a container or view root.",
    },
]

DEPENDENCY_EVIDENCE = [
    {
        "id": "club2-team-pointers",
        "statement": "Current club2 TEAM pointers match their TEAM_BASE low23-bit index entries 2/2.",
        "impact": "A property registration can resolve to a TEAM_BASE context even when its name suggests another domain.",
    },
    {
        "id": "nextfixture-property-resolution",
        "statement": "NextFixture literal 13696 slot 0x330B698 native key 0x6E654669 first resolves TEAM_BASE context via global 0x5703768, not fixtures.",
        "impact": "Property names and literal slots are not proof of business-object identity; context resolution must be proven before any entry or field claim.",
    },
]

UNRESOLVED_NATIVE_KEYS = [
    "DebugContractExpiryAnalysis native property key",
    "DebugContractExpiryAnalysisAverage native property key",
    "DebugContractExpiryAnalysisItem native property key",
    "DebugContractExpiryAnalysisOverviewReference native property key",
    "DebugContractExpiryAnalysisTableList native property key",
    "LastContractWage native property key",
    "resolved context/global for each registration",
    "entry RVA for each registration",
]

UNRESOLVED_OFFSETS = [
    "all property-to-entry offsets",
    "all field offsets for returned candidates",
]

MAX_INPUT_BYTES = 1024 * 1024

CANDIDATE_KEYS = [
    "propertyCandidates",
    "properties",
    "candidates",
    "returnedCandidates",
    "entries",
]

RANKED_KEYS = [
    "rankedRegistrations",
    "nextRegistrations",
    "registrations",
]

HASH_FIELDS = ("imageSha256", "imageHash", "gamePluginSha256", "gamePluginHash")
GA_HASH_FIELDS = ("gameAssemblySha256", "gameAssemblyHash")


def _copy_candidates():
    return [dict(item) for item in PROPERTY_CANDIDATES]


def _copy_ranked():
    return [dict(item) for item in RANKED_REGISTRATIONS]


def manifest():
    candidates = _copy_candidates()
    ranked = _copy_ranked()
    return {
        "lane": LANE,
        "status": "static-property-candidates",
        "binary": {
            "imageSha256": IMAGE_SHA256,
            "gameAssemblySha256": GAME_ASSEMBLY_SHA256,
            "metadataSignature": METADATA_SIGNATURE,
            "metadataVersion": METADATA_VERSION,
            "imageBase": IMAGE_BASE,
            "mode": MODE,
            "liveRecordsRead": 0,
            "outputTruncated": False,
        },
        "sourceProbe": {
            "command": SOURCE_PROBE,
            "lane": LANE,
            "mode": MODE,
            "matches": len(PROPERTY_CANDIDATES),
            "truncated": False,
        },
        "propertyCandidates": candidates,
        "properties": [dict(item) for item in candidates],
        "candidates": [dict(item) for item in candidates],
        "returnedCandidates": [dict(item) for item in candidates],
        "entries": [dict(item) for item in candidates],
        "rankedRegistrations": ranked,
        "nextRegistrations": [dict(item) for item in ranked],
        "registrations": [dict(item) for item in ranked],
        "nativeKeys": {
            "status": "unknown",
            "values": {},
            "confirmed": [],
            "unresolved": list(UNRESOLVED_NATIVE_KEYS),
            "note": "No native key or entry RVA is proven for any returned candidate.",
        },
        "offsets": {
            "status": "unknown",
            "confirmed": [],
            "unresolved": list(UNRESOLVED_OFFSETS),
            "values": {},
            "note": "No property or field offset is confirmed by this probe.",
        },
        "dependencyEvidence": [dict(item) for item in DEPENDENCY_EVIDENCE],
        "limits": {
            "maxInputBytes": MAX_INPUT_BYTES,
            "propertyCandidateCount": len(PROPERTY_CANDIDATES),
            "rankedRegistrationCount": len(RANKED_REGISTRATIONS),
        },
        "warnings": [
            "Returned names are unverified property names only.",
            "Debug* names likely refer to UI, news, operations, or debug views, not business fields.",
            "LastContractWage is only a business-field candidate, not a proven wage field.",
            "Native keys, entry RVAs, functions, and offsets remain null or unknown.",
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


def _is_empty_values(value):
    return value in (None, {}, [], "unknown")


def _candidate_ok(item, errors):
    if not isinstance(item, dict):
        errors.append("property candidate entry must be an object")
        return
    name = item.get("name")
    if name not in KNOWN_CANDIDATES:
        errors.append(f"unconfirmed property candidate: {name!r}")
        return
    expected = KNOWN_CANDIDATES[name]
    if "literalIndex" in item and item["literalIndex"] is not None:
        if item["literalIndex"] != expected["literalIndex"]:
            errors.append(f"literalIndex mismatch for {name!r}")
    if "slotRvas" in item and isinstance(item["slotRvas"], list):
        if item["slotRvas"] != expected["slotRvas"]:
            errors.append(f"slotRvas mismatch for {name!r}")
    if "semantics" in item and item["semantics"] is not None:
        if item["semantics"] != expected["semantics"]:
            errors.append(f"semantics mismatch for {name!r}")
    for field in ("nativeKey", "entryRva", "resolvedContext", "function"):
        if field in item and item[field] not in (None, "unknown"):
            errors.append(f"unproven {field} for property candidate {name!r}")
    offsets = item.get("offsets")
    if isinstance(offsets, dict):
        if offsets.get("values") not in (None, {}):
            errors.append(f"offset values must remain empty for {name!r}")
        if offsets.get("confirmed") not in (None, []):
            errors.append(f"confirmed offsets must remain empty for {name!r}")
        for key, value in offsets.items():
            if key in ("status", "confirmed", "unresolved", "values", "note"):
                continue
            if value not in (None, "unknown", [], {}):
                errors.append(f"unresolved offset field must not be populated: {key!r}")
    elif offsets not in (None, "unknown", {}):
        errors.append(f"property candidate {name!r} has an invented offset")
    if "functions" in item and not _is_empty_values(item.get("functions")):
        errors.append(f"fabricated function list in property candidate {name!r}")


def validate_manifest(data):
    errors = []
    warnings = []
    if not isinstance(data, dict):
        return {"valid": False, "errors": ["input must be an object"], "warnings": warnings}

    if "lane" in data and data["lane"] != LANE:
        errors.append(f"lane must be {LANE}")

    binary = data.get("binary", data)
    if isinstance(binary, dict):
        for field in HASH_FIELDS:
            if field in binary and binary[field] is not None and binary[field] != IMAGE_SHA256:
                errors.append("game_plugin image hash does not match the pinned probe")
        for field in GA_HASH_FIELDS:
            if field in binary and binary[field] is not None and binary[field] != GAME_ASSEMBLY_SHA256:
                errors.append("GameAssembly image hash does not match the pinned probe")
        if "metadataSignature" in binary and binary["metadataSignature"] is not None:
            if binary["metadataSignature"] != METADATA_SIGNATURE:
                errors.append("metadata signature does not match the pinned probe")
        if "metadataVersion" in binary and binary["metadataVersion"] is not None:
            if binary["metadataVersion"] != METADATA_VERSION:
                errors.append("metadata version does not match the pinned probe")
    elif isinstance(binary, str):
        if binary != IMAGE_SHA256:
            errors.append("image hash does not match the pinned probe")

    for field in HASH_FIELDS:
        if field in data and data[field] is not None and data[field] != IMAGE_SHA256:
            errors.append("game_plugin image hash does not match the pinned probe")

    for key in CANDIDATE_KEYS:
        value = data.get(key)
        if isinstance(value, list):
            for item in value:
                _candidate_ok(item, errors)

    for key in RANKED_KEYS:
        value = data.get(key)
        if not isinstance(value, list):
            continue
        ranks = []
        for item in value:
            if not isinstance(item, dict):
                errors.append("ranked registration entry must be an object")
                continue
            name = item.get("name")
            if name not in KNOWN_CANDIDATES:
                errors.append(f"unconfirmed ranked registration: {name!r}")
                continue
            expected = KNOWN_CANDIDATES[name]
            if "literalIndex" in item and item["literalIndex"] is not None:
                if item["literalIndex"] != expected["literalIndex"]:
                    errors.append(f"literalIndex mismatch for ranked registration {name!r}")
            if "slotRvas" in item and isinstance(item["slotRvas"], list):
                if item["slotRvas"] != expected["slotRvas"]:
                    errors.append(f"slotRvas mismatch for ranked registration {name!r}")
            for field in ("nativeKey", "entryRva", "resolvedContext", "function"):
                if field in item and item[field] not in (None, "unknown"):
                    errors.append(f"unproven {field} in ranked registration {name!r}")
            if "offsets" in item and not _is_empty_values(item.get("offsets")):
                if not (isinstance(item.get("offsets"), dict) and item["offsets"].get("values") in (None, {})):
                    errors.append(f"ranked registration {name!r} has an invented offset")
            if "rank" in item and item["rank"] is not None:
                ranks.append(item["rank"])
        if ranks and len(ranks) == len(value):
            if sorted(ranks) != list(range(1, len(value) + 1)):
                errors.append("ranked registration ranks must be a contiguous 1-based sequence")

    for container_key in ("nativeKeys", "nativeEntries", "entriesNative"):
        container = data.get(container_key)
        if isinstance(container, dict):
            values = container.get("values")
            if values not in (None, {}):
                errors.append("native key values must remain empty")
            confirmed = container.get("confirmed")
            if isinstance(confirmed, list) and confirmed:
                errors.append("no native key is confirmed by this probe")
            for key, value in container.items():
                if key in ("status", "values", "confirmed", "unresolved", "note"):
                    continue
                if value not in (None, "unknown", [], {}):
                    errors.append(f"unresolved native key field must not be populated: {key!r}")

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
            if value not in (None, "unknown", [], {}):
                errors.append(f"unresolved offset field must not be populated: {key!r}")

    if "functions" in data and not _is_empty_values(data.get("functions")):
        errors.append("fabricated functions are not allowed")

    if "ripCandidateTarget" in data and data["ripCandidateTarget"] is not None:
        if data["ripCandidateTarget"] != "0x4B00AE8":
            errors.append("ripCandidateTarget does not match the confirmed vtable")

    return {"valid": not errors, "errors": errors, "warnings": warnings}


def self_test():
    result = manifest()
    assert len(result["propertyCandidates"]) == 6
    assert len(result["rankedRegistrations"]) == 6
    assert result["binary"]["liveRecordsRead"] == 0
    assert result["offsets"]["values"] == {}
    assert result["nativeKeys"]["values"] == {}
    assert all(item["nativeKey"] is None for item in result["propertyCandidates"])
    assert all(item["offsets"] == "unknown" for item in result["propertyCandidates"])

    validation = validate_manifest(result)
    assert validation["valid"] is True, validation["errors"]

    bad_key = json.loads(json.dumps(result))
    bad_key["propertyCandidates"][0]["nativeKey"] = "GCuM"
    assert validate_manifest(bad_key)["valid"] is False

    bad_offset = json.loads(json.dumps(result))
    bad_offset["offsets"]["values"] = {"lastContractWage": 16}
    assert validate_manifest(bad_offset)["valid"] is False

    bad_candidate = json.loads(json.dumps(result))
    bad_candidate["propertyCandidates"].append({"name": "FabricatedProperty", "literalIndex": 1})
    assert validate_manifest(bad_candidate)["valid"] is False

    bad_slot = json.loads(json.dumps(result))
    bad_slot["propertyCandidates"][0]["slotRvas"] = ["0x0"]
    assert validate_manifest(bad_slot)["valid"] is False

    bad_rank = json.loads(json.dumps(result))
    bad_rank["rankedRegistrations"][0]["rank"] = 99
    assert validate_manifest(bad_rank)["valid"] is False

    bad_function = json.loads(json.dumps(result))
    bad_function["functions"] = ["FabricatedFunction"]
    assert validate_manifest(bad_function)["valid"] is False

    assert validate_manifest({"lane": LANE})["valid"] is True
    print("PASS: property candidate manifest, ranked registrations, null native keys, empty offsets, validation guards")


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
