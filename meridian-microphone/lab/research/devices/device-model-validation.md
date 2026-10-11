# Device model validity — current review 11 October 2026

**Partial evidence.** [Parts002](parts-database-expansion-002.md) covers20 semiconductors/27 files/18 types. No complete JFET/CMOS/bipolar/P48 population supports production or architectural ranking.

[Registry](../../models/semiconductor/registry.yaml) · [independent references](../../models/semiconductor/references.yaml) · [coupled corners](../../models/semiconductor/corners.yaml) · [decisions](device-model-decisions.md)

[Prerequisites001](simulation-prerequisites-001.md): refined numerical follower H2/H3; microphone nonlinear/headroom and floating OPA held. Preserve original models/failures.

## Supported scope and discrepancies

| Model | Evidence / limit |
| --- | --- |
| JFE150 |25°C,VDS10V,VGS0 generic Idss26.902mA is within24–46mA, but gm49.109mS misses55mS minimum by10.71%. Weak17.904mA/36.469mS and strong40.049mA/37.215mS do not establish guaranteed production corners |
| Coupled Shockley control |24mA/55mS predicts cutoff−0.87095V, outside−1.5…−0.9V. Approximation permits Idss only above≈24.800mA under these constraints; retain uncovered24mA manufacturer bound |
| OPA197 | Tested grounded,mid-common-mode,small-signal DC/cap/bandwidth/noise agreement; five nonlinear jobs fail. No floating,low-supply,clipping/recovery,thermal/SOA or process qualification |
| BC846B/BC856B | Authored one-node emitter repair retains vendor parent; nominal DC/saturation/bandwidth hypotheses only. Capacitance/NF/flicker/temperature gaps remain |
| Vishay2N7002K Rev.B | Threshold/RDS/gm agreement coexists with output/capacitance/temperature discrepancies; leakage/ESD/1f/process absent.2014model predates retained2017sheet; continuity unknown |

Guaranteed limits, typical values, visual intervals and numerical refinement are separate evidence states.20% typical-value and1% refinement screens are unchanged research accuracy checks. MOS high-current reference pulses (≤300µs,≤2%duty) are approximated isothermally; this authorizes no physical DC/SOA test. Missing behavior earns no favorable zero.

## Method, failures and preservation

The [characterizer](../../models/semiconductor/characterize.py) freezes versions, sources, references, decks, temperatures, raw/CSV/log hashes, errors and parents. Deterministic grids have no manufacturing probability. Preserve invalid clamped-drain/common-mode/bandwidth/deck parents and nonlinear failures; scoped agreement cannot erase them.

The9October MOS parent had a wrong drain-observer sign; its corrected child and independent square-law/passive-admittance controls retain all bytes. [38-test original verification](../../results/verification/20261009T070533Z_a602e6d5/verification.json), [integrity](../device_model_integrity_2026-10-09.json) and [258-file inventory](../../results/evidence-20261009T070957Z-3092a887.sha256) cover the original follow-up, not today's test count.

Exact source versions/notices and failed HTML/challenge/403 downloads remain private. [Dated sourcing](../procurement/semiconductors_2026-10-09.yaml) supplies documentary routes, not live stock or delivered totals. [Patent flags](../patents/device_library_2026-10-05.yaml) do not complete claims/status review.

Next: acquire independent current/noise/leakage/temperature behavior at intended bias, validate joint bounds and floating integrations, then realize/requalify exact BOMs. Keep every family open while its prerequisites remain unsupported.

[Complete dated original](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/device_model_validation.md) · [Current verification](../../../../docs/validation.md). Original tables, failures, conditions and decisions remain authoritative.
