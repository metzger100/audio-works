# Simulation evidence storage

GitHub is canonical for authored source/spec/implementation snapshots, decks, logs, compact results/trials, reports and checksum inventories, **including failures**. Original raw waveforms/exports and vendor bytes remain local/ignored supporting evidence. A clone restores the committed repository; affected scientific reproduction also needs those original inputs. Ignoring evidence never authorizes deletion. Reruns create new experiments.

## Evidence map

| Research | Current findings / dated inventory or receipt |
| --- | --- |
| Foundation | [Phase 0](../research/architectures/phase0-report.md), [raw inventory](raw-data.sha256) |
| Original device controls | [Validity](../research/devices/device-model-validation.md), [raw](device-model-raw-data.sha256), [CSV](device-model-csv-data.sha256), [integrity](../research/devices/device-model-integrity.json) |
| MOS follow-up | [258 files](evidence-20261009T070957Z-3092a887.sha256), [integrity](../research/device_model_integrity_2026-10-09.json) |
| Six mechanisms | [First batch](../research/architectures/first-architecture-batch.md), [1981 files](evidence-20261009T082728Z-78caabc6.sha256), [integrity](../research/first_architecture_integrity_2026-10-09.json) |
| Robust optimization | [Findings](../research/architectures/optimization/robust-optimization-report.md), [4198 files](evidence-20261009T091504Z-58b871ef.sha256), [recovery](../research/robust_optimization_preservation_2026-10-09.json) |
| Comparison001 | [Findings](../research/architectures/architecture-comparison-001.md), [derived evidence](reports/architecture-comparison-001/INDEX.md), [71 files](evidence-20261009T121907Z-3c4139cd.sha256) |
| Parts001/002 | [001](../research/devices/parts-database-expansion-001.md), [002](../research/devices/parts-database-expansion-002.md), source-stable controls and original failures |
| Capsule001 | [Envelope](../research/capsules/evidence-envelope-001.md), [finite cohorts and integrity receipt](../research/capsules/analysis-001.md); original assumed ranges and prior failures retained |
| Prerequisites001 | [Findings](../research/devices/simulation-prerequisites-001.md), [three frozen cohorts and integrity](../research/devices/simulation-prerequisites-integrity-001.json);119 jobs,19 execution errors, scoped follower H2/H3 only |
| Latest repository/lab checks | [Validation](../../../docs/validation.md), [generated evidence index](../../../docs/evidence.md) |

[Complete navigation](INDEX.md) links every retained record/inventory. Historical test counts belong to their original cohorts; current counts are in validation. Derived archive/fronts are rebuildable views, never replacement evidence. Every implementation remains unqualified.

## Verify and preserve

Inventory paths are laboratory-relative. For example, from the lab:

```sh
sha256sum -c results/raw-data.sha256
```

Use the root [evidence tools](../../../docs/maintaining-repository.md#private-evidence) for additional dated inventories and complete source/job hash verification. Do not replace earlier inventories. Private capture/restore is optional; its result reports actual coverage separately from repository status. Exact private destinations stay outside Git. Historical audit declarations remain preserved, with no current recovery task or qualification credit assigned to them.

The2026-10-06 folder rename preserves relative laboratory paths; original absolute/legacy paths and all frozen bytes remain unchanged. [Path migrations](../../../docs/config/path-migrations.json) resolve current authored locations. Vendor terms/notices remain original; no redistribution permission is inferred. Downloaded runtimes/environments/caches and synthetic provenance fixtures are excluded, while real physics-control decks/logs/failures remain retained. [Licensing](../../../LICENSE) retains authority; [current storage policy](../../../docs/decisions/2026-10-11-github-canonical.md) supersedes earlier recovery requirements.
