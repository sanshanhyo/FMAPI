#!/usr/bin/env python3
"""Machine-readable manifest and validator for property-to-entry candidates.

This is an offline research scaffold. It records only the two property names,
literal indices, and encoded slot RVAs actually returned by the
fixtures-matches static property probe. It does not invent native keys,
field offsets, function RVAs, collection routes, or fixture readers. Native
keys and offsets remain null until independently proven.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PINNED_HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = "0x180000000"
MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
RVA_RE = re.compile(r"^0x[0-9A-Fa-f]+$")

PROBE_RESULT = {
    "lane": "fixtures-matches",
    "mode": "static-property-candidates",
    "matches": 2,
    "truncated": False,
    "liveRecordsRead": 0,
    "entries": [
        {
            "name": "FixtureDate",
            "literalIndex": 8701,
            "slotRvas": ["0x3325e28"],
            "semantics": "unverified-property-name",
        },
        {
            "name": "NextFixture",
            "literalIndex": 13696,
            "slotRvas": ["0x330b698"],
            "semantics": "unverified-property-name",
        },
    ],
}

PROPERTY_CANDIDATES = [
    {
        "name": "FixtureDate",
        "literalIndex": 8701,
        "slotRvas": ["0x3325e28"],
        "probeSemantics": "unverified-property-name",
        "fieldRoleHypothesis": "business-field-candidate (unverified name only)",
        "refersToBusinessField": "unknown",
        "refersToUiNewsOrOperations": "unknown",
        "roleEvidence": "Property name suggests a fixture date, but no registration context, native key, offset, or live read proves that role.",
        "nativeKey": None,
        "nativeKeyStatus": "null-unproven",
        "offset": None,
        "offsetStatus": "null-unproven",
        "requiresDisassembly": True,
        "liveRead": False,
    },
    {
        "name": "NextFixture",
        "literalIndex": 13696,
        "slotRvas": ["0x330b698"],
        "probeSemantics": "unverified-property-name",
        "fieldRoleHypothesis": "operations-or-ui-candidate (team context; not a proven fixture business field)",
        "refersToBusinessField": "unlikely",
        "refersToUiNewsOrOperations": "possible",
        "roleEvidence": (
            "Coordinator evidence states that this slot's reported native key first resolves "
            "TEAM_BASE context via global 0x5703768, not a fixture record."
        ),
        "nativeKey": None,
        "nativeKeyStatus": "null-unproven",
        "offset": None,
        "offsetStatus": "null-unproven",
        "requiresDisassembly": True,
        "liveRead": False,
    },
]

COORDINATOR_EVIDENCE = {
    "attribution": "coordinator-provided; not locally executed in this wave",
    "club2TeamPointersMatchTeamBaseLow23Bit": "2/2",
    "nextFixture": {
        "literalIndex": 13696,
        "slotRva": "0x330b698",
        "nativeKeyReported": "0x6E654669",
        "firstResolves": "TEAM_BASE context via global 0x5703768",
        "notFixtures": True,
    },
    "note": (
        "The reported native key is recorded as coordinator evidence only. It is not treated "
        "as a validated offset, proven registration function, or fixture field layout."
    ),
}

RANKED_REGISTRATIONS = [
    {
        "rank": 1,
        "registrationSlotRva": "0x3325e28",
        "propertyName": "FixtureDate",
        "literalIndex": 8701,
        "priority": "high",
        "reason": (
            "Highest priority: the property name suggests a fixture date. Inspect this "
            "GameAssembly registration and its disassembly to determine whether it is a "
            "business field or UI/news/operations. Native key and offset remain unproven."
        ),
        "nativeKey": None,
        "offset": None,
        "liveRead": False,
    },
    {
        "rank": 2,
        "registrationSlotRva": "0x330b698",
        "propertyName": "NextFixture",
        "literalIndex": 13696,
        "priority": "medium",
        "reason": (
            "Second priority: coordinator evidence says this property first resolves "
            "TEAM_BASE context via global 0x5703768, not fixtures. Inspect its registration "
            "to confirm whether it is team-context/UI/operations rather than a fixture "
            "business field. Native key and offset remain unproven."
        ),
        "nativeKey": None,
        "offset": None,
        "liveRead": False,
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def build_manifest():
    return {
        "tool": "property_entry_fixtures_matches.py",
        "role": "offline-static-property-entry-manifest-validator",
        "mode": "offline-static",
        "lane": "fixtures-matches",
        "liveReader": False,
        "liveRecordsRead": 0,
        "processAccess": False,
        "networkAccess": False,
        "binary": {
            "name": "game_plugin.dll",
            "sha256": PINNED_HASH,
            "imageBase": IMAGE_BASE,
        },
        "executedProbe": PROBE_RESULT,
        "propertyCandidateCount": len(PROPERTY_CANDIDATES),
        "propertyCandidates": PROPERTY_CANDIDATES,
        "propertyEntries": PROPERTY_CANDIDATES,
        "registrationCandidateCount": len(RANKED_REGISTRATIONS),
        "rankedRegistrations": RANKED_REGISTRATIONS,
        "nextRegistrations": RANKED_REGISTRATIONS,
        "registrationsToInspect": RANKED_REGISTRATIONS,
        "coordinatorEvidence": COORDINATOR_EVIDENCE,
        "unresolved": {
            "nativeKeys": "unknown",
            "offsets": "unknown",
            "fieldSemantics": "unknown",
            "registrationRoles": "unknown",
            "collectionRoute": "unknown",
            "uiNewsOperationsDistinction": "unknown",
        },
        "limitations": [
            "Property names and encoded slots are structural candidates only.",
            "No native key, field offset, function RVA, record size, or collection route is confirmed.",
            "No process, game, UI, private sample, or network access is performed.",
            "No live reader is implemented.",
            "Coordinator evidence is attributed and is not a local live result.",
        ],
    }


def validate_manifest(manifest):
    errors = []

    required_top = {
        "tool",
        "role",
        "mode",
        "lane",
        "liveReader",
        "liveRecordsRead",
        "processAccess",
        "networkAccess",
        "binary",
        "executedProbe",
        "propertyCandidateCount",
        "propertyCandidates",
        "propertyEntries",
        "registrationCandidateCount",
        "rankedRegistrations",
        "nextRegistrations",
        "registrationsToInspect",
        "coordinatorEvidence",
        "unresolved",
        "limitations",
    }
    missing = required_top - set(manifest)
    if missing:
        errors.append("missing top-level keys: %s" % sorted(missing))

    if manifest.get("liveReader") is not False:
        errors.append("liveReader must be false")
    if manifest.get("liveRecordsRead") != 0:
        errors.append("liveRecordsRead must be 0")
    if manifest.get("processAccess") is not False:
        errors.append("processAccess must be false")
    if manifest.get("networkAccess") is not False:
        errors.append("networkAccess must be false")

    binary = manifest.get("binary", {})
    if not isinstance(binary, dict):
        errors.append("binary must be an object")
    else:
        if binary.get("sha256") != PINNED_HASH:
            errors.append("binary sha256 mismatch")
        if binary.get("imageBase") != IMAGE_BASE:
            errors.append("binary imageBase mismatch")

    probe = manifest.get("executedProbe", {})
    if not isinstance(probe, dict):
        errors.append("executedProbe must be an object")
    else:
        if probe.get("liveRecordsRead") != 0:
            errors.append("executedProbe liveRecordsRead must be 0")
        if probe.get("matches") != len(probe.get("entries", [])):
            errors.append("executedProbe matches mismatch")
        if probe.get("truncated") is not False:
            errors.append("executedProbe truncated must be false")

    if manifest.get("propertyCandidateCount") != len(manifest.get("propertyCandidates", [])):
        errors.append("propertyCandidateCount mismatch")
    if manifest.get("registrationCandidateCount") != len(manifest.get("rankedRegistrations", [])):
        errors.append("registrationCandidateCount mismatch")

    expected_names = {"FixtureDate", "NextFixture"}
    actual_names = {item.get("name") for item in manifest.get("propertyCandidates", []) if isinstance(item, dict)}
    if actual_names != expected_names:
        errors.append("property candidate names mismatch: %r" % sorted(actual_names))

    for item in manifest.get("propertyCandidates", []):
        if not isinstance(item, dict):
            errors.append("property candidate is not an object")
            continue
        if item.get("probeSemantics") != "unverified-property-name":
            errors.append("unexpected property probe semantics")
        if item.get("nativeKey") is not None:
            errors.append("property nativeKey must be null until proven")
        if item.get("offset") is not None:
            errors.append("property offset must be null until proven")
        if not RVA_RE.match(str(item.get("slotRvas", [""])[0] if item.get("slotRvas") else "")):
            errors.append("invalid property slotRva")
        for slot in item.get("slotRvas", []):
            if not RVA_RE.match(str(slot)):
                errors.append("invalid property slotRva: %r" % slot)

    ranks = []
    for item in manifest.get("rankedRegistrations", []):
        if not isinstance(item, dict):
            errors.append("ranked registration is not an object")
            continue
        if item.get("nativeKey") is not None:
            errors.append("registration nativeKey must be null until proven")
        if item.get("offset") is not None:
            errors.append("registration offset must be null until proven")
        if not RVA_RE.match(str(item.get("registrationSlotRva", ""))):
            errors.append("invalid registrationSlotRva: %r" % item.get("registrationSlotRva"))
        if not isinstance(item.get("rank"), int):
            errors.append("registration rank must be an integer")
        else:
            ranks.append(item["rank"])

    if sorted(ranks) != list(range(1, len(ranks) + 1)):
        errors.append("registration ranks must be contiguous from 1")

    unresolved = manifest.get("unresolved", {})
    if not isinstance(unresolved, dict) or not unresolved:
        errors.append("unresolved must be a non-empty object")
    else:
        for value in unresolved.values():
            if value != "unknown":
                errors.append("unresolved values must be unknown")
                break

    always_forbidden = {
        "fieldOffset",
        "fieldOffsets",
        "recordOffset",
        "functionRva",
        "function",
        "entryPoint",
        "entrypoint",
    }

    def check_forbidden(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in always_forbidden:
                    errors.append("forbidden key: %s" % key)
                if key in {"offset", "nativeKey"} and value is not None:
                    errors.append("unproven key must be null: %s" % key)
                check_forbidden(value)
        elif isinstance(obj, list):
            for value in obj:
                check_forbidden(value)

    check_forbidden(manifest)

    return errors


def self_test():
    manifest = build_manifest()
    errors = validate_manifest(manifest)
    if errors:
        print("self-test: FAIL")
        for error in errors:
            print(" - %s" % error)
        return 1

    assert manifest["propertyCandidateCount"] == 2
    assert manifest["registrationCandidateCount"] == 2
    assert manifest["liveReader"] is False
    assert manifest["executedProbe"]["matches"] == 2
    assert all(item["nativeKey"] is None for item in manifest["propertyCandidates"])
    assert all(item["offset"] is None for item in manifest["propertyCandidates"])
    assert all(item["nativeKey"] is None for item in manifest["rankedRegistrations"])
    assert all(item["offset"] is None for item in manifest["rankedRegistrations"])

    text = json.dumps(manifest, indent=2)
    assert len(text.encode("utf-8")) <= MAX_OUTPUT_BYTES
    parsed = json.loads(text)
    assert parsed == manifest

    print("self-test: PASS (property candidates, ranked registrations, null native keys/offsets)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Machine-readable manifest and validator for property-to-entry candidates"
    )
    parser.add_argument("--output", help="Write JSON to this file instead of stdout")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic checks and exit")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    manifest = build_manifest()
    errors = validate_manifest(manifest)
    if errors:
        raise SystemExit("manifest validation failed: %s" % "; ".join(errors))

    text = json.dumps(manifest, indent=2)
    if len(text.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise SystemExit("output exceeds size limit")

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
