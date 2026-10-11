<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Simulation prerequisite validation — 2026-10-11

[Findings](../../meridian-microphone/lab/research/devices/simulation-prerequisites-001.md) · [Revision decision](../../meridian-microphone/lab/research/devices/simulation-prerequisites-decisions-001.md) · [Available-byte integrity](../../meridian-microphone/lab/research/devices/simulation-prerequisites-integrity-001.json).

The locked M100 Meridian MIC-34-M/MIC-34-C/K47FRB baseline and all scientific thresholds/budgets remain unchanged. Three unique finite cohorts retain119 jobs and19 execution errors. Isolated follower H2/H3 supports only the specified numerical fixture; full microphone H2/H3/THD and electronics clipping/headroom remain unavailable. No model/candidate promotion, physical measurement, procurement or legal clearance follows.

| Check | Observed result |
| --- | --- |
| Final full laboratory verification | [109 tests pass](../../meridian-microphone/lab/results/verification/20261011T183943Z_8f8299de/verification.json); source unchanged true; locked spec SHA256 `f5201295bef7855bced5157cf9727f95d057c2b17589f9f55b8fd6fb17445bbd` |
| Actual-fix regressions |15 focused tests: independent product-to-sum H1–H10/THD, harmonic phases/adaptive sampling, magnitude/phase/DC drift, partial/startup retention, headroom drift and timeout log/process-group preservation |
| Shared repository checks |37 Git/recovery and23 fast regressions pass; pinned correctness/format pass; refresh, audit and working-file check pass |
| Finite numerical evidence | Three SPICE cohorts:119 jobs,19 execution errors. Separate [frozen replay](../../meridian-microphone/lab/results/device_models/20261011T183846Z_extraction_d0b338ed/results.json):60 phasor fits, its earlier60-fit parent retained;0 new SPICE jobs; source/input unchanged; H2/H3 numerical refinement passes |
| Batch/source integrity |990 declared files in five complete inventories verify;10 retrieval bodies (9 documents,1 HTML failure),85 archive members and4 nominal core comparisons verify |
| New waveform inventory | [284 additional originals](../../meridian-microphone/lab/results/evidence-20261011T183333Z-07e25ed2.sha256), including failed/intermediate/final verification waves; plus [71 final phasor-verification originals](../../meridian-microphone/lab/results/evidence-20261011T184234Z-646bf44f.sha256); original three cohort waveforms are in their separate inventories |
| Full original-evidence audit | [Final preservation receipt](2026-10-11-prerequisite-phasor-preservation.json) reports completeness separately from repository consistency |

The first full verification retained106 passes and two failed legacy warning mocks in [failed parent](../../meridian-microphone/lab/results/verification/20261011T182410Z_3a409d41/verification.json). Their old subprocess interface no longer exercised the runner; successor tests retain exact warning/advisory requirements. Three intermediate108-test passes remain as separate records; the final cohort includes the phase-drift repair and extraction replay tooling. An initial root regression invocation encountered a registered validation page before creation; all37 setup errors were navigation setup errors. Maintained CSV exports now use LF endings; their original scientific waves/decks/source snapshots remain unchanged.

Current runtime-library hashes are supplemental; they do not reconstruct the initial cohorts' omitted per-library freeze. Earlier web query/timestamp/raw-response metadata gaps remain explicit in the query ledger. Generic/TINA byte identity and four matching nominal parameter cores supply duplicate evidence only. Exact PSpice reference dependencies are missing and TINA binaries lack an installed backend. No independent measured nonlinear/noise extraction, full open-emitter capacitance, joint process/SOA/thermal or floating OPA qualification follows.

The repository's original-evidence audit is a separate coverage state. Pre-existing89 historical snapshot gaps are declared in [original gap record](../history/2026-10-11/legacy-source-gaps.json); this task does not restore or invent those bytes. Final counts and exact gap-set comparison are in the preservation receipt. Checks establish local consistency and available-byte integrity, not physical model validation or remote synchronization. All authored changes remain local; no publication, contact, purchase or licence acceptance is authorized.

The earlier [preservation audit](2026-10-11-prerequisite-preservation.json) remains as parent. Phasor settling closes a measured0.04rad phase-step acceptance gap at the unchanged1e−3 limit. No scientific threshold, model or timeout budget changed.
