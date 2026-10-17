<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Comparison002 execution and reproduction — 17 October 2026

[Main report](architecture-comparison-002.md) · [Finite plan](architecture-comparison-002.yaml)

The common batch is [9392cebd](../../results/mechanism_controls/20261017T090130Z_comparison002_9392cebd/results.json). Its [frozen plan/holdout values](../../results/mechanism_controls/20261017T090130Z_comparison002_9392cebd/plan.json) and [source/BOM/backend manifest](../../results/mechanism_controls/20261017T090130Z_comparison002_9392cebd/manifest.json) bind exact netlists, per-reference BOMs, parents, models, specifications, code and documentary records. All eight suites share spec `f5201295bef7855bced5157cf9727f95d057c2b17589f9f55b8fd6fb17445bbd` and one suite/source identity; the provenance records the complete suite hash. ngspice47 binary, wrapper and loaded XSPICE modules were frozen and checked; Python3.12.14,NumPy2.4.2,SciPy1.17.1 and simulator/software versions are recorded. Sources were unchanged through execution.

Seed134047 belongs to the ordinary suite. Its passive-count-dependent random draws remain unpaired and supply no cross-candidate yield comparison. Seed144047 generates16 common quantile vectors over the union of keys: external capsule/interface values match, while each design retains its own passive ranges, including3.3kΩ versus1kΩ source degeneration. No new training or holdout-based design selection occurred. These uniform/log-uniform artificial stresses are not production populations; guaranteed/typical device limits are not distributions.

The optional input-admittance annotation initially assumed the fixed-bias node name on both servos:82 cells retained a reporting error after their DC/AC/noise jobs completed. The [finite read-only recovery](../../results/reports/architecture_comparison_002/recovery-plan.json) reads the actual `Rbias/Cbiasstray` return and saved traces; [original errors and successor extractions](../../results/reports/architecture_comparison_002/recovery.json) remain separate. All203 cells stay in both original and corrected summaries. No solver error is recovered as a pass. Renderer development also retained a missing-import regression failure, the unchanged text-budget rejection for the larger connectivity graph and a provenance pagination failure; regression/validation records describe their repairs. Full raw suites and failure logs remain canonical; compact views reference them rather than duplicate them.

## Reproduction and storage

From the lab, with original private waveforms/vendor/source bytes available:

```sh
PYTHONPATH=src MPLCONFIGDIR=/tmp/meridian-comparison-mpl .venv/bin/python tools/reporting/compare_architectures_002.py
./run doctor
./run verify
```

The renderer verifies frozen code/input/job/raw hashes, reconstructs conditional spectra and recovery, and writes bounded static/machine outputs. `tools/controls/comparison_cohort_002.py` is the finite evaluator; it refuses an already registered cohort. Its frozen original preserves the annotation defect; the active version resolves the actual netlist return and has an independent RC regression. A new simulation requires a new dated cohort/plan identity; it cannot overwrite this evidence or pool previous cohorts. [Validation](../../../../docs/validation/2026-10-17-comparison-002.md) records link/value/hash checks, dated inventories and original-evidence limitations separately from repository checks. GitHub covers committed authored/compact evidence; ignored original/vendor bytes remain local. No purchase, contact, licence acceptance, commit, push or external publication occurred.
