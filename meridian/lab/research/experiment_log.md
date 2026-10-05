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
