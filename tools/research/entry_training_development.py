#!/usr/bin/env python3
"""Focused native-entry manifest and validator for the training-development lane.

This is an offline manifest/validator only. It contains confirmed game_plugin RTTI
type and vtable evidence from one static probe. It is not a live reader and does
not read processes, memory, UI, saves, network resources, or private captures.
"""
import argparse
import json
import sys
from pathlib import Path

GAME_PLUGIN_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = "0x180000000"

CONFIRMED_TYPES = [
    {"rva": "0x5671B70", "name": ".?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@", "category": "ui-handler"},
    {"rva": "0x5671BE0", "name": ".?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@", "category": "ui-handler"},
    {"rva": "0x5676AF0", "name": ".?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@", "category": "ui-handler-server"},
    {"rva": "0x5676B70", "name": ".?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@", "category": "ui-handler-server"},
    {"rva": "0x567AEC0", "name": ".?AV?$_Func_impl_no_alloc@V<lambda_3>@?0??is_training_session_available@calendar_ui_handler_helper@game_plugin@@YA_NAEBVTRAINING_SCHEDULE_WEEK@@W4TRAINING_SESSION_TYPE@@CW4TRAINING_SESSION_INDEX@@_N1AEBVRECORD@sicore@@3AEBVTEAM_BASE@db@@AEBVTYPED_LIST@9@C3@Z@_NW46@@std@@", "category": "std-function-impl"},
    {"rva": "0x567AFE0", "name": ".?AV<lambda_3>@?0??is_training_session_available@calendar_ui_handler_helper@game_plugin@@YA_NAEBVTRAINING_SCHEDULE_WEEK@@W4TRAINING_SESSION_TYPE@@CW4TRAINING_SESSION_INDEX@@_N1AEBVRECORD@sicore@@3AEBVTEAM_BASE@db@@AEBVTYPED_LIST@8@C3@Z@", "category": "lambda"},
    {"rva": "0x567EC30", "name": ".?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER@game_plugin@@", "category": "ui-handler"},
    {"rva": "0x5680AE0", "name": ".?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER_SERVER@game_plugin@@", "category": "ui-handler-server"},
]

CONFIRMED_VTABLES = [
    {"rva": "0x4AE5858", "type": ".?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@", "slots": ["0x1EA800", "0x1E3E70", "0x78A8C0", "0x1E3C80", "0x78DAA0", "0x1EA320", "0x1EA330", "0x1EA340", "0x1EA350", "0x1EA360", "0x787D80", "0x1E4140"]},
    {"rva": "0x4AE59C8", "type": ".?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@", "slots": ["0x1EA830", "0x1E3E70", "0x78A8C0", "0x1E3C80", "0x78DAA0", "0x1EA320", "0x1EA330", "0x1EA340", "0x1EA350", "0x1EA360", "0x787D80", "0x1E4140"]},
    {"rva": "0x4AF4BA8", "type": ".?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@", "slots": ["0x1EFE00", "0x1EC5C0", "0x1EC6C0", "0x7C7AB0", "0x7C7AC0", "0x7C7A90", "0x1EF680", "0x49FA20", "0x1EFE60", "invalid", "0x5676AEE80000000", "0x4AF4BEE84AF4C08"]},
    {"rva": "0x4AF4C68", "type": ".?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@", "slots": ["0x1EFE70", "0x1EC5C0", "0x1EC6C0", "0x7C7AB0", "0x7C7AC0", "0x7C7A90", "0x1EF680", "0x49FD30", "0x1EFED0", "invalid", "0x5676B6E80000000", "0x4AF4CAE84AF4CC8"]},
    {"rva": "0x4AFC418", "type": ".?AV?$_Func_impl_no_alloc@V<lambda_3>@?0??is_training_session_available@calendar_ui_handler_helper@game_plugin@@YA_NAEBVTRAINING_SCHEDULE_WEEK@@W4TRAINING_SESSION_TYPE@@CW4TRAINING_SESSION_INDEX@@_N1AEBVRECORD@sicore@@3AEBVTEAM_BASE@db@@AEBVTYPED_LIST@9@C3@Z@_NW46@@std@@", "slots": ["0x234B10", "0x234B30", "0x234B50", "0x234B70", "0x234B80", "0x234B90", "invalid", "invalid", "0x567AEBE80000000", "0x4AFC44E84AFC468", "invalid", "0x4AFC47680000002"]},
    {"rva": "0x4B0F1A8", "type": ".?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER@game_plugin@@", "slots": ["0x38F970", "0x314ED0", "0x310D70", "0x310E30", "0x78DAA0", "0x1EA320", "0x1EA330", "0x1EA340", "0x1EA350", "0x1EA360", "0x787D80", "0x314F00"]},
    {"rva": "0x4B14168", "type": ".?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER_SERVER@game_plugin@@", "slots": ["0x395B60", "0x315D30", "0x316510", "0x7C7AB0", "0x7C7AC0", "0x7C7A90", "invalid", "invalid", "0x5680ADE80000000", "0x4B1419E84B141B8", "invalid", "0x4B141C680000003"]},
]

RIP_CANDIDATES = [
    {"displacement": "0x1E74C4", "function": "0x1E66D0", "target": "0x4AE5858", "targetType": ".?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@"},
    {"displacement": "0x1E862A", "function": "0x1E66D0", "target": "0x4AE59C8", "targetType": ".?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@"},
    {"displacement": "0x1ECF0A", "function": "0x1EC790", "target": "0x4AF4C68", "targetType": ".?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@"},
    {"displacement": "0x1EDD47", "function": "0x1EC790", "target": "0x4AF4BA8", "targetType": ".?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@"},
    {"displacement": "0x22D14F", "function": "0x22D0D0", "target": "0x4AFC418", "targetType": ".?AV?$_Func_impl_no_alloc@V<lambda_3>@?0??is_training_session_available@calendar_ui_handler_helper@game_plugin@@YA_NAEBVTRAINING_SCHEDULE_WEEK@@W4TRAINING_SESSION_TYPE@@CW4TRAINING_SESSION_INDEX@@_N1AEBVRECORD@sicore@@3AEBVTEAM_BASE@db@@AEBVTYPED_LIST@9@C3@Z@_NW46@@std@@"},
    {"displacement": "0x234B1A", "function": "0xFFFFFFFF", "target": "0x4AFC418", "targetType": ".?AV?$_Func_impl_no_alloc@V<lambda_3>@?0??is_training_session_available@calendar_ui_handler_helper@game_plugin@@YA_NAEBVTRAINING_SCHEDULE_WEEK@@W4TRAINING_SESSION_TYPE@@CW4TRAINING_SESSION_INDEX@@_N1AEBVRECORD@sicore@@3AEBVTEAM_BASE@db@@AEBVTYPED_LIST@9@C3@Z@_NW46@@std@@"},
    {"displacement": "0x234B3A", "function": "0xFFFFFFFF", "target": "0x4AFC418", "targetType": ".?AV?$_Func_impl_no_alloc@V<lambda_3>@?0??is_training_session_available@calendar_ui_handler_helper@game_plugin@@YA_NAEBVTRAINING_SCHEDULE_WEEK@@W4TRAINING_SESSION_TYPE@@CW4TRAINING_SESSION_INDEX@@_N1AEBVRECORD@sicore@@3AEBVTEAM_BASE@db@@AEBVTYPED_LIST@9@C3@Z@_NW46@@std@@"},
    {"displacement": "0x385310", "function": "0x385300", "target": "0x4B0F1A8", "targetType": ".?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER@game_plugin@@"},
    {"displacement": "0x385C2A", "function": "0x3853B0", "target": "0x4B14168", "targetType": ".?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER_SERVER@game_plugin@@"},
]

PROPOSED_NARROWER_NAMES = [
    "TRAINING_SCHEDULE",
    "TRAINING_SCHEDULE_WEEK",
    "TRAINING_SESSION",
    "TRAINING_SESSION_TYPE",
    "TRAINING_SESSION_INDEX",
    "CUSTOM_TRAINING_SCHEDULE",
    "PERSON_REST_TRAINING_SCHEDULE",
    "PERSON_CANCEL_REST_TRAINING_SCHEDULE",
    "calendar_ui_handler_helper",
    "action_ui_handler_helper",
]

MISSING_SEMANTICS = [
    "No training business-object RTTI type or vtable was confirmed by the probe.",
    "No field offsets, collection entry, UID linkage, calendar/date units, load units, attendance, reports, mentor, adaptation, or attribute-change semantics are confirmed.",
    "UI-handler slot semantics are not decoded.",
    "No live process, game UI, save, or private capture evidence was used.",
]

def manifest():
    return {
        "schema": "fmapi.native-entry.manifest.v1",
        "lane": "training-development",
        "source": "static-pinned-file probe output",
        "probe": {
            "mode": "static-pinned-file",
            "imageBase": IMAGE_BASE,
            "gamePluginSha256": GAME_PLUGIN_SHA256,
            "types": 8,
            "vtables": 7,
            "liveRecordsRead": 0,
            "outputTruncated": False,
        },
        "confirmedRttiTypes": CONFIRMED_TYPES,
        "confirmedVtables": CONFIRMED_VTABLES,
        "ripCandidates": RIP_CANDIDATES,
        "entryHypothesis": {
            "status": "no-business-object-type-in-probe",
            "basis": "Confirmed RTTI names are UI handlers/helpers only; no training business object type was returned.",
            "uiHandlerTypes": [
                ".?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@",
                ".?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER@action_ui_handler_helper@game_plugin@@",
                ".?AVPERSON_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@",
                ".?AVPERSON_CANCEL_REST_TRAINING_SCHEDULE_ACTION_UI_HANDLER_SERVER@action_ui_handler_helper@game_plugin@@",
                ".?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER@game_plugin@@",
                ".?AVCUSTOM_TRAINING_SCHEDULE_UI_HANDLER_SERVER@game_plugin@@",
            ],
            "proposedNarrowerNames": PROPOSED_NARROWER_NAMES,
            "confirmedOffsets": {},
            "offsetStatus": "unknown",
        },
        "missingSemantics": MISSING_SEMANTICS,
    }

def validate_manifest(data):
    if not isinstance(data, dict):
        raise ValueError("manifest must be an object")
    for key in ("schema", "lane", "probe", "confirmedRttiTypes", "confirmedVtables", "entryHypothesis", "missingSemantics"):
        if key not in data:
            raise ValueError("missing manifest key: %s" % key)
    if data["schema"] != "fmapi.native-entry.manifest.v1":
        raise ValueError("unsupported manifest schema")
    if data["lane"] != "training-development":
        raise ValueError("unsupported lane")
    probe = data["probe"]
    if probe.get("gamePluginSha256") != GAME_PLUGIN_SHA256:
        raise ValueError("unsupported game_plugin fingerprint")
    if probe.get("liveRecordsRead") != 0:
        raise ValueError("probe must be static only")
    types = data["confirmedRttiTypes"]
    vtables = data["confirmedVtables"]
    if not isinstance(types, list) or len(types) != probe.get("types"):
        raise ValueError("RTTI type count mismatch")
    if not isinstance(vtables, list) or len(vtables) != probe.get("vtables"):
        raise ValueError("vtable count mismatch")
    seen_types = set()
    for item in types:
        if not isinstance(item, dict) or "rva" not in item or "name" not in item:
            raise ValueError("invalid RTTI type entry")
        if "offset" in item or "offsets" in item:
            raise ValueError("invented offset in RTTI type entry")
        if item["rva"] in seen_types:
            raise ValueError("duplicate RTTI RVA")
        seen_types.add(item["rva"])
    for item in vtables:
        if not isinstance(item, dict) or "rva" not in item or "type" not in item or "slots" not in item:
            raise ValueError("invalid vtable entry")
        if "offset" in item or "offsets" in item:
            raise ValueError("invented offset in vtable entry")
        if not isinstance(item["slots"], list) or len(item["slots"]) != 12:
            raise ValueError("vtable slot count must be 12")
    hypothesis = data["entryHypothesis"]
    if hypothesis.get("status") != "no-business-object-type-in-probe":
        raise ValueError("unexpected entry hypothesis status")
    if hypothesis.get("confirmedOffsets") != {}:
        raise ValueError("confirmed offsets must be empty")
    if hypothesis.get("offsetStatus") != "unknown":
        raise ValueError("offset status must be unknown")
    return True

def self_test():
    data = manifest()
    rendered = json.dumps(data, sort_keys=True)
    parsed = json.loads(rendered)
    validate_manifest(parsed)
    assert len(parsed["confirmedRttiTypes"]) == 8
    assert len(parsed["confirmedVtables"]) == 7
    assert parsed["probe"]["types"] == 8
    assert parsed["probe"]["vtables"] == 7
    assert parsed["probe"]["liveRecordsRead"] == 0
    assert "0x5671B70" in rendered
    assert "0x4B14168" in rendered
    assert "0x1E74C4" in rendered
    assert parsed["entryHypothesis"]["confirmedOffsets"] == {}
    assert parsed["entryHypothesis"]["offsetStatus"] == "unknown"
    assert "TRAINING_SCHEDULE_WEEK" in parsed["entryHypothesis"]["proposedNarrowerNames"]
    assert all("offset" not in item for item in parsed["confirmedRttiTypes"])
    assert all("offset" not in item for item in parsed["confirmedVtables"])
    print("PASS: training-development native-entry manifest and validator")

def main():
    parser = argparse.ArgumentParser(description="Training-development native-entry manifest/validator")
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
