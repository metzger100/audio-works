# Quality implementation validation — 2026-10-05

This dated audit records the implemented organization, preservation and context tooling. It is separate from microphone qualification and the laboratory's previously recorded 31-test verification.

| Check | Recorded result |
| --- | --- |
| Common onboarding | 31,537 characters; approximately 7,884 tokens by characters ÷ 4; below the 32,000-character limit |
| Current state | 135 words, below 300 |
| Active links/classification/generated freshness | Repository gate passes |
| Maintenance gate | Installed locally; staged checker and actual hook pass in a separate restored checkout (about 0.54 / 0.68 seconds) |
| Tooling regressions | 22 tests pass, including partial staging, false-success prevention, historical immutability and safe recovery |
| Protected original files | 7,237 baseline files unchanged; original scientific contract and Meridian brief preserved in full |
| Waveform/CSV integrity | All 3,902 inventoried files present, zero mismatches, zero uninventoried files |
| Surviving source snapshots | Zero mismatches; 89 pre-existing missing source files remain explicitly declared |
| Full available-byte capture/restore | 11,512 files captured and restored with matching hashes/modes, including ignored evidence and Git history |
| Independent preservation | Incomplete: temporary test storage is not independent persistent storage; owner destination pending |

The original onboarding audit measured 92,943 characters. The new common entry set is about 66% smaller; engineering routes deliberately read additional necessary specifications and evidence.

The complete available archive test was captured at `20261005T201139Z_6848c405`; its private path and attestations remain outside Git. The temporary restored copy verifies recovery mechanics, not independent durability. See [legacy gaps](LEGACY-EVIDENCE.md): unavailable originals have not been fabricated or removed from their experiment manifests.

Repeat the [contributor completion gate](../CONTRIBUTING.md) after relevant changes. Keep future dated audits explicit; current quality comes from running the checks, not this historical result. [Quality contract](../QUALITY.md) and [current project state](../CURRENT.md) remain the entry points.

## Public documentation review — 2026-10-06

Documentation polish follows [D021](../meridian-microphone/DECISIONS.md#d021--2026-10-06--public-documentation). The root README now introduces the workshop, projects and build readiness; the contributor guide defines future revision-matched build packages. No new repository files, dependencies, automation or empty hardware directories were added.

| Check | Recorded result |
| --- | --- |
| Repository gate | Refresh/check pass; generated pages rebuilt from sources; common context remains below the unchanged 32,000-character limit |
| Documentation links | Modified Markdown and LICENSE local links, heading anchors and HTML image sources checked; six external URLs verified |
| Tooling regressions | All 22 existing repository tests pass |
| Presentation | Local Markdown preview inspected with GitHub's current light/dark styles and existing artwork; status is visible on the first screen, with projects/build guidance directly below |
| Engineering boundaries | Original phase, technical readiness, blockers, stages, evidence pointers, specifications and thresholds retained; sourcing/patent policies checked for preserved requirements |
| Evidence integrity | 3,902 declared waveforms and 1,357 snapshot-file declarations checked: no damaged or uninventoried files; the same 89 pre-existing source gaps remain |
| Independent preservation | Still incomplete; no independent restored backup attestation. No research batch was created by this documentation change |

Public laboratory/prompt instructions now use repository-relative paths. Dedicated environment records, frozen evidence, old decisions and archived artwork retain their original provenance. No simulator/model/code change was made, so no new scientific verification or measurement is claimed.

Follow-up, 2026-10-06: [D023](../meridian-microphone/DECISIONS.md#d023--2026-10-06--release-status) removes the added public maturity table. Project overviews now say released or not released; the added documentation-readiness entry was removed from the register. Existing scientific records and release requirements are retained.

Follow-up, 2026-10-06: [D024](../meridian-microphone/DECISIONS.md#d024--2026-10-06--current-work-and-goals) makes the wider product range an explicit goal. The README identifies condenser-microphone research as the current work; branding describes an intended scope rather than an existing range.

## README banner review — 2026-10-06

[D025](../meridian-microphone/DECISIONS.md#d025--2026-10-06--readme-banner) uses the standard lockup on a fixed ivory background in both README headers. The existing artwork builder generates the banner and verifies exact reuse of the lockup, allowed colours and absence of external resources or live text. The original masters, all 44 raster previews and contact sheets remain byte-for-byte unchanged.

The root README was inspected with GitHub's light and dark styles; the banner loaded in both with no horizontal overflow. Modified Markdown links, repository refresh/check and all 22 tooling tests passed. Hardware status and the existing independent-backup gap are unchanged.

## Project folder rename — 2026-10-06

[D026](../meridian-microphone/DECISIONS.md#d026--2026-10-06--project-folder) renames the existing microphone project to `meridian-microphone/`. Maintained links, reading routes, licence scope, ignore rules and generated indexes use that path. Future folders include the device type; no preamp folder was created.

An available-file manifest before and after the move found all 11,516 files retained, with 11,268 frozen files unchanged in bytes and executable flags. All 3,902 inventoried waveforms/exports and surviving source snapshots retain their hashes. The same 89 source gaps and independent-backup requirement remain; the original gap ledger and dated environment records are unchanged. No research batch or hardware-status change was introduced.

Repository refresh/check and Markdown links pass. All 24 tooling tests pass, including rejection of changed, deleted or mode-changed frozen files during relocation, recognition of the original gap ledger and restoration of a backup with the earlier layout. The laboratory's `doctor` command and all 31 existing tests pass from the new folder; test scratch files were kept outside the repository. Shorter README wording keeps common reading within the unchanged 32,000-character limit.
