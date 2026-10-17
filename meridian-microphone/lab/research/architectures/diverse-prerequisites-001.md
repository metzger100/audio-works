<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Diverse mechanisms through independent prerequisites — 001

16 October 2026. M100 Meridian MIC-34-M/MIC-34-C, K47FRB/P48. **Charge/reset and ideal periodic-noise oracles are supported in their declared fixtures; actual floating CMOS, BJT noise/authority and integrated carrier prerequisites remain incomplete.** All14 families survive. No implementation, BOM, measured result, prototype or PCB is promoted. The realized JFET path remains primary; no unsupported advantage is claimed.

[Exact finite plan](diverse-plan-001.yaml) · [Independent derivations](diverse-derivations-001.md) · [Source methods](diverse-source-notes-001.md) · [Receipt/query ledger](diverse-sources-001.json) · [22-concept knowledge matrix](diverse-knowledge-001.json) · [Machine analysis](diverse-analysis-001.json) · [Behavior rows](diverse-behavior-001.csv) · [Coverage table](diverse-coverage-001.md) · [Feature/patent review](../patents/diverse-prerequisites-001.md).

## Audit and cohorts

Inspected all contracts/specifications,22 concepts/14 families, exact0012/0010/0014/0013 and0024 netlists/failures, comparison001, carrier protocol and actual Prompts6–9. Their device identities, capsule envelopes, nonlinear limits, leakage/startup/driver failures and full-suite states remain authoritative.

The catalogue retains22 concepts:20 nonconventional inputs and17 instrumentation transfers. This is **not a periodic Inventor challenge**: the20/10/5 minimums remain unchanged. All nine physical answers and proposal/performance flags survive. [Continuation audit](diverse-continuation-audit-001.md) verifies the retained evidence; no implementation or performance is inherited.

| Cohort | Actual finite execution / retention |
| --- | --- |
| [Preflight62bed241](../../results/mechanism_controls/20261016T130908Z_diverse_preflight_62bed241/failure.json) |0 simulations; preserved Markdown-as-YAML traversal error and exact runner bytes |
| [Primary00c8217a](../../results/mechanism_controls/20261016T130909Z_diverse_00c8217a/results.json) |50 simulator attempts:48 isolated jobs plus2 exact-parent diagnostics;15 execution errors including missing environment dependency and one island timeout.32 separate seeded numerical records. Source unchanged true |
| [Follow-up2834cfe4](../../results/mechanism_controls/20261016T131328Z_diverse_followup_2834cfe4/results.json) |3 predeclared repeats: two parent DC/AC jobs with missing P48 include frozen, one carrier-off saved-window repeat. All execute; frozen bytes unchanged. Original failures remain |

Total53 simulator attempts:38 execute,15 retain errors. Execution is not qualification. The15s timeouts, numerical options, optimization reservations and scientific thresholds are unchanged. The successor freezes the missing include and saves20–30ms. The carrier-off timeout retained its log; no waveform was written. Completed cases retain startup. The report checks1,033 inventory entries; frozen sources remain original.

## Track1 — BJT charge/reset

Twelve finite-gain AC controls span2Cf×2Rf×3capsule C; complex KCL differs from SPICE by at most1.12e−15 relative. Two independently calculated constant-gain reset pulses differ by less than0.089µV. Two DC current-demand controls expose unlimited-source voltage demand and receive no real-device authority pass. These are ideal mechanism controls before any structural child.

Exact0012/0024 replay uses the complete original P48/capsule/output circuit. Independent input KCL retains actual capsule polarization, backplate motion, case/mutual capacitance, reset network and observed macro base current; relative residuals are9.43e−13/2.84e−14. This tests the external conversion calculation, not independent semiconductor physics.

| Nominal diagnostic |0012 |0024 |
| --- | --- | --- |
| Effective feedback C |100nF |99.9001pF plus actual losses/insulation |
| DC reset |500kΩ |500kΩ |
| Approximate RfCf corner |3.183Hz |3186Hz |
| Actual input base current |1.93383µA |1.93383µA |
| Reset DC supplied current |1.933807µA |1.933807µA |
| Differential sensitivity at1kHz |13.2233µV/Pa |1.45903mV/Pa |
| Differential output conversion at1kHz |25.4009MV/C |2.80268GV/C |
|1Hz-origin64/dec response deviation, exact20Hz/20kHz edges |20.9266dB |32.8229dB |

These diagnostics supplement the original32/dec full-suite deviations20.9306/32.8192dB. They use simulated polarization22.3107V and motional charge0.520584pC/Pa. Raw global voltages include microphone-ground offset; conversion/KCL use differences. Tiny electrode voltage is not treated as loss of charge. The parent has low charge-to-voltage scale; the smaller-C child gains output but moves the bleed corner into audio. Base conductance/capacitance, finite differential-stage gain and coupled supply/backplate/output loading remain relevant.

The independent hypothetical current-noise example at IB0.5µA,Vp40V yields15.26–16.75mPa RMS over20Hz–20kHz for white shot+reset noise, rising28.55–29.38mPa with an assumed100Hz current-flicker corner. These are conditional mathematical scales, **not0012 noise results**. Actual KF/current spectra and production coverage remain missing. Raising reset resistance to100MΩ at the observed1.934µA would require about193V; mean-current cancellation alone cannot eliminate shot noise.

No BJT child is justified yet by reset authority or measured current/flicker noise. Replacing the input with a JFET would change the mechanism. The surviving no-FET niche is a separately controlled AC charge loop with an independently noisy DC current actuator, or a bipolar carrier detector; both remain proposals. Before realization, measure/model low-current BJT two-port/capacitance and base-current spectra at the intended bias, then run two actuator-current endpoints. If that falsifies the LF noise/authority hypothesis, retain the result without retiring all no-FET mechanisms.

## Track2 — CMOS translation and guard/charge

The unchanged macros use16V rails,8V input/output-load reference,10kΩ load. Both rails and every input/output/load reference translate with local ground; ideal gauge controls give8V relative output at0/+20/−20V. They receive no CMOS current/noise credit.

| Actual macro follower |0V reference |+20V |−20V |
| --- | --- | --- | --- |
| OPA197 |8.00001962V;1.000002mA |Convergence warning, unsupported |Relative-output delta1.34nV; supply-current delta2.56pA, local screen passes |
| OPA928 |7.99999846V;0.275000mA |Convergence warning, unsupported |Convergence warning, unsupported |

Grounded0.1/15.9V CM executes; OPA928 upper-CM1kHz gain is0.95045 versus1.00000 at8V, without nonlinear/common-mode qualification. Grounded rail power is16.0000mW/4.4000mW before other microphone circuitry. Ground/reference source currents are retained; baseline translation-source residual is−8.53pA/+0.274pA. No P48 dynamic-power or implicit-ground leakage qualification follows.

OPA197's global-ground capacitors, rail-conversion/MID and limiter/noise blocks are explicit macro dependencies; its header already describes a ground-float IQ change. +20V failure and −20V success do not identify a unique broken switch or justify changing vendor internals. A physical rail-reference translation should be invariant; this limited asymmetric numerical behavior remains a macro/backend prerequisite. Preserve original macros and failed0010/0014 integrations.

Both actual grounded and+20V charge fixtures remain unsupported. Both OPA197 reset transients fail strict prerequisites; no settling/noise result is extracted. The independent charge oracle still predictsτ0.1s and noise gain≥1.7 for70pF/100pF, while the full retained leakage envelope can exceed real DC output authority. A finite ideal reset diagnosis cannot rate CMOS performance.

The two-macro grounded OPA928 external guard executes with1kΩ isolation and load0/100pF/1nF. At20kHz, complex tracking changes from0.999906−j0.014465 to0.983741−j0.138325. The observed input admittance includes actual macro input C and driven-guard coupling; its negative real component is not a stability proof. OPA197 guard cases warn/fail. Separate ideal feedback controls match the admittance equation within2.34e−15; excessive gain2 gives RHP poles+35.86/+10186.77s⁻¹ despite a converged AC solution. This falsifies “good AC execution implies stable bootstrap,” without asserting actual CMOS instability.

Next: reproduce the actual macro's **grounded charge** DC/AC/reset fixture in its documented reference backend and compare terminal currents with the unchanged file. Then test the complete translated fixture and isolate rail/limiter dependencies. For a physical guard, add driver noise and loaded return-ratio tests before a child. No ideal substitution or internal rewrite is promoted.

## Track3 — carrier ideal mechanism and physical integration

The successful older isolated bridge control and failed integrated P48 parent0013 remain separate. The new isolated anti-phase fixture recovers1kHz at1.00350/1.00528 of its analytic27.34µV peak oracle at32/64 maximum steps per carrier; relative change0.001775 is below the retained0.005 screen. Zero pressure gives2.54e−11 of oracle; the carrier-off successor gives1.25e−4. The extra sideband `/2` in the older prose is corrected by the anti-phase derivative in the new derivation; the old executable/bytes stay intact.

A separate seeded **ideal LPTV** bridge/mixer/filter example uses one-sided arm PSD1e−16V²/Hz, cross-correlation0.6,100kHz carrier and100µs RC. White and AR(1)10kHz colored spectra, four seeds, two sample rates and two record lengths produce32 saved records. Source variance ratios are0.96155–1.00466. Individual output/analytic power ratios are0.92946–1.07259; eight ensemble means are0.98343–1.02982 and all pass the predeclared10% local screen. Their independent-seed95% intervals include unity. This is finite statistical agreement, not an arbitrarily precise noise rating.

Covariance-series versus independently shifted-spectrum integration differs by at most5.54e−13. Parseval closes normalization; identical shared sources cancel exactly. Carrier-off variance, source correlations, Hann/boxcar PSDs and ENBW remain. PSD bins48.83/97.66Hz and ENBW73.24/146.48Hz do not resolve the20Hz edge; selected-bin integrals are not a qualified20Hz–20kHz estimate. Burn-in20τ and raw arrays are saved. The colored source is Lorentzian-like, not a substituted semiconductor1/f law. Sampling refinements test the declared discrete process and its images; unmodeled analog noise above Nyquist is not assumed absent.

[ngspice47](https://ngspice.sourceforge.io/docs/ngspice-47-manual.pdf) documents experimental autonomous PSS and experimental TRNOISE injection, without establishing native periodically biased transistor noise for this architecture. [Xyce documentation](https://xyce.sandia.gov/documentation-tutorials/) does not establish that ordinary NOISE plus HB supplies a periodic-noise analysis. No alternate solver was installed/pooled. The precise missing prerequisite is a validated periodic operating point with bias-dependent device source spectra and sideband covariance, or independently calibrated explicitly seeded physical-device sources under periodic bias, within the existing settling/refinement/estimator protocol. Ordinary stationary `.noise` remains ineligible.

Real oscillator, buffers, mixer, output stage, switched/guard current, loading and RF-safe capsule conditions are still missing.0013's DC1.234mA is partial ideal-hardware accounting, not total architecture power. No native periodic microphone noise number is reported. Next: validate the same calculable correlated-noise bridge in an accessible periodic-capable reference backend or a documented seeded source-injection circuit; only then substitute each real oscillator/buffer/mixer source and its dynamic supply paths.

## All-family finite next tasks and parts

The matrix gives every family a distinct finite prerequisite with conditions/count and a stop rule. Executed rows link this batch; remaining tasks are unexecuted. Minimal-device transformer loss, differential capacitance/covariance and current-conveyor noise retain their own niches. No failed macro or absent ideal power retires a family.

Useful library lead **ADA4530-1ARZ**,8-lead SOIC, has documented guarding and an official macro link, but that link redirects to an explicit licence agreement. Acceptance is unauthorized; no model was downloaded or added to the validated registry. A future acquisition needs owner-authorized terms and grounded/translated/charge/guard/noise controls. **Hamamatsu S5973-01**,TO-18 lens photodiode, is an informative optical-actuator limit, not a qualified reset part: dark-current limits and temperature/noise must be checked at actual near-zero-bias conditions. The source paper's custom photoemissive cell does not satisfy the ordinary-production-part constraint and its zero-dark-current assertion supplies no noise proof. [Primary part notes](diverse-source-notes-001.md) preserve the conflicting photodiode test-bias descriptions.

Keep0019/0023/0025 as the realized JFET investigation: focused001's nominal filtering benefit survives its retained1GΩ authority and servo-startup failures. Next is the unchanged bilateral multi-loop prerequisite and a separately derived leakage-authority remedy. No new full comparison is warranted while different mechanisms have unequal prerequisite coverage.

[Patent-feature alternatives](../patents/diverse-prerequisites-001.md) separately compare explicit structures with two official publications. Granted/amended claims, official territorial/current status and wider searches remain incomplete; no design-around/clearance is claimed. No BOM is invented for ideal or unimplemented controls. Any later structural child must use mutation registration, exact ordinary parts and full applicable requalification.

## Reproduction and completion

From the lab, new finite experiments use `MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python tools/controls/diverse_prerequisites.py`. The explicitly pinned repair is `tools/controls/diverse_followup.py`; it reads the retained original cohort and creates a unique successor. Rebuild only tables/integrity with `MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python tools/reporting/diverse_report.py`. Sources, models, specifications, runtime and implementations freeze before execution; reruns create new records.

[Completion validation](../../../../docs/validation/2026-10-16-diverse-prerequisites.md) records doctor, full shared regression, root gates, inventory and original-evidence limitations. Raw waveforms/seeded arrays/vendor/document bytes remain local with inventories; GitHub covers committed authored/compact records. No commit/push/publication, purchase, contact or licence acceptance was performed. Qualified fronts remain empty; capsule safety/mechanics, real-device noise/production, sourcing and patent gates are unchanged.
