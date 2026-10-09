# Laboratory setup and commands

[Laboratory](../README.md) · [Circuit interface](circuit-interface.md)

## Environment

Recorded environment: ngspice 47, Python 3.12.14, NumPy 2.4.2, SciPy 1.17.1, pandas 3.0.1, Matplotlib 3.10.8, PyYAML 6.0.3, pytest 9.0.2. See [host record](../tools/environment.json), [requirements](../requirements.txt) and [package checksums](../tools/packages.sha256). Extracted runtime archives and original licence notices stay local; they are third-party distributions.

On a compatible Linux x86_64 host with internet access and Python 3.12:

```sh
cd meridian-microphone/lab
MERIDIAN_PYTHON=python3.12 bash tools/bootstrap.sh
./run doctor
./run verify
```

`MERIDIAN_PYTHON` can point to the bundled desktop Python. Bootstrap downloads pinned Arch packages. Host glibc, ncurses, readline, C++/OpenMP and X11/Xt/Xmu/Xpm must be compatible. On other platforms install/build ngspice 47 and set `MERIDIAN_NGSPICE`. Record platform/library differences; do not assume numerical identity. An official archive may replace an unavailable mirror only with the same pinned checksum. Bundled simulator paths require no spaces because of codemodel parsing.

Install the root [quality environment and hooks](../../../docs/maintaining-repository.md#local-setup) in each checkout; these are separate from the lab environment.

## Research commands

```sh
./run evaluate fixture_0001 --samples 16 --seed 34047
.venv/bin/python optimization/optimize_values.py fixture_0001 \
  --parameters BIAS_R POLAR_R OUTPUT_C --iterations 6 --seed 34047
.venv/bin/python search/generate_topology.py
.venv/bin/python search/selection.py
.venv/bin/python search/loop.py --evaluations 1 --samples 16
.venv/bin/python tools/controls/parts_database.py --counts
.venv/bin/python tools/controls/parts_database.py --audit
```

Evaluation exit 2 is a rejected/incomplete qualification, including for the ideal fixture. Optimization returns a retained proposal; actual-BOM realization and the full suite are required before acceptance. Noise optimization on that ideal fixture requires `--legacy-fixture`. Prerequisite holds and no feasible point are valid outcomes; do not relax budgets or requirements.

Use [structural registration](../search/mutate.py) for new children with parents/hypotheses; value-only changes use the optimizer. The [diversity archive](../search/INDEX.md) keeps niches separate from eligibility. Rebuild with `search/archive.py` only while evaluators are idle.

## Reproduce derived reports

```sh
.venv/bin/python tools/reporting/render_initial_report.py
.venv/bin/python tools/reporting/render_device_report.py
.venv/bin/python tools/reporting/compare_architectures.py
.venv/bin/python tools/reporting/render_robust_report.py \
  results/optimization_batches/20261009T090126Z_4735cd2a
.venv/bin/python tools/reporting/verify_robust_batch.py \
  results/optimization_batches/20261009T090126Z_4735cd2a
```

Restore original private evidence first where required. Report generation creates derived outputs; rerunning simulation creates a new experiment and cannot recover old waveforms. Initial reporting selects the verification belonging to its original source cohort. Current software verification is recorded separately.
