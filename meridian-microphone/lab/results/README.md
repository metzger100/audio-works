# Simulation evidence storage

Git retains authored source/spec/implementation snapshots, decks, logs, compact results/trials, reports and checksum inventories, **including failures**. Original raw waveforms/exports and vendor bytes remain private/ignored; a clone cannot reproduce full original evidence without restoring them. Ignoring evidence never authorizes deletion. Reruns create new experiments, not restored originals.

## Evidence map

| Research | Current findings / dated inventory or receipt |
| --- | --- |
| Foundation | [Phase 0](../research/architectures/initial/phase0-report.md), [raw inventory](raw-data.sha256) |
| Original device controls | [Validity](../research/devices/device-model-validation.md), [raw](device-model-raw-data.sha256), [CSV](device-model-csv-data.sha256), [integrity](../research/devices/device-model-integrity.json) |
| MOS follow-up | [258 files](evidence-20261009T070957Z-3092a887.sha256), [integrity](../research/device_model_integrity_2026-10-09.json) |
| Six mechanisms | [First batch](../research/architectures/first-architecture-batch.md), [1981 files](evidence-20261009T082728Z-78caabc6.sha256), [integrity](../research/first_architecture_integrity_2026-10-09.json) |
| Robust optimization | [Findings](../research/architectures/optimization/robust-optimization-report.md), [4198 files](evidence-20261009T091504Z-58b871ef.sha256), [recovery](../research/robust_optimization_preservation_2026-10-09.json) |
| Comparison001 | [Findings](../research/architectures/architecture-comparison-001.md), [derived evidence](reports/architecture-comparison-001/INDEX.md), [71 files](evidence-20261009T121907Z-3c4139cd.sha256) |
| Parts001/002 | [001](../research/devices/parts-database-expansion-001.md), [002](../research/devices/parts-database-expansion-002.md), source-stable controls and original failures |
| Latest repository/lab checks | [Validation](../../../docs/validation.md), [generated evidence index](../../../docs/evidence.md) |

[Complete navigation](INDEX.md) links every retained record/inventory. Historical test counts belong to their original cohorts; current counts are in validation. Derived archive/fronts are rebuildable views, never replacement evidence. Every implementation remains unqualified.

## Verify and preserve

Inventory paths are laboratory-relative. For example, from the lab:

```sh
sha256sum -c results/raw-data.sha256
```

Use the root [evidence tools](../../../docs/maintaining-repository.md#private-evidence) for additional dated inventories, complete source/job hash verification, idle capture and private restore checks. Do not replace earlier inventories. A same-computer recovery copy does not establish independent persistent preservation. **89pre-existing source gaps and independent backup remain incomplete.** Exact private destinations stay outside Git.

The2026-10-06 folder rename preserves relative laboratory paths; original absolute/legacy paths and all frozen bytes remain unchanged. [Path migrations](../../../docs/config/path-migrations.json) resolve current authored locations. Vendor terms/notices remain original; no redistribution permission is inferred. Downloaded runtimes/environments/caches and synthetic provenance fixtures are excluded, while real physics-control decks/logs/failures remain retained. [Licensing](../../../LICENSE) and [legacy gaps](../../../docs/legacy-evidence.md) retain authority.
