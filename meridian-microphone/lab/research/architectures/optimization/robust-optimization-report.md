# Robust optimization research — 9 October 2026

M100 Meridian MIC-34-M/MIC-34-C, Arienne Audio Flat K47 Cardioid/Omni K47FRB, realistic P48. **All implementations remain unqualified.** This is restricted, model-conditional response optimization: the prerequisite audit found no complete validated semiconductor/noise/process set permitting an architectural performance ranking. No production topology, PCB or prototype is selected. No purchase, supplier contact, licence acceptance or external publication occurred.

[Contract](../../../CONTRACT.md) · [specification](../../../spec/microphone-spec.yaml) · [capsule uncertainties](../../../spec/capsule-model.yaml) · [model validity](../../devices/device-model-validation.md) · [first batch](../first-architecture-batch.md) · [dated decisions](robust-optimization-decisions.md). Physics/measurements → SPICE → tests → numerical optimization → engineering reasoning → LLM intuition.



## Prerequisites and scope



JFE150 and authored BC846B permit falsifiable nominal hypotheses within the library’s documented discrepancies, not a production-bounded response/noise prediction. OPA197’s grounded small-signal agreement does not validate these floating integrations. Carrier ordinary AC/stationary-noise objectives are blocked. `noise`, `distortion`, `headroom`, `loading`, `balance`, `drive`, `current` and `complexity` remain separate objective interfaces; missing behavior prerequisites block the corresponding optimization axis. No weighted engineering/cost winner score exists. Legacy noise optimization is restricted to the ideal infrastructure fixture.

## Budget, parameters and termination



[Predeclared plan](../../../optimization/robust-plan.yaml) gives every one of six mechanisms 12 unique design-vector evaluations, three scenarios each. Prerequisite/integration holds leave unused budget visible. Sources and every implementation file freeze before each run; individual trials never edit canonical parents. [Batch plan](../../../results/optimization_batches/20261009T090126Z_4735cd2a/plan.json) and [search index](../../../results/optimization_batches/20261009T090126Z_4735cd2a/search.json) preserve the actual allocation.

## Continuous proposals and withheld uncertainty



| Family | Baseline nominal deviation dB | Continuous C µF/leg | Continuous nominal / trained worst dB | Withheld corner worst dB | Independent random DC/AC passes |
| --- | ---: | ---: | ---: | ---: | --- |
| conventional_jfet | 1.117 | 188 | 0.6612 / 0.6696 | 23.55 | 16/16; 95% sampler interval [0.7941, 1] |
| unconventional_jfet | 0.9131 | 175.8 | 0.4771 / 0.4895 | 21.48 | 7/16; 95% sampler interval [0.1975, 0.7012] |

## Actual BOM combinations and full-suite outcomes



[Realizations](../../../results/optimization_batches/20261009T090126Z_4735cd2a/realization.json) preserve continuous proposal ancestry. Each leg uses one to four individual Panasonic EEU-FR1J470, 47 µF ±20%, 63 V radial parts, each with independent capacitance and explicit loss/leakage controls. [Primary observations](../../architecture_sources/robust_observations_2026-10-09.json) and [dated procurement](../../procurement/robust_parts_2026-10-09.yaml) separate manufacturer limits from indexed order observations.

## Family-specific implications and next experiments



1. Conventional JFET: output-capacitance tuning improves the modeled LF response; finite output impedance/balance, noise-model validity and nonlinear/startup failures still prevent advancement. Low capsule-leakage-resistance stress sharply defeats response. Measure/validate the capsule leakage and the JFE operating point under that load before extending value search. Keep the filtered-input niche as a research representative.

## Procurement, patent and physical gates



Use one capsule for one finished microphone. Count every installed capacitor and unavoidable pack excess, retain intended quantities, retail MOQ1 and indexed freshness separately from the manufacturer’s 5000-piece packaging. New capacitor stock observation is four months old and live retrieval failed. Exact lead/dispatch, some existing semiconductor/passive orderability, TME shipping, tax basis and import/payment fees remain unresolved.

## Checks and preservation



57 laboratory regressions passed before this batch, including missing-noise/periodic gates, adverse specimens, strict budgets, unchanged capsule uncertainty, design-tolerance non-narrowing, complete coupled corner rendering and an independent parallel-capacitance oracle. One early 51-pass/one-failure verification and the repaired successors remain; an initial driver import failure is preserved in [its probe](../../probes/robust_driver_import_2026-10-09/failure.log). [Integrity](../../robust_optimization_integrity_2026-10-09.json) and [private recovery receipt](../../robust_optimization_preservation_2026-10-09.json) record final hash, inventory, restore and repository checks.


## Reading and evidence



This compact view retains findings and limits. Consult the [complete original report](../../../../../docs/history/2026-10-09/meridian-microphone/lab/research/robust_optimization_report.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../../docs/evidence.md) and [scientific contract](../../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../../docs/validation.md).


## Reading and evidence


This compact view retains findings and limits. Consult the [complete original report](../../../../../docs/history/2026-10-09/meridian-microphone/lab/research/robust_optimization_report.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../../docs/evidence.md) and [scientific contract](../../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../../docs/validation.md).

## Reading and evidence

This compact view retains findings and limits. Consult the [complete original report](../../../../../docs/history/2026-10-09/meridian-microphone/lab/research/robust_optimization_report.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../../docs/evidence.md) and [scientific contract](../../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../../docs/validation.md).
