# Architecture comparison 001 — 9 October 2026

**No tested implementation supports prototype selection.** Compare model-conditional niches and failures, preserving all 14 families. There are no physical measurements, valid acoustic-pattern ratings or qualified production fronts.

[Plan/cohort](architecture-comparison-001.yaml) · [derived tables](../../results/reports/architecture-comparison-001/tables.md) · [machine-readable comparison](../../results/reports/architecture-comparison-001/architecture-comparison-001.json) · [decisions](architecture-comparison-001-decisions.md)

## Representatives

| Candidate | Mechanism | Finding / blocker |
| --- | --- | --- |
|0019|Filtered fixed-bias JFET|Useful nominal response; adverse endpoints,noise/output and nonlinear evidence fail/incomplete |
|0023|Discrete servo JFET|Flatter nominal response; unfiltered backplate noise,startup and adverse-case failures |
|0012|BJT charge feedback|DC/energy accounting works; finite-loop conversion/bandwidth/output noise fail |
|0010|Guarded CMOS|Macro integration/convergence failure; no mechanism-level rejection |
|0014|CMOS charge|Same unsupported numerical integration; no fabricated ideal substitute |
|0013|Carrier bridge|Isolated conversion control only; integrated transient,periodic noise and total power unsupported |

Representatives are scoped to niches, not equally qualified or globally optimal. Exact netlists/BOMs, lower-count children, statuses and raw noise contributions remain in the derived evidence.

## Physical interpretation

At1kHz,0019/0023 voltage-loading ratios are0.93743/0.91998 (0.5612/0.7244dB loss), with modeled input capacitance2.17/2.67pF and conductance≈1nS. A charge input's electrode-voltage ratio alone is not a conversion-loss metric. Conditional20Hz–20kHz electronics noise requires validated spectra and capsule transfer; it is not acoustic self-noise/SPL.

Servo0023 is flatter nominally, but0019 is flatter at shared low-rear-capacitance/high-parasitic/long-cable/high-preamp-impedance endpoints. Both fail retained1GΩ leakage stress. First random samples are unpaired across passive counts and cannot rank family yield. Sensitivity rescaling alone does not reverse normalized linear response; physical parameter correlations remain unknown.

Noise root-vector integration closes numerical power: unfiltered servo backplate noise dominates; fixed-bias filtering exposes bias/degeneration/output contributions. Closure does not validate missing semiconductor spectra.0019 startup passes the supported screen;0023's5s observation edge is not achieved settling. Unsettled/failed transients supply no harmonic/headroom estimates.

## Gates and next action

Exact ordinary-part costs remain incomplete catalogue scenarios; all delivered totals are unknown. K47FBSB Cardioid-only EUR pricing cannot price K47FRB. Carrier0013 has ideal outputs despite older patent-feature wording; the dated correction retains that original. [Patent screening001](../patents/candidate-screening-001.md) adds exact-version claim mappings and13 dated German records. Official US/current amended-claim/family coverage and material interpretation remain incomplete; affected implementation gates stay held. These documentary findings do not replace this comparison's engineering cohort.

Reproduce with [comparison tool](../../tools/reporting/compare_architectures.py) using original private waveforms. [Provenance](../../results/reports/architecture-comparison-001/provenance.json) identifies checked sources/cohort and outputs. Follow [measurement priorities](../../measurement/priority-plan.md), repair independent behavior prerequisites, then recompute a shared cohort without weakening bounds.

[Complete dated original](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/architecture_comparison_001.md) · [Current verification](../../../../docs/validation.md). Original tables, failures, conditions and decisions remain authoritative.

[Capsule envelope 001](../capsules/evidence-envelope-001.md), 11 October 2026, adds a separate frozen shared capsule scenario cohort. It confirms capsule-only response reversals and conditional noise reversals at failed 1GΩ cases. It does not replace this baseline cohort, its full-suite failures or eligibility gates.

[Simulation prerequisites001](../devices/simulation-prerequisites-001.md) adds a separate119-job terminal/reduced-DUT diagnosis. Isolated follower H2/H3 and extraction controls pass; full DUT prerequisites remain unsupported. No common full comparison, microphone harmonics, headroom or eligibility is promoted.
