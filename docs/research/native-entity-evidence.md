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

## Named familiarity fields and natural-position mask

The metadata PositionMask enum was independently decoded from the pinned v39 field/default tables. Its metadata file SHA-256 is A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C. The native pure mask builder is RVA 0x499AEB0; its lookup table is RVA 0x4D36ACC. Actual-player virtual +0x478 is RVA 0x15E7970, which supplies the structure at player +0x148 to that builder.

The builder tests structure +8 (player +0x150) for GK, then loops over structure +0x0A..+0x16 (player +0x152..+0x15E). It ORs the matching named mask bit when a familiarity is >= the supplied threshold. Structure +9/player +0x151 is skipped. The table's skipped entry corresponds to metadata SweeperCentreNotInUse; the diagnostic retains that byte only as unusedSlot151Raw.

| Player offset | Code | Native enum name | Mask bit |
|---|---|---|---|
| 0x150 | GK | Goalkeeper | 0x1 |
| 0x152 | DL | DefenderLeft | 0x8 |
| 0x153 | DC | DefenderCentre | 0x10 |
| 0x154 | DR | DefenderRight | 0x4 |
| 0x155 | DM | DefensiveMidfielderCentre | 0x80 |
| 0x156 | ML | MidfielderLeft | 0x200 |
| 0x157 | MC | MidfielderCentre | 0x400 |
| 0x158 | MR | MidfielderRight | 0x100 |
| 0x159 | AML | AttackingMidfielderLeft | 0x1000 |
| 0x15A | AMC | AttackingMidfielderCentre | 0x2000 |
| 0x15B | AMR | AttackingMidfielderRight | 0x800 |
| 0x15C | ST | AttackerCentre | 0x4000 |
| 0x15D | WBL | WingBackLeft | 0x40 |
| 0x15E | WBR | WingBackRight | 0x20 |

The order is recovered from the native table, not guessed from common football abbreviations. Left/right are especially easy to reverse. Other enum members such as AttackerRight/AttackerLeft have no corresponding familiarity in this analyzed loop and are not fabricated as zero-rated extra fields.

NaturalPositionMask's metadata literal index 13549 is registered in GameAssembly as key 0x62704D52 at RVA 0x53A410..0x53A481. Native property dispatch 0x521540 routes that key to underlying Pnps (0x506E7073) at 0x52A15C. The player dispatch path at 0x1BCA89B calls virtual +0x478 with threshold 0x12 (18). The research decoder reproduces that route's natural mask using >=18; it does not conflate it with the separate goalkeeper business threshold >=15.

`PositionFields.cs` is original internal probe-only decoding code. Its synthetic checks cover a GK + left-defender mask, a high unused slot that must not emit a bit, the 17/18 natural boundary, the 14/15 goalkeeper boundary, and malformed block size/range. A separate original `tools/research/position_layout_probe.py` reads only the pinned native lookup table and metadata enum, without any process access, and recovered all 14 name/bit/offset mappings. Its output agreed with the C# decoder.

The previously captured 27 complete UID-linked blocks were decoded offline through `--decode-position-capture`; all produced 14 named familiarities and nonempty natural masks, and their goalkeeper predicates agreed with the prior raw result. This is interpretation of measured bytes under the proven layout, not a second measurement or a UI comparison. The original capture is preserved. The decoder's interpretation profile does not retroactively assert that all interpretation fingerprints were recorded in older capture headers.
