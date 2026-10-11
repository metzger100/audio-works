<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Capsule envelope 001 finite analysis receipt — 11 October 2026

[Findings](evidence-envelope-001.md) · [Predeclared scenario ledger](scenarios-001.yaml) · [Independent equations](physics-001.md) · [Decision record](decisions-001.md). This receipt describes documentary and simulated controls; no physical measurements or qualified implementation exist.

## Cohorts and retained failures

| Frozen cohort | Treatment and evidence |
| --- | --- |
| [First circuit/math cohort](../../results/mechanism_controls/20261011T171905Z_capsule_b306ab46/manifest.json) | Retained parent. Tiny-value math comparisons used the default absolute tolerance, so its math acceptance receives no credit. |
| [Corrected circuit/math cohort](../../results/mechanism_controls/20261011T172018Z_capsule_e4938198/manifest.json) | Authoritative for this finite analysis: zero absolute tolerance in independent controls. Source, frozen snapshot and original-source checks pass; [integrity](../../results/mechanism_controls/20261011T172018Z_capsule_e4938198/integrity.json). |
| [First supplementary cohort](../../results/mechanism_controls/20261011T172829Z_capsule_excess_22732ac7/plan.json) | Retained parent; subsequent lint correction removes one unused array, with no change to equations or results. |
| [Supplementary rerun](../../results/mechanism_controls/20261011T173125Z_capsule_excess_27afa7ab/plan.json) | Twelve isolated-node loss/current/sensitivity combinations, frozen six inputs and source-stability checks; [integrity](../../results/mechanism_controls/20261011T173125Z_capsule_excess_27afa7ab/integrity.json). |

The shared locked specification remains `f5201295bef7855bced5157cf9727f95d057c2b17589f9f55b8fd6fb17445bbd`. Every circuit batch freezes shared sources, JSON retrieval/query ledgers, four candidate implementation manifests and exact model inputs before execution. Every job retains rendered deck, model checksums, simulator log and original outputs. The original comparison001 baseline cohort and its full suites are preserved and not pooled with this new cohort. Frozen sources matched at run start/end; later authored report/navigation updates do not change the run's snapshots.

The declared finite budget is 14 scenarios × 4 candidates = 56 DC/AC sets, 42 JFET noise jobs and 6 nominal refinement jobs; no optimizer, random seed or fitted likelihood. All 56 sets completed: **34 DC/AC screen passes, 22 failures, zero execution errors**. A screen pass is not qualification. All three nominal refinement pairs passed the separately declared 0.01 dB response / 0.001 relative noise tolerances. The largest absolute response change is 0.002234 dB and largest relative noise change is 0.0001844. No finer numerical grid is confused with greater uncertainty coverage.

The independent controls check dimensional relationships, central finite-difference capacitance derivative, membrane averaging, positive capacitance-matrix eigenvalues and analytical versus numerical RC thermal integrals. Zero absolute tolerance prevents tiny SI magnitudes from passing trivially. Full-band RC noise is kT/C, distinct from the 20 Hz–20 kHz integral. Softening ratios are assumed local diagnostics, not pull-in/safety calculations.

The additional material control retains [its first cohort](../../results/mechanism_controls/20261011T173900Z_capsule_material_7c0f6309/plan.json) and [the lint-corrected rerun](../../results/mechanism_controls/20261011T173920Z_capsule_material_28cd5584/plan.json). Each evaluates exactly six coupled gap examples and four sensitivity/material endpoint checks. [Annular table](../../results/mechanism_controls/20261011T173920Z_capsule_material_28cd5584/annular.csv), [material endpoint table](../../results/mechanism_controls/20261011T173920Z_capsule_material_28cd5584/sensitivity-material.csv) and [integrity](../../results/mechanism_controls/20261011T173920Z_capsule_material_28cd5584/integrity.json) retain the failed disk/low-sensitivity transfers. No circuit result or locked range changes. The printed June2003 Mylar bulletin date differs from search/hosting metadata; the grade92A typical data supply no capsule-film allowable stress.

## Tables and plots

- [All circuit scenario rows](../../results/mechanism_controls/20261011T172018Z_capsule_e4938198/scenarios.csv): individual failure states, DC polarization, transfer and conditional unweighted electronics noise. The full per-case JSON retains actual parameters/jobs. No acoustic noise, noise covariance or calibrated system rating is supplied.
- [Response and noise sensitivity plot](../../results/mechanism_controls/20261011T172018Z_capsule_e4938198/scenario-sensitivity.png): includes failed leakage cases; 0017/0019 traces overlap at this scale. The report table resolves their response differences.
- [Independent calculations](../../results/mechanism_controls/20261011T172018Z_capsule_e4938198/math-controls.json) and [nominal refinement](../../results/mechanism_controls/20261011T172018Z_capsule_e4938198/refinement.json).
- [Supplementary spectra table](../../results/mechanism_controls/20261011T173125Z_capsule_excess_27afa7ab/supplementary.csv) and [plot](../../results/mechanism_controls/20261011T173125Z_capsule_excess_27afa7ab/supplementary.png).

At the assumed 20 mV/Pa mathematical reference, 40 V and isolated 70 pF + 2 pF node, assumed tan(delta)=1e-4/1e-3 produces 0.1563/0.4944 µV RMS over 20 Hz–20 kHz. Hypothetical 1/10 fA/sqrt(Hz) excess current at 100 Hz with 1/f PSD produces 0.7815/7.815 µV RMS. Node voltage is the directly calculated quantity; the table's 12.06/38.14/60.29/602.89 µPa equivalents divide by an explicitly assumed isolated sensitivity. They are not candidate results or intrinsic acoustic bounds. Quadrature versus 1000-point logarithmic sampling differs by at most 4.782e-5 relative. Sources support mechanisms, not these assumed amplitudes.

## Reproduction and preservation

From `meridian-microphone/lab`, after the established bootstrap/model prerequisites:

```sh
MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python tools/reporting/capsule_envelope.py
MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python tools/reporting/capsule_excess_controls.py
MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python tools/reporting/capsule_material_controls.py
```

Each invocation creates a distinct timestamp/UUID batch and preserves errors. The main runner requires the original private source bytes at the recorded relative roots with matching SHA256; reacquired bytes are a new retrieval, not silently substituted originals. The supplementary script is an isolated analytic diagnostic, not an implementation comparison. No archive/latest/archive-candidate promotion occurs.

Each of the six research batches has its own dated `batch.sha256` listing all source/deck/log/raw/table/plot bytes with laboratory-relative paths. Original public documents remain ignored under the three private roots in the retrieval ledgers; 26 acquired originals and the HTTP429 failure body retain hashes. Two Shure PDF revisions are not independent experiments. The initial DNS failures and browser-provider errors remain recorded. GitHub covers committed authored/compact evidence only; private originals and raw outputs remain required locally.

Full lab verification passed **94 tests**. The final formatter changed only whitespace/quotes in the three new scripts; identical parsed AST hashes were verified, with the frozen scripts retained in their original cohorts. No candidate/model/spec file was changed; this capsule-only analysis therefore supplements earlier full candidate suites without claiming a new complete nonlinear/startup/production qualification. [Validation](../../../../docs/validation/2026-10-11-capsule-envelope.md) and [machine integrity receipt](integrity-001.json) record37 Git/recovery and23 fast regressions, all3016 new batch files verified, and the unchanged89 historical missing snapshots separately.
