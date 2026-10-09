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

## Device-model follow-up, 9 October 2026

The separately dated [`evidence-20261009T070957Z-3092a887.sha256`](evidence-20261009T070957Z-3092a887.sha256) adds 258 raw/CSV files from three MOS-model batches and the 38-test verification, including the failed observer parent. Previous inventories and frozen evidence were not modified. [New-record integrity](../research/device_model_integrity_2026-10-09.json) verifies 364 source snapshots and 194 declared device waveform/export hashes without mismatch.

The newly acquired Vishay archive, original copyright notice, model guide, datasheet and their frozen copies remain local and ignored. No redistribution permission was established. [Acquisition](../models/semiconductor/acquisition.yaml) and [current validation](../research/device_model_validation.md) pin exact versions, compatibility, reference conditions, failures and missing behavior. A new run creates new evidence; it does not recover the original archive.

Available bytes can be verified with the root evidence tool; 89 pre-existing missing legacy source files remain disclosed. Independent persistent backup/restore coverage remains incomplete until an owner-controlled destination is available. Temporary local recovery verification does not establish that coverage.


## First six-mechanism architecture batch, 9 October 2026

[Architecture report](../research/first_architecture_batch.md) links six original DUT attempts and nine preserved children, final evaluations, realized intended-quantity BOMs and two isolated carrier controls. Final verification has 45 passing regressions; every candidate remains unqualified. [Batch integrity](../research/first_architecture_integrity_2026-10-09.json) verifies 62 new run/control/verification records and declared source/implementation/deck/raw hashes, including failures and analysis repairs.

The separately dated [new inventory](evidence-20261009T082728Z-78caabc6.sha256) adds 1981 waveform/export files. Previous declarations and frozen evidence remain. Raw/CSV and vendor copies stay local/ignored under the existing storage boundary; no deletion is authorized. Source observations, model IDs, seeds, solver settings and parent relationships remain in original records.

The isolated bridge/demodulator is explicit ideal/analytic evidence; successful deterministic recovery does not qualify P48 integration, periodic noise or oscillator/mixer power. Available new bytes are verified, while 89 legacy sources and independent persistent backup coverage remain incomplete. The batch report records private local capture/restore checks separately.

## Scoped robust optimization, 9 October 2026

[Report](../research/robust_optimization_report.md): six budgeted optimization records, 17 full-suite reevaluations and nine realized/structural children remain unqualified. [Batch](optimization_batches/20261009T090126Z_4735cd2a/evaluation.json) retains independent validation, exact source/model/spec cohorts and all adverse/error cases. [Integrity](../research/robust_optimization_integrity_2026-10-09.json) verifies 13,804 declared files without hash errors.

[New inventory](evidence-20261009T091504Z-58b871ef.sha256) adds 4,198 waveforms/exports, including failed and repaired regression controls. Original inventories/snapshots remain unchanged. Root evidence verification has zero damaged/uninventoried files; the same 89 missing legacy sources remain disclosed.

[Private recovery receipt](../research/robust_optimization_preservation_2026-10-09.json) records idle capture and restore of 46,629 available files. Actual private storage paths stay in ignored local attestations. This same-device copy cannot establish independent persistent preservation or recover the legacy originals. No simulation/procurement/patent/physical gate is promoted by these checks.

## Intermediate architecture comparison 001, 9 October 2026

[Comparison](../research/architecture_comparison_001.md), [generated tables](reports/architecture_comparison_001/tables.md) and [machine-readable evidence](reports/architecture_comparison_001/architecture_comparison_001.json) retain six representative families, original failures and exact identities. Four static plots, netlist connectivity graphs and separate research Pareto projections reproduce from original local evidence with `research/compare_architectures.py`. The physical-qualified front remains empty.

[Provenance](reports/architecture_comparison_001/provenance.json) verifies 9,117 declared files; repeated rendering reproduces 34 outputs byte-for-byte. [Verification](verification/20261009T121724Z_12bf12df/verification.json) has 61 passing laboratory regressions and unchanged frozen sources. The [new inventory](evidence-20261009T121907Z-3c4139cd.sha256) adds 71 waveform/export files without changing previous declarations. [Validation](../research/architecture_comparison_001_validation.json) and [private recovery coverage](../research/architecture_comparison_001_preservation.json) retain incomplete independent preservation and 89 missing legacy originals. Delivered costs, Phase 8 patent screening and physical qualification remain incomplete.

## Parts expansion001 controls

[Report and reproduction](../research/parts_database_expansion_001.md) index three sequential immutable device_models records:20261009T133250Z_parts_ec54d567 (driver/fixture failure),20261009T133422Z_parts_9ee64bfd (source-integrity failure from live log), and20261009T133651Z_parts_d3c30763 (49jobs7errors, stable source). Parent records, all raw/deck/log/CSV hashes and unqualified states remain. Additional inventories and local recovery receipts are separate; no independent backup completion inferred.

## Parts strengthening002

The [current report](../research/parts_database_expansion_002.md) retains46 isolated jobs/21errors and source-stable frozen drivers/plans/models. Software/provenance checks remain separate from behavior, sourcing, patent, measurements and independent backup.
