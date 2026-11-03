"""Machine-readable manifest and validator for confirmed messages-news native entries.

This is an original offline research scaffold. It records only RTTI type, vtable,
and RIP-candidate evidence from the pinned static probe. It does not read a
process, invoke a game function, or invent unresolved offsets. Unknown entry
roles, slot meanings, field offsets, and constructor semantics are deliberately
absent rather than estimated.
"""
import argparse
import json
from pathlib import Path

PINNED_BINARY_HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = "0x180000000"
REPO = Path(__file__).resolve().parents[2]

CONFIRMED_TYPES = [
    {"rva": "0x5685680", "name": ".?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@"},
    {"rva": "0x56856C0", "name": ".?AV?$NEWS_ITEM_UI_SPECIFIC@VWELCOME_TO_THE_CLUB_NEWS@@@news_ui@@"},
    {"rva": "0x56C0AC0", "name": ".?AVWELCOME_TO_THE_CLUB_NEWS@@"},
]

CONFIRMED_VTABLES = [
    {
        "rva": "0x4B234F8",
        "typeName": ".?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@",
        "slots": [
            "0x4580F0", "0x458100", "0x458110", "0x458120", "0x458150",
            "0x458170", "0x4581A0", "0x4581D0", "0x4581F0", "0x458200",
            "0x458210", "0x458230",
        ],
    },
    {
        "rva": "0x4D86CF8",
        "typeName": ".?AVWELCOME_TO_THE_CLUB_NEWS@@",
        "slots": [
            "0x179A080", "0x24D9C0", "0x24D9D0", "0x24D9E0", "0x24D9F0",
            "0x24DA00", "0x24DA10", "0x24DA20", "0x24DA30", "0x24DA40",
            "0x24DA50", "0x24DA60",
        ],
    },
]

CONFIRMED_RIP_CANDIDATES = [
    {
        "displacement": "0x4594B1",
        "function": "0x459460",
        "target": "0x4B234F8",
        "typeName": ".?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@",
    },
    {
        "displacement": "0x175E275",
        "function": "0x1750CC0",
        "target": "0x4D86CF8",
        "typeName": ".?AVWELCOME_TO_THE_CLUB_NEWS@@",
    },
    {
        "displacement": "0x1C8BAE1",
        "function": "0x1C89D70",
        "target": "0x4D86CF8",
        "typeName": ".?AVWELCOME_TO_THE_CLUB_NEWS@@",
    },
]

ALLOWED_TOP_KEYS = {
    "status", "lane", "probeMode", "binarySha256", "imageBase",
    "liveRecordsRead", "types", "vtables", "ripCandidates",
    "confirmedEntryHypothesis", "unresolved", "limitations",
}

ALLOWED_TYPE_KEYS = {"rva", "name"}
ALLOWED_VTABLE_KEYS = {"rva", "typeName", "slots"}
ALLOWED_RIP_KEYS = {"displacement", "function", "target", "typeName"}
ALLOWED_HYPOTHESIS_KEYS = {
    "businessObjectType", "uiItemType", "businessEntryCandidateFunctions",
    "uiEntryCandidateFunction", "roleConfirmed",
}


def build_manifest():
    return {
        "status": "static-entry-manifest",
        "lane": "messages-news",
        "probeMode": "static-pinned-file",
        "binarySha256": PINNED_BINARY_HASH,
        "imageBase": IMAGE_BASE,
        "liveRecordsRead": 0,
        "types": [dict(item) for item in CONFIRMED_TYPES],
        "vtables": [dict(item) for item in CONFIRMED_VTABLES],
        "ripCandidates": [dict(item) for item in CONFIRMED_RIP_CANDIDATES],
        "confirmedEntryHypothesis": {
            "businessObjectType": ".?AVWELCOME_TO_THE_CLUB_NEWS@@",
            "uiItemType": ".?AVWELCOME_TO_THE_CLUB_NEWS_ITEM_UI@@",
            "businessEntryCandidateFunctions": ["0x1750CC0", "0x1C89D70"],
            "uiEntryCandidateFunction": "0x459460",
            "roleConfirmed": False,
        },
        "unresolved": [
            "constructor/factory/registration role of each RIP candidate",
            "vtable slot semantics",
            "field offsets and object layout",
            "constructor ABI, size, lifetime, and ownership",
            "relationship between business, UI-specific, and UI item types",
        ],
        "limitations": [
            "Static PE/RTTI evidence only; no process memory was read.",
            "RIP candidates are references only, not confirmed constructors or entry points.",
            "No field offsets, vtable slot meanings, or ABI details are claimed.",
            "Not an SDK, adapter, game reader, or live capability.",
        ],
    }


def _same_list_of_dicts(actual, expected, keys):
    if not isinstance(actual, list) or len(actual) != len(expected):
        return False
    actual_norm = [tuple(sorted((k, v) for k, v in item.items() if k in keys)) for item in actual if isinstance(item, dict)]
    expected_norm = [tuple(sorted((k, v) for k, v in item.items() if k in keys)) for item in expected]
    return sorted(actual_norm) == sorted(expected_norm)


def validate_manifest(document):
    if not isinstance(document, dict):
        raise ValueError("manifest must be a JSON object")
    if set(document) - ALLOWED_TOP_KEYS:
        raise ValueError("manifest contains unsupported or invented top-level fields")
    if document.get("lane") != "messages-news":
        raise ValueError("unexpected lane")
    if document.get("binarySha256") != PINNED_BINARY_HASH:
        raise ValueError("unsupported binary profile")
    if str(document.get("imageBase", "")).lower() != IMAGE_BASE.lower():
        raise ValueError("unsupported image base")
    if document.get("liveRecordsRead") != 0:
        raise ValueError("liveRecordsRead must be 0 for this static manifest")
    if not _same_list_of_dicts(document.get("types"), CONFIRMED_TYPES, ALLOWED_TYPE_KEYS):
        raise ValueError("types must exactly match confirmed RTTI evidence")
    if not _same_list_of_dicts(document.get("vtables"), CONFIRMED_VTABLES, ALLOWED_VTABLE_KEYS):
        raise ValueError("vtables must exactly match confirmed vtable evidence")
    if not _same_list_of_dicts(document.get("ripCandidates"), CONFIRMED_RIP_CANDIDATES, ALLOWED_RIP_KEYS):
        raise ValueError("rip candidates must exactly match confirmed RIP evidence")
    # Per-entry key checks.
    for item in document.get("types", []):
        if set(item) != ALLOWED_TYPE_KEYS:
            raise ValueError("type entry contains unsupported fields")
    for item in document.get("vtables", []):
        if set(item) != ALLOWED_VTABLE_KEYS:
            raise ValueError("vtable entry contains unsupported fields")
        if not isinstance(item.get("slots"), list) or any(not isinstance(x, str) for x in item["slots"]):
            raise ValueError("vtable slots must be strings")
    for item in document.get("ripCandidates", []):
        if set(item) != ALLOWED_RIP_KEYS:
            raise ValueError("rip candidate contains unsupported fields")
    hypothesis = document.get("confirmedEntryHypothesis")
    if hypothesis is not None:
        if not isinstance(hypothesis, dict) or set(hypothesis) != ALLOWED_HYPOTHESIS_KEYS:
            raise ValueError("invalid confirmedEntryHypothesis")
        if hypothesis.get("roleConfirmed") is not False:
            raise ValueError("entry role is not confirmed")
    # Slot exactness.
    for actual, expected in zip(
        sorted(document.get("vtables", []), key=lambda x: x.get("rva", "")),
        sorted(CONFIRMED_VTABLES, key=lambda x: x["rva"]),
    ):
        if actual.get("slots") != expected["slots"]:
            raise ValueError("vtable slots must exactly match confirmed evidence")
    return True


# Backwards/alternate names used by callers or tests.
validate = validate_manifest
manifest = build_manifest


def read_json(path):
    raw = path.read_bytes()
    if len(raw) > 1024 * 1024:
        raise ValueError("JSON input size limit")
    return json.loads(raw.decode("utf-8-sig"))


def self_test():
    built = build_manifest()
    validate_manifest(built)
    text = json.dumps(built, ensure_ascii=False)
    reparsed = json.loads(text)
    validate_manifest(reparsed)
    assert reparsed["liveRecordsRead"] == 0
    assert len(reparsed["types"]) == 3
    assert len(reparsed["vtables"]) == 2
    assert len(reparsed["ripCandidates"]) == 3
    assert reparsed["confirmedEntryHypothesis"]["roleConfirmed"] is False
    # Mutated type RVA must fail.
    bad = json.loads(text)
    bad["types"][0]["rva"] = "0x56C0AC0"
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("mutated type accepted")
    # Invented offset field must fail.
    bad = json.loads(text)
    bad["types"][0]["constructorRva"] = "0x1234"
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invented offset accepted")
    # Missing vtable slot must fail.
    bad = json.loads(text)
    bad["vtables"][0]["slots"] = bad["vtables"][0]["slots"][:-1]
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete vtable accepted")
    # Role claim must fail.
    bad = json.loads(text)
    bad["confirmedEntryHypothesis"]["roleConfirmed"] = True
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unconfirmed role accepted")
    print("PASS: confirmed type/vtable/RIP manifest, round trip, and rejection of invented or incomplete evidence")


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
        document = read_json(args.validate)
        validate_manifest(document)
        print(f"VALID: {args.validate}")
        return
    built = build_manifest()
    text = json.dumps(built, ensure_ascii=False, indent=2)
    if args.output is not None:
        output = args.output.resolve()
        if output.is_relative_to(REPO):
            parser.error("private output must remain outside repository")
        output.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote native entry manifest: {output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
