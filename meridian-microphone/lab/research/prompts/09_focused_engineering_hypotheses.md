<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Prompt 9 — Test bias authority, backplate filtering and output-stage hypotheses

Work in `meridian-microphone/lab` on M100 Meridian MIC-34-M/MIC-34-C, K47FRB under P48. Read and apply [the continuation execution contract](RESEARCH_WORKFLOW.md). Use route `qualification` and read the optimization route's relevant evidence. Inspect comparison 001, exact frozen netlists/BOMs/results for 0019/0017 and 0023, robust plan/batch/holdouts, model validation, source/procurement/patent records and actual outputs of Prompts 6–8. Audit later children first; do not hard-code a new candidate ID or repeat completed work.

Execute three focused, falsifiable hypotheses with independent calculations and preserved children. Allocate most immediate effort to the two JFET niches, while retaining other families and unsupported checks. Further output-capacitance optimization is lower priority: nominal LF improvement does not fix leakage, bias, noise or imbalance. No production topology/PCB selection follows.

## Research and hypothesis plans

Perform extensive primary-source research before implementation: high-impedance bias/leakage control, discrete DC servos and multi-loop stability, capsule backplate filtering, phantom extraction, balanced-driver impedance/noise and finite cable/preamp interfaces. Search instrumentation analogies, original equations/application notes and candidate-feature patents. Turn each borrowed principle into an independent calculation and an actual netlist hypothesis; no schematic cloning or transferred performance claim. Map the proposed change to exact source conditions and applicable patent flags.

### A — Fixed-bias versus servo no-trim authority

Derive loaded DC equations/KCL, gate/leakage current, divider/base-current effects, source current, device terminal limits and rail/polarization authority for the actual fixed-bias and servo circuits. Use the retained 1GΩ–100TΩ capsule leakage envelope and documented coupled device/passive/temperature/interface stresses. Separate unavoidable capsule discharge paths, board contamination and model assumptions. The recorded 1GΩ failures are mandatory adversarial cases, not discardable outliers.

Compare equal external conditions, preserving nonlinear dependencies and model identities. Test whether either topology has a useful no-selection authority region, identify loss of control/saturation and link each failure to a physical mechanism. Use no hand matching, altered specimen populations, hidden trimming or favorable noise omission. Study startup/recovery and independently measured/calculated return-ratio/Nyquist or other appropriate loop criteria where supported; a quiet closed-loop AC trace is not stability proof. If a structural remedy is supported, register a small explicitly planned child and preserve the parent.

### B — Actual final-backplate-filter child of 0023

Check whether later work already implemented the hypothesis. Derive the polarization-network transfer/noise, leakage/DC load, charging energy and settling effect of a filter at the actual final backplate path. The fixed-bias 0019 filter is comparative evidence, not proof that a servo child will benefit or remain stable.

Register a child of the actual current 0023 version through the existing mutation workflow. Use an exact standard part/value/tolerance/rating and documented insulation/loss/parasitic assumptions; preserve the unfiltered parent and all other conditions in a matched cohort. Do not assume safe physical capsule bias. Evaluate nominal/adverse noise contributions, bias/current/loading, audio response, startup and servo/audio interaction. Run the complete applicable suite with explicit incomplete/error states where prerequisites are still missing. Report the benefit, regressions, numerical uncertainty and added component/space/sourcing burden. An untested filter value receives no improvement claim.

### C — Output-drive noise and two-port impedance balance

Independently derive the actual drivers' small-signal two-port behavior, phase inversion, source impedance, passive coupling and supply interactions. Preserve finite device/base-current/noise effects, asymmetric loads, cable/preamp impedances, P48 feed mismatch and correlated supply noise. Separate differential impedance, conductor balance and fixture common-mode susceptibility; do not label fixture injection as intrinsic CMRR. Symmetric resistor labels do not imply symmetric ports.

Use isolated driver/control decks before integrated microphone children. Verify noise power accounting and source transfers independently. Investigate source-linked ordinary BJT/other production alternatives from Prompt 6, including high-voltage parts only where their actual role and model support warrant them. Compare exact realized variants without importing another manufacturer's model or ignoring beta/capacitance/leakage changes. Retain documented output/coupling tolerances and physical count. Startup/hot-plug, thermal/SOA/protection, RF and stability gaps remain explicit. Include nonlinear/headroom only after Prompt 8 supports it; preserve errors and censoring otherwise.

## Common comparison and outputs

Predeclare finite separate plans for A/B/C, analysis prerequisites, seeds and stopping rules under the existing budgets. Freeze one matched source/model/spec/backend/test cohort for each parent/child comparison. Every realized child/substitute/combination receives the complete applicable suite and independent retained adverse validation; missing checks cannot pass. Do not narrow capsule/device uncertainty or optimize an unvalidated scalar winner score.

Deliver `research/focused_hypotheses_001.md`, machine-readable hypothesis/child/check/coverage tables, analytical derivations, faithful netlist diagrams, exact BOM/cost/source records, source/patent research logs and immutable raw results. State what falsifies each hypothesis, where a change helps, and where it fails. Follow shared tests/preservation/current-state updates. Preserve nominal research fronts separately from empty/unmet production and physical gates.
