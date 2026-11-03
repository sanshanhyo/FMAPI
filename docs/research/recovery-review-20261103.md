# Recovery review: 2026-11-03

## Scope and evidence level

Local curation from the emergency rescue, based on `dd1348ab7464a5904fed6f69e49b3860e2fb3389` (`research/parallel-consolidated`). This review adds no runtime interfaces, SDK contracts, memory writes, or game compatibility claim. No Windows/game process or private captures were available or accessed.

The integrated branch already contains the earlier documented current-manager link, bounded inbox/template capture, explicit-player position/contract links, two-club-team container and TEAM_BASE index evidence. They remain historical, bounded evidence, not a complete roster/fixture/news reader. This review did not repeat those real-game checks.

## Accepted work

- 24 static research notes across all 12 domains: manager/club, player positions/state, contracts/finance/transfers, fixtures/matches, messages/news, tactics, training/development, scouting/recruitment, staff/responsibilities, national registration, youth development, board/facilities/history.
- 14 offline manifest/validator scripts passed their synthetic self-tests after curation. Static RTTI/property names are leads, not business-field semantics or new live reads. The property-probe notes report `liveRecordsRead=0`.
- 114 recovered changed/untracked file entries were inventoried in [recovery-review-inventory.json](recovery-review-inventory.json), with original and accepted-content SHA-256 hashes and an inclusion decision.
- Existing integrated tools and inventories were retained rather than overwritten by stale per-lane copies. For example the lane fixture locator still contains the previously corrected PE section tuple bug; its integrated replacement is retained.
- Workstation-specific command paths were replaced by placeholders. Accidental generation text and code prefixes were removed from two native-entry notes; stray generation tails were removed from tactics/staff notes. Original rescued files remain unchanged in the separate recovery snapshots.

## Not accepted as runnable tools

The following 10 formal scripts failed qualification and remain only in the original rescue. Do not interpret a companion-script mention in a historical note as delivery of these tools:

- `entry_player_position_state.py`: syntax-failed.
- `property_entry_player_position_state.py`: syntax-failed.
- `entry_board_facilities_history.py`: selftest-failed.
- `property_entry_board_facilities_history.py`: selftest-failed.
- `property_entry_manager_club.py`: selftest-failed.
- `property_entry_national_registration.py`: selftest-failed.
- `entry_fixtures_matches.py`: selftest-failed.
- `property_entry_staff_responsibilities.py`: syntax-failed.
- `entry_scouting_recruitment.py`: selftest-failed.
- `property_entry_scouting_recruitment.py`: selftest-failed.

The syntax failures are truncated/generated source. Other failures include offset-policy text mistaken for invented offsets, undefined registration constants, manifest rejection and self-test assertion mismatches. They were not weakened or silently marked passed. The broken `_test_write.py`, duplicate input documents, duplicate misplaced tools and older parallel-note changes were also not promoted; every decision is listed in the inventory.

## Checks actually run

- Python syntax compilation for all research Python files in the curated worktree.
- 28 `--self-test` entry points passed: 14 newly accepted plus 14 pre-existing tools. Synthetic checks only; no game execution or new actual-file binary validation.
- New-file credential/private-key and workstation-path pattern scan; no matches after curation. This is a bounded content check, not a guarantee that unrelated historic Git objects contain no sensitive data.
- Original 1,080 snapshot file hashes rechecked unchanged across the original 14 worktrees.
- `git diff --cached --check` and repository `git fsck --full`.

Not run: .NET build (no SDK/Core changes), Windows installation, actual game-memory capture, native calls, GitHub CI or remote publication. This is a local research preservation commit, not a release-ready game adapter.
