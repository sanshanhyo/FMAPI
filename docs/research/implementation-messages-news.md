# Implementation note: sanitized message-capture summary

Artifact: `tools/research/summarize_messages.py`

## Purpose

Produce a sanitized aggregate summary of a bounded FMAPI message capture. It is
a standalone Python CLI for coordinator/audit use; it is not an SDK, adapter, or
game reader, and it does not access any process, file outside the supplied JSON
inputs, network, or game state.

## Usage

```text
python tools/research/summarize_messages.py --self-test
python tools/research/summarize_messages.py --capture <private-capture.json> [--renderer <private-renderer.json>] [--output <private-summary.json>]
```

- `--capture`: private JSON from `FMAPI.MessageProbe` or a synthetic fixture with
  the same shape. Required unless `--self-test`.
- `--renderer`: optional private JSON from `tools/research/render_welcome.py`.
- `--output`: optional private output path. It must be outside the repository.
- Without `--output`, the sanitized summary is printed to stdout.

## Output fields

- `messageCount`: total reported, returned, and listed counts.
- `dateDecodeCoverage`: decoded dates versus returned entries.
- `titleTemplateStatus` / `bodyTemplateStatus`: template availability state only.
- `titleResolvedAvailable` / `bodyResolvedAvailable`: true only when a renderer
  result is complete and has a non-empty `formattedText`.
- `unresolvedTokenNames`: sorted unique token names only; raw template text is
  never emitted.
- `binaryProfileSupported`, `repeatVerified`, and limitations.

## Evidence basis

- Probe capture shape and fields from `tools/FMAPI.MessageProbe/Program.cs`
  (`status`, `count`, `returned`, `messages[].date`, template statuses).
- Renderer shape and `missingTokens` from `tools/research/render_welcome.py`.
- Pinned binary hash `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`.

## Machine-readable synthetic edge-case expected outputs

```json
{
  "missingRenderer": {
    "input": "capture with 4 reported, 3 returned, 2 decoded dates; title template-only; body unavailable; no renderer",
    "expected": {
      "messageCount": {"totalReported": 4, "returned": 3, "listed": 3},
      "dateDecodeCoverage": {"decoded": 2, "returned": 3},
      "titleTemplateStatus": "template-only",
      "bodyTemplateStatus": "unavailable",
      "rendererInput": "not-supplied",
      "titleResolvedAvailable": false,
      "bodyResolvedAvailable": false,
      "unresolvedTokenNames": []
    }
  },
  "completeTitlePartialBody": {
    "input": "same capture with renderer title complete and body partial missing [%male#1-first]",
    "expected": {
      "titleResolvedAvailable": true,
      "bodyResolvedAvailable": false,
      "unresolvedTokenNames": ["[%male#1-first]"]
    }
  },
  "nullAndUnknownTokens": {
    "input": "renderer missingTokens contains null, non-string, and malformed token values",
    "expected": {
      "unresolvedTokenNames": []
    }
  }
}
```

## Limitations

- Summary-only; no message bodies, titles, names, UIDs, pointers, or template
  prose are output.
- Template-only is not rendered text.
- Body availability requires an actual complete non-null renderer result.
- No game/process/UI access, native calls, subprocesses, or new live reads.
- Synthetic self-test covers only parser and gating logic; it is not a live
  game-data validation. Coordinator execution/verification remains pending.
