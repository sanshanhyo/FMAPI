> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Property-entry evidence: tactics lane

Status: static property-candidate evidence only. The reviewed fixed-file property probe opened pinned metadata as data; it did not open a process, read process memory, call game functions, use UI, or read private samples. `liveRecordsRead=0`. This is research tooling, not SDK, adapter, or game client behavior.

## Executed probe

Command:

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-property-probe.ps1' -Lane 'tactics'
```

Returned result:

```json
{"lane": "tactics", "mode": "static-property-candidates", "matches": 1, "truncated": false, "liveRecordsRead": 0, "entries": [{"name": "TacticRoleMenuModuleBindings", "literalIndex": 18799, "slotRvas": ["0x32f7040"], "semantics": "unverified-property-name"}]}
```

Summary:

- `lane`: `tactics`
- `mode`: `static-property-candidates`
- `matches`: `1`
- `truncated`: `false`
- `liveRecordsRead`: `0`
- candidate property name: `TacticRoleMenuModuleBindings`
- literal index: `18799`
- encoded slot RVA: `0x32f7040`
- semantics: `unverified-property-name`

## Source and hash

- Property-name source: GameAssembly.dll metadata, separately fingerprinted as `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`.
- Metadata signature/version: `0xFAB11BAF` / `39`.
- Native context source: game_plugin.dll, SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`.
- Image base used for module-relative RVAs: `0x180000000`.
- Probe mode: static pinned file only. No process, save, UI, network, or private capture was used.

## Candidate classification

`TacticRoleMenuModuleBindings` is a returned property name only. The name suggests a tactic role menu module binding, but that is not proof of a business tactic field. It is classified as a UI/module/operations candidate until registration disassembly establishes a native key, dispatch shape, and context resolution. It must not be described as a tactic business field, tactic owner, formation, lineup, role, duty, instruction, set-piece, or familiarity value.

Coordinator evidence used to sharpen this classification:

- Current club2 TEAM pointers match their TEAM_BASE low23-bit index entries, 2/2.
- `NextFixture` literal index `13696`, slot RVA `0x330B698`, native key `0x6E654669`, first resolves TEAM_BASE context through global `0x5703768`, not fixtures.
- Therefore property names are unreliable business-target labels. `NextFixture` is a comparator for registration shape only, not a fixture reader and not a tactics field.

## Unproven values kept null

For the actual returned tactics candidate, all of the following remain null or unknown:

- native property key
- native offset
- native function RVA
- context resolution
- object field offsets
- tactic owner
- active versus selected tactic slot

No function, key, or offset was fabricated. The only function RVAs that may be used are those already established by separate native-entry evidence; this manifest adds none.

## Ranked next registrations to inspect

1. `TacticRoleMenuModuleBindings`, literal index `18799`, slot RVA `0x32f7040`: inspect its exact GameAssembly registration block for native key construction and context resolution. Compare its shape with the `NextFixture` comparator.
2. `NextFixture`, literal index `13696`, slot RVA `0x330B698`: use only as a proven comparator showing misleading property-name resolution. It is not a tactics target.

## Next bounded live request

No live request is genuinely supported for the tactics candidate. A bounded process read would require a proven native key, owner, or pointer source, none of which exists for `TacticRoleMenuModuleBindings`. The next action is static disassembly of the exact registration block at GameAssembly slot RVA `0x32f7040`, followed by comparison with the `NextFixture` comparator at slot RVA `0x330B698`.

If that static work later establishes a stable object, a future live read must remain bounded to 64 KiB total, 32 objects, 8 KiB per read, two passes, and at most two already-analyzed pointer hops, with exact RTTI/vtable checks and immediate abort on any pointer, type, or state change. No writes, game calls, UI, native calls, network access, or private capture access are permitted.

Machine-readable manifest: `tools/research/property_entry_tactics.py`.
