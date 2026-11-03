#!/usr/bin/env python3
"""Offline manifest/validator for native manager-club entry evidence.

Reads only the pinned static probe transcript for lane manager-club.  It emits
a machine-readable manifest of RTTI types and vtables actually printed by that
probe.  It never opens a process, reads game memory, or invents field offsets.

Usage:
    python tools/research/entry_manager_club.py
    python tools/research/entry_manager_club.py --output manifest.json
    python tools/research/entry_manager_club.py --validate entries.json
    python tools/research/entry_manager_club.py --self-test
"""
import argparse
import json
import sys
from pathlib import Path

PINNED_BINARY_SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = 0x180000000
PROBE_COUNTS = {"types": 19, "vtables": 10, "liveRecordsRead": 0, "outputTruncated": True}

_CONFIRMED_TYPES = [
    ("EXTERN_NATIONAL_TEAM", ".?AVEXTERN_NATIONAL_TEAM@db@@", 0x569E290, False),
    ("EXTERN_TEAM", ".?AVEXTERN_TEAM@db@@", 0x569ECC0, False),
    ("STARTING_RESERVE_TEAM", ".?AVSTARTING_RESERVE_TEAM@db@@", 0x56A0330, True),
    ("DATABASE_TABLE_STARTING_RESERVE_TEAM", ".?AV?$DATABASE_TABLE@VSTARTING_RESERVE_TEAM@db@@@db@@", 0x56A13F0, True),
    ("FUNC_BASE_STARTING_RESERVE_TEAM", ".?AV?$_Func_base@XPEAVSTARTING_RESERVE_TEAM@db@@AEA_N@std@@", 0x56A1A00, False),
    ("TEAM", ".?AVTEAM@db@@", 0x56A2A60, True),
    ("FUNC_IMPL_SETUP_STARTING_RESERVE_TEAM", ".?AV?$_Func_impl_no_alloc@VSETUP_STARTING_RESERVE_TEAM@db@@XPEAVSTARTING_RESERVE_TEAM@2@AEA_N@std@@", 0x56A3910, False),
    ("SETUP_STARTING_RESERVE_TEAM", ".?AVSETUP_STARTING_RESERVE_TEAM@db@@", 0x56A3990, True),
    ("FUNC_IMPL_COUNT_STARTING_RESERVE_TEAM", ".?AV?$_Func_impl_no_alloc@VCOUNT_STARTING_RESERVE_TEAM@db@@XPEAVSTARTING_RESERVE_TEAM@2@AEA_N@std@@", 0x56A39D0, False),
    ("COUNT_STARTING_RESERVE_TEAM", ".?AVCOUNT_STARTING_RESERVE_TEAM@db@@", 0x56A3A50, True),
    ("FUNC_IMPL_LAMBDA0_SET_PIECE_CANDIDATES_TEAM", ".?AV?$_Func_impl_no_alloc@V<lambda_0>@?0??get_set_piece_candidates@TEAM@db@@QEBAXAEAVCONST_PLAYER_ARRAY@4@W4SET_PIECE_TACTICAL_TYPE@simatchshared@@W4SET_PIECE_SIDE@7@AEBVTACTICS_INFO@simatch@@AEBV?$REFERENCE_COUNTER@VFILTER@simigration@@@sicore@@@Z@HAEAVACTUAL_PLAYER@4@@std@@", 0x56AB010, False),
    ("LAMBDA0_SET_PIECE_CANDIDATES_TEAM", ".?AV<lambda_0>@?0??get_set_piece_candidates@TEAM@db@@QEBAXAEAVCONST_PLAYER_ARRAY@3@W4SET_PIECE_TACTICAL_TYPE@simatchshared@@W4SET_PIECE_SIDE@6@AEBVTACTICS_INFO@simatch@@AEBV?$REFERENCE_COUNTER@VFILTER@simigration@@@sicore@@@Z@", 0x56AB180, False),
    ("FUNC_IMPL_LAMBDA1_PENALTY_CANDIDATES_TEAM", ".?AV?$_Func_impl_no_alloc@V<lambda_1>@?0??get_penalty_candidates@TEAM@db@@QEBAXAEAVCONST_PLAYER_ARRAY@4@AEBVTACTICS_INFO@simatch@@AEBV?$REFERENCE_COUNTER@VFILTER@simigration@@@sicore@@@Z@HAEAVACTUAL_PLAYER@4@@std@@", 0x56AB280, False),
    ("LAMBDA1_PENALTY_CANDIDATES_TEAM", ".?AV<lambda_1>@?0??get_penalty_candidates@TEAM@db@@QEBAXAEAVCONST_PLAYER_ARRAY@3@AEBVTACTICS_INFO@simatch@@AEBV?$REFERENCE_COUNTER@VFILTER@simigration@@@sicore@@@Z@", 0x56AB370, False),
    ("NATIONAL_TEAM", ".?AVNATIONAL_TEAM@db@@", 0x56C5D10, True),
    ("FUNC_IMPL_LAMBDA3_SQUAD_PLANNER", ".?AV?$_Func_impl_no_alloc@V<lambda_3>@?0??setup_implementation@SQUAD_PLANNER@@AEAAXAEBVTACTICS_CREATOR@simatch@@W4SQUAD_PLAN_TYPE@@W4TACTIC_SLOT@tactical_training_flags@5@AEBVTEAM@db@@AEBVPLAYER_ARRAY@db@@AEBVPERSON_ARRAY@db@@@Z@_NPEAVPLAYER@db@@@std@@", 0x56D38D0, False),
    ("LAMBDA3_SQUAD_PLANNER", ".?AV<lambda_3>@?0??setup_implementation@SQUAD_PLANNER@@AEAAXAEBVTACTICS_CREATOR@simatch@@W4SQUAD_PLAN_TYPE@@W4TACTIC_SLOT@tactical_training_flags@4@AEBVTEAM@db@@AEBVPLAYER_ARRAY@9@AEBVPERSON_ARRAY@9@@Z@", 0x56D3A20, False),
    ("FUNC_IMPL_LAMBDA4_SQUAD_PLANNER", ".?AV?$_Func_impl_no_alloc@V<lambda_4>@?0??setup_implementation@SQUAD_PLANNER@@AEAAXAEBVTACTICS_CREATOR@simatch@@W4SQUAD_PLAN_TYPE@@W4TACTIC_SLOT@tactical_training_flags@5@W4TC_POSITION@simatchshared@@AEBVTEAM@db@@AEBVPLAYER_ARRAY@db@@AEBVPERSON_ARRAY@db@@@Z@_NPEAVPLAYER@db@@@std@@", 0x56D3B00, False),
    ("LAMBDA4_SQUAD_PLANNER", ".?AV<lambda_4>@?0??setup_implementation@SQUAD_PLANNER@@AEAAXAEBVTACTICS_CREATOR@simatch@@W4SQUAD_PLAN_TYPE@@W4TACTIC_SLOT@tactical_training_flags@4@W4TC_POSITION@simatchshared@@AEBVTEAM@db@@AEBVPLAYER_ARRAY@db@@AEBVPERSON_ARRAY@db@@@Z@", 0x56D3C30, False),
]

_CONFIRMED_VTABLES = {
    ".?AV?$DATABASE_TABLE@VSTARTING_RESERVE_TEAM@db@@@db@@": (0x4CA63F8, [0xD94D00, 0xD5AD00, 0xD5B210, 0xD5B230, 0xD5B710, 0xD5B5E0, 0xD5AD50, 0xD5B890, 0xD5B8A0, 0xD5AD70, 0xC92770, 0xD5BD80]),
    ".?AVSTARTING_RESERVE_TEAM@db@@": (0x4CB1E28, [0xDA1530, 0x389AC40, 0x389B530, 0x414370, 0x414380, 0x414390, 0x4143A0, 0x4144C0, 0x4143C0, 0xEF3880, 0x4143D0, 0x4143E0]),
    ".?AV?$_Func_impl_no_alloc@VSETUP_STARTING_RESERVE_TEAM@db@@XPEAVSTARTING_RESERVE_TEAM@2@AEA_N@std@@": (0x4CBAC38, [0xE3ED80, 0xE3EDA0, 0xE3EDC0, 0xE3EDD0, 0xE3EDE0, 0xE3EDF0, None, None, 0x56A390E80000000, 0x4CBAC6E84CBAC88, None, 0x4CBAC9680000002]),
    ".?AV?$_Func_impl_no_alloc@VCOUNT_STARTING_RESERVE_TEAM@db@@XPEAVSTARTING_RESERVE_TEAM@2@AEA_N@std@@": (0x4CBACF8, [0xE3EE00, 0xE3EE20, 0xE3EE40, 0xE3EE50, 0xE3EE60, 0xE3EE70, None, None, 0x56A39CE80000000, 0x4CBAD2E84CBAD48, None, 0x4CBAD5680000002]),
    ".?AVTEAM@db@@": (0x4CE1108, [0x121AC10, 0x11FDA20, 0x1202320, 0x11DDD90, 0x414380, 0x414390, 0x4143A0, 0xDA0AA0, 0x120E480, 0x1185810, 0x4143D0, 0x117A4C0]),
}

_NO_MATCH = [
    {
        "requestedName": ".?AVCLUB@db@@",
        "status": "no-match-in-this-probe",
        "reason": "CLUB RTTI type was not printed by the pinned lane probe; no vtable or offset evidence exists in this artifact.",
        "proposedNarrowerNames": [
            ".?AVCLUB@db@@",
            ".?AVTEAM@db@@ (employment team payload; club reached via team+0x30 per prior docs, not this probe)",
            "EXTERN_TEAM / STARTING_RESERVE_TEAM type nodes as hierarchy probes",
        ],
    },
    {
        "requestedName": ".?AVHUMAN_NON_PLAYER_MANAGER@db@@",
        "status": "no-match-in-this-probe",
        "reason": "Manager/human RTTI types were not printed by the pinned lane probe; active-manager identity is not established by this artifact.",
        "proposedNarrowerNames": [
            ".?AVHUMAN_NON_PLAYER_MANAGER@db@@",
            ".?AVHUMAN_NON_PLAYER@db@@",
            "GameCurrentManager / GCuM selected record RTTI (prior native-entity evidence)",
        ],
    },
    {
        "requestedName": ".?AVPERSON@db@@",
        "status": "no-match-in-this-probe",
        "reason": "PERSON RTTI type was not printed by the pinned lane probe; no person-field offsets are confirmed here.",
        "proposedNarrowerNames": [
            ".?AVPERSON@db@@",
            ".?AVACTUAL_PLAYER@db@@",
            "DATABASE_TABLE<PERSON> vtable 0x4CA5278 (prior doc, not this probe)",
        ],
    },
    {
        "requestedName": ".?AVFULL_CONTRACT@db@@",
        "status": "no-match-in-this-probe",
        "reason": "Contract RTTI type was not printed by the pinned lane probe; contract kind/team/club offsets remain prior-doc evidence only.",
        "proposedNarrowerNames": [
            ".?AVFULL_CONTRACT@db@@",
            ".?AVCONTRACT@db@@",
        ],
    },
    {
        "requestedName": ".?AVFIXTURE@db@@",
        "status": "no-match-in-this-probe",
        "reason": "Fixture RTTI type was not printed by the pinned lane probe.",
        "proposedNarrowerNames": [
            ".?AVFIXTURE@db@@",
            ".?AVMATCH@db@@",
        ],
    },
]


def _hex(value):
    if value is None:
        return None
    return "0x%X" % value


def build_manifest():
    entries = []
    for short_id, rtti_name, rtti_rva, business_relevant in _CONFIRMED_TYPES:
        vt_rva = None
        vt_slots = None
        if rtti_name in _CONFIRMED_VTABLES:
            vt_rva, vt_slots = _CONFIRMED_VTABLES[rtti_name]
        entries.append({
            "id": short_id,
            "rttiName": rtti_name,
            "rttiRva": _hex(rtti_rva),
            "vtableRva": _hex(vt_rva),
            "vtableSlotCount": len(vt_slots) if vt_slots is not None else None,
            "vtableSlots": [_hex(x) for x in vt_slots] if vt_slots is not None else None,
            "businessRelevant": business_relevant,
            "evidenceStatus": "confirmed-type-and-vtable" if vt_rva is not None else "confirmed-type-only",
            "offsets": {},
            "fields": [],
        })
    return {
        "lane": "manager-club",
        "mode": "static-pinned-file",
        "binarySha256": PINNED_BINARY_SHA256,
        "imageBase": _hex(IMAGE_BASE),
        "probeCounts": dict(PROBE_COUNTS),
        "liveRecordsRead": 0,
        "confirmedEntries": entries,
        "noMatch": [dict(x) for x in _NO_MATCH],
        "unresolved": [
            "field offsets for every confirmed type",
            "vtable slot semantics and method identities",
            "vtables not printed in the truncated/private probe output (5 of 10)",
            "CLUB, MANAGER/HUMAN, PERSON, CONTRACT, FIXTURE type nodes",
            "team hierarchy and reserve/youth/national classification",
        ],
        "limitations": [
            "Derived only from the pinned static probe transcript; no process memory was read.",
            "Offsets are intentionally absent; any offset in input is rejected as unverified.",
            "RTTI type presence is not a claim of object availability in a live save.",
            "Slot RVAs are raw code pointers, not validated field offsets.",
        ],
    }


def _is_empty_offsets(value):
    if value is None:
        return True
    if isinstance(value, dict):
        return len(value) == 0
    if isinstance(value, list):
        return len(value) == 0
    if isinstance(value, str):
        return value.strip().lower() in ("", "unknown", "absent", "none", "null")
    return False


def _lookup_entry(name):
    manifest = build_manifest()
    for entry in manifest["confirmedEntries"]:
        if name in (entry["id"], entry["rttiName"]):
            return entry
    for nm in manifest["noMatch"]:
        if name == nm["requestedName"]:
            return nm
    return None


def validate_input(data):
    if isinstance(data, dict) and "entries" in data and isinstance(data["entries"], list):
        items = data["entries"]
    elif isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = [data]
    else:
        raise ValueError("input must be an entry, a list of entries, or an object with 'entries'")

    matched = []
    unmatched = []
    errors = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append({"index": idx, "error": "entry must be an object"})
            continue
        for key in ("offsets", "fields", "fieldOffsets", "offset"):
            if key in item and not _is_empty_offsets(item.get(key)):
                errors.append({"index": idx, "error": "unresolved offsets must be absent/unknown, not invented", "field": key})
        name = item.get("id") or item.get("rttiName") or item.get("name") or item.get("requestedName")
        if not name:
            errors.append({"index": idx, "error": "entry requires id/rttiName/name/requestedName"})
            continue
        confirmed = _lookup_entry(name)
        if confirmed is None:
            unmatched.append({"index": idx, "name": name, "status": "no-match", "proposedNarrowerNames": []})
            continue
        if "status" in confirmed and str(confirmed.get("status", "")).startswith("no-match"):
            unmatched.append({"index": idx, "name": name, "status": confirmed["status"], "proposedNarrowerNames": confirmed.get("proposedNarrowerNames", [])})
            continue
        ok = True
        detail = {"index": idx, "name": name, "status": "match"}
        if "rttiRva" in item and item.get("rttiRva") is not None:
            if str(item.get("rttiRva")).upper() != str(confirmed["rttiRva"]).upper():
                ok = False
                detail["rttiRva"] = "mismatch"
            else:
                detail["rttiRva"] = "match"
        if "vtableRva" in item and item.get("vtableRva") is not None:
            if confirmed["vtableRva"] is None:
                ok = False
                detail["vtableRva"] = "unconfirmed-in-probe"
            elif str(item.get("vtableRva")).upper() != str(confirmed["vtableRva"]).upper():
                ok = False
                detail["vtableRva"] = "mismatch"
            else:
                detail["vtableRva"] = "match"
        if ok:
            matched.append(detail)
        else:
            detail["status"] = "mismatch"
            unmatched.append(detail)

    status = "ok" if not errors and not unmatched else ("error" if errors else "partial")
    return {"status": status, "matched": matched, "unmatched": unmatched, "errors": errors}


def self_test():
    manifest = build_manifest()
    assert len(manifest["confirmedEntries"]) == 19, len(manifest["confirmedEntries"])
    assert sum(1 for e in manifest["confirmedEntries"] if e["vtableRva"] is not None) == 5
    for e in manifest["confirmedEntries"]:
        assert e["offsets"] == {}, e["id"]
        assert e["fields"] == [], e["id"]
    assert manifest["binarySha256"] == PINNED_BINARY_SHA256
    nm_names = [n["requestedName"] for n in manifest["noMatch"]]
    assert ".?AVCLUB@db@@" in nm_names
    assert ".?AVHUMAN_NON_PLAYER_MANAGER@db@@" in nm_names
    res = validate_input({"entries": [{"id": "TEAM", "rttiRva": "0x56A2A60", "vtableRva": "0x4CE1108"}]})
    assert res["status"] == "ok", res
    assert len(res["matched"]) == 1
    res2 = validate_input({"entries": [{"id": "TEAM", "offsets": {"uid": 12}}]})
    assert res2["status"] == "error", res2
    assert any("invented" in e["error"] for e in res2["errors"])
    res3 = validate_input({"entries": [{"rttiName": ".?AVNOPE@db@@"}]})
    assert res3["status"] == "partial", res3
    assert len(res3["unmatched"]) == 1
    json.dumps(manifest)
    print("PASS: entry_manager_club synthetic checks (5 cases)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.validate is not None:
        raw = args.validate.read_text(encoding="utf-8-sig")
        data = json.loads(raw)
        result = validate_input(data)
        text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output is not None:
            args.output.write_text(text, encoding="utf-8")
            print("Wrote validation result to %s" % args.output)
        else:
            print(text, end="")
        return

    manifest = build_manifest()
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
        print("Wrote manifest to %s" % args.output)
    else:
        print(text, end="")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as e:
        print(json.dumps({"status": "error", "reason": str(e)}), file=sys.stderr)
        sys.exit(3)
