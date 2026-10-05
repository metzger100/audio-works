# M100 Meridian analog research laboratory

An executable, evidence-first workspace for **Arienne Audio Flat K47 Cardioid/Omni K47FRB** under realistic P48. The Phase 0–2 foundation now has a [Phase 3 semiconductor-model prerequisite report](research/device_model_validation.md), with scoped agreement and preserved failures. No production microphone architecture is selected, and no circuit is qualified for prototyping.

**Standard parts and availability are a core project constraint.** Follow the [repository component policy](../../COMPONENTS.md) and [Germany procurement contract](research/procurement_germany.md). Implement candidates with documented, currently obtainable parts and actual nominal values, qualify their tolerances, and retain dated small-quantity Germany sourcing and delivered-cost evidence. Ideal-value results and unsourced concepts remain research evidence until their concrete implementations are verified. The current laboratory does not certify a build-ready BOM or implement an automatic availability gate.

**Patent non-infringement is a mandatory project constraint.** Follow the [repository policy](../../PATENTS.md) and [patent track](research/patents/README.md). Track candidate-linked claims, territory, current status and unresolved risks. A credible unresolved potentially blocking claim holds the affected implementation from prototype selection, manufacture or publication of implementation/build guidance. Patent review is separate from numerical engineering qualification; the current workspace has no candidate-level legal clearance.

Start with [the formal specification](spec/microphone_spec.yaml), [capsule uncertainty](spec/capsule_model.yaml), [P48/environment constraints](spec/design_constraints.yaml), [source register](research/sources.yaml) and [Phase 0 report](research/phase0_report.md). Existing capsule research and purchase history remain in the parent `meridian/` project.

## Run in this workspace

```sh
cd /home/leobareth/Dokumente/Audiotech/meridian/lab
./run doctor
./run verify
./run evaluate fixture_0001 --samples 16 --seed 34047
```

`verify` runs independent physics and software-integrity regressions. `evaluate` runs the initial engineering suite. **Exit 2 is expected for the ideal fixture:** it fails requirements and has incomplete qualification evidence. It must never become a microphone champion.

The current local environment uses ngspice 47, Python 3.12.14, NumPy 2.4.2, SciPy 1.17.1, pandas 3.0.1, Matplotlib 3.10.8, PyYAML 6.0.3 and pytest 9.0.2. The simulator and missing runtime library were extracted inside `tools/`; no system installation or PCB package is required. `tools/packages.sha256` pins their archive integrity. Original package licence files remain in the extracted distribution; ignored binaries are not project-authored hardware.

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

Optimization uses SciPy differential evolution and explicit current/response constraints to minimize one stated axis, electronics noise. It keeps every trial, returns a value proposal and runs the full suite before acceptance. A search can legitimately find **no feasible point**; inspect the limiting physics without relaxing the requirements. The fixture exercise proves the workflow, not an architecture's merits.

[Inventor/Engineer roles](research/roles.md) separate diversity from viability. [22 initial concepts](search/concepts.yaml) cover all [14 persistent families](search/families.yaml), with nine falsification questions per concept. They are **not simulated designs**. Twenty avoid a conventional JFET voltage-buffer input. The bounded loop evaluates supplied Engineer netlists; it currently reports `awaiting_engineer_netlists` because none are implemented. No AI service or unattended background process is installed.

`search/mutate.py` registers structural children with new IDs and parent hypotheses. Value-only edits use the optimizer. Novelty uses approximate value-independent graph and functional descriptors, and never contributes engineering credit. The allocation helper tracks 50/25/15/10 exploration proportions. Diversity retention preserves niches independently of the global winner.

`results/archive.json`, `pareto_front.json` and `leaderboard.csv` are derived from full records. Only fully qualified candidates enter the eligible Pareto front. Missing objectives cannot establish dominance, and incomparable specification/suite/backend cohorts are separated. Global philosophy/objective champions remain empty until the relevant evidence is complete. Rebuild a derived index with `search/archive.py` only while evaluators are idle.

The initial [results report](research/phase0_report.md) and its response/noise plots are rendered from immutable records by `research/render_initial_report.py`. It checks that the compared runs and verification use the same sources and specification before reporting the comparison. Population percentiles include completed simulations that fail requirements; missing/error counts remain explicit.

## Next phases

Phase 3: obtain current, documented semiconductor models/limits and build a strong conventional JFET reference plus fundamentally different controls. Optimize them fairly under the same environment and no-selection requirement. Phase 4–7: implement diverse concepts, perform structural search and broaden robust qualification, with early patent-feature flags. Phase 8: separate claim/territory/status screening and resolution of implementation patent holds; no legal conclusion is asserted by the agent. Phase 9–10: only then advance eligible prototype implementations and close the measurement/model-correction loop.

The [measurement interchange](measurement/result.schema.json) shares check names, units, statuses and provenance with simulation. `measurement/compare.py` imports physical records and reports differences without changing models or thresholds. No physical measurements have been made.

Software and project-authored electrical models are provided under [MIT](LICENSE). Third-party documents, packages and future vendor models retain their own terms. A hardware publication licence and model redistribution audit should be resolved before publishing a mature circuit.
