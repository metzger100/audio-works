# Experiment log

Machine-readable records under `results/runs/` are authoritative. Every experiment keeps candidate/parent IDs, hypothesis, structural changes, optimizer details, stimulus/environment, source/spec hashes, raw simulator files, failure reasons, comparison fields and next experiment. Nothing is deleted because it failed.

This header was established during infrastructure construction. Earlier smoke and debugging records already preserved under `results/runs/` include serialization, initialization and transient failures. Subsequent entries append automatically. See `specification_amendments.md` for the sole specification serialization correction.

## 20261005T111159Z_39710784 — fixture_0001

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261005T111159Z_39710784/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261005T112227Z_optimization_3f0165c4 — failed optimization of fixture_0001

105 saved trials; no feasible proposal. [Record](../results/runs/20261005T112227Z_optimization_3f0165c4/optimization.json). Constraints and ranges retained.

## 20261005T105259Z_5838a3a9 — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: failed; eligible: False. [Full original record](../results/runs/20261005T105259Z_5838a3a9/results.json). Original raw files and failures are preserved.

## 20261005T105336Z_887ca146 — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: failed; eligible: False. [Full original record](../results/runs/20261005T105336Z_887ca146/results.json). Original raw files and failures are preserved.

## 20261005T105400Z_4bd46f4c — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: failed; eligible: False. [Full original record](../results/runs/20261005T105400Z_4bd46f4c/results.json). Original raw files and failures are preserved.

## 20261005T105653Z_03fe9987 — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: failed; eligible: False. [Full original record](../results/runs/20261005T105653Z_03fe9987/results.json). Original raw files and failures are preserved.

## 20261005T110218Z_b4d4a9d2 — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: failed; eligible: False. [Full original record](../results/runs/20261005T110218Z_b4d4a9d2/results.json). Original raw files and failures are preserved.

## 20261005T110411Z_cb170d4b — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: failed; eligible: False. [Full original record](../results/runs/20261005T110411Z_cb170d4b/results.json). Original raw files and failures are preserved.

## 20261005T110554Z_d4d0b3e8 — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: failed; eligible: False. [Full original record](../results/runs/20261005T110554Z_d4d0b3e8/results.json). Original raw files and failures are preserved.

## 20261005T110607Z_88e36da3 — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: incomplete; eligible: False. [Full original record](../results/runs/20261005T110607Z_88e36da3/results.json). Original raw files and failures are preserved.

## 20261005T110727Z_a75bc476 — fixture_0001 (index backfill)

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.. Result: failed; eligible: False. [Full original record](../results/runs/20261005T110727Z_a75bc476/results.json). Original raw files and failures are preserved.

## 20261005T111201Z_optimization_02ad5b89 — optimization (index backfill)

Result: no_feasible_proposal; trials: 40. [Original record](../results/runs/20261005T111201Z_optimization_02ad5b89/optimization.json). All existing trials/source records retained.

## 20261005T113001Z_optimization_47348f4b — optimization (index backfill)

Result: error; trials: 8. [Original record](../results/runs/20261005T113001Z_optimization_47348f4b/optimization.json). All existing trials/source records retained.

## 20261005T114150Z_816f3e4b — fixture_0001

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261005T114150Z_816f3e4b/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \n\nWarning", "headroom": "No valid distortion bracket", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261005T114408Z_213dac42 — fixture_0001

Hypothesis: Numerically improve fixture values while frozen current and response constraints apply; full suite decides acceptance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261005T114408Z_213dac42/results.json). Parent experiments: ['20261005T114150Z_816f3e4b']. Optimization: {'schema_version': 1, 'experiment_id': '20261005T114342Z_optimization_c7e7091b', 'candidate_id': 'fixture_0001', 'parent_candidates': [], 'parent_experiments': ['20261005T114150Z_816f3e4b'], 'hypothesis': 'Numerical value optimization within declared bounds; full suite still decides acceptance.', 'structural_changes': None, 'algorithm': 'scipy differential_evolution with NonlinearConstraint', 'objective': 'electronics_noise_pa_rms', 'constraints': 'current and response thresholds from frozen spec', 'seed': 34047, 'continuous_parameters': ['BIAS_R', 'POLAR_R', 'OUTPUT_C'], 'bounds': {'BIAS_R': [100000000.0, 100000000000.0], 'POLAR_R': [10000000.0, 1000000000.0], 'OUTPUT_C': [1e-05, 0.0001]}, 'trials': 202, 'spec_sha256': 'f5201295bef7855bced5157cf9727f95d057c2b17589f9f55b8fd6fb17445bbd', 'versions': {'python': '3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]', 'numpy': '2.4.2', 'scipy': '1.17.1', 'pandas': '3.0.1', 'matplotlib': '3.10.8', 'yaml': '6.0.3', 'ngspice': '******\n** ngspice-47 : Circuit level simulation program\n** Compiled with KLU Direct Linear Solver\n** The U. C. Berkeley CAD Group\n** Copyright 1985-1994, Regents of the University of California.\n** Copyright 2001-2026, The ngspice team.\n** Please get your ngspice manual from https://ngspice.sourceforge.io/docs.html\n** Please file your bug-reports at http://ngspice.sourceforge.net/bugrep.html\n** Creation Date: Wed Aug 19 09:38:31 UTC 2026\n******'}, 'next_potential_experiment': 'Inspect the limiting constraint and investigate a structural change or additional declared parameters; keep thresholds fixed.', 'status': 'proposal_requires_full_suite', 'scipy_success': False, 'message': 'Maximum number of iterations has been exceeded.'}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261005T114342Z_optimization_c7e7091b — numerical optimization of fixture_0001

Constrained objective: electronics noise; parameters: ['BIAS_R', 'POLAR_R', 'OUTPUT_C']. Seed: 34047. Trials: 202. [Record](../results/runs/20261005T114342Z_optimization_c7e7091b/optimization.json). Final full-suite experiment: 20261005T114408Z_213dac42; qualified: False. Values are a proposal; canonical netlist and specification were not edited.

## 20261005T115024Z_aabe3af7 — fixture_0001

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.

Result: **error**, qualified: False. Seed: 34047. [Full record](../results/runs/20261005T115024Z_aabe3af7/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed", "source_integrity": "Research sources changed during evaluation. Rerun from a stable source snapshot."}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## model_probe_ddt_ac — reproduced implementation failure

Fresh reproduction of zero AC transfer using a behavioral derivative capsule; [record](probes/ddt_ac_reproducer/results.json), [netlist](probes/ddt_ac_reproducer/circuit.cir). Original exploratory terminal data were not saved as a structured record; this repeat preserves raw data and provenance. No physical mechanism is rejected from the implementation failure.

## 20261005T115530Z_bb6221ee — fixture_0001

Hypothesis: A physical charge-based capsule and loaded P48 interface can be measured by the harness and compared with analytic limits.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261005T115530Z_bb6221ee/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261005T120010Z_97214525 — fixture_0001

Hypothesis: Re-evaluate the saved numerical proposal against the full suite with stable sources; compare with the same-suite nominal fixture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261005T120010Z_97214525/results.json). Parent experiments: ['20261005T115530Z_bb6221ee']. Optimization: {'performed_this_run': False, 'value_proposal_origin': '20261005T114342Z_optimization_c7e7091b', 'algorithm': 'scipy differential_evolution with explicit constraints', 'trials': 202, 'parameters': ['BIAS_R', 'POLAR_R', 'OUTPUT_C']}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261005T121311Z_f11a711a — fixture_0001

Hypothesis: Final nominal control with adverse completed scenarios included in all percentile and worst-case summaries; frozen sources and thresholds.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261005T121311Z_f11a711a/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261005T121440Z_8f1bc311 — fixture_0001

Hypothesis: Re-evaluate the saved 202-trial numerical proposal against the corrected full suite; preserve adverse scenario metrics and all requirement failures.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261005T121440Z_8f1bc311/results.json). Parent experiments: ['20261005T121311Z_f11a711a']. Optimization: {'performed_this_run': False, 'value_proposal_origin': '20261005T114342Z_optimization_c7e7091b', 'algorithm': 'scipy differential_evolution with explicit constraints', 'trials': 202, 'parameters': ['BIAS_R', 'POLAR_R', 'OUTPUT_C']}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## Phase 3 device-library prerequisite — 2026-10-05

[Corrected isolated batch](../results/device_models/20261005T185102Z_95a6dda5/results.json): 118 jobs, seven numerical errors, additional invalid-MOS acquisition rejection, stable frozen sources. Deterministic grids, no random population/seed. Parent chain: 183110Z_eb7e089d → 183611Z_5b4724a8 → 184201Z_af7b16c1 → 185102Z_95a6dda5 (all date prefix 20261005T). No device is fully production-qualified. [Coupled controls](../results/device_models/20261005T185438Z_corners_0b8875db/results.json) preserve failed r1, scoped r2 and corrected parent evidence. [Report](device_model_validation.md) separates engineering, procurement and patent scope. No candidate, optimization, topology/PCB selection or purchase occurred.

Final Phase3 prerequisite checks: doctor succeeds; [verification](../results/verification/20261005T190817Z_17885439/verification.json) passes31 with stable sources/spec. The retained 190717Z verification exposed the metadata alias; [corrected controls](../results/device_models/20261005T190815Z_corners_851e1161/results.json) preserve original r1/r2 values and corrected ancestry. Waveform inventory covers857 files with zero declared-hash mismatches. No device-model disagreement was converted into a production pass.

## 20261009T073506Z_1cda48d6 — candidate_0001

Hypothesis: A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T073506Z_1cda48d6/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T073508Z_e9040470 — candidate_0002

Hypothesis: A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T073508Z_e9040470/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T073513Z_e3db0296 — candidate_0003

Hypothesis: A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T073513Z_e3db0296/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T073515Z_03f66e3e — candidate_0004

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T073515Z_03f66e3e/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T073518Z_30ec6d70 — candidate_0005

Hypothesis: An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.

Result: **incomplete**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T073518Z_30ec6d70/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T073519Z_7e3ec6c2 — candidate_0006

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T073519Z_7e3ec6c2/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T074905Z_eed9e3eb — candidate_0007

Hypothesis: A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.

Result: **incomplete**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T074905Z_eed9e3eb/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T074906Z_cf107ee3 — candidate_0008

Hypothesis: A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.

Result: **incomplete**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T074906Z_cf107ee3/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T074907Z_7f820c8b — candidate_0009

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **incomplete**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T074907Z_7f820c8b/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T074907Z_1697b862 — candidate_0010

Hypothesis: A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T074907Z_1697b862/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T074911Z_537c2dca — candidate_0011

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T074911Z_537c2dca/results.json). Parent experiments: []. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075653Z_56b3f772 — candidate_0001

Hypothesis: A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075653Z_56b3f772/results.json). Parent experiments: ['20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075654Z_1409215c — candidate_0002

Hypothesis: A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075654Z_1409215c/results.json). Parent experiments: ['20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075659Z_4af47900 — candidate_0003

Hypothesis: A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075659Z_4af47900/results.json). Parent experiments: ['20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075701Z_89a8da44 — candidate_0004

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075701Z_89a8da44/results.json). Parent experiments: ['20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075704Z_160da119 — candidate_0005

Hypothesis: An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075704Z_160da119/results.json). Parent experiments: ['20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: Command '['/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab/tools/ngspice-run', '-n', '-b', 'job.cir']' timed out after 60 seconds", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075811Z_20f26efe — candidate_0006

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075811Z_20f26efe/results.json). Parent experiments: ['20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075817Z_36deb9d8 — candidate_0007

Hypothesis: A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075817Z_36deb9d8/results.json). Parent experiments: ['20261009T075653Z_56b3f772']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075824Z_f60e9f1e — candidate_0008

Hypothesis: A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075824Z_f60e9f1e/results.json). Parent experiments: ['20261009T075654Z_1409215c']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075833Z_d772fead — candidate_0009

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075833Z_d772fead/results.json). Parent experiments: ['20261009T075811Z_20f26efe']. Optimization: {'performed': False}.

Failures/incomplete: {"carrier_mechanism": "SimulationError: Missing required vector v(mic_g); never treated as a pass", "frequency_response": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "noise": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "distortion": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "headroom": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "output_impedance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "balance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "phantom_supply": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "temperature": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "semiconductor_corners": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "monte_carlo": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "loading": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "startup": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "stability": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075914Z_8810416a — candidate_0010

Hypothesis: A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075914Z_8810416a/results.json). Parent experiments: ['20261009T075659Z_4af47900']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075917Z_977e6e5b — candidate_0011

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075917Z_977e6e5b/results.json). Parent experiments: ['20261009T075701Z_89a8da44']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T075919Z_e6e99e40 — candidate_0012

Hypothesis: An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T075919Z_e6e99e40/results.json). Parent experiments: ['20261009T075704Z_160da119']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: Command '['/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab/tools/ngspice-run', '-n', '-b', 'job.cir']' timed out after 60 seconds", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080026Z_21cbd366 — candidate_0013

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080026Z_21cbd366/results.json). Parent experiments: ['20261009T075833Z_d772fead']. Optimization: {'performed': False}.

Failures/incomplete: {"carrier_mechanism": "SimulationError: Missing required vector v(mic_g); never treated as a pass", "frequency_response": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "noise": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "distortion": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "headroom": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "output_impedance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "balance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "phantom_supply": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "temperature": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "semiconductor_corners": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "monte_carlo": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "loading": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "startup": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "stability": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080104Z_d06a19d4 — candidate_0014

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080104Z_d06a19d4/results.json). Parent experiments: ['20261009T075917Z_977e6e5b']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080529Z_bcae5f2f — candidate_0001

Hypothesis: A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080529Z_bcae5f2f/results.json). Parent experiments: ['20261009T075653Z_56b3f772', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080530Z_be15abf9 — candidate_0002

Hypothesis: A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080530Z_be15abf9/results.json). Parent experiments: ['20261009T075654Z_1409215c', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080535Z_7267ca69 — candidate_0003

Hypothesis: A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080535Z_7267ca69/results.json). Parent experiments: ['20261009T075659Z_4af47900', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080537Z_4e344dd2 — candidate_0004

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080537Z_4e344dd2/results.json). Parent experiments: ['20261009T075701Z_89a8da44', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080540Z_ff008315 — candidate_0005

Hypothesis: An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080540Z_ff008315/results.json). Parent experiments: ['20261009T075704Z_160da119', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: Command '['/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab/tools/ngspice-run', '-n', '-b', 'job.cir']' timed out after 60 seconds", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080648Z_149737e8 — candidate_0006

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080648Z_149737e8/results.json). Parent experiments: ['20261009T075811Z_20f26efe', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080654Z_fd6e2214 — candidate_0007

Hypothesis: A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080654Z_fd6e2214/results.json). Parent experiments: ['20261009T075817Z_36deb9d8', '20261009T080529Z_bcae5f2f']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080700Z_25371f0c — candidate_0008

Hypothesis: A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080700Z_25371f0c/results.json). Parent experiments: ['20261009T075824Z_f60e9f1e', '20261009T080530Z_be15abf9']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080710Z_a4b32696 — candidate_0009

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **error**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080710Z_a4b32696/results.json). Parent experiments: ['20261009T075833Z_d772fead', '20261009T080648Z_149737e8']. Optimization: {'performed': False}.

Failures/incomplete: {"carrier_mechanism": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "frequency_response": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "noise": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "distortion": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "headroom": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "output_impedance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "balance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "phantom_supply": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "temperature": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "semiconductor_corners": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "monte_carlo": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "loading": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "startup": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "stability": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "source_integrity": "Research or implementation sources changed during evaluation. Rerun from a stable source snapshot."}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080750Z_e50070e3 — candidate_0010

Hypothesis: A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080750Z_e50070e3/results.json). Parent experiments: ['20261009T075914Z_8810416a', '20261009T080535Z_7267ca69']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080753Z_5e30de91 — candidate_0011

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080753Z_5e30de91/results.json). Parent experiments: ['20261009T075917Z_977e6e5b', '20261009T080537Z_4e344dd2']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080756Z_5cff4a8f — candidate_0012

Hypothesis: An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080756Z_5cff4a8f/results.json). Parent experiments: ['20261009T075919Z_e6e99e40', '20261009T080540Z_ff008315']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: Command '['/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab/tools/ngspice-run', '-n', '-b', 'job.cir']' timed out after 60 seconds", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080903Z_2e3b6436 — candidate_0013

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080903Z_2e3b6436/results.json). Parent experiments: ['20261009T080026Z_21cbd366', '20261009T080710Z_a4b32696']. Optimization: {'performed': False}.

Failures/incomplete: {"carrier_mechanism": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "frequency_response": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "noise": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "distortion": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "headroom": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "output_impedance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "balance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "phantom_supply": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "temperature": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "semiconductor_corners": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "monte_carlo": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "loading": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "startup": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "stability": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T080943Z_c80c6e97 — candidate_0014

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T080943Z_c80c6e97/results.json). Parent experiments: ['20261009T080104Z_d06a19d4', '20261009T080753Z_5e30de91']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081228Z_4348e0f5 — candidate_0015

Hypothesis: If the unfiltered final 1Mohm backplate feed dominates the conventional reference noise, an actual 100nF backplate bypass should lower that contribution without selecting a JFET or changing voltage conversion.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081228Z_4348e0f5/results.json). Parent experiments: ['20261009T080654Z_fd6e2214']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081731Z_fc3fdae1 — candidate_0001

Hypothesis: A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081731Z_fc3fdae1/results.json). Parent experiments: ['20261009T080529Z_bcae5f2f', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081732Z_92f6292d — candidate_0002

Hypothesis: A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081732Z_92f6292d/results.json). Parent experiments: ['20261009T080530Z_be15abf9', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081737Z_f5141f0b — candidate_0003

Hypothesis: A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081737Z_f5141f0b/results.json). Parent experiments: ['20261009T080535Z_7267ca69', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081739Z_9d13e69b — candidate_0004

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081739Z_9d13e69b/results.json). Parent experiments: ['20261009T080537Z_4e344dd2', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081741Z_4b7b1c19 — candidate_0005

Hypothesis: An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081741Z_4b7b1c19/results.json). Parent experiments: ['20261009T080540Z_ff008315', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: Command '['/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab/tools/ngspice-run', '-n', '-b', 'job.cir']' timed out after 60 seconds", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081849Z_c8c08dee — candidate_0006

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081849Z_c8c08dee/results.json). Parent experiments: ['20261009T080648Z_149737e8', '20261005T121440Z_8f1bc311']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081855Z_00510538 — candidate_0007

Hypothesis: A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081855Z_00510538/results.json). Parent experiments: ['20261009T080654Z_fd6e2214', '20261009T081731Z_fc3fdae1']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081902Z_45f64ff4 — candidate_0008

Hypothesis: A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081902Z_45f64ff4/results.json). Parent experiments: ['20261009T080700Z_25371f0c', '20261009T081732Z_92f6292d']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081912Z_048f3bb8 — candidate_0009

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081912Z_048f3bb8/results.json). Parent experiments: ['20261009T080710Z_a4b32696', '20261009T081849Z_c8c08dee']. Optimization: {'performed': False}.

Failures/incomplete: {"carrier_mechanism": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "frequency_response": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "noise": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "distortion": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "headroom": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "output_impedance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "balance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "phantom_supply": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "temperature": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "semiconductor_corners": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "monte_carlo": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "loading": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "startup": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "stability": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081953Z_850aaca0 — candidate_0010

Hypothesis: A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081953Z_850aaca0/results.json). Parent experiments: ['20261009T080750Z_e50070e3', '20261009T081737Z_f5141f0b']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081956Z_3e19c047 — candidate_0011

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081956Z_3e19c047/results.json). Parent experiments: ['20261009T080753Z_5e30de91', '20261009T081739Z_9d13e69b']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T081958Z_98b1ab70 — candidate_0012

Hypothesis: An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T081958Z_98b1ab70/results.json). Parent experiments: ['20261009T080756Z_5cff4a8f', '20261009T081741Z_4b7b1c19']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: Command '['/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab/tools/ngspice-run', '-n', '-b', 'job.cir']' timed out after 60 seconds", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T082105Z_98724e41 — candidate_0013

Hypothesis: A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T082105Z_98724e41/results.json). Parent experiments: ['20261009T080903Z_2e3b6436', '20261009T081912Z_048f3bb8']. Optimization: {'performed': False}.

Failures/incomplete: {"carrier_mechanism": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "frequency_response": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "noise": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "distortion": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "headroom": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "output_impedance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "balance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "phantom_supply": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "temperature": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "semiconductor_corners": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "monte_carlo": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "loading": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "startup": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "stability": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T082146Z_25aa5621 — candidate_0014

Hypothesis: Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T082146Z_25aa5621/results.json). Parent experiments: ['20261009T080943Z_c80c6e97', '20261009T081956Z_3e19c047']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T082147Z_487720eb — candidate_0015

Hypothesis: If the unfiltered final 1Mohm backplate feed dominates the conventional reference noise, an actual 100nF backplate bypass should lower that contribution without selecting a JFET or changing voltage conversion.

Result: **failed**, qualified: False. Seed: 34047. [Full record](../results/runs/20261009T082147Z_487720eb/results.json). Parent experiments: ['20261009T081228Z_4348e0f5', '20261009T081855Z_00510538']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090337Z_3c7187fa — candidate_0015

Hypothesis: Current frozen-cohort baseline; preserve prior source cohorts and all checks

Result: **failed**, qualified: False. Seed: 84047. [Full record](../results/runs/20261009T090337Z_3c7187fa/results.json). Parent experiments: ['20261009T082147Z_487720eb']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090344Z_f2f3eb75 — candidate_0015

Hypothesis: Full suite of continuous response proposal; physical BOM still parent nominal, design tolerances explicitly recentered, not a realized hardware claim

Result: **failed**, qualified: False. Seed: 84047. [Full record](../results/runs/20261009T090344Z_f2f3eb75/results.json). Parent experiments: ['20261009T090337Z_3c7187fa']. Optimization: {'performed': True, 'proposal_experiment': '20261009T090126Z_robust_3a561a91', 'training_budget': 12, 'termination': 'evaluation_budget_exhausted'}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090403Z_bdcfe8b9 — candidate_0008

Hypothesis: Current frozen-cohort baseline; preserve prior source cohorts and all checks

Result: **failed**, qualified: False. Seed: 84047. [Full record](../results/runs/20261009T090403Z_bdcfe8b9/results.json). Parent experiments: ['20261009T081902Z_45f64ff4']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090412Z_5620861e — candidate_0008

Hypothesis: Full suite of continuous response proposal; physical BOM still parent nominal, design tolerances explicitly recentered, not a realized hardware claim

Result: **failed**, qualified: False. Seed: 84047. [Full record](../results/runs/20261009T090412Z_5620861e/results.json). Parent experiments: ['20261009T090403Z_bdcfe8b9']. Optimization: {'performed': True, 'proposal_experiment': '20261009T090135Z_robust_1f191c37', 'training_budget': 12, 'termination': 'evaluation_budget_exhausted'}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090436Z_496da267 — candidate_0010

Hypothesis: Current frozen-cohort baseline; preserve prior source cohorts and all checks

Result: **failed**, qualified: False. Seed: 84047. [Full record](../results/runs/20261009T090436Z_496da267/results.json). Parent experiments: ['20261009T081953Z_850aaca0']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090439Z_77e9f0c9 — candidate_0014

Hypothesis: Current frozen-cohort baseline; preserve prior source cohorts and all checks

Result: **failed**, qualified: False. Seed: 84047. [Full record](../results/runs/20261009T090439Z_77e9f0c9/results.json). Parent experiments: ['20261009T082146Z_25aa5621']. Optimization: {'performed': False}.

Failures/incomplete: {"operating_point": "ngspice exit 0: Warning", "frequency_response": "ngspice exit 0: Warning", "noise": "ngspice exit 0: Warning", "distortion": "ngspice exit 0: Warning", "headroom": "ngspice exit 0: Warning", "output_impedance": "ngspice exit 0: Warning", "balance": "ngspice exit 0: Warning", "phantom_supply": "ngspice exit 0: Warning", "temperature": "ngspice exit 0: Warning", "semiconductor_corners": "ngspice exit 0: Warning", "monte_carlo": "ngspice exit 0: Warning", "loading": "ngspice exit 0: Warning", "startup": "ngspice exit 0: Warning", "stability": "ngspice exit 0: Warning"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090439Z_c6d23a08 — candidate_0012

Hypothesis: Current frozen-cohort baseline; preserve prior source cohorts and all checks

Result: **failed**, qualified: False. Seed: 84047. [Full record](../results/runs/20261009T090439Z_c6d23a08/results.json). Parent experiments: ['20261009T081958Z_98b1ab70']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: Command '['/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab/tools/ngspice-run', '-n', '-b', 'job.cir']' timed out after 60 seconds", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090547Z_1f85c513 — candidate_0013

Hypothesis: Current frozen-cohort baseline; preserve prior source cohorts and all checks

Result: **failed**, qualified: False. Seed: 84047. [Full record](../results/runs/20261009T090547Z_1f85c513/results.json). Parent experiments: ['20261009T082105Z_98724e41']. Optimization: {'performed': False}.

Failures/incomplete: {"carrier_mechanism": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "frequency_response": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "noise": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "distortion": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "headroom": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "output_impedance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "balance": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "phantom_supply": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "temperature": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "semiconductor_corners": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "monte_carlo": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "loading": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "startup": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior", "stability": "Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090628Z_d87c22bb — candidate_0016

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T090628Z_d87c22bb/results.json). Parent experiments: ['20261009T090344Z_f2f3eb75', '20261009T090337Z_3c7187fa']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090650Z_595690f6 — candidate_0017

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T090650Z_595690f6/results.json). Parent experiments: ['20261009T090344Z_f2f3eb75', '20261009T090337Z_3c7187fa']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090713Z_3965ee56 — candidate_0018

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T090713Z_3965ee56/results.json). Parent experiments: ['20261009T090344Z_f2f3eb75', '20261009T090337Z_3c7187fa']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090737Z_40e6a493 — candidate_0019

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T090737Z_40e6a493/results.json). Parent experiments: ['20261009T090344Z_f2f3eb75', '20261009T090337Z_3c7187fa']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090802Z_0b46cfbc — candidate_0020

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T090802Z_0b46cfbc/results.json). Parent experiments: ['20261009T090412Z_5620861e', '20261009T090403Z_bdcfe8b9']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090831Z_ea375e10 — candidate_0021

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T090831Z_ea375e10/results.json). Parent experiments: ['20261009T090412Z_5620861e', '20261009T090403Z_bdcfe8b9']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090859Z_5f41d82e — candidate_0022

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T090859Z_5f41d82e/results.json). Parent experiments: ['20261009T090412Z_5620861e', '20261009T090403Z_bdcfe8b9']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T090930Z_1acba093 — candidate_0023

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T090930Z_1acba093/results.json). Parent experiments: ['20261009T090412Z_5620861e', '20261009T090403Z_bdcfe8b9']. Optimization: {'performed': False}.

Failures/incomplete: {"noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: ngspice exit 0: \ndoAnalyses: TRAN:  Timestep too small", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "startup": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.

## 20261009T091002Z_36aac551 — candidate_0024

Hypothesis: Full suite of distinct sourced BOM combination/structural child; never inherit continuous/nominal qualification

Result: **failed**, qualified: False. Seed: 94047. [Full record](../results/runs/20261009T091002Z_36aac551/results.json). Parent experiments: ['20261009T090439Z_c6d23a08']. Optimization: {'performed': False}.

Failures/incomplete: {"frequency_response": "Numerical acceptance requirement failed", "noise": "Numerical acceptance requirement failed", "distortion": "SimulationError: Command '['/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab/tools/ngspice-run', '-n', '-b', 'job.cir']' timed out after 60 seconds", "headroom": "No valid distortion bracket", "output_impedance": "Numerical acceptance requirement failed", "balance": "Numerical acceptance requirement failed", "phantom_supply": "Numerical acceptance requirement failed", "temperature": "Numerical acceptance requirement failed", "semiconductor_corners": "No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield", "monte_carlo": "Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established", "loading": "Numerical acceptance requirement failed", "stability": "Numerical acceptance requirement failed"}

Next: Resolve failed checks and missing evidence without changing acceptance thresholds.
