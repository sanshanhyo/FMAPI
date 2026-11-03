# Implementation note: staff responsibilities metadata literal lookup

## Artifact

- `tools/research/find_property_literals.py`
- Offline only. No process, credentials, generated metadata export, network, or subagent use.

## Purpose

Bounded lookup of exact provided names in the pinned Il2Cpp `global-metadata.dat` string-literal table. It reports literal indices only, with explicit candidate semantics. It does not claim property registration, dispatch, roster membership, or runtime behavior.

## Usage

```text
python tools/research/find_property_literals.py <global-metadata.dat> --name GameCurrentManager --name UniqueId
python tools/research/find_property_literals.py <global-metadata.dat> GameCurrentManager UniqueId --output result.json
python tools/research/find_property_literals.py --self-test
```

## Pinned profile

- Metadata SHA-256: `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`
- Sanity: `0xFAB11BAF`
- Version: `39`
- Control literal: index `9070` must decode exactly to `GameCurrentManager`.
- Section 0 is the string-literal boundary/offset table; section 1 is the string-literal data bytes.
- Lookup decodes each UTF-16LE literal and compares the full decoded value for exact equality.

## Evidence and limits

- The tool is original repository code and uses only the Python standard library.
- It validates file size, sanity, version, section boundaries, entry alignment, entry count, data indices, UTF-16LE decoding, embedded NUL rejection, and the known control literal.
- It returns indices as candidates only. A matching literal index does not establish that the name is registered, dispatched, selected, or available in any runtime state.
- It does not read any game process, resolve RVAs, or inspect generated assemblies.
- It does not modify SDK, inventory, or other implementation files.
- Synthetic self-tests cover successful control/exact lookup and fail-closed handling for truncated, wrong-profile, bad-boundary, and wrong-control inputs.
- No live metadata read or real sample output is included in this repository.
- Coordinator execution/build/verification remains pending; this note does not claim tests were run.
