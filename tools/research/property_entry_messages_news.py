"""Machine-readable manifest and validator for messages-news property-to-entry candidates.

This is an original offline research scaffold. It records only the property
names, literal indices, and slot RVAs returned by the reviewed fixed-file static
probe for the pinned binary. It does not read a process, invoke a game
function, invent offsets, or fabricate registrations. Native keys, entry
offsets, registration functions, and constructor roles are deliberately null or
absent until proven.
"""
import argparse
import json
from pathlib import Path

PINNED_BINARY_HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
IMAGE_BASE = "0x180000000"
REPO = Path(__file__).resolve().parents[2]

CONFIRMED_PROPERTY_CANDIDATES = [
    {"name": "HumanCanMarkSelectedPortalMessagesAsUnread", "literalIndex": 10136, "slotRvas": ["0x32dc628"], "semantics": "unverified-property-name"},
    {"name": "HumanPortalNewestUnreadMessage", "literalIndex": 10204, "slotRvas": ["0x32e0290"], "semantics": "unverified-property-name"},
    {"name": "HumanPortalNewestUnreadMessageIndex", "literalIndex": 10205, "slotRvas": ["0x32e0370"], "semantics": "unverified-property-name"},
    {"name": "HumanPortalNextUnreadMessage", "literalIndex": 10211, "slotRvas": ["0x32e08d0"], "semantics": "unverified-property-name"},
    {"name": "HumanPortalOldestUnreadMessage", "literalIndex": 10212, "slotRvas": ["0x32e09b8"], "semantics": "unverified-property-name"},
    {"name": "HumanPortalOldestUnreadMessagesIndex", "literalIndex": 10213, "slotRvas": ["0x32e0aa0"], "semantics": "unverified-property-name"},
    {"name": "HumanPortalPreviousUnreadMessage", "literalIndex": 10217, "slotRvas": ["0x32e0e10"], "semantics": "unverified-property-name"},
    {"name": "HumanPortalUnreadMessages", "literalIndex": 10219, "slotRvas": ["0x32e0fe8"], "semantics": "unverified-property-name"},
    {"name": "NewsBodyString", "literalIndex": 13657, "slotRvas": ["0x3309360"], "semantics": "unverified-property-name"},
    {"name": "NumberUnreadMessages", "literalIndex": 14030, "slotRvas": ["0x331e688"], "semantics": "unverified-property-name"},
    {"name": "ShortlistScoutingSendReportsToInbox", "literalIndex": 17503, "slotRvas": ["0x32acfd0"], "semantics": "unverified-property-name"},
]

# Name-surface classification only. The probe supplies names, not runtime referents;
# coordinator evidence shows names can resolve a different context than their surface
# (for example NextFixture resolves TEAM_BASE context, not fixtures).
PROPERTY_SURFACE = {
    "HumanCanMarkSelectedPortalMessagesAsUnread": ("ui-news-operations", "ui-operation"),
    "HumanPortalNewestUnreadMessage": ("ui-news-operations", "ui-portal"),
    "HumanPortalNewestUnreadMessageIndex": ("ui-news-operations", "ui-portal"),
    "HumanPortalNextUnreadMessage": ("ui-news-operations", "ui-portal"),
    "HumanPortalOldestUnreadMessage": ("ui-news-operations", "ui-portal"),
    "HumanPortalOldestUnreadMessagesIndex": ("ui-news-operations", "ui-portal"),
    "HumanPortalPreviousUnreadMessage": ("ui-news-operations", "ui-portal"),
    "HumanPortalUnreadMessages": ("ui-news-operations", "ui-portal"),
    "NewsBodyString": ("business-field", "business-field"),
    "NumberUnreadMessages": ("ui-news-operations", "ui-count"),
    "ShortlistScoutingSendReportsToInbox": ("ui-news-operations", "scouting-operation"),
}

PROPERTY_RANK = {
    "NewsBodyString": 1,
    "NumberUnreadMessages": 2,
    "HumanPortalUnreadMessages": 3,
    "HumanPortalNewestUnreadMessage": 4,
    "HumanPortalOldestUnreadMessage": 5,
    "HumanPortalNextUnreadMessage": 6,
    "HumanPortalPreviousUnreadMessage": 7,
    "HumanPortalNewestUnreadMessageIndex": 8,
    "HumanPortalOldestUnreadMessagesIndex": 9,
    "HumanCanMarkSelectedPortalMessagesAsUnread": 10,
    "ShortlistScoutingSendReportsToInbox": 11,
}

INSPECT_REASONS = {
    "NewsBodyString": "Known MSG-02 business field with a documented body route; inspect its slot RVA for entry registration.",
    "NumberUnreadMessages": "Count candidate for MSG-01 read/unread state; inspect before navigation entries.",
    "HumanPortalUnreadMessages": "Candidate collection of unread entries; inspect registration and contained entry type.",
    "HumanPortalNewestUnreadMessage": "Portal navigation entry; inspect after collection/count.",
    "HumanPortalOldestUnreadMessage": "Portal navigation entry; inspect after collection/count.",
    "HumanPortalNextUnreadMessage": "Portal navigation entry; inspect after collection/count.",
    "HumanPortalPreviousUnreadMessage": "Portal navigation entry; inspect after collection/count.",
    "HumanPortalNewestUnreadMessageIndex": "Index companion to a navigation entry; inspect with its entry.",
    "HumanPortalOldestUnreadMessagesIndex": "Index companion to a navigation entry; inspect with its entry.",
    "HumanCanMarkSelectedPortalMessagesAsUnread": "Mutation-style operation; inspect registration only, never invoke.",
    "ShortlistScoutingSendReportsToInbox": "Scouting-to-inbox operation; lowest relevance to messages-news business entries.",
}

ALLOWED_TOP_KEYS = {
    "status", "lane", "probeMode", "binarySha256", "imageBase",
    "liveRecordsRead", "propertyCandidates", "propertyEntries",
    "nextRegistrationsToInspect", "unresolved", "limitations",
}

ALLOWED_PROPERTY_CANDIDATE_KEYS = {"name", "literalIndex", "slotRvas", "semantics"}

ALLOWED_PROPERTY_ENTRY_KEYS = {
    "propertyName", "literalIndex", "slotRvas", "surfaceGroup",
    "nameSurfaceClass", "nativeKey", "entryOffset",
    "registrationFunctionRva", "status", "rank", "nextInspectReason",
}

ALLOWED_SURFACE_GROUPS = {"ui-news-operations", "business-field"}
ALLOWED_SURFACE_CLASSES = {
    "ui-portal", "ui-operation", "ui-count", "business-field", "scouting-operation",
}


def _entry_for(candidate):
    name = candidate["name"]
    group, cls = PROPERTY_SURFACE[name]
    return {
        "propertyName": name,
        "literalIndex": candidate["literalIndex"],
        "slotRvas": list(candidate["slotRvas"]),
        "surfaceGroup": group,
        "nameSurfaceClass": cls,
        "nativeKey": None,
        "entryOffset": None,
        "registrationFunctionRva": None,
        "status": "candidate-unproven",
        "rank": PROPERTY_RANK[name],
        "nextInspectReason": INSPECT_REASONS[name],
    }


def build_manifest():
    entries = sorted((_entry_for(c) for c in CONFIRMED_PROPERTY_CANDIDATES), key=lambda x: x["rank"])
    return {
        "status": "static-property-entry-manifest",
        "lane": "messages-news",
        "probeMode": "static-pinned-file",
        "binarySha256": PINNED_BINARY_HASH,
        "imageBase": IMAGE_BASE,
        "liveRecordsRead": 0,
        "propertyCandidates": [dict(item) for item in CONFIRMED_PROPERTY_CANDIDATES],
        "propertyEntries": entries,
        "nextRegistrationsToInspect": [e["propertyName"] for e in entries],
        "unresolved": [
            "whether each property name resolves to a UI/news/operations or business entry at runtime",
            "native key, entry offset, and registration function for each property",
            "vtable slot meaning for each slot RVA",
            "field offsets and object layout for any constructed entry",
            "whether portal unread properties are a collection, index, or view",
            "whether NewsBodyString registration is the same route as MSG-02 body",
            "whether ShortlistScoutingSendReportsToInbox is message-related or only an inbox sink",
        ],
        "limitations": [
            "Static PE/metadata property-name evidence only; no process memory was read.",
            "Property names are unverified surface names, not proven runtime referents.",
            "Slot RVAs are module-relative references only, not confirmed entry points.",
            "Native keys, offsets, and registration functions remain null until proven.",
            "No live read, UI action, game function call, write, scan, or state change is performed.",
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
    if not _same_list_of_dicts(document.get("propertyCandidates"), CONFIRMED_PROPERTY_CANDIDATES, ALLOWED_PROPERTY_CANDIDATE_KEYS):
        raise ValueError("property candidates must exactly match probe evidence")
    for item in document.get("propertyCandidates", []):
        if set(item) != ALLOWED_PROPERTY_CANDIDATE_KEYS:
            raise ValueError("property candidate contains unsupported fields")
    entries = document.get("propertyEntries")
    if not isinstance(entries, list) or len(entries) != len(CONFIRMED_PROPERTY_CANDIDATES):
        raise ValueError("propertyEntries must contain one entry per probe candidate")
    entry_keys_ok = all(isinstance(x, dict) and set(x) == ALLOWED_PROPERTY_ENTRY_KEYS for x in entries)
    if not entry_keys_ok:
        raise ValueError("property entry contains unsupported fields")
    # Candidate correspondence.
    by_name = {e.get("propertyName"): e for e in entries}
    if set(by_name) != {c["name"] for c in CONFIRMED_PROPERTY_CANDIDATES}:
        raise ValueError("propertyEntries names must match probe candidates")
    ranks = []
    for entry in entries:
        cand = next(c for c in CONFIRMED_PROPERTY_CANDIDATES if c["name"] == entry["propertyName"])
        if entry["literalIndex"] != cand["literalIndex"]:
            raise ValueError("property entry literalIndex must match probe evidence")
        if entry["slotRvas"] != cand["slotRvas"]:
            raise ValueError("property entry slotRvas must match probe evidence")
        if entry["surfaceGroup"] not in ALLOWED_SURFACE_GROUPS:
            raise ValueError("invalid surfaceGroup")
        if entry["nameSurfaceClass"] not in ALLOWED_SURFACE_CLASSES:
            raise ValueError("invalid nameSurfaceClass")
        if entry["nativeKey"] is not None or entry["entryOffset"] is not None or entry["registrationFunctionRva"] is not None:
            raise ValueError("native keys/offsets/functions must remain null until proven")
        if entry["status"] != "candidate-unproven":
            raise ValueError("property entry status must remain candidate-unproven")
        if not isinstance(entry["rank"], int) or isinstance(entry["rank"], bool):
            raise ValueError("rank must be an integer")
        if not isinstance(entry["nextInspectReason"], str) or not entry["nextInspectReason"]:
            raise ValueError("nextInspectReason must be a non-empty string")
        ranks.append(entry["rank"])
    if sorted(ranks) != list(range(1, len(entries) + 1)):
        raise ValueError("ranks must be a unique 1..N ordering")
    # nextRegistrationsToInspect must be the rank order.
    expected_order = [e["propertyName"] for e in sorted(entries, key=lambda x: x["rank"])]
    actual_order = document.get("nextRegistrationsToInspect")
    if not isinstance(actual_order, list) or any(not isinstance(x, str) for x in actual_order):
        raise ValueError("nextRegistrationsToInspect must be a list of strings")
    if actual_order != expected_order:
        raise ValueError("nextRegistrationsToInspect must follow rank order")
    if len(set(actual_order)) != len(actual_order):
        raise ValueError("nextRegistrationsToInspect must be unique")
    return True


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
    assert len(reparsed["propertyCandidates"]) == 11
    assert len(reparsed["propertyEntries"]) == 11
    assert reparsed["nextRegistrationsToInspect"][0] == "NewsBodyString"
    # Mutated native key must fail.
    bad = json.loads(text)
    bad["propertyEntries"][0]["nativeKey"] = "0x1234"
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invented native key accepted")
    # Invented function must fail.
    bad = json.loads(text)
    bad["propertyEntries"][0]["registrationFunctionRva"] = "0x459460"
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invented function accepted")
    # Extra top-level field must fail.
    bad = json.loads(text)
    bad["invented"] = True
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invented top-level field accepted")
    # Missing candidate must fail.
    bad = json.loads(text)
    bad["propertyCandidates"] = bad["propertyCandidates"][:-1]
    bad["propertyEntries"] = bad["propertyEntries"][:-1]
    bad["nextRegistrationsToInspect"] = bad["nextRegistrationsToInspect"][:-1]
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("missing candidate accepted")
    # Rank claim must fail.
    bad = json.loads(text)
    bad["propertyEntries"][0]["rank"] = 99
    try:
        validate_manifest(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid rank accepted")
    print("PASS: property-to-entry manifest, round trip, and rejection of invented or incomplete evidence")


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
        print(f"Wrote property entry manifest: {output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
