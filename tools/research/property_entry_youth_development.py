#!/usr/bin/env python3
"""Machine-readable bounded property-to-entry manifest and validator.

Lane: youth-development.
Input evidence: the authorized static property-candidate probe (15 names) plus
coordinator evidence about TEAM_BASE context resolution. This is NOT a live
reader and NOT an SDK: it performs no process, game, UI, network, credential,
or raw-sample access. Native keys, offsets, function RVAs, field types and slot
semantics remain null/unresolved until independently proven.
"""

import argparse
import json
from pathlib import Path

LANE = "youth-development"
PROBE_MODE = "static-property-candidates"
MATCHES = 15
TRUNCATED = False
LIVE_RECORDS_READ = 0

SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = 0x180000000

PROBE_COMMAND = (
    "& 'pwsh' -NoProfile -File "
    "'<research-workspace>/agent-tools/"
    "run-lane-property-probe.ps1' -Lane 'youth-development'"
)

PROPERTIES = [
    {"name": "DaysUntilYouthIntake", "literalIndex": 6579, "slotRvas": ["0x32ace90"], "semantics": "unverified-property-name"},
    {"name": "HighestLevelYouthTeam", "literalIndex": 9941, "slotRvas": ["0x32d1650"], "semantics": "unverified-property-name"},
    {"name": "SecondHighestLevelYouthTeam", "literalIndex": 16963, "slotRvas": ["0x3329d88"], "semantics": "unverified-property-name"},
    {"name": "YouthIntakeDescription", "literalIndex": 22257, "slotRvas": ["0x33205e8"], "semantics": "unverified-property-name"},
    {"name": "YouthIntakeFeedbackString", "literalIndex": 22258, "slotRvas": ["0x33206d0"], "semantics": "unverified-property-name"},
    {"name": "YouthIntakeGrade", "literalIndex": 22259, "slotRvas": ["0x33207b8"], "semantics": "unverified-property-name"},
    {"name": "YouthIntakeLevel", "literalIndex": 22260, "slotRvas": ["0x3320898"], "semantics": "unverified-property-name"},
    {"name": "YouthIntakePositionPreviews", "literalIndex": 22261, "slotRvas": ["0x3320970"], "semantics": "unverified-property-name"},
    {"name": "YouthIntakeRating", "literalIndex": 22262, "slotRvas": ["0x3320a50"], "semantics": "unverified-property-name"},
    {"name": "YouthIntakeStatus", "literalIndex": 22263, "slotRvas": ["0x3320b30"], "semantics": "unverified-property-name"},
    {"name": "YouthTeam", "literalIndex": 22276, "slotRvas": ["0x3321668"], "semantics": "unverified-property-name"},
    {"name": "YouthTeam3", "literalIndex": 22277, "slotRvas": ["0x3321748"], "semantics": "unverified-property-name"},
    {"name": "YouthTeam4", "literalIndex": 22278, "slotRvas": ["0x3321838"], "semantics": "unverified-property-name"},
    {"name": "YouthTeam5", "literalIndex": 22279, "slotRvas": ["0x3321920"], "semantics": "unverified-property-name"},
    {"name": "YouthTeams", "literalIndex": 22280, "slotRvas": ["0x3321a08"], "semantics": "unverified-property-name"},
]

CLASSIFICATION = {
    "DaysUntilYouthIntake": "operations-candidate",
    "HighestLevelYouthTeam": "team-context-candidate",
    "SecondHighestLevelYouthTeam": "team-context-candidate",
    "YouthIntakeDescription": "ui-or-news-candidate",
    "YouthIntakeFeedbackString": "ui-or-news-candidate",
    "YouthIntakeGrade": "business-field-candidate",
    "YouthIntakeLevel": "business-field-candidate",
    "YouthIntakePositionPreviews": "ui-or-news-candidate",
    "YouthIntakeRating": "business-field-candidate",
    "YouthIntakeStatus": "operations-candidate",
    "YouthTeam": "team-context-candidate",
    "YouthTeam3": "team-context-candidate",
    "YouthTeam4": "team-context-candidate",
    "YouthTeam5": "team-context-candidate",
    "YouthTeams": "team-context-candidate",
}

ALLOWED_CLASSIFICATIONS = {
    "business-field-candidate",
    "team-context-candidate",
    "operations-candidate",
    "ui-or-news-candidate",
}

PRIORITY = {
    "team-context-candidate": "high",
    "business-field-candidate": "medium",
    "operations-candidate": "medium",
    "ui-or-news-candidate": "low",
}

RANKED_ORDER = [
    "YouthTeams",
    "YouthTeam",
    "YouthTeam3",
    "YouthTeam4",
    "YouthTeam5",
    "HighestLevelYouthTeam",
    "SecondHighestLevelYouthTeam",
    "YouthIntakeRating",
    "YouthIntakeGrade",
    "YouthIntakeLevel",
    "DaysUntilYouthIntake",
    "YouthIntakeStatus",
    "YouthIntakeDescription",
    "YouthIntakeFeedbackString",
    "YouthIntakePositionPreviews",
]

COORDINATOR_EVIDENCE = {
    "source": "coordinator-evidence",
    "independentlyVerified": False,
    "club2TeamPointersMatchTeamBaseLow23BitIndex": "2/2",
    "teamBaseContextGlobalRva": "0x5703768",
    "nextFixture": {
        "literalIndex": 13696,
        "slotRva": "0x330B698",
        "nativeKey": "0x6E654669",
        "firstResolves": "TEAM_BASE context via global 0x5703768",
        "resolvesFixtures": False,
    },
    "implication": (
        "A property whose name suggests fixtures or teams may first resolve "
        "TEAM_BASE context through global 0x5703768. Team-named youth "
        "properties are therefore treated as team-context candidates until "
        "their registrations and returned values are inspected."
    ),
}

REASONS = {
    "YouthTeams": "Collection/team reference; inspect first because coordinator evidence shows team-named properties can resolve TEAM_BASE context via global 0x5703768 rather than direct business data.",
    "YouthTeam": "Single team reference; same team-context dependency risk as NextFixture.",
    "YouthTeam3": "Indexed team slot; verify whether it is a real youth-team business object or a TEAM_BASE context entry.",
    "YouthTeam4": "Indexed team slot; verify whether it is a real youth-team business object or a TEAM_BASE context entry.",
    "YouthTeam5": "Indexed team slot; verify whether it is a real youth-team business object or a TEAM_BASE context entry.",
    "HighestLevelYouthTeam": "Team reference whose name implies hierarchy; may resolve team context rather than a youth squad entity.",
    "SecondHighestLevelYouthTeam": "Team reference whose name implies hierarchy; may resolve team context rather than a youth squad entity.",
    "YouthIntakeRating": "Candidate business field; no native key or offset proven; inspect registration and returned value type.",
    "YouthIntakeGrade": "Candidate business field; no native key or offset proven; inspect registration and returned value type.",
    "YouthIntakeLevel": "Candidate business field; no native key or offset proven; inspect registration and returned value type.",
    "DaysUntilYouthIntake": "Counter candidate; may be UI-facing; inspect after team context and business fields.",
    "YouthIntakeStatus": "Status candidate; may be UI-facing; inspect after team context and business fields.",
    "YouthIntakeDescription": "Name suggests UI/news text, not a business field; inspect only for news/UI subtype scope.",
    "YouthIntakeFeedbackString": "Name suggests UI/news text, not a business field; inspect only for news/UI subtype scope.",
    "YouthIntakePositionPreviews": "Name suggests UI preview, not a business field; inspect only for UI/news subtype scope.",
}


def _hex(value):
    return "0x{:X}".format(value)


def _property_by_name(name):
    for prop in PROPERTIES:
        if prop["name"] == name:
            return prop
    return None


def _ranked_entry(name, rank):
    prop = _property_by_name(name)
    classification = CLASSIFICATION[name]
    return {
        "rank": rank,
        "propertyName": name,
        "literalIndex": prop["literalIndex"],
        "slotRvas": list(prop["slotRvas"]),
        "classification": classification,
        "priority": PRIORITY[classification],
        "reason": REASONS[name],
        "dependency": (
            "coordinator-evidence: NextFixture literal 13696 / slot 0x330B698 / "
            "native key 0x6E654669 first resolves TEAM_BASE context via global "
            "0x5703768, not fixtures"
            if classification == "team-context-candidate"
            else "pinned binary + static property-candidate probe only"
        ),
    }


def build_ranked():
    return [_ranked_entry(name, rank) for rank, name in enumerate(RANKED_ORDER, start=1)]


def build_manifest():
    ranked = build_ranked()
    rank_by_name = {entry["propertyName"]: entry["rank"] for entry in ranked}
    properties = []
    for prop in PROPERTIES:
        classification = CLASSIFICATION[prop["name"]]
        properties.append(
            {
                "name": prop["name"],
                "literalIndex": prop["literalIndex"],
                "slotRvas": list(prop["slotRvas"]),
                "semantics": prop["semantics"],
                "classification": classification,
                "inspectionRank": rank_by_name[prop["name"]],
                "uiOrNewsOrOperations": classification in ("ui-or-news-candidate", "operations-candidate"),
                "businessField": classification == "business-field-candidate",
                "teamContextCandidate": classification == "team-context-candidate",
                "entry": {
                    "kind": "property-to-entry-candidate",
                    "nativeKey": None,
                    "offset": None,
                    "functionRva": None,
                    "fieldType": None,
                    "status": "unverified",
                },
            }
        )

    counts = {}
    for classification in ALLOWED_CLASSIFICATIONS:
        counts[classification] = sum(
            1 for prop in properties if prop["classification"] == classification
        )

    return {
        "schema": "fmapi.property-entry.v1",
        "lane": LANE,
        "status": "static-property-candidates-only",
        "probe": {
            "mode": PROBE_MODE,
            "command": PROBE_COMMAND,
            "matches": MATCHES,
            "truncated": TRUNCATED,
            "liveRecordsRead": LIVE_RECORDS_READ,
        },
        "binary": {
            "sha256": SHA256,
            "imageBase": _hex(IMAGE_BASE),
            "source": "docs/research/native-entry-youth-development.md",
        },
        "coordinatorEvidence": COORDINATOR_EVIDENCE,
        "properties": properties,
        "classifications": {
            "allowed": sorted(ALLOWED_CLASSIFICATIONS),
            "counts": counts,
        },
        "rankedNextRegistrations": ranked,
        "limits": [
            "Static property-candidate names only; no process or live record was read",
            "Property names are unverified and may refer to UI, news, operations, or business fields",
            "Native keys, offsets, function RVAs, field types, and slot semantics remain null/unresolved",
            "Coordinator evidence about NextFixture/TEAM_BASE is recorded as provided, not independently verified here",
            "No SDK, adapter, or live reader is included",
        ],
        "nextBoundedRequest": {
            "static": [
                "Inspect property registrations for the ranked team-context candidates first",
                "Confirm whether each slot resolves TEAM_BASE context via global 0x5703768 or direct business data",
            ],
            "live": [
                "Coordinator-approved read-only probe only: read global RVA 0x5703768 pointer, "
                "the TEAM_BASE low 23-bit index entries for at most the two current-club TEAM pointers, "
                "and a small raw prefix; process recheck before and after; aggregate budget <= 64 KiB; "
                "no writes, UI, match advancement, or save changes",
            ],
        },
    }


def classify_property(name):
    normalized = str(name).strip()
    if normalized in CLASSIFICATION:
        ranked = build_ranked()
        rank_by_name = {entry["propertyName"]: entry["rank"] for entry in ranked}
        return {
            "matched": True,
            "name": normalized,
            "classification": CLASSIFICATION[normalized],
            "inspectionRank": rank_by_name[normalized],
            "proposedClassifications": [],
        }
    return {
        "matched": False,
        "name": normalized,
        "classification": None,
        "inspectionRank": None,
        "proposedClassifications": sorted(ALLOWED_CLASSIFICATIONS),
    }


def validate_manifest(manifest):
    errors = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]

    expected = build_manifest()

    for key in ("lane", "binary", "properties", "classifications", "rankedNextRegistrations", "coordinatorEvidence"):
        if key not in manifest:
            errors.append("missing required key: {}".format(key))

    if manifest.get("lane") != LANE:
        errors.append("lane must be {}".format(LANE))

    binary = manifest.get("binary")
    if not isinstance(binary, dict):
        errors.append("binary must be an object")
    else:
        if binary.get("sha256") != SHA256:
            errors.append("binary sha256 mismatch or missing")
        if binary.get("imageBase") != _hex(IMAGE_BASE):
            errors.append("binary imageBase mismatch or missing")

    probe = manifest.get("probe")
    if not isinstance(probe, dict):
        errors.append("probe must be an object")
    else:
        if probe.get("mode") != PROBE_MODE:
            errors.append("probe.mode must be {}".format(PROBE_MODE))
        if probe.get("matches") != MATCHES:
            errors.append("probe.matches must be {}".format(MATCHES))
        if probe.get("truncated") is not False:
            errors.append("probe.truncated must be false")
        if probe.get("liveRecordsRead") != 0:
            errors.append("probe.liveRecordsRead must be 0")

    properties = manifest.get("properties")
    if not isinstance(properties, list):
        errors.append("properties must be an array")
    else:
        if len(properties) != len(PROPERTIES):
            errors.append("properties must contain exactly {} candidates".format(len(PROPERTIES)))
        expected_properties = expected["properties"]
        if properties != expected_properties:
            errors.append("properties must equal the actual returned candidate set")

    classifications = manifest.get("classifications")
    if not isinstance(classifications, dict):
        errors.append("classifications must be an object")
    else:
        if classifications.get("allowed") != sorted(ALLOWED_CLASSIFICATIONS):
            errors.append("classifications.allowed mismatch")
        counts = classifications.get("counts")
        if not isinstance(counts, dict):
            errors.append("classifications.counts must be an object")
        else:
            for classification in ALLOWED_CLASSIFICATIONS:
                expected_count = sum(1 for prop in PROPERTIES if CLASSIFICATION[prop["name"]] == classification)
                if counts.get(classification) != expected_count:
                    errors.append("classifications.counts.{} mismatch".format(classification))

    ranked = manifest.get("rankedNextRegistrations")
    if ranked != expected["rankedNextRegistrations"]:
        errors.append("rankedNextRegistrations must equal the ranked candidate set")

    # Reject invented field offsets / native keys anywhere in the manifest.
    def contains_invented(value):
        if isinstance(value, str):
            normalized = value.replace(" ", "")
            return "+0x" in normalized or "+0X" in normalized
        if isinstance(value, dict):
            return any(contains_invented(item) for item in value.values())
        if isinstance(value, list):
            return any(contains_invented(item) for item in value)
        return False

    if contains_invented(manifest):
        errors.append("manifest contains an invented field-offset reference")

    # Keep unresolved native entry fields null.
    for prop in (properties if isinstance(properties, list) else []):
        entry = prop.get("entry") if isinstance(prop, dict) else None
        if not isinstance(entry, dict):
            errors.append("property entry must be an object")
            continue
        if entry.get("nativeKey") is not None:
            errors.append("property nativeKey must remain null until proven")
        if entry.get("offset") is not None:
            errors.append("property offset must remain null until proven")
        if entry.get("functionRva") is not None:
            errors.append("property functionRva must remain null until proven")
        if entry.get("fieldType") is not None:
            errors.append("property fieldType must remain null until proven")

    return errors


def self_test():
    manifest = build_manifest()
    assert manifest["lane"] == LANE
    assert manifest["probe"]["matches"] == 15
    assert len(manifest["properties"]) == 15
    assert len(manifest["rankedNextRegistrations"]) == 15
    assert validate_manifest(manifest) == []

    assert validate_manifest({}) != []

    bad = json.loads(json.dumps(manifest))
    bad["properties"][0]["entry"]["nativeKey"] = "0x123"
    assert validate_manifest(bad) != []

    bad2 = json.loads(json.dumps(manifest))
    bad2["properties"][0]["entry"]["offset"] = "0x10"
    assert validate_manifest(bad2) != []

    # invented offset string anywhere
    bad4 = json.loads(json.dumps(manifest))
    bad4["properties"][0]["name"] = "X+0x10"
    assert validate_manifest(bad4) != []

    match = classify_property("YouthTeams")
    assert match["matched"] is True
    assert match["classification"] == "team-context-candidate"
    assert match["inspectionRank"] == 1

    no_match = classify_property("UNKNOWN_PROPERTY")
    assert no_match["matched"] is False
    assert no_match["classification"] is None
    assert no_match["proposedClassifications"]

    print("PASS: youth-development property-entry manifest synthetic checks")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--classify-name")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.classify_name is not None:
        rendered = json.dumps(classify_property(args.classify_name), ensure_ascii=False, indent=2)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
            print("Wrote property classification to {}".format(args.output))
        else:
            print(rendered)
        return

    if args.validate is not None:
        try:
            info = args.validate.stat()
        except OSError as error:
            raise SystemExit("invalid input: {}".format(error))
        if info.st_size == 0 or info.st_size > 1024 * 1024:
            raise SystemExit("input missing or outside 1..1048576 bytes")
        try:
            candidate = json.loads(args.validate.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise SystemExit("invalid input: {}".format(error))
        errors = validate_manifest(candidate)
        result = {"valid": not errors, "errors": errors}
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
            print("Wrote validation result to {}".format(args.output))
        else:
            print(rendered)
        return

    manifest = build_manifest()
    rendered = json.dumps(manifest, ensure_ascii=False, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print("Wrote property-entry manifest to {}".format(args.output))
    else:
        print(rendered)


if __name__ == "__main__":
    main()
