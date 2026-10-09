# Initial research foundation — 5 October 2026

Phase 0–2 provides executable physics/software controls, bounded numerical search and evidence retention. **Both ideal-buffer fixture evaluations are unqualified and ineligible by construction.** No real topology or prototype is selected.

[Original-cohort comparison](../../../results/reports/initial-summary.md) · [baseline](../../../results/runs/20261005T121311Z_f11a711a/results.json) · [proposal](../../../results/runs/20261005T121440Z_8f1bc311/results.json) · [22 concepts](../../../search/concepts.yaml) · [14 families](../../../search/families.yaml)

## Findings

The passive fixture exercises loaded P48, capsule charge/loading, response/noise, output ports, startup, uncertainty and metrics. Ideal noiseless buffers omit real power, clipping and semiconductor behavior.202 differential-evolution trials improve nominal response3.882→0.994dB but worsen conditional noise/balance; full qualification rejects the proposal. The search reaches its iteration budget without convergence/global-optimality evidence.

The imposed charge law `Q=C0(1+k·p)V` has independent AC/transient and timestep controls. Gear-2 scaled native-capacitor observation resolves earlier numerical failures. Cubic-spline coherent harmonic extraction avoids interpolation artifacts. These are numerical controls, not capsule safety, mechanical noise/SPL or physical performance measurements.

## Evidence boundaries and next action

[Formal requirements](../../../spec/microphone-spec.yaml), [capsule assumptions](../../../spec/capsule-model.yaml) and [environment](../../../spec/design-constraints.yaml) retain provisional thresholds and broad uncertainty. Typical electrical scenarios do not establish production yield or safe stimulation. Earlier percentiles excluded completed failing cases; corrected summaries retain them with missing/error counts and unchanged denominators. Original runs remain intact.

Original-cohort verification had22 passing regressions. Derived eligible fronts/champions remain empty; archive novelty earns no performance credit. The [measurement adapter smoke result](../../../results/reports/measurement-adapter-smoke.json) is synthetic, not physical data.

Continue independent device validation, diverse actual-BOM mechanisms and full robust/noise/nonlinear/stability work. Capsule safe bias/mechanics/noise/polar response, candidate claims/current status, RF/ESD/humidity/hot-plug and calibrated measurements remain prerequisites. [Current comparison](../architecture-comparison-001.md) supersedes this report for research progress; original failures and foundation scope remain.

[Complete dated original](../../../../../docs/history/2026-10-09/meridian-microphone/lab/research/phase0_report.md) · [Current verification](../../../../../docs/validation.md). Original tables, failures, conditions and decisions remain authoritative.
