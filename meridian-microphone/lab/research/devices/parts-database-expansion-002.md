# Parts evidence 002 — 9 October 2026

**20 exact semiconductors, 27 distinct hash-pinned SPICE files across 18 types, 16 passives and 17 documentary leads.** Metadata/search and restricted controls improved; no microphone implementation is qualified. Owned stock, live Germany orderability, complete delivered costs, candidate claims/status and physical behavior remain unresolved.

[Resolved matrix](parts-database-expansion-002.yaml) · [CSV index](parts-database-expansion-002.csv) · [search receipts](../parts_sources_expansion_002_2026-10-09.yaml) · [sourcing](../procurement/parts_expansion_002_2026-10-09.yaml) · [patent flags](../patents/parts_expansion_002_2026-10-09.yaml) · [decisions](parts-database-expansion-002-decisions.md)

## Findings and failures

| Exact device / conditions | Finding | Boundary |
| --- | --- | --- |
| MMBT5401-7-F, VCE5V/25°C | β121.94 at1mA,124.92 at10mA; Cobo3.706pF atVCB10V/1MHz; ICBO6.37pA at120V/25°C,4.78nA at100°C | Restricted model points pass corresponding limits; no population/thermal/SOA evidence |
| Same PNP,200µA/5V/Rs10Ω,1kHz | NF8.790dB exceeds8dB | Conditional failure; unspecified reference filter prevents measured equivalence; KF absent |
| DMMT5401-7-F | Conditioned gain/cap/100°C leakage pass; NF fails;25°C leakage convergence warning | Ordinary documented2% matching bounds; equal nominal halves do not prove covariance.200mA/half,300mW combined |
| Diotec2N5551 / MMBT5551 | Separate pi-only fixture parses but ignores BVCBO/BVBE | Strict failure, no breakdown credit; NPNs, not JFETs. Diotec datasheet600mA controls conflicting web1500mA |
| LSK389A metadata child | ISR/NR/ALPHA/VK ignored | No accepted behavior; preserve original/child ancestry |
| OPA928,grounded16V/25°C |15.684nV/√Hz at1kHz,275µA macro current | +20V translation fails convergence; OPA1656/LMP7721 retain15s timeouts |

Four JFE150 variants remain one part. Distinct older OPA1656/OPA928 TI revisions are uncharacterized historical controls; byte-identical members are not extra files/devices. The preserved SOT23 Diotec control label has an incorrect datasheet date; exact numeric limits were checked, frozen label unchanged.

## Passive/support implications

Exact WIMA MKP2D031001F00KSSD:100nF±10%,100V,PP,5×10×7.2mm/5mm pitch. Dated sheet IR≥100GΩ at20°C/100V/1 minute and discrete DF/absorption guidance do not establish a broadband/time/temperature law. Recorded retailer stock was zero; datasheet100°C controls web110°C. TMUX1102DCKR has documented conditioned switch/injection limits but no acquired analog periodic-noise model.

At1GΩ,10pA→10mV,5nA→5V,300pA→0.3V at their separate source conditions. Johnson noise is4.058fA/√Hz at298.15K; excess noise/board leakage remain unknown. Two500MΩ parts need a new realized child. EEU-FR1J470 rated-bias2 minute leakage29.6µA scales arithmetically with count only under that test condition; it supplies no low-bias/reverse-startup qualification.

## Evidence and next action

[Plan003](parts-control-plan-003.yaml): [27 jobs/14 errors](../../results/device_models/20261009T145346Z_parts2_742caaa3/results.json).
[Plan004](parts-control-plan-004.yaml): [6 jobs/6 errors](../../results/device_models/20261009T170734Z_constant_ae3a9e1d/results.json).
[Plan005](parts-control-plan-005.yaml): [13 jobs/1error](../../results/device_models/20261009T171204Z_dual_pnp_9ff5882e/results.json).
All 46 jobs/21 errors and stable source snapshots remain.15s/100job budgets,20% typical/1% numerical screens and scientific gates are unchanged.

Use [parts search/audit](../../tools/controls/parts_database.py) via `--counts`, `--audit`, exact names or `--role`/`--state`. The audit rejects canonical identity/hash/state drift and unconditioned behavior passes. Next: restricted PMBT5551/MMBT5401 feedback/power controls, dual-package mismatch/combined-power sensitivity, independent JFET discrepancy and OPA928 grounded/floating prerequisites. No purchase selection follows.

[Validation](parts-database-expansion-002-validation.json) and [recovery receipt](parts-database-expansion-002-preservation.json) retain14search sessions (13raw records; first timestamp/raw absent),32direct receipts. GitHub holds committed records; vendor bytes/waveforms remain local.

[Complete dated original](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/parts_database_expansion_002.md) · [Current verification](../../../../docs/validation.md). Original tables, failures, conditions and decisions remain authoritative.
