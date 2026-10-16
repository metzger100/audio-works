# Folder-layout validation — 2026-10-11

[Decision](decisions/2026-10-11-folder-layout.md) · [Folder map](repository-layout.md) · [Previous reading cleanup](validation/2026-10-11-reading-and-data-layout.md)

The folder audit identified duplicate page containers and single-document research wrappers. Consolidation reduces the active tree without merging candidate identities, experiments or current findings with originals.

| Measure | Before | After |
| --- | --- | --- |
| Maintained folders | 206 | 167 (19% fewer) |
| Split structured-data folders | 85 | 56 shared `data-pages` folders |
| Maintained research subjects | 12 | 8 |
| Maximum maintained directory depth | 8 | 7 |
| Generated navigation/evidence outputs | 233 | 201 |

BOM and topology pages share their candidate's page container; document names and stable hashes prevent namespace overlap. Architecture sources, mechanisms, benchmark guidance and foundation findings belong to the architecture hub; manufacturer-source interpretation belongs to devices. Existing optimization, candidates, models and executable roles retain useful boundaries.

The baseline's 16,064 original-only folders remain preserved. New failed/passing verification cohorts add their own frozen snapshots and jobs. Audit reports those folders separately from maintained material, excluding local environments and ignored caches; the total filesystem count is not an active-structure score.

| Verification | Result |
| --- | --- |
| Scientific records | All 157 compared resolved documents retain exact values/types, identities, conditions and parent relationships |
| Existing originals | All 41,852 baseline files retain hashes and modes; original declarations are identical |
| Repository regressions | 23 fast and 33 Git/recovery tests pass; pinned lint/format pass |
| Laboratory verification | [80 tests pass](../meridian-microphone/lab/results/verification/20261011T122931Z_d7b00d15/verification.json); source unchanged true; all 872 captured source files match current files |
| Generated layout | Deterministic refresh; removed wrappers absent; every maintained file reachable; no stale output, text-size violation or repeated substantial prose |
| Private evidence | [142 new original files inventoried](../meridian-microphone/lab/results/evidence-20261011T123030Z-defb051e.sha256); zero damaged/uninventoried files; 85,875 captured files restored with matching bytes/modes |
| Gate runtime | Working check passed in 18.74s while private restoration ran; all four blocking gates use the same checks |
| Mechanical enforcement | Existing four hooks and CI reject legacy document-specific partitions and nested page wrappers; audits expose folder counts by root |

The [failed verification](../meridian-microphone/lab/results/verification/20261011T122847Z_dfbbc8e8/verification.json) remains intact. One regression expected the previous folder name; its replacement verifies page inclusion and an identical restored implementation manifest. Other fixtures prove independent sibling-page replacement, format separation, rejection of foreign namespaces/symlinks before writes, correct link rebasing and rejected commits leaving staged/working content unchanged.

This changes serialization/navigation, without threshold, budget or qualification changes. New verification evidence is inventoried and integrity-checked; private restoration is verified. Synthetic unsafe-input fixtures remain private under the existing scratch policy, with outcome/log/source records retained. Current storage requirements follow the [GitHub owner decision](decisions/2026-10-11-github-canonical.md). Remote publication and settings are unchanged.

Latest continuation: [GitHub storage-policy checks](validation/2026-10-11-github-canonical.md). Earlier rows above record the requirements and outcomes observed at their dates; current storage authority follows the new owner decision.

Latest capsule continuation: [documentary envelope and integrity checks](validation/2026-10-11-capsule-envelope.md), retaining the historical original-byte limitations separately from repository checks.

Latest device continuation: [simulation prerequisites and preservation](validation/2026-10-11-simulation-prerequisites.md);109 lab tests pass, scoped follower H2/H3 supported, microphone nonlinear/headroom held.

Latest focused engineering continuation: [A/B/C hypotheses and completion checks](validation/2026-10-12-focused-hypotheses.md);0025 supplies a resolved conditional filter benefit while bias/startup and qualification failures remain.
