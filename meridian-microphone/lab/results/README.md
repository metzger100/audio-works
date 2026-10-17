# Simulation evidence storage

GitHub holds committed snapshots,decks,logs,compact results/reports and inventories,including failures. Keep local/ignored waveforms,exports and vendor bytes for reproduction. Reruns are new experiments.

## Evidence map

| Research | Current findings / dated inventory or receipt |
| --- | --- |
| Foundation | [Phase 0](../research/architectures/phase0-report.md), [raw inventory](raw-data.sha256) |
| Original device controls | [Validity](../research/devices/device-model-validation.md), [raw](device-model-raw-data.sha256), [CSV](device-model-csv-data.sha256), [integrity](../research/devices/device-model-integrity.json) |
| MOS follow-up | [258 files](evidence-20261009T070957Z-3092a887.sha256), [integrity](../research/device_model_integrity_2026-10-09.json) |
| Six mechanisms | [First batch](../research/architectures/first-architecture-batch.md), [1981 files](evidence-20261009T082728Z-78caabc6.sha256), [integrity](../research/first_architecture_integrity_2026-10-09.json) |
| Robust optimization | [Findings](../research/architectures/optimization/robust-optimization-report.md), [4198 files](evidence-20261009T091504Z-58b871ef.sha256), [recovery](../research/robust_optimization_preservation_2026-10-09.json) |
| Comparison001/002 | [001](../research/architectures/architecture-comparison-001.md), [002](../research/architectures/architecture-comparison-002.md); separate cohorts;[001 inventory](evidence-20261009T121907Z-3c4139cd.sha256) |
| Parts001/002 | [001](../research/devices/parts-database-expansion-001.md), [002](../research/devices/parts-database-expansion-002.md), source-stable controls and original failures |
| Capsule001 | [Envelope](../research/capsules/evidence-envelope-001.md), [finite cohorts and integrity receipt](../research/capsules/analysis-001.md); original assumed ranges and prior failures retained |
| Prerequisites001 | [Findings](../research/devices/simulation-prerequisites-001.md), [three frozen cohorts and integrity](../research/devices/simulation-prerequisites-integrity-001.json);119 jobs,19 execution errors, scoped follower H2/H3 only |
| Focused001 | [Bias/filter/driver findings](../research/architectures/focused-hypotheses-001.md), [new-byte integrity](../research/architectures/focused-integrity-001.json);parents,preflight and recovery failures preserved |
| Diverse001 | [Independent mechanisms](../research/architectures/diverse-prerequisites-001.md),53 simulator attempts/15 retained errors,32 seeded ideal records; inventories in each frozen cohort |
| Latest repository/lab checks | [Validation](../../../docs/validation.md), [generated evidence index](../../../docs/evidence.md) |

[Navigation](INDEX.md) links records/inventories. Counts belong to their cohorts; current checks are in validation. Derived fronts never replace evidence. All implementations remain unqualified.

## Verify and preserve

Inventories use laboratory-relative paths. From the lab:

```sh
sha256sum -c results/raw-data.sha256
```

[Root evidence tools](../../../docs/maintaining-repository.md#private-evidence) create additional dated inventories and verify source/job bytes. Preserve earlier records; private capture/restore is optional and reports its actual scope. A repository pass does not recover historical missing originals. Keep private destinations/credentials outside Git.

[Path migrations](../../../docs/config/path-migrations.json) resolve renamed authored files; frozen bytes and vendor notices remain unchanged. Runtimes/caches/synthetic fixtures are excluded; real decks/logs/failures remain. [Licensing](../../../LICENSE) and [storage policy](../../../docs/decisions/2026-10-11-github-canonical.md) apply. Ignored originals are outside GitHub coverage.
