# Semiconductor evidence library

Read [the validation report](../../research/device_model_validation.md), [registry](registry.yaml), [reference conditions](references.yaml) and [coupled controls](corners.yaml) together. No complete production device set is qualified. Scoped agreement does not establish production noise, manufacturing yield, floating P48 operation or a build-ready BOM.

## Reproduce acquisition and characterization

From `meridian-microphone/lab`, with the documented runtime installed:

```sh
.venv/bin/python models/semiconductor/acquire.py
.venv/bin/python models/semiconductor/prepare.py
MPLCONFIGDIR=/tmp/meridian-mpl .venv/bin/python models/semiconductor/characterize.py
MPLCONFIGDIR=/tmp/meridian-mpl .venv/bin/python models/semiconductor/validate_corners.py
./run doctor
./run verify
```

Acquisition uses public manufacturer URLs and pins bytes in [acquisition.yaml](acquisition.yaml). It neither logs in nor submits an agreement. Redistribution permission was not established, so original vendor archives/models/datasheets and the structural child remain in the ignored local `vendor/` directory. Fresh checkouts reacquire the files. If an explicit licence acceptance becomes required, stop that acquisition and record the gap; acceptance is not authorized. Changed bytes are retained as failures and cannot silently replace audited versions. The recorded 2N7002 response is HTML: acquisition exits **2** for that entry while retaining usable downloads. A changed challenge response may instead fail its hash; neither is a model.

`prepare.py` preserves the original BC846B bytes and creates the one-node structural hypothesis. It refuses a changed parent or existing child. No electrical parameter is fitted. `characterize.py` generates isolated DC/AC/noise/transient decks and creates a unique `results/device_models/` directory with a frozen source snapshot, exact model/version hashes, logs, ASCII raw files, CSVs, comparisons, deterministic-grid seed state and parents. Exit **2** reports observed disagreements/errors. Use `--models <registered-ID> ...` to repeat affected parts and `--parent-experiment <preserved-ID>` to link revisions. Never acquire or edit shared sources while evaluation runs.

Waveforms and their CSV exports are preserved locally and ignored by Git; the [storage record](../../results/README.md) links their checksum inventories. A fresh clone retains compact results and comparison plots. Regenerating the recorded plots requires the original local CSV archive; acquisition and a new characterization run do not recreate the original experiment identity.

`validate_corners.py` independently tests analytic controls in ngspice and explicitly expects the retained r1 cutoff-limit failure. Success means the failed parent and feasible r2 subset were reproduced; it grants no production-corner coverage. Original r1 files remain under `proposals/`. Guaranteed limits are not probability distributions; r2 does not remove the uncovered manufacturer range.

## Future candidate provenance

Declare exact registry IDs in `topology.yaml`, for example:

```yaml
semiconductor_models:
  - opa197_pspice
```

The harness resolves declarations against frozen registry/file hashes, records complete version metadata in candidate provenance/jobs, and supplies frozen absolute include paths. Unregistered includes, missing/changed files, failed acquisition and duplicate SPICE definitions are rejected. Local model names retain subcircuit namespaces. Separate JFE150 files repeat shared definitions: use the one combined `jfe150_pspice` file for multiple JFE150 subcircuits in one deck. Do not include original BC846B and its child together.

TI files require explicit ngspice PSpice compatibility initialized before parsing. Ordinary files use native syntax. Identity provenance does not bypass qualification, sourcing or patent gates. Macro global-ground references require floating-common-mode testing before use with the floating microphone ground.

Both bipolar files omit KF/1/f. A converged white-noise-only device cannot qualify a low-noise input. No safe capsule polarization rating follows from electronics simulation. No device selection or hidden trimming is permitted.
