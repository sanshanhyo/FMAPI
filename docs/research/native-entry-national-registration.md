> Recovery review (2026-11-03): historical static research, not a new live read. Property names are unverified candidates, not working APIs. Consult [the recovery review](recovery-review-20261103.md) for accepted tools and known failures. Original workstation paths are replaced with placeholders.

# Native entry lane: national-registration

## Authorized probe command

```text
& 'pwsh' -NoProfile -File '<research-workspace>/agent-tools/run-lane-probe.ps1' -Lane 'national-registration'
```

## Actual probe output

```text
{"lane":"national-registration","mode":"static-pinned-file","types":1,"vtables":1,"liveRecordsRead":0,"outputTruncated":false}
SHA256 BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F ImageBase 0x180000000
TYPE 0x56BC920 .?AVMANAGER_APPOINTED_COMPETITION_RULES_NEWS@@
VTABLE 0x4D5E108 .?AVMANAGER_APPOINTED_COMPETITION_RULES_NEWS@@ slots=0x17837F0,0x24D9C0,0x24D9D0,0x24D9E0,0x24D9F0,0x24DA00,0x24DA10,0x24DA20,0x24DA30,0x24DA40,0x24DA50,0x24DA60
RIP_CANDIDATE displacement=0x176062E function=0x1750CC0 target=0x4D5E108 .?AVMANAGER_APPOINTED_COMPETITION_RULES_NEWS@@
RIP_CANDIDATE displacement=0x1C9085A function=0x1C89D70 target=0x4D5E108 .?AVMANAGER_APPOINTED_COMPETITION_RULES_NEWS@@
```

The probe read only the pinned static binary. It did not read process memory, records, UI, saves, or game state.

## Match result

No matching type for a national-registration business object was found. The only confirmed RTTI type is `MANAGER_APPOINTED_COMPETITION_RULES_NEWS`, with vtable `0x4D5E108`. Its name describes a news item about a manager being appointed to competition rules; it is not evidence of a national-team, squad-registration, eligibility, quota, work-permit, or competition-rule entity.

## Narrow business-object entry hypothesis

The only verified native entry surface from this lane is the news type above. It may be a downstream notification or presentation object rather than a data owner. No instance layout, collection pointer, field offset, UID relation, or registration state is confirmed. Consequently, this lane currently has no usable business-object entry and no live reader should be created from it.

## Exact missing semantics

- National-team entity, tier, age group, call-up status, report/return dates, squad membership, camp, and club availability impact (NAT-01).
- Nationality, eligibility, represented country, caps, selection status, and multiple-nationality handling (NAT-02).
- National-team competition history, world ranking/coefficients, and age-group qualification scope (NAT-03).
- Next-match eligibility, registration status, suspension/discipline reason, and applicable competition (REG-01).
- Registration windows, squad-size/age/homegrown quotas, foreign-player limits, work permits, and registration/loan limits (REG-02).
- Promotion/relegation/competition format, cumulative card/suspension rules, financial compliance, and transfer-window boundaries (REG-03).
- Jurisdiction-specific rules and historical changes, including rule-definition versus engine-result distinction (REG-04).
- Any instance offsets, vtable slot semantics, UID linkage, collection traversal, or live capture validation for the confirmed type.

## Next bounded read request

1. Run static RTTI/name searches over the same pinned binary for narrower fragments: `REGISTRATION`, `NATIONAL`, `NATIONAL_TEAM`, `SQUAD`, `ELIGIBILITY`, `WORK_PERMIT`, `COMPETITION_RULES`, and `NEWS` only as supporting context.
2. If a candidate type whose name and vtable are specific to national registration is found, request coordinator approval for a bounded process probe that records only that type, its vtable slots, and RIP/xref candidates. No instance reads yet.
3. Only after a matching type and vtable are confirmed, request a separate bounded layout probe with explicitly supplied UIDs or fixture identities. Keep all outputs outside the repository and fail closed on fingerprint mismatch.

Until those steps succeed, the lane remains static evidence only and must report `unavailable` for every NAT/REG field.
