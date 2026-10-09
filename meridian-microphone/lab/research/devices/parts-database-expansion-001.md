# Parts evidence 001 — 9 October 2026

Continuation baseline: **17 exact devices,21 distinct model files across15 types,15 passives**. [Expansion002](parts-database-expansion-002.md) is the current handoff. Models, ordinary factory matching and source metadata do not qualify a microphone or physical population.

[Resolved role matrix](parts-database-expansion-001.yaml) · [dated search](../parts_sources_2026-10-09.yaml) · [sourcing](../procurement/parts_expansion_001_2026-10-09.yaml) · [decisions](parts-database-expansion-001-decisions.md)

## Useful controls and limits

| Scope | Result / remaining gap |
| --- | --- |
| JFE2140 ordinary dual | Conditioned matching:4mV VGS at25°C/2mA,4.2mV full-temperature,Idss ratio0.95–1.05. Identical half-models/TINA members do not model mismatch or count as independent devices |
| PMBT5551,215 NPN | At5V/25°C β143 at1mA,121 at10mA versus minimum80; fixed-base52V/102°C stress reaches114mA, invalidating assumed2mA/104mW thermal point. Cap/leakage convergence warnings and absent KF block credit |
| Independent JFET / electrometer leads | Restricted discrepancy/DC work only; current-noise, leakage, floating/charge and joint populations incomplete |
| High-R/passive dependencies | Thick-film excess noise, HVA tolerance/TCR/VCR, board insulation and real combinations require controls.500MΩ substitutions create children; no inherited1GΩ qualification |

Deterministic bias/temperature grids retain their conditions and failures. Guaranteed bounds, typical references and numerical consistency remain separate. No independent transient reference exists; no fabricated fitting/selection is used.

## Records and next action

[Plan001](parts-control-plan-001.yaml) and [child plan002](parts-control-plan-002.yaml) retain15s/job,100job bounds and20% typical/1% numerical screens. Three original records remain: [driver failure](../../results/device_models/20261009T133250Z_parts_ec54d567/failure.json), [source-integrity failure](../../results/device_models/20261009T133422Z_parts_9ee64bfd/results.json), [stable49 jobs/7 errors](../../results/device_models/20261009T133651Z_parts_d3c30763/results.json).

Exact sourcing observations include variant, age, MOQ/pack, private Germany route, dispatch and conditional costs. Failed retail fetches and indexed stock are not live orderability. All confirmed delivered totals remain unknown; alternative BOMs are not a shopping basket. Patent feature flags lack candidate-linked current claim/status screening. Preserve these holds and follow the current expansion's focused prerequisites.

[Complete dated original](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/parts_database_expansion_001.md) · [Current verification](../../../../docs/validation.md). Original tables, failures, conditions and decisions remain authoritative.
