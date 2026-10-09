<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Meridian measurement priorities — 9 October 2026

No physical capsule/device data or equipment access has been established. This plan reduces the uncertainties exposed by [comparison 001](../research/architectures/architecture-comparison-001.md); it authorizes no purchase, supplier contact, capsule bias, prototype selection or build. Use the one intended finished microphone's K47FRB capsule when access is authorized and safe prerequisites are established. Do not buy comparison capsules, matching specimens or instruments without a concrete finished-project use and a separate owner decision.

Start with an inventory of existing and borrowed equipment, calibration records and facilities. **Access is unknown for every item below.** Borrowing/access may require later owner arrangements; no contact is made here. Needed functions, not purchase recommendations, are listed. If equipment or capsule limits cannot be established, retain the blocked measurement and continue the independent model/control work.

The priority order is dependency-driven: interface/safety → electrical parameters → sensitivity/noise → acoustic limits → integrated qualification. The high-leakage capsule endpoint defeats both JFET implementations; rear C/parasitics reverse their response order. Missing CMOS/carrier metrics primarily need simulation/backend repair before comparison hardware is useful.


## Common raw-data and calibration contract

Use [the result schema](result.schema.json) and existing [measurement comparison adapter](compare.py) for corresponding check names/units and pass/fail/error/incomplete states. Retain the instrument's untouched original files, including failed/partial measurements, and SHA256 manifests. Export SI-unit CSVs without replacing originals. Each session has a JSON/YAML sidecar with UTC timestamp, K47FRB serial/batch, front/rear/back/case lead map, fixture revision and photographs/drawings, instrument IDs/firmware/software, calibration certificate/date and correction curves, wiring, approved limits/source, actual applied voltage/current/pressure, duration, sampling/timebase, bandwidth/weighting/window, averaging/PSD confidence, temperature/RH and expanded uncertainty budget. Record range/overload flags and calibration failures; they cannot become passes.

Include open/short/known-reference/blank-fixture records with the same settings. Separate instrument/fixture backgrounds from DUT data, keep complex transfer/cross-spectral data when correlated noise matters, and propagate calibration/fixture uncertainty. Compare only equivalent stimulus, P48/loading, bias and temperature conditions; never pool different instruments/backends into asserted production yield. One capsule is a characterized intended unit, not a population.

Measured parameter changes require a separately dated model/specification decision, a new model identity and uncertainty/correlation evidence. Preserve old assumptions/records and rerun physics controls, affected device validation and complete applicable candidate suites under a common new frozen cohort. Do not silently tighten the existing exploratory envelope, infer a safe bias from simulated operation or fit unknown noise away.


## P0 — Electrode isolation, lead map and approved operating limits

**Uncertainty reduced:** front/rear/backplate/case assignment, tied electrodes, isolation to mounting/case and applicable DC/RF polarity/limits. These are prerequisites for every candidate and both MIC-34 variants; a tied rear electrode would change the servo/carrier/charge fixtures and could invalidate their present port model. Safe polarization is unknown, not 20–70 V or the simulated 22–29 V.

**Fixture/calibration:** first inspect applicable current-batch manufacturer documentation and the unpowered capsule/mount. Only after permissible test stimulus/energy is established, use an existing/borrowed current-limited continuity/isolation fixture to trace accessible leads and metalwork. Record its actual open-circuit voltage, compliance, range and input impedance with a calibrated meter before connection. Never use a high-voltage insulation tester or infer diaphragm isolation by shorting electrodes. Fixture leakage must be measured with a blank mount. Guarding and ESD handling must meet established limits, not assumed capsule ratings.

**Raw format:** `lead_map.csv` (lead_a, lead_b, state, test_voltage_V, current_A, resistance_ohm or lower_bound, uncertainty), original meter logs and fixture photographs; sidecar identifies documentation and unresolved polarity/electrode questions. Resistance above the instrument range is a lower bound, not infinity.

**Safe prerequisites:** no electrode polarization or continuity stimulus without applicable safe conditions; record unresolved limits as blocked. Obtain approved polarization, ramp/discharge, RF allowance and operating environment through existing documented evidence or later separately authorized access/communication. No exploratory pull-in/collapse test is proposed. Without these data, proceed only with documentary and noncontact inspection.

**Model update:** revise port map/electrode connections and verified safe-use metadata separately. Approved maxima constrain later physical tests; they are not a measured mechanical-noise/overload rating. Keep simulation normalization distinct. Re-render all DUT/capsule interfaces and repeat analytic charge controls.


## P1 — Front/rear capacitance and fixture parasitics

**Uncertainty reduced:** assumed 45–100 pF per diaphragm, front/rear correlation, 0.5–10 pF case parasitic and 0–5 pF cross capacitance. This can reverse 0019 versus 0023 response order and affects charge noise gain and carrier bridge balance. Prioritize rear capacitance/case/cross terms as well as front C.

**Fixture/calibration:** existing/borrowed guarded LCR/impedance analyzer with accessible three-electrode configuration and calibrated low-C references. Establish open/short/load corrections at the capsule connector and repeat with the actual intended lead/mount geometry. Measure the complex three-port admittance matrix, including case, at multiple audio frequencies and at the carrier frequency if safe approved RF conditions exist. Report conductor/guard capacitance and uncertainty; do not subtract a guessed constant. Repeat mounting/lead placement to estimate fixture repeatability without purchasing comparison hardware.

**Raw format:** instrument complex impedance exports and `admittance.csv` (frequency_Hz, port_i, port_j, real_Y_S, imag_Y_S, stimulus_V_rms, DC_bias_V, uncertainty/covariance); preserve all calibration sweeps. Extract C/G with fixture corrections and state any noncapacitive loss.

**Safe prerequisites:** P0 lead map and permissible low-level measurement stimulus; begin unpolarized if approved. Bias dependence only within documented approved operating conditions, with discharge verified before reconfiguration. No RF/DC allowance is inferred from carrier simulations.

**Model update:** add measured matrix, uncertainty and correlations to a new capsule/fixture revision. Test whether fixed C is adequate versus frequency/approved bias. Preserve distinction between electrode capacitance, lead/mount parasitics and model lumping error. Re-evaluate 0019/0017/0023 and charge/carrier controls under common conditions before new rank claims.


## P2 — Leakage, settling and low-frequency excess noise

**Uncertainty reduced:** assumed 1 GΩ–100 TΩ, polarity/temperature/RH dependence, charging transients, excess noise beyond Johnson behavior. The shared 1 GΩ endpoint causes 22.80/18.46 dB response deviation and perturbs JFET bias/current. This measurement can defeat both fixed-bias and servo candidates before further optimization; it also bounds CMOS reset authority, bipolar base-current margins and carrier insulation demands.

**Fixture/calibration:** existing/borrowed electrometer or low-current TIA and calibrated current/charge injection, shielded guarded intended mount, quiet approved source, temperature/RH logging. Demonstrate instrument/fixture leakage with open input and blank mount, and calibrate gain/offset/frequency response using traceable injection. Record settling until a defensible endpoint or censoring limit; isolate supply ripple/correlated environmental noise with synchronized source and output channels. Avoid contamination or stressing the intended capsule. Document background subtraction and uncertainty rather than reporting a zero residual.

**Raw format:** untouched time series, `leakage.csv` (time_s, electrode_voltage_V, current_A, temperature_C, RH_percent, range/overload), and `noise_psd.csv` (frequency_Hz, current_PSD_A2_per_Hz, voltage_PSD_V2_per_Hz, cross_PSD_real/imag, degrees_of_freedom, confidence bounds). Include settling fits only as derived files and retain outliers/failures.

**Safe prerequisites:** P0 approved bias/polarity/environment and current limiting, P1 fixture knowledge; no humidity/voltage sweep beyond approved conditions. Do not force a bias to match a simulated endpoint. Access to any environmental facility is unknown; document controlled ambient conditions if no chamber is available.

**Model update:** replace the purely resistive leakage hypothesis where supported with measured I–V/time/RH/temperature dependence and separately evidenced noise spectra/correlations. Update DC and stochastic models independently; retain uncertainty outside measured conditions. Pair no-trim bias-authority scenarios, rerun startup/full suite and map whether the measured unit lies in a ranking reversal region. A single unit cannot close production leakage/yield coverage.


## Immediate next work and stopping rules

First establish capsule/equipment/documentation access and safe conditions. Meanwhile continue the paired endpoint and analytic controls without hardware. P1/P2 most directly test the 0019/0023 ranking reversals and shared low-leakage failure; P3/P4 determine whether electronics merits can satisfy system goals. Keep 0012 as a charge/reset falsification control and retain CMOS/carrier niches on their prerequisite tracks.

Stop or mark incomplete when calibration fails, instrument/fixture floor dominates, safe limits are absent, a transient is unsettled, parameter extraction is not identifiable, or an affected implementation gate is unresolved. Preserve the record and explain which uncertainty remains. No purchases, supplier messages, unused comparison hardware or safe bias inferred from a simulation are requested.

[Remaining procedures and closure criteria](priority-procedures.md).
