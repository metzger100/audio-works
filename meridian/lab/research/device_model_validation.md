# Phase 3 semiconductor-model prerequisite — 2026-10-05

**Readiness is partial and behavior-specific.** Eight hash-pinned SPICE files represent four exact device types, alongside a rejected MOSFET download and alternative investigations. OPA197 alone is the smallest set agreeing with the tested grounded, mid-common-mode, small-signal DC/capacitance/bandwidth/noise references. There is **no fully validated device set for a complete JFET/CMOS/bipolar microphone architectural comparison**, production variation or P48 output/power qualification. No architecture, PCB or prototype is selected.

The [registry](../models/semiconductor/registry.yaml) records exact variants/packages, manufacturer lifecycle/ratings, source/date, version/hash, syntax, redistribution state and represented/missing behavior. [References](../models/semiconductor/references.yaml), [primary evidence](device_sources/README.md) and [Germany procurement](procurement/semiconductors_2026-10-05.yaml) remain separate. Unknown behavior is never zero or a pass.

## Method and evidence

Manufacturer tables/curves constrain the models; independent physical controls constrain SPICE. No physical semiconductor or capsule measurements exist. Guaranteed limits, typical values, coarse graph-reading intervals and numerical consistency have distinct statuses. The predeclared ±20% typical-value screen is a research model-accuracy check, not a microphone specification or production bound; numerical refinement uses 1%. Neither threshold changed to admit a device. Typical weak/strong noise/curves remain quantified references, not guaranteed corner limits.

The [characterizer](../models/semiconductor/characterize.py) freezes shared sources before evaluation and captures model/version/deck hashes, syntax mode, temperature, raw data, CSVs, errors and parents. Deterministic grids use `rng_seed: null`; no statistical manufacturing distribution is inferred. Vendor bytes, original notices, failed responses, full waveforms and their CSV exports remain locally preserved. Copyright/model redistribution permission was not established, so fresh checkouts use reproducible acquisition rather than redistributed models. Git retains authored scripts, metadata, logs, decks, compact records and waveform checksum inventories; ignored evidence is not deleted.

The authoritative corrected batch is [20261005T185102Z_95a6dda5](../results/device_models/20261005T185102Z_95a6dda5/results.json): **118 jobs, 111 complete, seven rejected numerical jobs, plus the pre-simulation 2N7002 acquisition rejection**; sources remained unchanged. Vendor decks set operating temperature explicitly; nominal jobs use 25°C, with ngspice’s global TNOM=27°C logged unless a model overrides it. The original model calibration and temperature laws are preserved, not refitted; calibration-temperature fidelity remains an uncertainty. Completed jobs can still disagree with published evidence. Later metadata/provenance safeguards do not alter the vendor bytes or these electrical results; final verification captures the updated sources separately.

## Coverage matrix

Agreement means only the listed conditions. Recorded numerical behavior without independent device agreement remains unqualified.

| Device/model | DC and bias | Capacitance / bandwidth | Temperature / leakage | Voltage, current, 1/f noise | Clipping / supply current | Scope |
|---|---|---|---|---|---|---|
| JFE150 generic / combined PSpice | Nominal Idss/bias mostly within limits; guaranteed GFS fails | Bias-dependent capacitance recorded; reference gate bias ambiguous; broadband unqualified | Five-temperature transfer; nominal full-temperature Idss limits agree; specified 25°C leakage agrees; high-field/temperature leakage unknown | Useful nominal voltage spectra; 100 µA/10 Hz and gate-current noise disagree; production maxima unknown | Native large-signal/current records refine; physical clamp, overload and SOA unknown | Nominal hypothesis work; no complete bounded production/noise set |
| JFE150 weak / strong | Weak Idss low; both GFS low; strong bias limits fail | Recorded, not qualified corners | Weak full-temperature Idss fails; correlations unknown | Spectra retained; typical data do not bound extreme corners | Transients refine; independent clipping validation missing | Coupled vendor proposals retained as failures |
| BC846B original | Floating Q2 emitter; −10°C/25°C jobs fail | Nominal work blocked | Partial other-temperature data retained | KF absent; no usable nominal validation | Unknown | Original file retained without performance credit |
| BC846B emitter-node child | Tested hFE/VBE limits agree | fT minimum agrees; Cc typical disagrees | Five temperatures recorded; reverse leakage, production variation and self-heating unknown | White/shot simulation; NF typical disagrees; 1/f and separate en/in unqualified | Saturation limit agrees at 10 mA/0.5 mA; broader dynamics/SOA unknown | Nominal DC/output-control research; correction not vendor-approved |
| BC856B original | Tested hFE/VBE agree; grade header conflicts | fT minimum agrees; Cc typical disagrees | Five temperatures recorded; no complete temperature/leakage validation | NF typical disagrees; KF/1/f absent | Saturation limit agrees; full output/power unknown | Nominal DC controls; exact-variant sourcing hold |
| OPA197 PSpice | Grounded mid-common-mode Ib/Iq agree | Common-mode Cin/open-loop GBW agree; differential Cin/floating operation unknown | −40…125°C macro laws recorded; no production bias/Iq population | Explicit voltage white/flicker and current-white sources; tested en/in agree; crossover/production unknown | Five nonlinear jobs fail; clipping, loaded current, recovery and THD unqualified | Smallest scoped small-signal/noise control set |
| Nexperia 2N7002 | No acquired model | Unknown | Unknown | Unknown, including low-current 1/f | Unknown | HTML response rejected despite HTTP success |
| MMBFJ113 / further alternatives | Primary electrical investigation only | No audited model | No full joint bounds | No qualified spectrum | No qualified output/power set | Exact active order code/model/sourcing unresolved |

OPA's five failures comprise two DC clipping branches, loaded-supply sweep and two transients; the other two numerical failures belong to original BC846B. The presence of macro protection blocks is not validation. Terminal currents do not qualify an external regulator, complete balanced output or P48 fault protection.

## Quantified disagreement and agreement

### JFE150

At 25°C, VDS=10 V/VGS=0, generic Idss is **26.902 mA** (guaranteed 24–46), GFS **49.109 mS**, **10.71% below** the guaranteed 55 mS minimum. Weak gives **17.904 mA / 36.469 mS**; its −40°C/125°C Idss **18.443 / 14.993 mA** fall below the full-temperature 22 mA minimum. Strong gives **40.049 mA / 37.215 mS**, and also misses the tested 2 mA/100 µA/100 nA gate-voltage intervals. Coupled BETA/VTO/series resistances remain unchanged; these are not a defensible guaranteed production set under tested conditions.

At VDS=5 V/2 mA, nominal en is **1.784 nV/√Hz at 10 Hz**, **0.8755 at 1 kHz**, against 1.6/0.9 typical (+11.5%/−2.72%). At 100 µA/10 Hz it is **2.349** against **3** typical (−21.7%), outside the screen. Gate-current noise at 2 mA/1 kHz is **0.4879 fA/√Hz** against **1.8** typical (−72.9%). Current noise remains unqualified. No typical noise value is a guaranteed production maximum. Noiseless CCVS observers and actual interpolated bias currents are recorded.

Specified leakage at VDS=2 V/VGS=−0.7 V/clamps +5/−5 V is **3.549 pA**, below 10 pA maximum. Other jobs use a high clamp at 25 V to avoid clamping a swept drain; their approximately 44 pA is a different bias, not failure of the 10 pA specification. High-field/temperature leakage remains unknown.

Operating Ciss is **15.506 pF**; explicit VGS=0 tests give **26.617 pF at VDS=0**, **17.818 at VDS=5 V**. The capacitance reference gate bias is unclear, and the table's default 2 mA cannot apply at VDS=0. Comparison with 30/24 pF typical is condition-unresolved; neither bias was chosen to declare validation. Crss/Coss, broadband and package parasitics need additional independent characterization.

Transfer figure 6-1 and output figure 6-3 conflict at the same stated VDS=5 V/VGS=−0.7 V beyond coarse reading intervals. The model gives **2.423 mA**, within the transfer interval 1.8–2.8 mA and below the output interval 3.5–4.3 mA. Both are preserved without fitting. Generic and combined PSpice versions have **zero disagreement in common measured scalars** because their electrical parameters match: compatibility agreement is not independent model consensus.

### Bipolar models

Original BC846B connects Q2's emitter to otherwise unconnected node 33. The [preparer](../models/semiconductor/prepare.py) creates a hash-pinned child changing **only 33 → 3**. The acquired complementary BC856 topology supports this hypothesis; vendor approval is not established. Original failures/partial results remain.

At 2 mA/5 V/25°C, corrected NPN hFE/VBE are **294.885 / 0.66677 V**; PNP **299.013 / 0.67590 V**, consistent with guaranteed grade/bias intervals. BC856's header hFE 125–250 conflicts with the B-grade 220–475 datasheet interval and remains flagged. At IC=10 mA/VCE=5 V the manufacturer's fT test (|hfe| at 100 MHz × 100 MHz) gives **216.97 / 118.90 MHz**, above 100 MHz minimum. Interpolated unity-current-gain frequencies are separate measurements. VCE(sat) **59.40 / 53.48 mV** at IC=10 mA/IB=0.5 mA agrees with 200/300 mV maxima. These independent nominal checks constrain the structural correction without fitted parameters.

Cc at |VCB|=10 V/1 MHz/approximately open emitter is **1.195 / 1.848 pF**, **−40.2% / −58.9%** versus 2/4.5 pF typical. Explicit 1 TΩ versus 1 GΩ emitter-return refinement changes it by <4×10⁻¹³ relatively. NPN remains below its 3 pF maximum, which does not validate typical accuracy. NF at 200 µA/5 V/2 kΩ/1 kHz is **0.571 / 0.697 dB**, **1.429 / 1.303 dB below** 2 dB typical, though below 10 dB maximum. KF is absent. Incomplete shot/thermal noise cannot qualify a low-noise input. Separate voltage/current spectra, correlations and production 1/f remain unknown; no favorable compensation was invented.

### OPA197

At ±18 V/25°C/grounded mid-common-mode/10 kΩ, Iq **1.0000 mA** agrees with 1.3 mA maximum, |Ib| **5.010 pA** with 20 pA maximum, and common-mode Cin **6.40016 pF** with 6.4 typical. En **10.285 / 6.091 nV/√Hz** at 100 Hz/1 kHz differs from 10.5/5.5 typical by −2.04%/+10.75%; in **1.4835 fA/√Hz** differs from 1.5 typical by −1.10%. Doubled noise-grid density/tighter tolerances agree within rounding. This validates tested macro behavior against typical references, not production noise maxima.

Follower −3 dB bandwidth **17.489 MHz** is not GBW. A DC-closed/AC-open 1 GH/1 F fixture gives unity open-loop gain at **10.043 MHz**, +0.432% from 10 MHz typical. The earlier proxy comparison and malformed bandwidth deck remain superseded predecessors.

Five nonlinear jobs still fail convergence/timestep checks. Headroom, loaded output supply current, clipping refinement, recovery and THD receive no acceptance. Large internal macro capacitors/global-ground references are documented, without invented transistor-level fidelity. Floating common-mode, low supplies, crossover, thermal/SOA and production correlations require independent tests before an architecture can rely on them.

## Physically coupled controls

[corners.yaml](../models/semiconductor/corners.yaml) preserves complete vendor weak/nominal/strong proposals and their failures. Bipolar IS/BF/temperature laws are not independently randomized; one-bias guaranteed base-current intervals do not justify a population. OPA197 has no defensible process distribution here.

Independent Shockley controls use β=gm²/(4·Idss), VTO=−2·Idss/gm and VGS(I)=VTO·(1−√(I/Idss)), with LAMBDA=0/no series resistance. The original 24 mA/55 mS tuple predicts cutoff **−0.87095 V**, outside −1.5…−0.9 V. The unchanged [r1 proposal](../models/semiconductor/proposals/corners_r1.yaml) is preserved. Given gm≥55 mS and the cutoff test, this approximation cannot cover Idss below approximately **24.800 mA**. Manufacturer lower bound **24 mA** remains explicit and uncovered, not narrowed away.

R2 tuples (28 mA/55 mS, 35 mA/68 mS, 46 mA/80 mS) satisfy checked DC terminal limits and independently reproduce native SPICE currents/gm. They are **feasible representatives, not exhaustive production corners**; noise/capacitance/temperature/output modulation/SOA are unqualified. [Preserved controls](../results/device_models/20261005T190815Z_corners_851e1161/results.json) reproduce both the failed parent and feasible subset. Exploratory stresses retain separate identities, without yield claims.

## Readiness, sourcing and implementation gates

For a **restricted numerical batch**, `opa197_pspice` alone supports tested grounded linear feedback/input-noise controls. Add `bc846b_emitter_r1`/`bc856b_vendor` only for nominal DC/saturation/bandwidth output hypotheses, carrying capacitance/flicker/temperature/sourcing gaps. This is not a qualified three-device microphone BOM or cross-family ranking. JFE nominal supports falsifiable hypothesis work with its recorded mismatch, not no-selection production evidence.

Unsupported as qualified microphone inputs: discrete MOSFET low-current/noise populations; production-bounded JFETs; bipolar low-frequency/1/f inputs; other JFET/electrometer ICs; floating/differential/carrier families; complete P48 regulator/protection/output combinations. Keep all 14 architecture families alive. A missing qualified model does not reject a physical mechanism; this task need not produce a passing microphone candidate.

Nexperia's 2N7002 download is HTML. Onsemi 2N7002ET1G and Diodes 2N7002-7-F have indexed retail alternatives but unvalidated models/substitutions. Vishay 2N7002E E3/GE3 alternatives are retailer-listed obsolete despite retained manufacturer model pages; they cannot be implementation dependencies. Manufacturer/supplier 2N7002K-T1-GE3 listings offer a further practical model-research route, with live quantities/model mapping/noise still unqualified. MMBFJ113 has primary electrical information but no audited model/current exact retail route. No NOS, selection or matching service is proposed.

The dated [procurement register](procurement/semiconductors_2026-10-05.yaml) lists exact package/variant, private Germany route evidence, dated inventory/freshness, MOQ/retail pack/factory reel, intended quantity one per possible functional slot, EUR net/gross prices, lead times and unresolved shipping/tax/import/fees. TI parts and TME BC846B have potential retail routes; live freshness and delivered quotes remain unknown. TI remains one manufacturer even with alternative sellers. BC856B exact-variant sourcing is held on conflicting backorder evidence. All confirmed delivered costs are null; scenarios are labelled, with no spending cap, selected basket or order. Substitutes/combinations require requalification. Default capsule quantity remains one for one finished microphone. No optimized proposal or realized candidate BOM was created here.

JFE150 ±40 V drain rating and OPA197 36 V recommended maximum cannot authorize exposure to unloaded P48 52 V. Bipolar ratings do not establish PCB thermal/SOA/hot-plug reliability. Models do not enforce every rating. Safe Flat K47 polarization remains unknown.

[Early patent-feature flags](patents/device_library_2026-10-05.yaml) separate isolated model work from future concrete implementations. Candidate-linked claim/territory/current official-status screening is not completed; no clearance is asserted. Clamps, floating bias/power, feedback/guarding and output combinations need actual candidate mapping before affected prototype/manufacture/build-publication gates. No contact, purchase, licence acceptance or external publication occurred.

## Preserved experiments

| Record | Meaning |
|---|---|
| [183110Z_eb7e089d](../results/device_models/20261005T183110Z_eb7e089d/results.json) | Interrupted invalid-fixture predecessor: clamp below swept drain; OPA stimulus outside common-mode range. No device credit. |
| [183611Z_5b4724a8](../results/device_models/20261005T183611Z_5b4724a8/results.json) | Corrected clamp/stimulus child, 101 jobs/six errors; bandwidth proxy superseded. |
| [184201Z_af7b16c1](../results/device_models/20261005T184201Z_af7b16c1/results.json) | Added capacitance/refinement/reference distinctions; malformed new bandwidth fixture retained, 118 jobs/eight errors. |
| [185102Z_95a6dda5](../results/device_models/20261005T185102Z_95a6dda5/results.json) | Corrected bandwidth child; authoritative 118-job batch/seven numerical errors and acquisition rejection. |
| [185348Z_corners_85090b81](../results/device_models/20261005T185348Z_corners_85090b81/failure.json) | Serialization failure after simulation; raw/source evidence retained. |
| [185414Z_corners_47cfb582](../results/device_models/20261005T185414Z_corners_47cfb582/provenance_correction.json) | Wrong parent identifier; explicitly superseded, original unchanged. |
| [185438Z_corners_0b8875db](../results/device_models/20261005T185438Z_corners_0b8875db/provenance_correction.json) | Correct parent-linked DC repetition, but a later regression exposed an alias in the metadata failed-parent field. Electrical files intact; metadata superseded. |
| [190815Z_corners_851e1161](../results/device_models/20261005T190815Z_corners_851e1161/results.json) | Corrected independent parent metadata; unchanged r1/r2 electrical controls and stable frozen sources. |

Use [library commands](../models/semiconductor/README.md); new runs create new evidence. [Comparison plots](device_model_comparison.png) and [rendering provenance](device_model_plot_provenance.json) derive from frozen CSVs/references. A fresh clone can display the committed plots; regeneration requires the original local CSV archive. The [raw inventory](../results/device-model-raw-data.sha256) covers **857 local waveforms**, including failed/partial analyses and this task’s verification runs. The [CSV inventory](../results/device-model-csv-data.sha256) covers **658 local waveform exports**. Declared job raw and CSV hashes have zero mismatches ([integrity record](device_model_integrity.json)); the storage cleanup leaves their bytes unchanged. No simulator processes from these jobs remain running.

## Final verification

`./run doctor` succeeds with ngspice47 and the unchanged specification hash `f5201295bef7855bced5157cf9727f95d057c2b17589f9f55b8fd6fb17445bbd`. [Final verification](../results/verification/20261005T190817Z_17885439/verification.json) passes **31 tests** with unchanged sources. It reruns loaded P48, capsule charge-law AC/transient agreement, timestep/harmonic refinement, noise-accounting, output/loading and new exact-model provenance/coupled native-DC controls. The earlier [30-pass/one-failure verification](../results/verification/20261005T190717Z_364690ea/verification.json) is preserved: it caught the failed-parent metadata alias, corrected without changing control values or limits. No physics-control failure remains in the final run. Device-model disagreements and the seven nonlinear/original-model failures remain unresolved, independent of passing software/physics controls.

Future candidate results resolve exact model IDs, versions, SHA256 hashes, parent models, compatibility and frozen include paths. Missing/changed files, invalid HTML, unregistered external includes and definition collisions fail resolution; namespace-safe local definitions remain allowed. Acquisition metadata and original bytes are included in the source manifest. This conveys provenance, not automatic component availability, patent screening or production qualification.
