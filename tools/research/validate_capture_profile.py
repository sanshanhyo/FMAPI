#!/usr/bin/env python3
"""Validate a FMAPI research capture profile without reading game data.

The validator checks pinned binary fingerprints when present, validates process
start identity only when a capture contains it, requires every atomicSnapshot
field to be false, and labels the profile as current-session or historical
evidence.  It prints profile coverage only; no identity, path, UID, name, or raw
sample values are emitted.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

NATIVE_HASH = "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F"
ASSEMBLY_HASH = "820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A"
METADATA_HASH = "A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C"
METADATA_SIGNATURE = 0xFAB11BAF
METADATA_VERSION = 39

NATIVE_KEYS = {"binarySha256", "nativeSha256", "gamePluginSha256", "nativeHash", "gamePluginHash"}
ASSEMBLY_KEYS = {"gameAssemblySha256", "assemblySha256", "gameAssemblyHash", "assemblyHash"}
METADATA_HASH_KEYS = {"metadataSha256", "metadataHash"}
METADATA_SIGNATURE_KEYS = {"metadataSignature", "metadataSig"}
METADATA_VERSION_KEYS = {"metadataVersion", "metadataSchemaVersion"}
PROCESS_ID_KEYS = {"processId", "pid", "processPid"}
PROCESS_START_KEYS = {"processStartedAt", "processStartTime", "startedAt", "processStart"}
EVIDENCE_LABEL_KEYS = {"evidenceLabels", "evidenceProfile", "evidenceScopes", "evidenceLabel"}
ALLOWED_EVIDENCE_LABELS = {"current", "historical"}
def _reject_constant(value):
    raise ValueError("invalid JSON constant")


def _iso8601(value):
    if not isinstance(value, str) or not value:
        return False
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(text)
    except ValueError:
        return False
    return True


def _collect(obj, bucket):
    stack = [obj]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for key, value in node.items():
                if not isinstance(key, str):
                    continue
                bucket["keys"].add(key)
                if key in NATIVE_KEYS:
                    bucket["native_present"] = True
                    bucket["native_count"] += 1
                    if value != NATIVE_HASH:
                        bucket["native_valid"] = False
                if key in ASSEMBLY_KEYS:
                    bucket["assembly_present"] = True
                    bucket["assembly_count"] += 1
                    if value != ASSEMBLY_HASH:
                        bucket["assembly_valid"] = False
                if key in METADATA_HASH_KEYS:
                    bucket["metadata_hash_present"] = True
                    bucket["metadata_hash_count"] += 1
                    if value != METADATA_HASH:
                        bucket["metadata_hash_valid"] = False
                if key in METADATA_SIGNATURE_KEYS:
                    bucket["metadata_sig_present"] = True
                    bucket["metadata_sig_count"] += 1
                    if value != METADATA_SIGNATURE:
                        bucket["metadata_sig_valid"] = False
                if key in METADATA_VERSION_KEYS:
                    bucket["metadata_ver_present"] = True
                    bucket["metadata_ver_count"] += 1
                    if value != METADATA_VERSION:
                        bucket["metadata_ver_valid"] = False
                if key in PROCESS_ID_KEYS:
                    bucket["process_id_present"] = True
                    bucket["process_id_count"] += 1
                    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                        bucket["process_id_valid"] = False
                if key in PROCESS_START_KEYS:
                    bucket["process_start_present"] = True
                    bucket["process_start_count"] += 1
                    if not _iso8601(value):
                        bucket["process_start_valid"] = False
                if key == "atomicSnapshot":
                    bucket["atomic_count"] += 1
                    if value is not False:
                        bucket["atomic_all_false"] = False
                if key in EVIDENCE_LABEL_KEYS:
                    bucket["evidence_labels_present"] = True
                    if isinstance(value, list):
                        bucket["evidence_labels"].extend(item for item in value if isinstance(item, str))
                    elif isinstance(value, str):
                        bucket["evidence_labels"].append(value)
                stack.append(value)
        elif isinstance(node, list):
            stack.extend(node)


def _scan_active(obj, bucket):
    stack = [obj]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if node.get("activeVerified") is True:
                bucket["active_verified_count"] += 1
                source = node.get("source")
                if not (isinstance(source, str) and ("gcum" in source.lower() or "gamecurrentmanager" in source.lower())):
                    bucket["active_sources_valid"] = False
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)


def _sections(obj):
    sections = []
    if isinstance(obj, dict):
        sections.extend(sorted(obj.keys()))
        result = obj.get("result")
        if isinstance(result, dict):
            sections.extend(f"result.{key}" for key in sorted(result.keys()))
    return sorted(set(sections))[:200]


def validate(obj):
    bucket = {
        "keys": set(),
        "native_present": False,
        "native_valid": True,
        "native_count": 0,
        "assembly_present": False,
        "assembly_valid": True,
        "assembly_count": 0,
        "metadata_hash_present": False,
        "metadata_hash_valid": True,
        "metadata_hash_count": 0,
        "metadata_sig_present": False,
        "metadata_sig_valid": True,
        "metadata_sig_count": 0,
        "metadata_ver_present": False,
        "metadata_ver_valid": True,
        "metadata_ver_count": 0,
        "process_id_present": False,
        "process_id_valid": True,
        "process_id_count": 0,
        "process_start_present": False,
        "process_start_valid": True,
        "process_start_count": 0,
        "atomic_count": 0,
        "atomic_all_false": True,
        "evidence_labels_present": False,
        "evidence_labels": [],
        "active_verified_count": 0,
        "active_sources_valid": True,
    }
    _collect(obj, bucket)
    _scan_active(obj, bucket)

    process_identity_present = bucket["process_id_present"] or bucket["process_start_present"]
    process_identity_valid = (bucket["process_id_valid"] and bucket["process_start_valid"]) if process_identity_present else None

    errors = []
    if not bucket["native_present"]:
        errors.append("native fingerprint missing")
    elif not bucket["native_valid"]:
        errors.append("native fingerprint mismatch")

    if bucket["assembly_present"] and not bucket["assembly_valid"]:
        errors.append("GameAssembly fingerprint mismatch")
    if bucket["metadata_hash_present"] and not bucket["metadata_hash_valid"]:
        errors.append("metadata fingerprint mismatch")
    if bucket["metadata_sig_present"] and not bucket["metadata_sig_valid"]:
        errors.append("metadata signature mismatch")
    if bucket["metadata_ver_present"] and not bucket["metadata_ver_valid"]:
        errors.append("metadata version mismatch")

    if bucket["process_id_present"] and not bucket["process_id_valid"]:
        errors.append("process id identity invalid")
    if bucket["process_start_present"] and not bucket["process_start_valid"]:
        errors.append("process start identity invalid")

    if bucket["atomic_count"] > 0 and not bucket["atomic_all_false"]:
        errors.append("atomicSnapshot must remain false")

    if bucket["evidence_labels_present"]:
        invalid_labels = sorted(set(bucket["evidence_labels"]) - ALLOWED_EVIDENCE_LABELS)
        if invalid_labels:
            errors.append("evidence label must be current or historical")
        if not bucket["evidence_labels"]:
            errors.append("evidence label list is empty")

    if bucket["active_verified_count"] > 1:
        errors.append("duplicate current manager selection")
    if not bucket["active_sources_valid"] and bucket["active_verified_count"] > 0:
        errors.append("current manager evidence lacks GCuM source")

    errors = list(dict.fromkeys(errors))

    current_evidence = bucket["active_verified_count"] > 0 or bucket["process_start_present"]
    evidence_label = "current" if current_evidence and bucket["native_valid"] else "historical"

    coverage = {
        "nativeFingerprint": {
            "present": bucket["native_present"],
            "valid": bucket["native_valid"] if bucket["native_present"] else None,
            "count": bucket["native_count"],
            "required": True,
        },
        "gameAssemblyFingerprint": {
            "present": bucket["assembly_present"],
            "valid": bucket["assembly_valid"] if bucket["assembly_present"] else None,
            "count": bucket["assembly_count"],
            "required": False,
        },
        "metadataFingerprint": {
            "present": bucket["metadata_hash_present"],
            "valid": bucket["metadata_hash_valid"] if bucket["metadata_hash_present"] else None,
            "count": bucket["metadata_hash_count"],
            "required": False,
        },
        "metadataSignature": {
            "present": bucket["metadata_sig_present"],
            "valid": bucket["metadata_sig_valid"] if bucket["metadata_sig_present"] else None,
            "count": bucket["metadata_sig_count"],
            "required": False,
        },
        "metadataVersion": {
            "present": bucket["metadata_ver_present"],
            "valid": bucket["metadata_ver_valid"] if bucket["metadata_ver_present"] else None,
            "count": bucket["metadata_ver_count"],
            "required": False,
        },
        "processStartIdentity": {
            "present": process_identity_present,
            "valid": process_identity_valid,
            "processIdPresent": bucket["process_id_present"],
            "processStartPresent": bucket["process_start_present"],
            "required": False,
        },
        "atomicSnapshot": {
            "fieldCount": bucket["atomic_count"],
            "allFalse": bucket["atomic_all_false"],
            "required": False,
        },
        "evidenceLabels": {
            "present": bucket["evidence_labels_present"],
            "valid": (all(label in ALLOWED_EVIDENCE_LABELS for label in bucket["evidence_labels"])
                     if bucket["evidence_labels_present"] else None),
            "currentCount": bucket["evidence_labels"].count("current"),
            "historicalCount": bucket["evidence_labels"].count("historical"),
            "otherCount": sum(label not in ALLOWED_EVIDENCE_LABELS for label in bucket["evidence_labels"]),
            "required": False,
        },
        "managerSelection": {
            "activeVerifiedCount": bucket["active_verified_count"],
            "sourcesValid": bucket["active_sources_valid"],
            "duplicateFree": bucket["active_verified_count"] <= 1,
        },
        "evidenceLabel": evidence_label,
        "sections": _sections(obj),
    }
    status = "valid" if not errors else "invalid"
    return status, coverage, errors


def read_capture(path):
    if path is None or path == "-":
        raw = sys.stdin.buffer.read()
    else:
        file_path = Path(path)
        if not file_path.is_file():
            raise ValueError("capture file not found")
        raw = file_path.read_bytes()
    if not raw:
        raise ValueError("capture is empty")
    if len(raw) > INPUT_LIMIT:
        raise ValueError("capture size limit")
    try:
        obj = json.loads(raw.decode("utf-8-sig"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("invalid JSON") from exc
    if not isinstance(obj, dict):
        raise ValueError("capture must be a JSON object")
    return obj


def self_test():
    base = {
        "result": {
            "binarySha256": NATIVE_HASH,
            "gameAssemblySha256": ASSEMBLY_HASH,
            "processId": 1234,
            "processStartedAt": "2026-11-03T00:00:00+00:00",
            "atomicSnapshot": False,
            "activeManager": {
                "activeVerified": True,
                "source": "native GameCurrentManager (GCuM) selection global",
                "atomicSnapshot": False,
            },
            "evidenceLabels": ["current", "historical"],
        }
    }
    status, coverage, errors = validate(base)
    assert status == "valid", errors
    assert coverage["evidenceLabel"] == "current"
    assert coverage["atomicSnapshot"]["allFalse"] is True

    old = {"result": {"binarySha256": NATIVE_HASH, "atomicSnapshot": False}}
    status, coverage, errors = validate(old)
    assert status == "valid", errors
    assert coverage["evidenceLabel"] == "historical"
    assert coverage["gameAssemblyFingerprint"]["present"] is False

    invalid_native = {"result": {"binarySha256": "0" * 64}}
    status, _, errors = validate(invalid_native)
    assert status == "invalid" and any("native fingerprint" in error for error in errors)

    invalid_atomic = {"result": {"binarySha256": NATIVE_HASH, "atomicSnapshot": True}}
    status, _, errors = validate(invalid_atomic)
    assert status == "invalid" and any("atomicSnapshot" in error for error in errors)

    invalid_label = {"result": {"binarySha256": NATIVE_HASH, "evidenceLabels": ["live"]}}
    status, _, errors = validate(invalid_label)
    assert status == "invalid" and any("evidence label" in error for error in errors)

    duplicate = {
        "result": {
            "binarySha256": NATIVE_HASH,
            "activeManager": {"activeVerified": True, "source": "native GameCurrentManager (GCuM) selection global"},
            "managerCandidates": [{"activeVerified": True, "source": "native GameCurrentManager (GCuM) selection global"}],
        }
    }
    status, _, errors = validate(duplicate)
    assert status == "invalid" and any("duplicate" in error for error in errors)

    invalid_process = {"result": {"binarySha256": NATIVE_HASH, "processId": 0}}
    status, _, errors = validate(invalid_process)
    assert status == "invalid" and any("process id" in error for error in errors)

    metadata_ok = {
        "result": {
            "binarySha256": NATIVE_HASH,
            "metadataSha256": METADATA_HASH,
            "metadataSignature": METADATA_SIGNATURE,
            "metadataVersion": METADATA_VERSION,
        }
    }
    status, coverage, errors = validate(metadata_ok)
    assert status == "valid", errors
    assert coverage["metadataFingerprint"]["present"] is True

    metadata_bad = {"result": {"binarySha256": NATIVE_HASH, "metadataVersion": 38}}
    status, _, errors = validate(metadata_bad)
    assert status == "invalid" and any("metadata version" in error for error in errors)

    print("PASS: capture profile fingerprints, optional metadata/process identity, atomicSnapshot, evidence labels, manager selection")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", nargs="?", help="capture JSON path, or - for stdin")
    parser.add_argument("--self-test", action="store_true", help="run synthetic checks")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    try:
        obj = read_capture(args.capture)
        status, coverage, errors = validate(obj)
    except ValueError as exc:
        print(json.dumps({"status": "invalid", "profileCoverage": None, "errors": [str(exc)]}, indent=2))
        return 2

    result = {"status": status, "profileCoverage": coverage, "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
