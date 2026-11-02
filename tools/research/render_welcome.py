"""Render only proven welcome-token branches from a private bounded probe capture.
Unknown tokens remain explicit and prevent a complete text result.
"""
import argparse
import json
import re
from pathlib import Path

HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
TOKEN = re.compile(r"\[%[^\]]*\]")


def render(template, resolve):
    if not isinstance(template, str) or len(template.encode("utf-8")) > 8192:
        raise ValueError("template size/type limit")
    pieces, coverage, missing = [], [], []
    cursor = 0
    for match in TOKEN.finditer(template):
        if len(coverage) >= 64:
            raise ValueError("token count limit")
        literal = template[cursor:match.start()]
        if "[%" in literal:
            raise ValueError("malformed token")
        pieces.append(literal)
        token = match.group()
        value, evidence = resolve(token)
        resolved = value is not None
        coverage.append({"token": token, "resolved": resolved, "evidence": evidence})
        if resolved:
            if not isinstance(value, str) or len(value.encode("utf-8")) > 1024:
                raise ValueError("substitution bounds")
            pieces.append(value)  # Substituted text is opaque, never parsed again.
        else:
            missing.append(token)
        cursor = match.end()
    tail = template[cursor:]
    if "[%" in tail:
        raise ValueError("malformed trailing token")
    pieces.append(tail)
    return {"status": "complete" if not missing else "partial", "rawTemplate": template,
            "formattedText": "".join(pieces) if not missing else None,
            "resolvedCount": sum(item["resolved"] for item in coverage),
            "tokenCount": len(coverage), "coverage": coverage, "missingTokens": missing}


def resolve_for(capture):
    result = capture["result"]
    if result.get("binarySha256") != HASH or result.get("scope") != "single-human-manager-associated-messages":
        raise ValueError("unsupported evidence profile")
    if sum(m.get("nativeType") == ".?AVWELCOME_TO_THE_CLUB_NEWS@@" for m in result["messages"]) != 1:
        raise ValueError("requires exactly one returned welcome entry")
    relations = result["welcomeRelationCandidates"]
    names = relations.get("nameOverridePresence", {})
    alternate = relations.get("clubAlternateNameRecords")
    short = relations.get("clubShortNameCandidate")
    proven_short = (relations.get("teamType") == ".?AVTEAM@db@@" and
                    relations.get("clubType") == ".?AVCLUB@db@@" and
                    relations.get("teamNameKindCandidate") == 0 and
                    relations.get("teamSpecialReplacementCase") is False and
                    relations.get("teamShortOverrideCandidate") in (None, "") and
                    names.get("team") is False and names.get("club") is False and
                    isinstance(alternate, list) and len(alternate) == 0 and
                    isinstance(short, str) and len(short) > 0)
    def resolve(token):
        if token in ("[%male#1-hidden]", "[%male#2-hidden]"):
            return "", "PERSON_HIDDEN_FORMATTER output RVA 0xA322C0 returns without appending"
        if token == "[%team#1-short]" and proven_short:
            return short, "Observed kind-zero short-mode branch: no overrides, special replacement or alternate names; CLUB getter +0x108 returns +0xC8"
        if token == "[%male#1-first]":
            return None, "Owner registry mapping verified separately; full first-name/common-name/locale formatting branch and supplied context still unproven"
        return None, "Unsupported token or unproven branch preconditions"
    return resolve


def read_json(path):
    raw = path.read_bytes()
    if len(raw) > 1024 * 1024:
        raise ValueError("JSON input limit")
    return json.loads(raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"))


def self_test():
    known = lambda token: ({"[%team#1-short]": "Synthetic [%male#2-hidden]", "[%male#1-hidden]": ""}.get(token), "synthetic")
    complete = render("Welcome [%team#1-short][%male#1-hidden]", known)
    assert complete["status"] == "complete" and complete["formattedText"] == "Welcome Synthetic [%male#2-hidden]"
    unknown = render("Unknown [%male#1-first]", known)
    assert unknown["formattedText"] is None and unknown["missingTokens"] == ["[%male#1-first]"]
    for invalid in ("[%broken", "x" * 8193):
        try:
            render(invalid, known)
        except ValueError:
            continue
        raise AssertionError("invalid template accepted")
    relations = {"teamType": ".?AVTEAM@db@@", "clubType": ".?AVCLUB@db@@",
                 "teamNameKindCandidate": 0, "teamSpecialReplacementCase": False,
                 "teamShortOverrideCandidate": None, "nameOverridePresence": {"team": False, "club": False},
                 "clubAlternateNameRecords": [], "clubShortNameCandidate": "Synthetic Club"}
    capture = {"result": {"binarySha256": HASH, "scope": "single-human-manager-associated-messages",
                          "messages": [{"nativeType": ".?AVWELCOME_TO_THE_CLUB_NEWS@@"}],
                          "welcomeRelationCandidates": relations}}
    assert render("[%team#1-short][%male#1-hidden]", resolve_for(capture))["formattedText"] == "Synthetic Club"
    relations["teamSpecialReplacementCase"] = True
    assert render("[%team#1-short]", resolve_for(capture))["formattedText"] is None
    relations["teamSpecialReplacementCase"] = False
    relations["clubAlternateNameRecords"] = [{"kind": 0x19, "language": 1}]
    assert render("[%team#1-short]", resolve_for(capture))["formattedText"] is None
    print("PASS: opaque substitutions, hidden zero output, unknown fail-closed, input bounds and branch guards")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--templates", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.capture or not args.templates or not args.output:
        parser.error("--capture, --templates and --output required")
    repo = Path(__file__).resolve().parents[2]
    output = args.output.resolve()
    if output.is_relative_to(repo):
        parser.error("private output must remain outside repository")
    capture, decoded = read_json(args.capture), read_json(args.templates)
    candidates = {entry["templateId"]: entry for entry in decoded["templates"]}
    resolver = resolve_for(capture)
    rendered = {}
    for field, key in (("title", 0xABDAF), ("body", 0xA2A90)):
        entry = candidates[key]
        if len(entry.get("variants", [])) != 1 or entry.get("status") != "template-only":
            raise ValueError("variant selection unsupported")
        rendered[field] = render(entry["variants"][0], resolver)
    rendered["status"] = "complete" if all(rendered[field]["status"] == "complete" for field in ("title", "body")) else "partial"
    rendered["context"] = {"scope": "explicit single inbox owner", "ownerRegistryLookupVerified": capture["result"]["welcomeRelationCandidates"].get("ownerLookupConfirmed") is True, "nativeSuppliedContextMatched": False}
    output.write_text(json.dumps(rendered, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Private result written; title:", rendered["title"]["status"], "body:", rendered["body"]["status"])


if __name__ == "__main__":
    main()
