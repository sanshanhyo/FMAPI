# Pinned native evidence: selected human and goalkeeper rule

This is an independently written semantic reconstruction, not bundled game disassembly or callable game code. No setter/formatter/game method is invoked by the probe. SDK and FA installation are unchanged.

## Fingerprints

- game_plugin.dll: BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F
- GameAssembly.dll: 820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A
- Installed metadata signature/version: 0xFAB11BAF / 39. Header sections were checked against their explicit offsets, sizes and counts. Static format references: [Cpp2IL metadata header](https://github.com/SamboyCoding/Cpp2IL/blob/development/LibCpp2IL/Metadata/Il2CppGlobalMetadataHeader.cs) and [Il2CppDumper v39 layout proposal](https://github.com/Perfare/Il2CppDumper/pull/922). No third-party implementation is copied into this repository.

All offsets below are module-relative to the indicated pinned binary. The live diagnostic refuses unsupported fingerprints before claiming this selection profile.

## Local current-manager selection

The static metadata literal at index 9070 is GameCurrentManager; index 9071 adds UniqueId. GameAssembly's encoded literal slot is RVA 0x333AD88. Instruction-boundary analysis of its registration block establishes key 0x4743754D (GCuM): the key is constructed at RVA 0x4F9DE0, saved into the registration argument, and paired with that exact literal at 0x4F9E39..0x4F9E4F. This establishes a named property-to-key mapping; metadata strings by themselves would not establish selection semantics.

In game_plugin.dll, property dispatch 0x380020 branches on GCuM at 0x380223. It validates and resolves the supplied record reference, then replaces the global pointer at RVA 0x56F32C8 at 0x38027D. No such write is executed by our research code. Leaf getters at 0x378FC0 and 0x3810B0 return that same global. Teardown paths including 0x381150 and 0x6CEFC70 clear it. Another property path at 0x37C980 reads the selected record's +0x0C UID. Getter 0x37CB40 also retrieves GCuM through the supplied property context; we do not read that context or UI instances.

Original read-only reconstruction used by the diagnostic:

```text
selected_person = read_pointer(native_module + 0x56F32C8)
require selected_person has HUMAN_NON_PLAYER PERSON RTTI
find an exact pointer match among validated human-owner PERSON subobjects
require exactly one matching ownership entry; never choose by collection order/count
read selected person's UID and its existing contract -> team -> club relation
recheck selection pointer, identity fields, human vector and relationship pointers
if absent/unmatched/changed: active selection is unavailable
```

A focused --manager-selection capture in the running loaded session succeeded: the global selected record was HUMAN_NON_PLAYER, exactly matched one validated human-owner PERSON subobject, and had a linked employment club. The diagnostic returned selection.status=available and activeVerified=true for this native current-selected local manager. This does not prove network authority or all multiplayer/hotseat semantics, does not make reads atomic, and has not been exercised across selection changes or reloads. No UI, screenshots, account/password values or game functions were used.

## Goalkeeper familiarity and native predicate

Business rule PLAYER_IS_GOALKEEPER is distinct from PLAYER_IS_CURRENTLY_PLAYING_AS_A_GOALKEEPER. Its evaluation is RVA 0x3C0EC90 with vtable 0x4D16C28. It obtains an actual player through PERSON virtual +0x680 and obtains a byte through actual-player virtual +0x348. The latter resolves to getter 0x16325D0, which reads actual player +0x150. The business rule compares it against 15.

Original external reconstruction:

```text
require person vtable == module + 0x4D27758 and ACTUAL_PLAYER RTTI
player = person - signed_int32_at(person - 4) - 0x288
require player primary vtable == module + 0x4D27228 and ACTUAL_PLAYER RTTI
familiarity = read_byte(player + 0x150)
require 0 <= familiarity <= 20
business_rule_is_goalkeeper = familiarity >= 15
```

The conversion arithmetic is established by getter 0x16360E0. All 27 explicitly requested roster UIDs matched the ordered native PERSON UID lookup and exact actual-player layouts in a live capture; two met this goalkeeper predicate. Raw player identities and positions remain private. This predicate is not current match assignment and is not proof of a general position-name mapping.

## Reusable code locations

- `tools/FMAPI.MessageProbe/Program.cs`: arguments, process/module/hash identity, fail-closed read transport and 64 KiB capture budget.
- `tools/FMAPI.MessageProbe/EntityLinks.cs`: native selection-global validation, human employment relationships, ordered UID lookup and direct familiarity reads.
- `docs/research/manager-player-links-checkpoint.md`: data provenance, validation limits and historical state.

Use --manager-selection for a minimal selection/employment capture without sampling positions or localization. Use --entity-links followed by a private UID-array file for at most 32 targeted player UID lookups. Keep output and UID arrays outside the repository. No remote push is part of this work.
