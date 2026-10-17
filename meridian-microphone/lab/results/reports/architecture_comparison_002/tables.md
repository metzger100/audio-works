# Common-cohort tables — 17 October 2026

Conditional numerical research; all implementations unqualified. Full reasons/raw identities remain in the machine records.

|Candidate|mA|Rail V|Bias V|Response dB|Noise µPa / A µPa|Count|
|---|---:|---:|---:|---:|---:|---:|
|0010|unknown|unknown|unknown|unknown|unknown / unknown|40|
|0012|4.086|13.5983|22.3107|20.9306|113896 / 84283.1|45|
|0013|1.23425|20.4644|29.2038|unknown|unknown / unknown|36|
|0014|unknown|unknown|unknown|unknown|unknown / unknown|38|
|0017|4.10355|13.5558|26.1001|0.792408|309.901 / 165.144|48|
|0019|4.10355|13.5558|26.1001|0.660555|309.895 / 165.141|52|
|0023|5.15043|11.0103|22.5462|0.472123|1051.74 / 959.674|72|
|0025|5.15043|11.0103|22.5434|0.575066|362.825 / 194.694|73|

Noise is conditional on unvalidated model spectra and assumed capsule transfer; capsule/environment Johnson surrogates are excluded. Carrier current/count are partial ideal-control accounting.

[All check states](coverage.csv) · [Exact BOM](bom.json) · [Uncertainty and denominators](uncertainty.csv) · [Holdouts and adverse cases](matched-scenarios.json) · [Realization deltas](realization-deltas.csv)

## Exact implementations

- candidate_0010: [frozen netlist](../../runs/20261017T090334Z_9ec74a8a/circuit.cir), [BOM](../../runs/20261017T090334Z_9ec74a8a/bom.yaml), [complete suite](../../runs/20261017T090334Z_9ec74a8a/results.json), [functional view](candidate-0010-functional.svg), [ordered connectivity](candidate-0010-connectivity.svg)
- candidate_0012: [frozen netlist](../../runs/20261017T090224Z_c10242f8/circuit.cir), [BOM](../../runs/20261017T090224Z_c10242f8/bom.yaml), [complete suite](../../runs/20261017T090224Z_c10242f8/results.json), [functional view](candidate-0012-functional.svg), [ordered connectivity](candidate-0012-connectivity.svg)
- candidate_0013: [frozen netlist](../../runs/20261017T090342Z_7651f2f8/circuit.cir), [BOM](../../runs/20261017T090342Z_7651f2f8/bom.yaml), [complete suite](../../runs/20261017T090342Z_7651f2f8/results.json), [functional view](candidate-0013-functional.svg), [ordered connectivity](candidate-0013-connectivity.svg)
- candidate_0014: [frozen netlist](../../runs/20261017T090340Z_19f315d1/circuit.cir), [BOM](../../runs/20261017T090340Z_19f315d1/bom.yaml), [complete suite](../../runs/20261017T090340Z_19f315d1/results.json), [functional view](candidate-0014-functional.svg), [ordered connectivity](candidate-0014-connectivity.svg)
- candidate_0017: [frozen netlist](../../runs/20261017T090132Z_e4e63a9c/circuit.cir), [BOM](../../runs/20261017T090132Z_e4e63a9c/bom.yaml), [complete suite](../../runs/20261017T090132Z_e4e63a9c/results.json), [functional view](candidate-0017-functional.svg), [ordered connectivity](candidate-0017-connectivity.svg)
- candidate_0019: [frozen netlist](../../runs/20261017T090144Z_c99f7ef8/circuit.cir), [BOM](../../runs/20261017T090144Z_c99f7ef8/bom.yaml), [complete suite](../../runs/20261017T090144Z_c99f7ef8/results.json), [functional view](candidate-0019-functional.svg), [ordered connectivity](candidate-0019-connectivity.svg)
- candidate_0023: [frozen netlist](../../runs/20261017T090156Z_283ceec4/circuit.cir), [BOM](../../runs/20261017T090156Z_283ceec4/bom.yaml), [complete suite](../../runs/20261017T090156Z_283ceec4/results.json), [functional view](candidate-0023-functional.svg), [ordered connectivity](candidate-0023-connectivity.svg)
- candidate_0025: [frozen netlist](../../runs/20261017T090210Z_00a1cb5e/circuit.cir), [BOM](../../runs/20261017T090210Z_00a1cb5e/bom.yaml), [complete suite](../../runs/20261017T090210Z_00a1cb5e/results.json), [functional view](candidate-0025-functional.svg), [ordered connectivity](candidate-0025-connectivity.svg)

## Finite holdout screen

|Candidate|Pass / attempted|Errors|Exact95% interval|Worst finite dB|
|---|---:|---:|---|---:|
|0012|0 / 16|0|[0.0, 0.2059072142078227]|22.6014|
|0017|13 / 16|0|[0.5435434537683883, 0.9595262660940541]|1.68275|
|0019|13 / 16|0|[0.5435434537683883, 0.9595262660940541]|1.42133|
|0023|2 / 16|0|[0.015513603815413885, 0.38347623684926346]|1.82701|
|0025|13 / 16|0|[0.5435434537683883, 0.9595262660940541]|1.29838|

Intervals concern the declared artificial DC/AC sampler only; they are not production yield or all-requirement pass rates.
