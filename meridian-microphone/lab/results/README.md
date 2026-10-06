# Simulation evidence storage

Storage decision: 2026-10-05, following the owner's request to keep the important project files in Git.

Git retains all compact experiment records, including failures: JSON results and optimization trials, simulator decks, parameter records, logs, source/specification snapshots, verification summaries, archive indexes and report plots. Research conclusions and evidence boundaries are unchanged.

Bulky ngspice `.raw` files and their `.raw.csv` waveform exports remain local and are excluded from Git. They have not been deleted, uploaded or moved to an external artifact store. A fresh clone therefore includes the experiment metadata but not the complete original waveform evidence. Other CSVs, such as compact archive and procurement summaries, are not excluded by this rule.

On 2026-10-06 the owner renamed the project folder to `meridian-microphone/`. All retained files moved together with the same relative laboratory paths. Frozen experiment records and environment observations retain their original recorded paths; their bytes and hashes are unchanged. Earlier private backups restore the layout they captured.

[`raw-data.sha256`](raw-data.sha256) inventories the retained experiment waveforms as of 2026-10-05. Paths are relative to the laboratory directory, now `meridian-microphone/lab/`; with the original archive available, verify them from that directory using:

```sh
sha256sum -c results/raw-data.sha256
```

This inventory identifies the original data; it does not replace or reconstruct them. Preserve raw evidence independently of Git, including failed experiments. New runs create additional raw files locally; extend the dated inventory when archiving new evidence. Re-running a recorded simulator deck is a new experiment, not a substitute for the original record.

Downloaded runtimes, local environments, caches, temporary synchronization locks and pytest aliases are also excluded. The repository retains bootstrap instructions, pinned package checksums and experiment provenance.

Following the owner's additional storage request on 2026-10-05, synthetic model/provenance test fixtures are ignored: dummy models/registries, external-include fixtures, definition-collision fixtures and fake source trees. Existing copies remain local. Real physics-control decks, simulator logs, verification summaries and failed experiments remain tracked; the whole `raw_tests/` tree is not ignored.

## Phase3 device-model evidence

[`device-model-raw-data.sha256`](device-model-raw-data.sha256) inventories 857 local waveforms from isolated device experiments and the three verification runs added during this task, including failures. [Integrity checks](../research/device_model_integrity.json) find no mismatch in declared job raw hashes. Verify from the lab directory with `sha256sum -c results/device-model-raw-data.sha256`.

[`device-model-csv-data.sha256`](device-model-csv-data.sha256) inventories all 658 retained waveform CSV exports, including superseded and failed experiments, as of the same date. Verify from the lab directory with `sha256sum -c results/device-model-csv-data.sha256`. CSV export bytes and immutable experiment records were not changed by the storage cleanup. The committed comparison plots can be viewed directly; regenerating them with `research/render_device_report.py` requires restoring the original local CSV archive at the inventoried paths. Re-running characterization creates a new experiment and does not restore the original evidence.

Vendor models/datasheets/archives/acquisition observations and their frozen copies remain local and ignored because redistribution permission is not established. Reproducible URLs/hashes and acquisition instructions remain tracked; a fresh clone does not inherit those copyrighted bytes. Decks, logs, compact numerical comparisons and authored snapshots remain tracked.
