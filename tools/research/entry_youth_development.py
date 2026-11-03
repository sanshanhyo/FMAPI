#!/usr/bin/env python3
"""Machine-readable manifest and validator for the youth-development native entry.

Offline static evidence only. NOT a live reader: it performs no process, game,
UI, network, credential, or raw-sample access. Only the RTTI type/vtable
evidence confirmed by the authorized static probe is included. Field offsets,
slot semantics, and instance layouts are unknown and are intentionally absent.
"""

import argparse
import json
from pathlib import Path

LANE = "youth-development"
TYPE_NAME = ".?AVREGENERATION_YOUTH_INTAKE_NEWS@@"
TYPE_RVA = 0x56BF770
VTABLE_RVA = 0x4D7A478
IMAGE_BASE = 0x180000000
SHA256 = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
SLOTS = [
    0x1792CB0,
    0x24D9C0,
    0x24D9D0,
    0x24D9E0,
    0x24D9F0,
    0x24DA00,
    0x24DA10,
    0x24DA20,
    0x24DA30,
    0x24DA40,
    0x24DA50,
    0x24DA60,
]
RIP_CANDIDATES = [
    {
        "displacementRva": 0x1761423,
        "functionRva": 0x1750CC0,
        "targetVtableRva": VTABLE_RVA,
    },
    {
        "displacementRva": 0x2FE2534,
        "functionRva": 0x2FE2500,
        "targetVtableRva": VTABLE_RVA,
    },
]
PROPOSED_NARROWER_NAMES = [
    "REGENERATION_YOUTH_INTAKE_NEWS",
    "REGENERATION_YOUTH_INTAKE",
    "YOUTH_INTAKE_NEWS",
    "YOUTH_INTAKE",
]


def _hex(value):
    return "0x{:X}".format(value)


def build_manifest():
    return {
        "schema": "fmapi.native-entry.v1",
        "lane": LANE,
        "status": "static-confirmed-type-only",
        "probe": {
            "mode": "static-pinned-file",
            "types": 1,
            "vtables": 1,
            "liveRecordsRead": 0,
            "outputTruncated": False,
        },
        "binary": {
            "sha256": SHA256,
            "imageBase": _hex(IMAGE_BASE),
        },
        "typeMatch": {
            "matched": True,
            "rttiName": TYPE_NAME,
            "typeRva": _hex(TYPE_RVA),
            "proposedNarrowerNames": [],
        },
        "entry": {
            "kind": "business-object-candidate",
            "rttiName": TYPE_NAME,
            "typeRva": _hex(TYPE_RVA),
            "vtableRva": _hex(VTABLE_RVA),
            "vtableAbsolute": _hex(IMAGE_BASE + VTABLE_RVA),
            "reportedSlotCount": len(SLOTS),
            "slots": [_hex(slot) for slot in SLOTS],
            "slotSemantics": "unknown",
            "offsets": {},
            "fields": [],
        },
        "ripCandidates": [
            {
                "displacementRva": _hex(item["displacementRva"]),
                "functionRva": _hex(item["functionRva"]),
                "targetVtableRva": _hex(item["targetVtableRva"]),
            }
            for item in RIP_CANDIDATES
        ],
        "hypothesis": {
            "status": "candidate-only",
            "text": (
                "The verified entry is an RTTI type named "
                ".?AVREGENERATION_YOUTH_INTAKE_NEWS@@ with vtable RVA "
                "0x4D7A478. Its name suggests a news/notification business "
                "object for regeneration youth intake, but no field offsets, "
                "slot semantics, constructor, owner, collection, or instance "
                "layout is confirmed."
            ),
        },
        "confirmed": [
            "RTTI type name .?AVREGENERATION_YOUTH_INTAKE_NEWS@@ exists in the pinned binary",
            "Type descriptor RVA 0x56BF770",
            "Vtable RVA 0x4D7A478",
            "Twelve vtable slot RVAs reported by the static scan",
            "Two RIP-relative references target vtable RVA 0x4D7A478",
        ],
        "unresolved": [
            "all field offsets",
            "vtable slot semantics",
            "constructor and factory confirmation",
            "owning collection or owner object",
            "instance layout and lifetime",
            "club, team, person, or manager linkage",
            "news content and localization linkage",
            "whether the type is instantiated in an ordinary loaded save",
            "whether the reported twelve slots are the complete vtable",
        ],
        "nextBoundedRead": {
            "static": [
                "Disassemble functions at RVA 0x1750CC0 and 0x2FE2500 with bounded length",
                "Confirm instruction boundaries and vtable stores before any live read",
            ],
            "live": [
                "Coordinator-approved process probe only after static confirmation",
                "Read only RTTI type name, vtable RVA, and a small raw prefix from few instances",
            ],
            "budget": "aggregate read budget <= 64 KiB; process recheck before and after; no writes",
        },
        "limitations": [
            "Static RTTI/vtable evidence only; no process or live record was read",
            "RIP candidates are unconfirmed until instruction-boundary disassembly",
            "No field offsets or slot semantics are included",
            "Not an SDK, adapter, or live reader",
        ],
    }


def match_type(fragment):
    normalized = str(fragment).strip().upper().replace(".?AV", "").replace("@@", "")
    if normalized == "REGENERATION_YOUTH_INTAKE_NEWS" or str(fragment).strip() == TYPE_NAME:
        return {
            "matched": True,
            "matchedName": TYPE_NAME,
            "proposedNarrowerNames": [],
        }
    proposals = [
        name
        for name in PROPOSED_NARROWER_NAMES
        if str(fragment).upper() in name or name in str(fragment).upper()
    ]
    if not proposals:
        proposals = list(PROPOSED_NARROWER_NAMES)
    return {
        "matched": False,
        "matchedName": None,
        "proposedNarrowerNames": proposals,
    }


def validate_manifest(manifest):
    errors = []
    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]

    expected = build_manifest()
    for key in ("lane", "binary", "typeMatch", "entry", "ripCandidates"):
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

    type_match = manifest.get("typeMatch")
    if not isinstance(type_match, dict):
        errors.append("typeMatch must be an object")
    else:
        if type_match.get("matched") is not True:
            errors.append("typeMatch.matched must be true for the confirmed entry")
        if type_match.get("rttiName") != TYPE_NAME:
            errors.append("typeMatch.rttiName must be the confirmed RTTI name")
        if type_match.get("typeRva") != _hex(TYPE_RVA):
            errors.append("typeMatch.typeRva must be the confirmed type RVA")

    entry = manifest.get("entry")
    if not isinstance(entry, dict):
        errors.append("entry must be an object")
    else:
        if entry.get("rttiName") != TYPE_NAME:
            errors.append("entry.rttiName must be the confirmed RTTI name")
        if entry.get("typeRva") != _hex(TYPE_RVA):
            errors.append("entry.typeRva must be the confirmed type RVA")
        if entry.get("vtableRva") != _hex(VTABLE_RVA):
            errors.append("entry.vtableRva must be the confirmed vtable RVA")
        if entry.get("slots") != [_hex(slot) for slot in SLOTS]:
            errors.append("entry.slots must equal the confirmed slot RVAs")
        if entry.get("offsets") != {}:
            errors.append("entry.offsets must be empty; unresolved offsets cannot be invented")
        if entry.get("fields") not in (None, []):
            errors.append("entry.fields must be empty or absent; unresolved fields cannot be invented")
        if entry.get("slotSemantics") not in (None, "unknown"):
            errors.append("entry.slotSemantics must remain unknown")

    if manifest.get("ripCandidates") != [
        {
            "displacementRva": _hex(item["displacementRva"]),
            "functionRva": _hex(item["functionRva"]),
            "targetVtableRva": _hex(item["targetVtableRva"]),
        }
        for item in RIP_CANDIDATES
    ]:
        errors.append("ripCandidates must equal the confirmed candidate set")

    # Reject obvious invented field offsets anywhere in the manifest.
    def contains_invented_offset(value):
        if isinstance(value, str):
            return "+0x" in value.replace(" ", "")
        if isinstance(value, dict):
            return any(contains_invented_offset(item) for item in value.values())
        if isinstance(value, list):
            return any(contains_invented_offset(item) for item in value)
        return False

    if contains_invented_offset(manifest):
        errors.append("manifest contains an invented field-offset reference")

    return errors


def self_test():
    manifest = build_manifest()
    assert manifest["lane"] == LANE
    assert manifest["entry"]["rttiName"] == TYPE_NAME
    assert manifest["entry"]["vtableRva"] == "0x4D7A478"
    assert manifest["entry"]["reportedSlotCount"] == 12
    assert len(manifest["entry"]["slots"]) == 12
    assert manifest["entry"]["offsets"] == {}
    assert manifest["entry"]["fields"] == []
    assert manifest["entry"]["slotSemantics"] == "unknown"
    assert len(manifest["ripCandidates"]) == 2
    assert validate_manifest(manifest) == []

    assert validate_manifest({}) != []
    bad = json.loads(json.dumps(manifest))
    bad["entry"]["offsets"] = {"player": "0x10"}
    assert validate_manifest(bad) != []

    match = match_type(TYPE_NAME)
    assert match["matched"] is True
    assert match["proposedNarrowerNames"] == []

    no_match = match_type("UNKNOWN_TYPE")
    assert no_match["matched"] is False
    assert no_match["matchedName"] is None
    assert no_match["proposedNarrowerNames"]

    print("PASS: youth-development native entry manifest synthetic checks")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--match-type")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.match_type is not None:
        rendered = json.dumps(match_type(args.match_type), ensure_ascii=False, indent=2)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
            print("Wrote type match result to {}".format(args.output))
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
        print("Wrote native entry manifest to {}".format(args.output))
    else:
        print(rendered)


if __name__ == "__main__":
    main()
