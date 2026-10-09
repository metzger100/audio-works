# Measurement procedures and closure

[Priority plan](priority-plan.md). All prerequisite gates remain applicable.

## P3 — Calibrated sensitivity and electrical/acoustic transfer

**Uncertainty reduced:** 5–40 mV/Pa at the 60 V mathematical reference, actual transfer at approved polarization, front/rear acoustic coupling and frequency response. Common sensitivity scaling changes conditional pressure-noise budgets by +12.04/−6.02 dB at the assumed endpoints; real bias/C/mechanical correlations could change relative merits. All families' absolute noise/headroom interpretations depend on this result.

**Fixture/calibration:** existing/borrowed calibrated acoustic reference and pressure calibration facility, low-noise interface and a separately characterized high-impedance test receiver. Reference hardware is a facility requirement, not a proposed purchase. Establish pressure at the intended capsule position, reference uncertainty, receiver input loading/capacitance/gain/noise, acoustic field reflections and headbasket effects. Use simultaneous pressure/electrical recording, quiet room/coupler appropriate to frequency, and deembed the receiver only within validated accuracy. Start with moderate approved pressure; characterize sensitivity/frequency response before angular tests. Pattern switching follows confirmed electrode configuration.

**Raw format:** original synchronized recordings and `transfer.csv` (frequency_Hz, pressure_Pa_rms, output_V_rms, complex_gain_V_per_Pa, coherence, angle_deg, bias_V, uncertainty), calibrated reference data and room/fixture configuration. Keep bare/intended-headbasket and front/rear/pattern conditions distinct.

**Safe prerequisites:** P0/P2 approved bias and stable leakage, calibrated test receiver, known acoustic exposure limits; no assumed 135 dB test. Physical implementation/prototype fixtures must meet the separate patent/engineering gates before affected construction/use is selected.

**Model update:** add a measured transfer function at actual approved bias rather than inventing a 60 V physical measurement. Version pressure normalization/compliance/temperature assumptions with measured uncertainty. Rerun electronics comparisons with common measured transfer; do not hide receiver noise/loading or claim that electronics repairs intrinsic acoustic problems.


## P4 — Capsule acoustic noise, mechanical nonlinearity and overload

**Uncertainty reduced:** absent Brownian/acoustic noise, room floor, mechanical response/distortion/pressure overload, bias-dependent softening and intended-headbasket angular behavior. This could show that every electronics optimization is below a capsule floor, or that the ≤7 dBA/approximately ≥135 dB SPL goals are unattainable for this intended unit. It affects all architectures and both variant claims, regardless of nominal electronics rank.

**Fixture/calibration:** existing/borrowed quiet acoustic chamber/facility, calibrated pressure reference and low-noise receiver with independently measured electrical floor. Validate room/chamber background, vibration isolation, receiver noise under equivalent sensor loading, pressure source harmonic distortion and dynamic range. Acoustic noise needs sufficiently long raw recordings and PSD uncertainty; A-weighted and unweighted bandwidths stay explicit. For overload, use controlled incremental acoustic stimuli within approved limits, independent source/reference monitoring, conservative stop conditions and recovery observations. No destructive capsule endpoint/pull-in search is planned.

**Raw format:** unedited audio/time series plus calibrated PSD/cross spectra and `harmonics.csv` (frequency_Hz, pressure_Pa_rms, H1–H10_V_rms, THD_percent, fitting/window settings, settling/change, source_distortion, uncertainty, censoring). Record first observed failure and safe-tested lower/upper brackets; an unobserved boundary stays right-censored and never becomes a maximum SPL. Preserve pressure/angle transfer files for cardioid/omni and intended headbasket separately.

**Safe prerequisites:** P0 approved capsule voltage/acoustic operating conditions, P3 calibration/receiver validation and applicable implementation gates. If an acoustic exposure ceiling is unknown, do not seek an overload boundary. Distinguish facility acoustic/receiver limits from capsule behavior.

**Model update:** add acoustic/mechanical transfer/noise/nonlinear terms only supported by deembedded evidence. Preserve background-limited bounds and uncertainty. Revisit system targets through a separate owner/spec decision if evidence warrants it; do not change thresholds merely to admit a candidate. Electronics distortion remains distinct from measured capsule distortion.


## P5 — Device and integrated interface falsification

**Uncertainty reduced:** JFE current-noise/gm/process discrepancies; bipolar 1/f/input-current/offset; OPA floating-rail behavior; driver noise/balance; servo loops; actual loss/leakage of capacitor combinations; carrier oscillator/mixer folding. These can change every electronics ranking after P1–P3 establish realistic loading. Independent simulated controls precede affected physical construction: floating-macro DC/current/common-mode oracle, servo return-ratio/Nyquist, BJT reset/charge oracle and calculable periodic noisy bridge.

**Fixture/calibration:** existing/borrowed low-noise analyzer, calibrated DC supplies/current limit, oscilloscope/differential probes, network/impedance injection and actual P48/cable/preamp interface. Validate probe loading/noise, common-mode range, injection gain/phase and feed mismatch. Characterize actual intended devices at corresponding biases; do not buy populations for self-selection or hand match. A permitted assembled design would measure device terminal current/power, three-port input loading, two-port impedance/balance, eight interface corners, startup/connect/disconnect and loop return ratio. RF/ESD/humidity/SOA need separate safe facilities and procedures; no access is assumed.

**Raw format:** original analyzer/scope files, DC terminal/current tables, complex port/loop CSVs, PSD/cross spectra, H2–H10/refinement/recovery time series, actual capacitor impedance/leakage versus frequency/voltage/temperature and explicit parts/fixture hashes. Record failed convergence/measurement runs and adverse cases; never average them away.

**Safe prerequisites:** documented device ratings/thermal/SOA and capsule-safe limits, resolved affected patent/prototype gates, realistic protection and current-limited commissioning. Carrier RF allowance and complete power/noise hardware remain unresolved; ordinary stationary SPICE noise cannot substitute for its periodic measurement/model protocol.

**Model update:** calibrated device/passive/loop observations create versioned models and scope restrictions; original manufacturer/child models stay intact. Freeze the new shared cohort and rerun all applicable tests/realized-BOM combinations/substitutes. Do not infer a production joint distribution from one intended microphone; credible yield needs separately sourced population evidence without any selection/trim strategy.
