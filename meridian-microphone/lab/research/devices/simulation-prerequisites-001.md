<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Simulation prerequisites 001 — 11 October 2026

M100 Meridian MIC-34-M/MIC-34-C, K47FRB under P48 remains research. Isolated numerical H2/H3 extraction is supported for the specified JFE150 follower; **microphone H2/H3, THD and clipping/headroom remain unavailable**. There is no new architecture winner, production qualification, measured capsule data or clearance. The [continuation contract](../prompts/research-workflow.md), locked specifications and existing acceptance/budgets remain in force.

[Revision decision](simulation-prerequisites-decisions-001.md) · [manufacturer/member comparison](simulation-prerequisites-sources-001.json) · [query/gap ledger](simulation-prerequisites-queries-001.json) · [full behavior/uncertainty data](simulation-prerequisites-behavior-001.json) · [validation/preservation](../../../../docs/validation/2026-10-11-simulation-prerequisites.md).

## Audit and frozen cohorts

The registry, acquisition, reference and coupled-corner records; characterizers; original failed controls; [model validity](device-model-validation.md); first/robust architecture batches; [comparison001](../architectures/architecture-comparison-001.md) and carrier protocol were inspected before execution. [Parts002](parts-database-expansion-002.md) and the [capsule envelope](../capsules/evidence-envelope-001.md) were available. Capsule physical measurements remain absent; imposed terminal/RC controls do not depend on them. Generic/weak/strong/PSpice JFE files and both BC846B parent/child already existed. No favorable corner or new vendor-approved repair was invented.

| Cohort / frozen plan | Jobs / execution errors | Scope |
| --- | --- | --- |
| [a7cc0cdb](../../results/device_models/20261011T175705Z_prerequisites_a7cc0cdb/results.json), [plan001](simulation-prerequisites-plan-001.yaml) |91 /13| Independent RC/nonlinear oracles;13 model identities, terminal transfer/output/noise/transients; OPA translation |
| [0f2c5116](../../results/device_models/20261011T180313Z_observer_diagnosis_0f2c5116/results.json), [plan002](simulation-prerequisites-plan-002.yaml) |19 /6| Charge/gauge and clamp controls; common reduced original DUTs and explicit observer children |
| [de3fa943](../../results/device_models/20261011T180615Z_high_impedance_de3fa943/results.json), [plan003](simulation-prerequisites-plan-003.yaml) |9 /0| Complete nominal JFE minimal stages at observed DUT bias; source impedance and phase |

Each unique batch contains frozen source bytes, full generated plans, model/spec/deck hashes, bias/temperature/options, raw waves, CSV where selected, complete available stdout/stderr and per-job retained hashes. All three source sets were unchanged during execution. Behavior tables distinguish successful solver execution from supported physical behavior: [JFE](simulation-prerequisites-jfet-001.csv), [bipolar](simulation-prerequisites-bipolar-001.csv), [OPA](simulation-prerequisites-opa-001.csv), [integration](simulation-prerequisites-integration-001.csv). No partial/error wave receives harmonic credit. The report builder independently rechecked797 frozen/job files; complete batch inventories include additional receipt bytes.

Original comparison parents remain:0019/`20261009T090737Z_40e6a493`,0023/`20261009T090930Z_1acba093`,0012/`20261009T090439Z_c6d23a08`,0010/`20261009T090436Z_496da267`,0014/`20261009T090439Z_77e9f0c9`,0013/`20261009T090547Z_1f85c513`. Their checks/hashes are retained in the behavior data. BJT distortion exhausted its60s budget; JFE jobs failed with timestep-too-small; OPA floating DC failed. Original characterizer/Parts002 parents are listed in plan001. Neither these failures nor older model-limit disagreements are overwritten.

## Manufacturer research and simulator baseline

[Source review](simulation-prerequisites-source-notes-001.md) records current TI archives, reference-deck gaps, installed ngspice47 documentation, switch/global-ground mechanisms and acquisition failures. Generic/PSpice/TINA/reference nominal cores are duplicates, not independent extractions. Exact archive/member/binary/wrapper hashes remain in the ledgers and frozen plans. Initial cohorts did not individually freeze loaded XSPICE modules; their later current hash receipt cannot attest historical run-time bytes. Future freezes include modules and transitive documentary pages.

Isolated options are `reltol=1e-6 abstol=1e-16 vntol=1e-10 gmin=1e-15 method=gear maxord=2`,15s per job. Reduced original DUTs retain `abstol=1e-15 vntol=1e-9` and60s. No tolerance search, rshunt, clamp deletion, hidden bias resistor or ideal substitute earned device performance.

## JFE150 behavior and coverage

Terminal pin order is D/G/S/VCH/VCL; clamp rails and source signs are explicit in each deck. Transfer sweeps use VDS5V, VGS−1.8…0V at−10/25/50°C; guaranteed Idss/gm use25°C,VDS10V,VGS0; output sweep VGS−0.7V,VDS0.01…20V. Five-terminal current balance and follower rail-energy integrals are retained. These check equations/signs, not a measured energy/thermal model.

| Full model | Idss at10V / gm | Guaranteed comparison | Isolated follower H2 / H3 |
| --- | --- | --- | --- |
| Generic/PSpice/TINA member |26.902mA /49.109mS| Idss24–46mA passes; gm55–80mS fails by10.71% |0.00372319% /0.00000484835% |
| Weak |17.904mA /36.469mS| Both lower guarantees fail |0.00468890% /0.00000632622% |
| Strong |40.049mA /37.215mS| gm lower guarantee fails |0.00207216% /0.00000216385% |

Admittance/native noise use interpolated2mA,VDS5V, measured actual simulated current and gate-voltage AC drive. Nominal VGS−0.726478V; Ciss15.506pF is diagnostic because the24pF typical table gate bias is ambiguous. en10Hz1.784nV/√Hz, en1kHz0.8755nV/√Hz; in1kHz0.4879fA/√Hz versus1.8fA/√Hz typical differs−72.9%. Voltage, current and low-frequency native spectra, total roots and sub-contributions remain raw. Numeric noise roots close to about9e−16 relative; behavioral/clamp physical noise completeness and measured flicker extraction remain unsupported. Leakage3.549pA atVDS2V,VGS−0.7V, clamp±5V is a scoped observation, not production leakage qualification.

The complete-model follower uses12V rail, gate1VDC+10mV peak at1kHz, ideal0Ω source, source load1kΩ and70pF. Direct and all-five-zero-volt-observer children both converge; zero observers alone do not explain the DUT failure. Retain startup0…64ms, compare16-cycle windows after32ms, refine2→1µs maximum step,128/256/512 samples and8/16-cycle windows. The [frozen60-fit replay](../../results/device_models/20261011T183846Z_extraction_d0b338ed/results.json) gives H2/H3 spread below existing1% refinement; full spreads are retained. This is **numerical H2/H3 support at this fixture only**, without independent measured nonlinear truth. Higher harmonics near numerical floor receive no real-device accuracy claim.

Source-limited100kΩ clamp ramps−1…+1V with clamp rails0 produce gate−0.475…+0.470V and5.299µA peak; generic/PSpice agree as duplicate cores. Minimal JFE stages at rail13.5557796V, gate3.3889452V, backplate29.5293276V, Rs3.3kΩ, gate70pF/1TΩ all reach4ms for source0/1k/1GΩ and voltage/current phase0/90. High impedance or phase alone is therefore insufficient to reproduce failure. Four milliseconds establishes no settled distortion, stability margin or headroom.

## Bipolar and OPA diagnosis

| Identity / ancestry | Observations / unresolved scope |
| --- | --- |
| BC846B original → existing emitter-r1 | Parent Q2 emitter33 is dangling; child changes33→3 only. Exact ancestry/diff remain in registry; independent Nexperia PMBT5551/BC850C networks connect both emitters to3. This supports a physical connectivity rationale, not vendor approval. Original−10/25°C DC time out15s;50°C partial success does not validate it |
| BC846B emitter-r1 | β294.886 at25°C,IC2mA,VCE5V meets200–450 gradeB only there. Grids0.1/1/2/10mA at−10/25/50°C expose bias dependence. SPICE C/B/E differs from package B/E/C; header110–450 is not the gradeB datasheet bound |
| PMBT5551 / BC850C / Diodes MMBT5401 | Independent full manufacturer files retained with exact identities/gain grade. DC/base authority and loaded AC/noise are diagnostic, not interchangeable devices or a joint population |
| Diotec MMBT5551 | All three transfer jobs reject unsupported BVCBO/BVBE terms; do not silently ignore parser warnings |
| Exact open-emitter capacitance | Child BC846B and PMBT5551 gmin/source-convergence warnings fail the strict gate despite eventual optran. Zero-current open fixture is retained; no leakage resistor rescues it |
| Saturation/recovery |5V/500Ω collector,500µA base pulse; child4.05µs,PMBT37.8µs,PNP5.649µs to90% are unmatched diagnostics. BC850C never reaches90%; pulse recurrence interrupts the off interval after≈6ms: censor recovery there |
| OPA197 / OPA928 |16V supply,8V common mode,10kΩ to midpoint: grounded/no-guess DC+AC passes. Translation+20V, and even several grounded `.nodeset` children, warn/time out. Preserve internal global-ground/macro-network suspicion; no proven repair or floating/nonlinear credit |

Bipolar loaded-base fixtures add2kΩ after choosing the unloaded2mA voltage: actual currents are1.4213mA(child),1.1236mA(PMBT),1.5906mA(BC850C),1.0404mA(PNP). Their current gain at100MHz is not fT, nor an exact2mA noise reference comparison. Terminal/base currents and recovery supply energy are retained. Missing KF/1f, measured spectra, joint process, SOA/self-heating and package matching remain unqualified. One successful beta point cannot validate the quasi-saturation network generally.

## Transient progression and actual fixes

An independent1kΩ/1µF RC step matches analytic response within0.5µV at both timesteps. A linear sine and independent product-to-sum oracle for `x+0.1x²+0.04x³` plus explicitH4–H10 calibrate peak/RMS, output fundamental, coherence/phase, H2/H3 and THD. Synthetic H1=0.72831993Vrms,H2=0.03535529Vrms,H3=0.00707103Vrms; THD4.95068%; worst H1–H10 error0.0563%, linear THD5.36e−13%. Independent regressions vary phase/adaptive sampling and reject partial/startup-discarded data, drifting H2 with stable H1, and DC drift.

The prior extractor tested only fundamental settling; headroom refinement did not apply even that test. The explicit software child now checks adjacent coherent H1–H10 phasors and DC windows with unchanged1e−3 acceptance, retains startup by changing saved TSTART to0, and requires two complete post-settling windows. Duration/timestep/0.5s settling,8 headroom bisections and physical thresholds are unchanged. Timeout handling kills the process group and retains complete available stdout/stderr/partial waves; older lost prefixes cannot be reconstructed. Independent timeout and headroom-drift regressions cover these fixes.

The [capsule signal-reference child](../../models/capsule/flat-k47-observer-r2.cir) changes only Bqf/Bqr and Cqf/Cqr internal reference g→global0, with frozen exact diff. It is an unpromoted equation/gauge diagnostic; no terminal load or bias assist is added. Both parent/child at local ground0/+20V match the linear charge/RC amplitude oracle within4.505e−6 relative. Residual reported THD0.0003341% is not a validated linear harmonic floor: slow startup can remain below the unchanged settling screen. Claim amplitude/gauge consistency only.

Common reduced original candidate0019/0023/0012 jobs use1kHz,1Pa RMS,LIN1,POLDC40,0…4ms. This imposed polarization differs from each original measured-in-simulation DC operating point: these are numerical diagnostic children, not full candidate re-evaluation. Both JFET DUTs fail in original, collapsed-terminal-observer and charge-reference-child forms; BJT reaches4ms in all three, with no settled credit.

The precise reduced failing reproducer is [candidate0019 observer-collapsed deck](../../results/device_models/20261011T180313Z_observer_diagnosis_0f2c5116/candidate_0019/terminal_observers_collapsed/job.cir) with its frozen includes/log/partial raw;0023 has the same child scope. It retains coupled P48/passive/output behavior. No smaller isolated JFE failure was found. Changing the blamed branch between runs does not identify physical instability; interaction of coupled charge/supply/output networks remains unresolved.

## Gates, alternative research route and legal/noise limits

| Analysis | Supported now |
| --- | --- |
| Synthetic H2/H3/H4–H10/THD, phase/RMS conventions | Numerical oracle and regression scope above |
| Complete-model JFE voltage-driven follower H2/H3 | Specified bias/load/isothermal fixture, refined numerical result only |
| Full microphone H2/H3/THD at100/1k/10kHz and1Pa/135dB | Unavailable: JFE timestep failures; original BJT60s exhausted; OPA DC prerequisites unsupported |
| Electronics clipping/headroom boundary | Unavailable without settled distortion bracket; right-censored results remain bounds |
| System SPL/mechanics/noise/production | Unsupported physical capsule/device/thermal/joint data; no numerical promotion |

Conditional continuation step7 is held: isolated scoped passes do not support affected DUT prerequisites. A new common full comparison would repeat unsupported gates. The independent route is terminal-source-impedance/load/temperature validation at intended biases, preserving all14 families and independent manufacturer BJT alternatives; then reduce the coupled failed deck one physical network at a time under another frozen plan. OPA ground-reference/floating behavior and a separately labelled documented backend remain research routes, not validated substitutes. No alternate backend is installed or pooled here.

Noise extraction requires measured bias/temperature/source impedance, resistor/fixture de-embedding, instrument background, frequency/window uncertainty, and independent voltage/current/flicker spectra. TI's retained SLVA043B note and [JFE noise/current discussion](https://e2e.ti.com/support/amplifiers-group/amplifiers/f/amplifiers-forum/1472837/jfe150-noise-density-versus-drain-source-current) distinguish thermal/isothermal assumptions from die heating. [Keithley high-impedance measurement guidance](https://www.tek.com/en/documents/product-article/keithley-low-level-measurements-handbook---7th-edition) separates shielding/guarding, cable/insulator leakage, burden and settling; no physical tests were performed. Licensing/redistribution and [feature/patent flags](../patents/device_library_2026-10-05.yaml) remain separate gates; no download, repair or duplicate agreement provides legal clearance.

Runnable commands from the lab: `PYTHONPATH=src .venv/bin/python tools/controls/simulation_prerequisites.py`; use the same prefix for `tools/controls/prerequisite_diagnosis.py`, `prerequisite_reproducer.py` and `prerequisite_extraction.py`. Audit existing batches first. Each freezes a new plan/source set. Rebuild tables/integrity with the scripts in `tools/reporting/prerequisite_{report,integrity}.py`. Frozen execution bytes remain authoritative.
