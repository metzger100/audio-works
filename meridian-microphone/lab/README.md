# M100 Meridian analog research laboratory

Current parts evidence: [strengthening002](research/parts_database_expansion_002.md), [searchable matrix](research/parts_database_expansion_002.yaml) and [search/audit tool](research/parts_database.py). Parts, model files, behavior and implementation gates remain separate.

[Project overview](../README.md) · [Current state](../../CURRENT.md) · [Run the lab](#run-the-lab) · [Scientific contract](CONTRACT.md) · [Evidence](results/README.md)

An executable, evidence-first workspace for **Arienne Audio Flat K47 Cardioid/Omni K47FRB** under realistic P48. The [first architecture batch](research/first_architecture_batch.md) records six mechanisms and preserved engineering children using the [partial device library](research/device_model_validation.md). No production architecture is selected or qualified for prototyping.

## Implementation constraints

**Standard parts and availability are a core project constraint.** Follow the [repository component policy](../../COMPONENTS.md) and [Germany procurement contract](research/procurement_germany.md). Implement candidates with documented, currently obtainable parts and actual nominal values, qualify their tolerances, and retain dated small-quantity Germany sourcing and delivered-cost evidence. Ideal-value results and unsourced concepts remain research evidence until their concrete implementations are verified. The current laboratory does not certify a build-ready BOM or implement an automatic availability gate.

**Patent non-infringement is a mandatory project constraint.** Follow the [repository policy](../../PATENTS.md) and [patent track](research/patents/README.md). Track candidate-linked claims, territory, current status and unresolved risks. A credible unresolved potentially blocking claim holds the affected implementation from prototype selection, manufacture or publication of implementation/build guidance. Patent review is separate from numerical engineering qualification; the current workspace has no candidate-level legal clearance.

Start with [the formal specification](spec/microphone_spec.yaml), [capsule uncertainty](spec/capsule_model.yaml), [P48/environment constraints](spec/design_constraints.yaml), [source register](research/sources.yaml) and [Phase 0 report](research/phase0_report.md). Existing capsule research and purchase history remain in the parent `meridian-microphone/` project.

## Run the lab

From the repository root, using an installed laboratory environment:

```sh
cd meridian-microphone/lab
./run doctor
./run verify
./run evaluate fixture_0001 --samples 16 --seed 34047
```

`verify` runs independent physics and software-integrity regressions. `evaluate` runs the initial engineering suite. **Exit 2 is expected for the ideal fixture:** it fails requirements and has incomplete qualification evidence. It must never become a microphone champion.

### Environment and bootstrap

The recorded local environment uses ngspice 47, Python 3.12.14, NumPy 2.4.2, SciPy 1.17.1, pandas 3.0.1, Matplotlib 3.10.8, PyYAML 6.0.3 and pytest 9.0.2. The simulator and missing runtime library were extracted inside `tools/`; no system installation or PCB package is required. `tools/packages.sha256` pins their archive integrity. Original package licence files remain in the extracted distribution; ignored binaries are not project-authored hardware.

For a fresh environment with internet access and Python 3.12:

```sh
MERIDIAN_PYTHON=python3.12 bash tools/bootstrap.sh
```

The bundled desktop Python can also be passed as `MERIDIAN_PYTHON`. On a compatible Linux x86_64 host the bootstrap downloads the pinned Arch packages. Host glibc, ncurses, readline, C++/OpenMP and X11/Xt/Xmu/Xpm libraries must be compatible; `tools/environment.json` records this machine. Other platforms should install/build ngspice 47 and set `MERIDIAN_NGSPICE` to its executable. Library/OS differences are recorded, not assumed numerically identical. Download mirrors may stop retaining old packages; use an official archive with the same pinned checksum. Paths for the bundled simulator currently require no spaces because of ngspice's codemodel command parsing.

## Circuit and evidence contract

The authoritative representation is a plain SPICE netlist containing:

```spice
.subckt DUT f b rear p n g rail
* front/back/rear capsule electrodes, XLR pins 2/3, local ground, observed internal rail
...
.ends DUT
```

The harness attaches the capsule, pressure stimuli, actual phantom feeds, cable, shield resistance and AC-coupled/mismatched preamp. One volt at a virtual pressure port represents one pascal, independently of electrical ground. Nominal rear pressure is zero; two electrical diaphragms do **not** constitute a validated acoustic cardioid/omni model. Future carrier front ends may require a separately documented environment/backend extension, preserving equivalent interface tests.

`topology.yaml` declares parameter bounds, provenance, device populations, corners, niche descriptors, parents and the hypothesis. Candidates may not insert analyses, simulator options or specification overrides. Ideal sources used as hypothetical amplifiers make the candidate ineligible. Device macro-model missing behaviors remain unknown. Per-device selection or hidden trimming is prohibited.

Every run creates a unique directory with candidate/source/spec snapshots, parameter values, exact rendered decks, complete raw data, simulator logs, versions, hashes and JSON results. The compact `candidates/*/results.json` points to the latest immutable experiment. Failed experiments remain. The initial debugging runs predate full source snapshots; their failed model implementations and result records are retained. Later experiments freeze the model files and check for source changes during execution.

Git retains compact results, decks, logs, parameter records, plots and source/spec snapshots. Bulky `.raw` waveforms and `.raw.csv` exports are preserved locally and excluded from Git; a fresh clone does not include them. The [results storage record](results/README.md) explains the boundary and links their dated checksum inventories. Ignoring waveform files does not authorize deleting experiment evidence.

`spec/lock.yaml` guards thresholds/ranges against silent edits. A specification amendment must be documented separately in `research/specification_amendments.md`. Optimizers never edit this lock, specification or canonical circuit.

## Tests and practical limits

The suite executes DC/loaded power, 1 Hz–10 MHz AC, unweighted **and** A-weighted noise with component contributions, settled H2–H10/THD, distortion-limited headroom brackets, two-port output-impedance deembedding, balance/common-mode screening, startup, supply/feed corners, temperature, three-port capsule loading, cable/preamp corners and seeded scenario Monte Carlo. Convergence errors, missing vectors, absent noise sources, truncated data and unsettled waveforms are failures.

The charge model obeys `Q=C0(1+k·p)V` with `k=Sref/Vref`; imposed linear diaphragm compliance is an **assumption**. A numerically scaled observer using a native capacitor realizes `I=dQ/dt`. Gear-2 integration and timestep-refinement controls are used. A linearized mode at the actual simulated polarization isolates electronics distortion. This cannot establish mechanical SPL limits, thermal/acoustic noise, electrostatic softening, pull-in or safe polarization.

These are initial screens, with explicit `incomplete` states. Full loop return-ratio/Nyquist and multi-loop stability, validated semiconductor/noise populations, safe operating area, distortion/noise at every environmental corner, statistically defensible all-requirement yield, RF/ESD/humidity and asymmetric hot-plug/disconnect qualification remain future work. Closed-loop peaking is not a stability proof. Sixteen assumed scenarios are not production yield, and no 99.9% claim is made. Unknown checks cannot qualify a candidate.

## Numerical optimization and diversity

```sh
.venv/bin/python optimization/optimize_values.py fixture_0001 \
  --parameters BIAS_R POLAR_R OUTPUT_C --iterations 6 --seed 34047
.venv/bin/python search/generate_topology.py
.venv/bin/python search/selection.py
.venv/bin/python search/loop.py --evaluations 1 --samples 16
```

The optimizer supports separate single-axis objectives, nominal/worst tested scenarios and empirical scenario percentiles. Noise/nonlinear/port objectives require their documented behavior prerequisites; the legacy fixture noise control uses `--legacy-fixture`. SciPy differential evolution enforces an explicit evaluation budget and separates feasibility constraints from the performance axis. It keeps every trial, returns a value proposal and runs the full suite before acceptance. A search can legitimately find **no feasible point**; inspect the limiting physics without relaxing the requirements. The fixture exercise proves the workflow, not an architecture's merits.

[Inventor/Engineer roles](research/roles.md) separate diversity from viability. [22 concepts](search/concepts.yaml) cover all [14 persistent families](search/families.yaml), with nine falsification questions each. Twenty avoid a conventional JFET voltage buffer. The [six-mechanism batch](research/first_architecture_batch.md) now supplies actual Engineer netlists and BOMs; remaining catalogue proposals await implementation. No AI service or unattended background process is installed.

The batch adds [terminal-energy accounting](src/meridian_lab/architectures.py), [independent regressions](tests/test_architectures.py), a scoped [carrier protocol](research/carrier_protocol.md), [ordinary-parts sourcing](research/procurement/architecture_parts_2026-10-09.yaml), [primary observations](research/architecture_sources/README.md), [candidate patent flags](research/patents/first_architecture_batch_2026-10-09.yaml) and [dated decisions](research/first_architecture_decisions.md). These records do not establish build readiness or legal clearance.

`search/mutate.py` registers structural children with new IDs and parent hypotheses. Value-only edits use the optimizer. Novelty uses approximate value-independent graph and functional descriptors, and never contributes engineering credit. The allocation helper tracks 50/25/15/10 exploration proportions. Diversity retention preserves niches independently of the global winner.

`results/archive.json`, `pareto_front.json` and `leaderboard.csv` are derived from full records. Only fully qualified candidates enter the eligible Pareto front. Missing objectives cannot establish dominance, and incomparable specification/suite/backend cohorts are separated. Global philosophy/objective champions remain empty until the relevant evidence is complete. Rebuild a derived index with `search/archive.py` only while evaluators are idle.

The initial [results report](research/phase0_report.md) and its response/noise plots are rendered from immutable records by `research/render_initial_report.py`. It checks that the compared runs and verification use the same sources and specification before reporting the comparison. Population percentiles include completed simulations that fail requirements; missing/error counts remain explicit.

[Scoped robust optimization](research/robust_optimization_report.md) adds constrained response proposals, nine realized/structural children and independent adverse-case validation. All remain unqualified. The [declared plan](optimization/robust_plan.yaml) and [batch runner](optimization/robust_batch.py) preserve budgets, source cohorts and separate procurement/patent gates.

[Architecture comparison 001](research/architecture_comparison_001.md) audits six tested families, exact BOMs, raw noise contributions, uncertainty reversals and separate research Pareto projections. [Generated tables and plots](results/reports/architecture_comparison_001/tables.md) are reproduced with `.venv/bin/python research/compare_architectures.py`; original local evidence is required. The [measurement priorities](measurement/priority_plan.md) address remaining physical uncertainty. No topology or PCB is selected.

## Next phases

Phase 3: obtain current, documented semiconductor models/limits and build a strong conventional JFET reference plus fundamentally different controls. Optimize them fairly under the same environment and no-selection requirement. Phase 4–7: implement diverse concepts, perform structural search and broaden robust qualification, with early patent-feature flags. Phase 8: separate claim/territory/status screening and resolution of implementation patent holds; no legal conclusion is asserted by the agent. Phase 9–10: only then advance eligible prototype implementations and close the measurement/model-correction loop.

The [measurement interchange](measurement/result.schema.json) shares check names, units, statuses and provenance with simulation. `measurement/compare.py` imports physical records and reports differences without changing models or thresholds. No physical measurements have been made.

The [continuation prompts 06–13](research/prompts/README.md#continuation-tasks--drafted-9-october-2026) cover parts/capsule literature, isolated model repair, focused JFET hypotheses, diverse mechanism controls, patents, sourcing/preservation and recomparison. Capsule measurement access is deferred; source-backed scenarios support continued research while physical gates remain open. The prompts are planned tasks, not new scientific results.

## License

Project-authored software is GPL-3.0-or-later; hardware design sources and electrical netlists/models are CERN-OHL-S-2.0. The [root licensing scope](../../LICENSE) applies throughout the laboratory, including snapshots. Third-party material retains its own terms; vendor-model redistribution permission and engineering/patent release gates remain separate unresolved matters.

[Parts evidence expansion001](research/parts_database_expansion_001.md) · [searchable role/model/behavior matrix](research/parts_database_expansion_001.yaml) · [dated decisions](research/parts_database_expansion_001_decisions.md). Scoped isolated controls expand the library without selecting a microphone implementation.
