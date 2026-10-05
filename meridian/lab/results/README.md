# Simulation evidence storage

Storage decision: 2026-10-05, following the owner's request to keep the important project files in Git.

Git retains all compact experiment records, including failures: JSON results and optimization trials, simulator decks, parameter records, logs, source/specification snapshots, verification summaries, archive indexes and report plots. Research conclusions and evidence boundaries are unchanged.

Bulky ngspice `.raw` files remain at their original local paths and are excluded from Git. They have not been deleted, uploaded or moved to an external artifact store. A fresh clone therefore includes the experiment metadata but not the complete original waveform evidence. References to raw files in immutable experiment records still describe the original local archive.

[`raw-data.sha256`](raw-data.sha256) inventories the retained experiment waveforms as of 2026-10-05. Paths are relative to `meridian/lab/`; with the original archive available, verify them from that directory using:

```sh
sha256sum -c results/raw-data.sha256
```

This inventory identifies the original data; it does not replace or reconstruct them. Preserve raw evidence independently of Git, including failed experiments. New runs create additional raw files locally; extend the dated inventory when archiving new evidence. Re-running a recorded simulator deck is a new experiment, not a substitute for the original record.

Downloaded runtimes, local environments, caches, temporary synchronization locks and pytest aliases are also excluded. The repository retains bootstrap instructions, pinned package checksums and experiment provenance.
