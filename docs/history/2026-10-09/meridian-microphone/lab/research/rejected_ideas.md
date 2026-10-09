# Rejected / failed experiments

## Parts strengthening002 boundaries — 2026-10-09

[Preserved controls](parts_database_expansion_002.md): do not promote ignored LSK389 or Diotec electrical parameters; declaring pi does not model breakdown. Do not pool historical TI revisions, count variants as parts, assume adjacent-die symmetry proves matching, translate grounded OPA928 behavior into floating operation, or assign a capacitor broadband/temperature law from discrete limits. PNP Rs10Ω NF differs from Rs2kΩ NPN tests and remains a failing conditional screen.

## Comparison 001 boundaries — 2026-10-09

Reject filling unavailable H2/H3/H4–H10, THD or headroom with partial/unsettled transient estimates; known timestep/timeout failures remain original evidence. Reject interpreting the servo's 5s observation edge as settling, carrier's ideal-block partial current as total architecture power, or a charge input's tiny electrode-voltage ratio alone as lost charge conversion.

Reject ranking families from unpaired artificial Monte Carlo pass counts, extrapolating deterministic endpoints to a full envelope, or treating a nominal research Pareto member as physical qualification. Reject transferring a EUR Cardioid-only capsule price to K47FRB. Preserve the old carrier patent-feature error and the dated correction; neither feature flags nor absent search results constitute claim/status screening. [Comparison 001](architecture_comparison_001.md) preserves all six mechanisms and their scoped failures.

## First architecture batch — 2026-10-09

See [all records](first_architecture_batch.md). Preserve these distinctions:

- OPA-based DUT parents and guarded/charge children: operating-point convergence/model integration failures; no physics rejection of CMOS, guarding or charge feedback.
- Discrete JFET/BJT implementations: actual response/noise/output/startup/loading budget misses where supported; reported per implementation, never a whole-family rejection. Backplate-feed noise is a physically supported implementation flaw; the filter child tests it and still fails other budgets.
- BJT1MΩ→500kΩ reset child: real DC-authority/sensitivity tradeoff, both full supported suites retained; no hidden trimming or class-level no-FET verdict.
- Carrier writer/extractor bugs: missing reference vector and omitted nuisance tones are preserved analysis failures, then repaired with independent controls. P48-integrated transient timestep failure remains an integration gap; ordinary DC noise is never a carrier-noise score.
- BOM-only structural registration: [failed proposal](probes/bom_only_registration_2026-10-09/results.json) preserved; unchanged-graph rule retained. A separately documented feedback-structure change establishes the later BJT child.
- Backordered10kΩ/100pF parent dependencies remain research. Available nominal substitutes need their own loss/device/BOM suite; exact MOQ/live stock and delivered-cost gaps still hold build readiness.
- Unscreened patent claims/status and absent physical ratings are qualification gates, not negative simulation results. No family is retired and no failed evidence is deleted.

Failure scope matters: a software realization failure does not reject the physical mechanism.

- **Behavioral B-source ddt capsule (tool probe):** ngspice 47 completed AC but produced zero capsule signal. Native charge-law implementation restored expected AC transfer. Reject that implementation until independently validated; preserve the derivative probe.
- **Native behavioral-Q capsule r1:** analytical AC/noise controls passed, but the full floating P48 transient produced a timestep-too-small failure. Failed jobs remain in `results/runs`; old implementation retained in `models/capsule/flat_k47_native_q_r1.cir`. No performance credit from those transient runs.
- **Scaled charge-observer r2 with trapezoidal integration:** analytical controls passed; transient failures remained at some frequencies. This rejects that numerical configuration, not the charge law. Gear-2 integration subsequently passed the AC/transient and timestep-refinement controls and is the current implementation. The earlier snapshot is retained in `models/capsule/flat_k47_scaled_observer_r2.cir`.
- **Series motion-source realization r3:** the equivalent series voltage source and fixed capacitor still produced transient convergence failures in the floating P48 system. Retained in `models/capsule/flat_k47_series_motion_r3.cir`; no performance credit from failed analyses.
- **Linear interpolation for harmonic estimation:** nonuniform transient-grid resampling created spurious harmonics in an analytically linear fixture. Cubic-spline coherent resampling passes the unchanged numerical-refinement criterion. Harmonic estimation must be validated against a physical oracle and timestep refinement before accepting low THD numbers.
- **Two-parameter fixture optimization:** changing only input and polarization resistances did not satisfy the frozen frequency-response limit; output coupling also matters. Failed numerical trials remain, and the search bounds/thresholds were not narrowed or relaxed.
- **Three-parameter fixture proposal:** 202 numerical trials found feasible nominal current/response values, but full-suite evaluation still fails noise, impedance balance, capsule loading and cable/load screening. This is not an improved microphone or an accepted topology. See `phase0_report.md`.
- **Early scenario percentile reporting:** filtering metric summaries to passing requirements excluded adverse completed simulations. Reject those aggregate percentiles; raw cases and failure denominators remain usable. Corrected summaries include completed failing cases and expose missing/error counts. Final comparison is repeated under the corrected suite.
- **Direct AD7746 audio signal path:** its documented update rate and capacitance range do not cover the microphone requirement. Carrier/floating capacitance-sensing mechanisms remain open (S09).
- **Initial fixture values:** nominal frequency response, electronics noise and impedance balance fail provisional requirements. Ideal buffers do not excuse that result; no semiconductor topology has been rejected by this fixture failure.

- **2026-10-05 device-model experiments:** retain the clamped-drain invalid fixture, OPA common-mode overdrive, follower-bandwidth proxy, malformed open-loop deck, original BC846B floating emitter, 2N7002 HTML response, coupled r1 cutoff failure and control serialization/parent errors. Corrected descendants preserve these parents; OPA nonlinear convergence failures remain unresolved. Model failure does not reject the corresponding architecture family. See [records and coverage](device_model_validation.md).
- **Vishay 2N7002E E3/GE3 implementation dependency:** obsolete retailer status conflicts with retained public model pages; no NOS implementation is proposed. Current 2N7002K-T1-GE3 is only an unvalidated research alternative.

- **2026-10-09 MOS threshold observer:** the first new batch completed six jobs but used the wrong sign of the diode-connected drain-current observer; interpolation then failed. Parent raw/source evidence remains unchanged. The corrected descendant and independent square-law control verify the observer sign; no vendor parameters changed.
- **Vishay 2N7002K Rev. B blanket qualification:** the final 38-job batch converges, yet output/capacitance/temperature comparisons disagree and gate leakage/ESD/1/f/process coverage is absent. Reject blanket low-noise/P48 qualification, not the MOS architecture family. The 2014 model and 2017 datasheet relationship remains uncertain; no favorable correction was fitted. See [current coverage](device_model_validation.md).

## Robust batch — 2026-10-09

[Full records](robust_optimization_report.md) preserve CMOS integration holds, carrier protocol hold, the 12-vector BJT feedback search without a feasible tested point, and the series-feedback structural child's failure. These are scoped implementation/model observations, not whole-family rejections. The optimized JFET responses still fail qualification at adverse capsule/interface endpoints and other full-suite requirements. No uncertainty envelope or threshold was reduced.

Reject using the first batch's unpaired random DC/AC pass fractions as a cross-family yield ranking. Different passive counts consume different RNG draws. Keep those valid individual artificial-scenario observations, including failures; use shared endpoint comparisons and plan a pair-matched protocol before a comparative statistical claim. Also retain the first failed optimizer-directory regression, initial driver import error and separate test-invocation collection error, with repaired successor verification.

## Parts-expansion exclusions —9 October2026

[Expansion001](parts_database_expansion_001.md) rejects treating JFE2140 halves/TINA archives as independent devices, copying nominal halves as guaranteed matching, transferring high-current noise to100uA, treating5551/5401 BJTs as JFETs, using a different manufacturer/package model as validated interchangeability, or assigning zero effects where KF/leakage are absent. ADA4530 licence acceptance remains unauthorized. Historical names, inaccessiblePNP models, unverified exactPP/high-R suffixes and indexed stock remain leads/gaps. No comparison-stock purchase or favorable retry/threshold fitting.
