"""Sanitized summary of a bounded FMAPI message capture.

Reads only a JSON capture produced by FMAPI.MessageProbe (or a synthetic
fixture with the same shape) and prints aggregate counts, date-decode
coverage, title/body template states, and unresolved token names. It never
prints message text, names, UIDs, pointers, template prose, or addresses.
Formatted-body availability is true only when a renderer result supplies a
non-empty complete formatted body.
"""
import argparse
import json
import re
from pathlib import Path

PINNED_BINARY_HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
REPO = Path(__file__).resolve().parents[2]


def unwrap_capture(document):
    if isinstance(document, dict) and "result" in document and isinstance(document["result"], dict):
        return document["result"], bool(document.get("repeatVerified", False))
    if isinstance(document, dict):
        return document, False
    raise ValueError("capture must be a JSON object")


def sanitized_token_name(token):
    if not isinstance(token, str):
        return None
    match = re.fullmatch(r"\[%[A-Za-z0-9_#-]+\]", token)
    return token if match else None


def summarize(capture, renderer=None):
    result, repeat_verified = unwrap_capture(capture)
    if result.get("binarySha256") not in (None, PINNED_BINARY_HASH):
        raise ValueError("unsupported binary profile")
    messages = result.get("messages")
    if not isinstance(messages, list):
        raise ValueError("messages must be a list")
    total = result.get("count")
    if not isinstance(total, int) or total < 0:
        total = len(messages)
    returned = result.get("returned")
    if not isinstance(returned, int) or returned < 0:
        returned = len(messages)
    if returned > len(messages):
        raise ValueError("returned count exceeds message list length")
    decoded_dates = sum(1 for message in messages if isinstance(message, dict) and message.get("date") is not None)
    title_template = result.get("welcomeTitleTemplate")
    body_template = result.get("welcomeBodyTemplate")
    title_status = title_template.get("status") if isinstance(title_template, dict) else "missing"
    body_status = body_template.get("status") if isinstance(body_template, dict) else "missing"

    unresolved = []
    title_resolved_available = False
    body_resolved_available = False
    renderer_status = "not-supplied"
    if renderer is not None:
        renderer_status = "provided"
        title_result = renderer.get("title") if isinstance(renderer, dict) else None
        body_result = renderer.get("body") if isinstance(renderer, dict) else None
        if isinstance(title_result, dict):
            if title_result.get("status") == "complete" and isinstance(title_result.get("formattedText"), str) and title_result["formattedText"]:
                title_resolved_available = True
            for token in title_result.get("missingTokens", []):
                name = sanitized_token_name(token)
                if name is not None and name not in unresolved:
                    unresolved.append(name)
        if isinstance(body_result, dict):
            if body_result.get("status") == "complete" and isinstance(body_result.get("formattedText"), str) and body_result["formattedText"]:
                body_resolved_available = True
            for token in body_result.get("missingTokens", []):
                name = sanitized_token_name(token)
                if name is not None and name not in unresolved:
                    unresolved.append(name)

    return {
        "status": "sanitized-summary",
        "binaryProfileSupported": result.get("binarySha256") == PINNED_BINARY_HASH,
        "repeatVerified": repeat_verified,
        "messageCount": {"totalReported": total, "returned": returned, "listed": len(messages)},
        "dateDecodeCoverage": {"decoded": decoded_dates, "returned": returned},
        "titleTemplateStatus": title_status,
        "bodyTemplateStatus": body_status,
        "rendererInput": renderer_status,
        "titleResolvedAvailable": title_resolved_available,
        "bodyResolvedAvailable": body_resolved_available,
        "unresolvedTokenNames": sorted(unresolved),
        "limitations": [
            "No message text, names, UIDs, pointers, or template prose are emitted.",
            "Template-only state is not rendered message text.",
            "A body is available only with a complete non-empty renderer result.",
        ],
    }


def read_json(path):
    raw = path.read_bytes()
    if len(raw) > 1024 * 1024:
        raise ValueError("JSON input size limit")
    return json.loads(raw.decode("utf-8-sig"))


def self_test():
    capture = {
        "repeatVerified": True,
        "result": {
            "binarySha256": PINNED_BINARY_HASH,
            "count": 3,
            "returned": 2,
            "messages": [
                {"date": "2026-11-03", "dateRaw": 1},
                {"date": None, "dateRaw": 2},
            ],
            "welcomeTitleTemplate": {"status": "template-only"},
            "welcomeBodyTemplate": {"status": "unavailable"},
        },
    }
    renderer = {
        "title": {"status": "complete", "formattedText": "Synthetic title", "missingTokens": []},
        "body": {"status": "partial", "formattedText": None, "missingTokens": ["[%male#1-first]", "not-a-token"]},
    }
    summary = summarize(capture, renderer)
    assert summary["messageCount"] == {"totalReported": 3, "returned": 2, "listed": 2}
    assert summary["dateDecodeCoverage"] == {"decoded": 1, "returned": 2}
    assert summary["titleTemplateStatus"] == "template-only"
    assert summary["bodyTemplateStatus"] == "unavailable"
    assert summary["titleResolvedAvailable"] is True
    assert summary["bodyResolvedAvailable"] is False
    assert summary["unresolvedTokenNames"] == ["[%male#1-first]"]
    assert "not-a-token" not in summary["unresolvedTokenNames"]
    no_renderer = summarize(capture)
    assert no_renderer["rendererInput"] == "not-supplied"
    assert no_renderer["unresolvedTokenNames"] == []
    print("PASS: sanitized summary counts, date coverage, template states, token filtering, and renderer gating")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--renderer", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.capture is None:
        parser.error("--capture is required unless --self-test is used")
    capture = read_json(args.capture)
    renderer = read_json(args.renderer) if args.renderer is not None else None
    summary = summarize(capture, renderer)
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.output is not None:
        output = args.output.resolve()
        if output.is_relative_to(REPO):
            parser.error("private summary output must remain outside the repository")
        output.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote sanitized summary: {output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
