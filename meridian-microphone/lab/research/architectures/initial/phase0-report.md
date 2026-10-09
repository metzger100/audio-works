# M100 Meridian: initial research environment and evidence report

Date: 2026-10-05. Scope: **Phase 0–2 foundation**, with initial Phase 4 concept proposals and a numerical-workflow control. No production topology or prototype has been selected.

The workspace now runs real ngspice analyses, records complete evidence, rejects incomplete qualification, performs bounded numerical value search and preserves architectural niches. **22 independent regression checks pass.** Both final fixture evaluations finish all their SPICE jobs successfully; both fail engineering qualification. The eligible Pareto front and champion registers are correctly empty.



## What is executable



- First-order two-diaphragm electrical capsule model, nonlinear charge law and a linearized electronics-distortion mode.
- Loaded P48 supply, separate feed resistors and mismatches, cable/shield resistance and capacitance, AC-coupled preamp impedance and mismatch.
- Fourteen named engineering checks: operating point, response, noise, distortion, headroom, output impedance, balance, P48, temperature, semiconductor corners, Monte Carlo, loading, startup and stability. Some remain explicit incomplete screens, as detailed below.
- Noise integration with unweighted and A-weighted results and separate bias, polarization, power, output and capsule-leakage-surrogate contributions; H2–H10 spectra and coherent settling checks.
- SciPy differential evolution, parameter bounds and numerical constraints, raw trial preservation, full-suite re-evaluation and controlled parent comparisons.
- Experiment snapshots, source/specification hashes, exact simulator decks, raw files, failure logs, software versions, seeded uncertainty scenarios and strict result status handling.
- A quality-diversity archive, separate novelty descriptors, structural child registration, exploration allocation and a bounded evaluator for supplied Engineer netlists.
- A measurement interchange contract and comparison adapter, with a [synthetic adapter smoke check](../../../results/reports/measurement-adapter-smoke.json). No physical data have been collected.

## Capsule evidence and uncertainty



The [current manufacturer page](https://store.arienneaudio.com/microphone-capsules/20-26-arienne-audio-flat-k47-microphone-capsule.html#/12-options-cardioid_omni) identifies the Flat K47 Cardioid/Omni K47FRB, modified tuning and changed manufacturing facility. It does not supply the electrical/mechanical data needed to qualify this microphone. A different regular K47's advertised capacitance is not transferred to this model.

## P48 evidence and environment



The [IEC official catalogue](https://webstore.iec.ch/en/publication/30762) identifies IEC 61938:2018 edition 3; its catalogue stability date is 2030. The public preview does not include the full phantom-power clauses. The [SCHOEPS manufacturer manual](https://schoeps.de/fileadmin/user_upload/user_upload/Downloads/Bedienungsanleitungen/Schoeps_Manual_V4_U_DE_1388740809.pdf) supports the public P48 summary of 44–52 V, nominal 6.8 kΩ feeds, pair matching below 0.4% and maximum total microphone current 10 mA.


## Frozen provisional requirements



Electronics targets are ±1 dB from 20 Hz to 20 kHz, unweighted EIN ≤1 µV RMS, conditional electronics noise ≤4 dBA, THD ≤0.01% at 1 Pa and ≤0.5% at the 135 dB pressure stimulus, output impedance ≤200 Ω, impedance mismatch ≤1%, HF peaking ≤3 dB and cold-start settling ≤5 s. Total current is limited to 10 mA. Inherited 7 dBA system noise and 135 dB SPL aspirations remain contingent on capsule measurements.

## Actual sanity-fixture results



The [plain netlist](../../../candidates/fixture_0001/circuit.cir) is an **ideal, noiseless differential-buffer infrastructure fixture**, with a passive P48 harvest/load network. Ideal active sources do not draw realistic audio-driver power or clip. Its current, THD and headroom screens cannot qualify any real architecture. It is ineligible by construction.

## Diversity and research memory



[22 Inventor concepts](../../../search/concepts.yaml) cover all [14 required architectural families](../../../search/families.yaml). Twenty avoid a conventional JFET voltage-buffer input; multiple proposals borrow charge amplifiers, electrometer guarding, capacitance bridges, low-current transimpedance sensing and sensor-interface mechanisms. Each specifies the sensed quantity, loading, DC bias, gain, balanced output, likely noise/distortion, fatal flaw and fastest falsification experiment. The [cross-domain register](../../cross-domain/mechanisms.md) links primary application reports, datasheets and research.


## Evidence needed before later phases



1. Phase 3: current, documented semiconductor types, model licences, manufacturer limits, noise/temperature behavior and defensible populations; then a strong fairly optimized no-selection JFET reference and several distinct controls.
2. Phase 4–7: Engineer netlists for diverse concepts, structural search, robust optimization, passive/semiconductor tolerance and correlation populations, full noise/distortion/environment coverage, meaningful loop injection and stability analysis, device power/SOA and statistically supported all-requirement yield. Current scenario Monte Carlo is only a screen.
3. Capsule characterization: safe polarization and lead isolation first; calibrated front/rear capacitance/parasitics, sensitivity/spectra, leakage versus humidity/temperature, noise/overload and angular response with the intended headbasket. Replace assumed model parameters without changing the software architecture.
4. Phase 8: the [patent track](../../patents/README.md) is prepared but has no screened patent claims yet. Relevant jurisdictions, priority/status/claims and uncertain cases require separate documented research; no freedom-to-manufacture conclusion is made.
5. Phase 9–10: compare several fundamental families before selecting prototypes; add RF/ESD/protection/humidity, connection transients and PCB parasitics; collect calibrated measurements through the [interchange](../../../measurement/README.md), compare with simulation and revise models from evidence.

## Reading and evidence



This compact view retains findings and limits. Consult the [complete original report](../../../../../docs/history/2026-10-09/meridian-microphone/lab/research/phase0_report.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../../docs/evidence.md) and [scientific contract](../../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../../docs/validation.md).


## Reading and evidence


This compact view retains findings and limits. Consult the [complete original report](../../../../../docs/history/2026-10-09/meridian-microphone/lab/research/phase0_report.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../../docs/evidence.md) and [scientific contract](../../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../../docs/validation.md).

## Reading and evidence

This compact view retains findings and limits. Consult the [complete original report](../../../../../docs/history/2026-10-09/meridian-microphone/lab/research/phase0_report.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../../docs/evidence.md) and [scientific contract](../../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../../docs/validation.md).
