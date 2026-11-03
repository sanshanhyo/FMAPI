# Implementation note: capture-profile validator

Artifact: `tools/research/validate_capture_profile.py`

## Purpose

Pure offline validator for research capture JSON profiles. It does not open a process, call native functions, use the network, read external directories, or modify captures. It emits profile coverage only; no identity, path, UID, name, or raw sample values are printed.

## Usage

```text
python tools/research/validate_capture_profile.py <capture.json>
python tools/research/validate_capture_profile.py -
python tools/research/validate_capture_profile.py --self-test
```

Input may be a capture object or an object containing `result`. Maximum input size is 1,000,000 bytes.

## Evidence and checks

- Pinned `game_plugin.dll` fingerprint is required and must equal `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`.
- `GameAssembly.dll`, metadata SHA-256, metadata signature `0xFAB11BAF`, and metadata version `39` are validated only when present.
- Process ID and process start timestamp are validated only when present.
- Every `atomicSnapshot` field anywhere in the capture must be `false`.
- `evidenceLabels` values, when present, must be `current` or `historical`.
- At most one `activeVerified: true` manager selection may appear, and it must carry a `GCuM`/`GameCurrentManager` source.
- The output classifies the profile as `current` when it has current-session selection or process-start identity; otherwise `historical`.

## Synthetic edge-case expected outputs

These are representative outputs for the current validator; full JSON also contains unchanged coverage fields and `sections`.

```json
{
  "oldMinimalCapture": {
    "input": {"result": {"binarySha256": "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F", "atomicSnapshot": false}},
    "expected": {"status": "valid", "profileCoverage.evidenceLabel": "historical", "profileCoverage.processStartIdentity.present": false, "profileCoverage.processStartIdentity.valid": null, "errors": []}
  },
  "currentCapture": {
    "input": {"result": {"binarySha256": "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F", "gameAssemblySha256": "820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A", "processId": 1234, "processStartedAt": "2026-11-03T00:00:00+00:00", "atomicSnapshot": false, "activeManager": {"activeVerified": true, "source": "native GameCurrentManager (GCuM) selection global"}, "evidenceLabels": ["current", "historical"]}},
    "expected": {"status": "valid", "profileCoverage.evidenceLabel": "current", "profileCoverage.processStartIdentity.present": true, "profileCoverage.processStartIdentity.valid": true, "profileCoverage.managerSelection.activeVerifiedCount": 1, "errors": []}
  },
  "atomicSnapshotTrue": {
    "input": {"result": {"binarySha256": "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F", "atomicSnapshot": true}},
    "expected": {"status": "invalid", "errors": ["atomicSnapshot must remain false"]}
  },
  "invalidEvidenceLabel": {
    "input": {"result": {"binarySha256": "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F", "evidenceLabels": ["live"]}},
    "expected": {"status": "invalid", "errors": ["evidence label must be current or historical"]}
  },
  "duplicateCurrentSelection": {
    "input": {"result": {"binarySha256": "BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F", "activeManager": {"activeVerified": true, "source": "native GameCurrentManager (GCuM) selection global"}, "managerCandidates": [{"activeVerified": true, "source": "native GameCurrentManager (GCuM) selection global"}]}},
    "expected": {"status": "invalid", "errors": ["duplicate current manager selection"]}
  },
  "missingNativeFingerprint": {
    "input": {"result": {"atomicSnapshot": false}},
    "expected": {"status": "invalid", "errors": ["native fingerprint missing"]}
  }
}
```
