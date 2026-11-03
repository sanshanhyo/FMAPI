#!/usr/bin/env python3
"""Bounded property-to-entry manifest and validator for training-development candidates.

This is an offline manifest/validator only. It records property names, literal
indices, and slot RVAs returned by one static probe. It does not prove native
keys, entry RVAs, offsets, business fields, or live values.
"""
import argparse
import json
import sys
from pathlib import Path

GAME_PLUGIN_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = "0x180000000"
PROBE_MODE = "static-property-candidates"
PROBE_MATCHES = 35
PROBE_RETURNED = 24
PROBE_TRUNCATED = True
PROBE_LIVE_RECORDS_READ = 0

PROPERTY_CANDIDATES = [
    {"name": "CanEditTrainingSchedule", "literalIndex": 4313, "slotRvas": ["0x32c81b8"], "semantics": "unverified-property-name", "classification": "ui-capability", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "CanPasteTrainingWeek", "literalIndex": 4336, "slotRvas": ["0x32c96f8"], "semantics": "unverified-property-name", "classification": "ui-capability", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "CanResetTrainingSchedule", "literalIndex": 4355, "slotRvas": ["0x32ca7f8"], "semantics": "unverified-property-name", "classification": "ui-capability", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "CurrentTrainingSchedule", "literalIndex": 6283, "slotRvas": ["0x3337990"], "semantics": "unverified-property-name", "classification": "ui-view-state", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "CustomTrainingSchedule", "literalIndex": 6344, "slotRvas": ["0x333b180"], "semantics": "unverified-property-name", "classification": "ui-view-state", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "DebugPotentialTrainingSchedules", "literalIndex": 6879, "slotRvas": ["0x32be638"], "semantics": "unverified-property-name", "classification": "ui-debug", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "DebugTrainingSchedule", "literalIndex": 7055, "slotRvas": ["0x32c8c38"], "semantics": "unverified-property-name", "classification": "ui-debug", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "DebugTrainingScheduleIndex", "literalIndex": 7056, "slotRvas": ["0x32c8d20"], "semantics": "unverified-property-name", "classification": "ui-debug", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "ExportTrainingSchedule", "literalIndex": 8142, "slotRvas": ["0x33062d0"], "semantics": "unverified-property-name", "classification": "operation", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "ExportTrainingScheduleType", "literalIndex": 8143, "slotRvas": ["0x33063b8"], "semantics": "unverified-property-name", "classification": "operation", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "FirstTrainingSchedule", "literalIndex": 8684, "slotRvas": ["0x3324f00"], "semantics": "unverified-property-name", "classification": "ui-view-state", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "FirstTrainingScheduleCategory", "literalIndex": 8685, "slotRvas": ["0x3324fe0"], "semantics": "unverified-property-name", "classification": "ui-view-state", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "IsTrainingScheduleCategoryValid", "literalIndex": 11581, "slotRvas": ["0x332e6f0"], "semantics": "unverified-property-name", "classification": "ui-validation", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "LoadTrainingScheduleType", "literalIndex": 12244, "slotRvas": ["0x32b8e60"], "semantics": "unverified-property-name", "classification": "operation", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "NextTrainingScheduleWeek", "literalIndex": 13734, "slotRvas": ["0x330d930"], "semantics": "unverified-property-name", "classification": "ui-view-state", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "ShowSimplifiedTrainingSchedule", "literalIndex": 17677, "slotRvas": ["0x32b7470"], "semantics": "unverified-property-name", "classification": "ui-display-preference", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "TrainingSchedule", "literalIndex": 20370, "slotRvas": ["0x32b50c8"], "semantics": "unverified-property-name", "classification": "identifier-or-label-unverified", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "TrainingScheduleCategory", "literalIndex": 20371, "slotRvas": ["0x32b51d0"], "semantics": "unverified-property-name", "classification": "identifier-or-label-unverified", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "TrainingScheduleCategoryDropdown", "literalIndex": 20372, "slotRvas": ["0x32b52d0"], "semantics": "unverified-property-name", "classification": "ui-control", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "TrainingScheduleDropdown", "literalIndex": 20373, "slotRvas": ["0x32b53c8"], "semantics": "unverified-property-name", "classification": "ui-control", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "TrainingScheduleDropdownName", "literalIndex": 20374, "slotRvas": ["0x32b54c0"], "semantics": "unverified-property-name", "classification": "ui-control", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "TrainingScheduleID", "literalIndex": 20375, "slotRvas": ["0x32b55b0"], "semantics": "unverified-property-name", "classification": "identifier-or-label-unverified", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "TrainingScheduleIndex", "literalIndex": 20376, "slotRvas": ["0x32b56a8"], "semantics": "unverified-property-name", "classification": "identifier-or-label-unverified", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
    {"name": "TrainingScheduleName", "literalIndex": 20377, "slotRvas": ["0x32b5798"], "semantics": "unverified-property-name", "classification": "identifier-or-label-unverified", "businessField": False, "newsRelated": False, "nativeKey": None, "key": None, "nativeEntryRva": None, "entryRva": None, "offset": None, "offsets": None},
]

CANDIDATES = PROPERTY_CANDIDATES
ENTRIES = PROPERTY_CANDIDATES

RANKED_REGISTRATION_NAMES = [
    "TrainingSchedule",
    "TrainingScheduleID",
    "TrainingScheduleName",
    "TrainingScheduleCategory",
    "TrainingScheduleIndex",
    "CurrentTrainingSchedule",
    "CustomTrainingSchedule",
    "FirstTrainingSchedule",
    "FirstTrainingScheduleCategory",
    "NextTrainingScheduleWeek",
    "IsTrainingScheduleCategoryValid",
    "CanEditTrainingSchedule",
    "CanPasteTrainingWeek",
    "CanResetTrainingSchedule",
    "ExportTrainingSchedule",
    "ExportTrainingScheduleType",
    "LoadTrainingScheduleType",
    "ShowSimplifiedTrainingSchedule",
    "DebugPotentialTrainingSchedules",
    "DebugTrainingSchedule",
    "DebugTrainingScheduleIndex",
    "TrainingScheduleCategoryDropdown",
    "TrainingScheduleDropdown",
    "TrainingScheduleDropdownName",
]

def _candidate_by_name(name):
    for item in PROPERTY_CANDIDATES:
        if item["name"] == name:
            return item
    return None

NEXT_REGISTRATIONS_TO_INSPECT = []
for rank, name in enumerate(RANKED_REGISTRATION_NAMES, start=1):
    candidate = _candidate_by_name(name)
    NEXT_REGISTRATIONS_TO_INSPECT.append({
        "rank": rank,
        "name": name,
        "literalIndex": candidate["literalIndex"],
        "slotRva": candidate["slotRvas"][0],
        "classification": candidate["classification"],
        "reason": "Returned by the static property probe with a literal index and slot RVA; inspect its property registration and native key before any live read.",
        "nativeKey": None,
        "key": None,
        "nativeEntryRva": None,
        "entryRva": None,
        "offset": None,
        "offsets": None,
    })

NEXT_REGISTRATIONS = NEXT_REGISTRATIONS_TO_INSPECT
RANKED_REGISTRATIONS = NEXT_REGISTRATIONS_TO_INSPECT

def manifest():
    return {
        "schema": "fmapi.property-entry.manifest.v1",
        "lane": "training-development",
        "source": "static property candidate probe output",
        "probe": {
            "mode": PROBE_MODE,
            "imageBase": IMAGE_BASE,
            "gamePluginSha256": GAME_PLUGIN_SHA256,
            "matches": PROBE_MATCHES,
            "returnedCandidates": PROBE_RETURNED,
            "truncated": PROBE_TRUNCATED,
            "liveRecordsRead": PROBE_LIVE_RECORDS_READ,
        },
        "propertyCandidates": PROPERTY_CANDIDATES,
        "candidates": PROPERTY_CANDIDATES,
        "entries": PROPERTY_CANDIDATES,
        "nextRegistrationsToInspect": NEXT_REGISTRATIONS_TO_INSPECT,
        "nextRegistrations": NEXT_REGISTRATIONS_TO_INSPECT,
        "rankedRegistrations": NEXT_REGISTRATIONS_TO_INSPECT,
        "entryHypothesis": {
            "status": "native-keys-unproven",
            "basis": "The probe returned 24 training-schedule property names with literal indices and one slot RVA each. These are metadata property names and slots only; no native key, entry function, offset, business object, or live value is proven.",
            "businessFieldNames": [],
            "newsRelatedNames": [],
            "uiOrOperationNames": [item["name"] for item in PROPERTY_CANDIDATES],
            "nativeContextEvidence": {
                "clubTeamPointerMatch": "current club2 TEAM pointers match TEAM_BASE low23-bit index entries 2/2",
                "nextFixtureContext": "NextFixture literal 13696 slot 0x330B698 native key 0x6E654669 first resolves TEAM_BASE context via global 0x5703768, not fixtures",
                "implication": "If training-schedule entries are team-scoped, investigate them through TEAM_BASE/global context rather than fixture context. Native keys remain null until proven.",
            },
            "rankedRegistrations": RANKED_REGISTRATION_NAMES,
            "confirmedNativeKeys": {},
            "nativeKeyStatus": "null-until-proven",
            "confirmedOffsets": {},
            "offsetStatus": "unknown",
        },
        "missingSemantics": [
            "No native key is assigned to any returned property candidate.",
            "No entry RVA or function is proven for any returned property candidate.",
            "No field offset, object size, base class, collection entry, or UID linkage is proven.",
            "The returned names are metadata property names only; they are not proven business fields, news fields, or operations.",
            "The probe returned 24 of 35 matches because its output was truncated.",
            "No live record, UI object, save, network resource, or private capture was read.",
        ],
        "prohibitedAccess": [
            "writes",
            "game calls",
            "UI reads",
            "native calls",
            "network access",
            "private capture access",
            "all-registry scans",
        ],
    }

def validate_manifest(data):
    if not isinstance(data, dict):
        raise ValueError("manifest must be an object")
    for key in ("schema", "lane", "probe", "propertyCandidates", "entryHypothesis", "missingSemantics"):
        if key not in data:
            raise ValueError("missing manifest key: %s" % key)
    if data["schema"] != "fmapi.property-entry.manifest.v1":
        raise ValueError("unsupported manifest schema")
    if data["lane"] != "training-development":
        raise ValueError("unsupported lane")
    probe = data["probe"]
    if not isinstance(probe, dict):
        raise ValueError("probe must be an object")
    if probe.get("gamePluginSha256") != GAME_PLUGIN_SHA256:
        raise ValueError("unsupported game_plugin fingerprint")
    if probe.get("liveRecordsRead") != 0:
        raise ValueError("probe must be static only")
    if probe.get("matches") != PROBE_MATCHES:
        raise ValueError("probe match count mismatch")
    if probe.get("returnedCandidates") != PROBE_RETURNED:
        raise ValueError("probe returned candidate count mismatch")
    if probe.get("truncated") is not True:
        raise ValueError("probe truncation flag mismatch")

    candidates = data.get("propertyCandidates")
    if candidates is None:
        candidates = data.get("candidates")
    if candidates is None:
        candidates = data.get("entries")
    if not isinstance(candidates, list) or len(candidates) != PROBE_RETURNED:
        raise ValueError("property candidate count mismatch")
    for alias in ("propertyCandidates", "candidates", "entries"):
        if alias in data and data[alias] is not candidates and len(data[alias]) != len(candidates):
            raise ValueError("property candidate alias count mismatch")

    seen_names = set()
    for item in candidates:
        if not isinstance(item, dict):
            raise ValueError("invalid property candidate")
        for required in ("name", "literalIndex", "slotRvas", "semantics"):
            if required not in item:
                raise ValueError("invalid property candidate")
        if not isinstance(item["name"], str) or not item["name"]:
            raise ValueError("invalid property name")
        if item["name"] in seen_names:
            raise ValueError("duplicate property name")
        seen_names.add(item["name"])
        if not isinstance(item["literalIndex"], int):
            raise ValueError("invalid literal index")
        if not isinstance(item["slotRvas"], list) or not item["slotRvas"]:
            raise ValueError("invalid slot RVA list")
        if not all(isinstance(value, str) and value for value in item["slotRvas"]):
            raise ValueError("invalid slot RVA")
        for nullable in ("nativeKey", "key", "nativeEntryRva", "entryRva", "offset", "offsets"):
            if nullable in item and item[nullable] is not None:
                raise ValueError("unproven native key or offset in property candidate")
        if item.get("businessField") is True:
            raise ValueError("unproven business field claim")
        if item.get("newsRelated") is True:
            raise ValueError("unproven news field claim")

    hypothesis = data["entryHypothesis"]
    if not isinstance(hypothesis, dict):
        raise ValueError("entry hypothesis must be an object")
    if hypothesis.get("status") != "native-keys-unproven":
        raise ValueError("unexpected entry hypothesis status")
    if hypothesis.get("confirmedNativeKeys") != {}:
        raise ValueError("confirmed native keys must be empty")
    if hypothesis.get("confirmedOffsets") != {}:
        raise ValueError("confirmed offsets must be empty")
    if hypothesis.get("nativeKeyStatus") != "null-until-proven":
        raise ValueError("native key status must remain null until proven")
    if hypothesis.get("offsetStatus") != "unknown":
        raise ValueError("offset status must remain unknown")
    if hypothesis.get("businessFieldNames") != []:
        raise ValueError("no business fields are proven")
    return True

def self_test():
    data = manifest()
    rendered = json.dumps(data, sort_keys=True)
    parsed = json.loads(rendered)
    validate_manifest(parsed)
    assert len(parsed["propertyCandidates"]) == PROBE_RETURNED
    assert len(parsed["nextRegistrationsToInspect"]) == PROBE_RETURNED
    assert parsed["probe"]["matches"] == PROBE_MATCHES
    assert parsed["probe"]["truncated"] is True
    assert parsed["probe"]["liveRecordsRead"] == 0
    assert all(item["nativeKey"] is None for item in parsed["propertyCandidates"])
    assert all(item["offset"] is None for item in parsed["propertyCandidates"])
    assert all(item["offsets"] is None for item in parsed["propertyCandidates"])
    assert "CanEditTrainingSchedule" in rendered
    assert "0x32c81b8" in rendered
    assert "0x330d930" in rendered
    assert parsed["entryHypothesis"]["confirmedNativeKeys"] == {}
    assert parsed["entryHypothesis"]["confirmedOffsets"] == {}
    assert parsed["entryHypothesis"]["nativeKeyStatus"] == "null-until-proven"
    print("PASS: training-development property-entry manifest and validator")

def main():
    parser = argparse.ArgumentParser(description="Training-development property-entry manifest/validator")
    parser.add_argument("--output", metavar="PATH", help="write manifest JSON to PATH")
    parser.add_argument("--validate", metavar="PATH", help="validate a manifest JSON file")
    parser.add_argument("--self-test", action="store_true", help="run synthetic manifest checks")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.validate:
        path = Path(args.validate)
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_manifest(data)
        print("VALID: %s" % path)
        return

    rendered = json.dumps(manifest(), indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

if __name__ == "__main__":
    main()
