# Offline evidence recheck - 2026-11-04

No game process was started, read or modified. Two independent checks ran concurrently as shell tool calls, not agent/model delegations.

## Reproduction and result

- All 28 research Python files declaring the literal --self-test option were executed with that option using Python 3.14.6: 28 exit-zero results, 0 failures. Includes manager, club-team, message, contract and position summarizers; native/property candidate manifests; bounded JSON and capture-profile validators. position_layout_probe.py does not declare that option and was not executed. No actual game file or private capture was supplied.
- Recovery inventory files with reviewedSha256: 38 checked, 0 missing, 0 mismatches after CRLF-to-LF normalization and UTF-8 SHA-256. This checks curated content against its recorded digest; it does not independently prove the original reverse engineering.
- Runtime test evidence remains the separately recorded 59 cached-dependency Core.Tests cases and MessageProbe self-test. These were not rerun for this documentation-only stage.

## Reuse decisions

| Chain | Reuse now | Still blocked |
| --- | --- | --- |
| Manager selection/employment | Existing bounded probe checks and sanitized summarizer; session read coordinator for eventual delivery | Coordinated live observer and process/save/selection lifetime qualification |
| Club teams | Existing bounded structural validator and summarizer; preserve notPlayerRoster and unverified hierarchy flags | Team roles, stable IDs, complete membership and reload behavior |
| Message dates | Shared pure decoder and existing calendar/sentinel checks | Independently proven current-game-date source |
| Other domains | Qualified manifests as static candidate inventories | Native semantics and current-session evidence; failed rescue tools remain excluded |

Do not create a second probe, import raw captures into git, or turn a successful manifest test into supported capabilities. The next game-dependent work is the agreed selected-manager observer/read window after Alpha.15 coordination; it is paused here. Exact-build fingerprints, bounded capture, identity rechecks and stale-result rejection must all remain in the eventual integration path.
