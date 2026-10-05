"""Render the initial infrastructure report from immutable experiment records.

This is reporting only: it changes no netlist, specification, result or archive.
Run from the lab: MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python research/render_initial_report.py
"""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE = "20261005T121311Z_f11a711a"
PROPOSAL = "20261005T121440Z_8f1bc311"
OPTIMIZATION = "20261005T114342Z_optimization_c7e7091b"


def read_run(identifier):
    return json.loads((ROOT / "results/runs" / identifier / "results.json").read_text())


def metrics(record, check):
    return record["checks"][check]["metrics"]


def main():
    baseline, proposal = read_run(BASE), read_run(PROPOSAL)
    assert baseline["spec_sha256"] == proposal["spec_sha256"]
    assert baseline["suite_sha256"] == proposal["suite_sha256"]
    assert not baseline["eligible"] and not proposal["eligible"]
    assert all(j["status"] == "ok" for r in [baseline, proposal] for j in r["jobs"])
    verification_path = sorted((ROOT / "results/verification").glob("*/verification.json"))[-1]
    verification = json.loads(verification_path.read_text())
    assert verification["status"] == "pass" and verification["source_unchanged"]
    assert verification["source_manifest"] == proposal["source_manifest"]
    suite = ET.parse(verification_path.with_name("junit.xml")).getroot().find("testsuite")
    assert suite is not None and suite.get("failures") == "0" and suite.get("errors") == "0"
    tests = int(suite.get("tests"))
    output = ROOT / "results/reports"
    output.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout="constrained")
    colors = ["#235789", "#bd5d1b"]
    for record, label, color in zip([baseline, proposal], ["Nominal fixture", "Numerical value proposal"], colors):
        response, noise = metrics(record, "frequency_response"), metrics(record, "noise")
        frequency = np.geomspace(20, 20000, 512)
        gain = np.exp(np.interp(np.log(frequency), np.log(response["frequency_hz"]), np.log(response["gain_v_per_pa"])))
        reference = response["sensitivity_v_per_pa_at_1khz"]
        axes[0].semilogx(frequency, 20 * np.log10(gain / reference), label=label, color=color, linewidth=2)
        axes[1].loglog(noise["frequency_hz"], np.array(noise["electronics_output_asd_v_per_sqrt_hz"]) * 1e9,
                       label=label, color=color, linewidth=2)
    axes[0].axhspan(-1, 1, color="#548c63", alpha=.13, label="Provisional response limits")
    axes[0].axhline(-1, color="#548c63", linestyle=":", linewidth=1)
    axes[0].axhline(1, color="#548c63", linestyle=":", linewidth=1)
    axes[0].set(xlabel="Frequency (Hz)", ylabel="Response relative to 1 kHz (dB)", ylim=(-4.3, 1.35),
                title="Frequency response under nominal loading")
    axes[1].set(xlabel="Frequency (Hz)", ylabel="Electronics output noise ASD (nV / √Hz)",
                title="Passive electronics noise; ideal buffers")
    for ax in axes:
        ax.set_xlim(20, 20000)
        ax.grid(True, which="both", alpha=.18)
        ax.legend(loc="best", fontsize=8)
    fig.suptitle("Infrastructure fixture only — both results are unqualified", fontsize=13)
    fig.savefig(output / "initial_fixture_comparison.png", dpi=180)
    fig.savefig(output / "initial_fixture_comparison.svg")
    plt.close(fig)

    b, p = baseline, proposal
    m = metrics
    rows = [
        ("Passive harvest current", f"{m(b,'operating_point')['current_a']*1000:.3f} mA", f"{m(p,'operating_point')['current_a']*1000:.3f} mA"),
        ("Loaded internal rail", f"{m(b,'operating_point')['internal_rail_v']:.3f} V", f"{m(p,'operating_point')['internal_rail_v']:.3f} V"),
        ("Simulated capsule polarization", f"{m(b,'operating_point')['polarization_dc_v']:.3f} V", f"{m(p,'operating_point')['polarization_dc_v']:.3f} V"),
        ("Maximum audio response deviation", f"{m(b,'frequency_response')['response_deviation_db']:.3f} dB", f"{m(p,'frequency_response')['response_deviation_db']:.3f} dB"),
        ("Electronics unweighted EIN, conditional", f"{m(b,'noise')['electronics_ein_v_rms_conditional']*1e6:.3f} µV RMS", f"{m(p,'noise')['electronics_ein_v_rms_conditional']*1e6:.3f} µV RMS"),
        ("Electronics unweighted equivalent pressure", f"{m(b,'noise')['electronics_noise_pa_rms']*1e6:.1f} µPa RMS", f"{m(p,'noise')['electronics_noise_pa_rms']*1e6:.1f} µPa RMS"),
        ("Electronics A-weighted noise, conditional", f"{m(b,'noise')['electronics_noise_dba_conditional']:.2f} dBA", f"{m(p,'noise')['electronics_noise_dba_conditional']:.2f} dBA"),
        ("Worst differential output impedance", f"{m(b,'output_impedance')['output_impedance_ohm']:.1f} Ω", f"{m(p,'output_impedance')['output_impedance_ohm']:.1f} Ω"),
        ("Worst diagonal impedance mismatch", f"{m(b,'balance')['impedance_mismatch_fraction']*100:.2f}%", f"{m(p,'balance')['impedance_mismatch_fraction']*100:.2f}%"),
        ("Cold-start settling to 1%", f"{m(b,'startup')['settling_to_1percent_s']:.3f} s", f"{m(p,'startup')['settling_to_1percent_s']:.3f} s"),
        ("DC/AC scenario screening", f"{m(b,'monte_carlo')['passing']}/16 pass", f"{m(p,'monte_carlo')['passing']}/16 pass"),
        ("Scenario response median", f"{m(b,'monte_carlo')['median']:.3f} dB", f"{m(p,'monte_carlo')['median']:.3f} dB"),
        ("Scenario response 95th / 99th percentile", f"{m(b,'monte_carlo')['p95']:.3f} / {m(b,'monte_carlo')['p99']:.3f} dB", f"{m(p,'monte_carlo')['p95']:.3f} / {m(p,'monte_carlo')['p99']:.3f} dB"),
        ("Scenario response worst observed", f"{m(b,'monte_carlo')['worst_observed']:.3f} dB", f"{m(p,'monte_carlo')['worst_observed']:.3f} dB"),
    ]
    table = "\n".join(f"| {name} | {before} | {after} |" for name, before, after in rows)
    checks = "\n".join(f"| {name} | {check['status']} | {p['checks'][name]['status']} |" for name, check in b['checks'].items())
    verification_relative = verification_path.relative_to(ROOT).as_posix()
    report = f"""# M100 Meridian: initial research environment and evidence report

Date: 2026-10-05. Scope: **Phase 0–2 foundation**, with initial Phase 4 concept proposals and a numerical-workflow control. No production topology or prototype has been selected.

The workspace now runs real ngspice analyses, records complete evidence, rejects incomplete qualification, performs bounded numerical value search and preserves architectural niches. **{tests} independent regression checks pass.** Both final fixture evaluations finish all their SPICE jobs successfully; both fail engineering qualification. The eligible Pareto front and champion registers are correctly empty.

## What is executable

- First-order two-diaphragm electrical capsule model, nonlinear charge law and a linearized electronics-distortion mode.
- Loaded P48 supply, separate feed resistors and mismatches, cable/shield resistance and capacitance, AC-coupled preamp impedance and mismatch.
- Fourteen named engineering checks: operating point, response, noise, distortion, headroom, output impedance, balance, P48, temperature, semiconductor corners, Monte Carlo, loading, startup and stability. Some remain explicit incomplete screens, as detailed below.
- Noise integration with unweighted and A-weighted results and separate bias, polarization, power, output and capsule-leakage-surrogate contributions; H2–H10 spectra and coherent settling checks.
- SciPy differential evolution, parameter bounds and numerical constraints, raw trial preservation, full-suite re-evaluation and controlled parent comparisons.
- Experiment snapshots, source/specification hashes, exact simulator decks, raw files, failure logs, software versions, seeded uncertainty scenarios and strict result status handling.
- A quality-diversity archive, separate novelty descriptors, structural child registration, exploration allocation and a bounded evaluator for supplied Engineer netlists.
- A measurement interchange contract and comparison adapter, with a [synthetic adapter smoke check](../results/reports/measurement_adapter_smoke.json). No physical data have been collected.

The local runtime is ngspice 47 and Python 3.12.14 with pinned NumPy/SciPy/pandas/Matplotlib/PyYAML/pytest. It is installed within the workspace. The [README](../README.md) contains commands, bootstrap details, platform dependencies and evidence contracts. No system package, PCB tool or background AI service is required.

## Capsule evidence and uncertainty

The [current manufacturer page](https://store.arienneaudio.com/microphone-capsules/20-26-arienne-audio-flat-k47-microphone-capsule.html#/12-options-cardioid_omni) identifies the Flat K47 Cardioid/Omni K47FRB, modified tuning and changed manufacturing facility. It does not supply the electrical/mechanical data needed to qualify this microphone. A different regular K47's advertised capacitance is not transferred to this model.

| Property | Model entry | Evidence status |
| --- | --- | --- |
| Product and cardioid/omni options | Flat K47 K47FRB | Manufacturer specification |
| Historical combined capacitance | 120–150 pF | Unmeasured community estimate; no current-batch guarantee |
| Front and rear capacitance | 70 pF nominal per side; 45–100 pF each | Assumed exploratory brackets; independent/correlated behavior unresolved |
| Sensitivity at 60 V normalization | 20 mV/Pa nominal; 5–40 mV/Pa | Assumed, not measured |
| Polarization normalization | 60 V | Mathematical reference only |
| Polarization simulation envelope | 20–70 V | Assumed numerical exploration, not a hardware rating |
| Maximum safe polarization | Unknown | Requires applicable manufacturer data or qualified characterization |
| Leakage | 1 TΩ nominal; 1 GΩ–100 TΩ | Assumed humidity/contamination envelope; not a production distribution |
| Electrode/case parasitic | 2 pF nominal; 0.5–10 pF | Assumed |
| Front/rear stray | 0.5 pF nominal; 0–5 pF | Assumed |
| Mechanical noise, overload and angular response | Unknown | Not established by this electrical model |

The [capsule specification](../spec/capsule_model.yaml) explicitly distinguishes manufacturer information, third-party estimates, assumptions and unknowns. The [source register](sources.yaml) links the historical estimate and records limits of applicability. Nominal values are scenario anchors, not probability means inferred from production samples.

The charge law is `Q=C0(1+k·p)V`, with `k=Sref/Vref`, imposed linear compliance and current `I=dQ/dt`. A scaled observer using a native capacitor realizes this law. Gear-2 integration passes analytical AC/transient agreement and timestep-refinement regressions. Pressure is a separate virtual port; no capsule acoustic polar pattern is inferred. Linearized mode uses the actual simulated DC polarization for electronics THD. Mechanical distortion, acoustic thermal noise, electrostatic softening, pull-in and pressure overload are absent. No system self-noise or maximum-SPL claim follows from these runs.

## P48 evidence and environment

The [IEC official catalogue](https://webstore.iec.ch/en/publication/30762) identifies IEC 61938:2018 edition 3; its catalogue stability date is 2030. The public preview does not include the full phantom-power clauses. The [SCHOEPS manufacturer manual](https://schoeps.de/fileadmin/user_upload/user_upload/Downloads/Bedienungsanleitungen/Schoeps_Manual_V4_U_DE_1388740809.pdf) supports the public P48 summary of 44–52 V, nominal 6.8 kΩ feeds, pair matching below 0.4% and maximum total microphone current 10 mA.

Absolute feed tolerance deliberately retains ±20% legacy coverage from that manual. An uncontrolled transcription of the newer standard suggests ±10%; this is not treated as authenticated. The 7 mA preferred-current target and 0.8% conductor-current condition are provisional pending controlled section 9.4/Table 6 verification. The model therefore supports research screening, **not an IEC compliance declaration**. These distinctions are recorded in [design constraints](../spec/design_constraints.yaml).

Nominal cable length is 10 m, with 0–100 m application scenarios and a separately recorded 300 m stress envelope. Nominal effective differential capacitance is 100 pF/m, while its direct and shield components are assumed. Preamp differential impedance is 2 kΩ nominal, 1–10 kΩ application scenarios, with 600 Ω stress cases and ±5% leg mismatch. Temperature screens span −10 to +50 °C. A lumped cable model cannot establish RF behavior.

## Frozen provisional requirements

Electronics targets are ±1 dB from 20 Hz to 20 kHz, unweighted EIN ≤1 µV RMS, conditional electronics noise ≤4 dBA, THD ≤0.01% at 1 Pa and ≤0.5% at the 135 dB pressure stimulus, output impedance ≤200 Ω, impedance mismatch ≤1%, HF peaking ≤3 dB and cold-start settling ≤5 s. Total current is limited to 10 mA. Inherited 7 dBA system noise and 135 dB SPL aspirations remain contingent on capsule measurements.

These are research requirements, not manufacturer promises. No threshold or uncertainty range was relaxed to accommodate failures. The sole specification amendment corrected YAML scientific-exponent typing without changing numeric values; [amendment record](specification_amendments.md). The frozen specification hash is `{b['spec_sha256']}`.

## Actual sanity-fixture results

The [plain netlist](../candidates/fixture_0001/circuit.cir) is an **ideal, noiseless differential-buffer infrastructure fixture**, with a passive P48 harvest/load network. Ideal active sources do not draw realistic audio-driver power or clip. Its current, THD and headroom screens cannot qualify any real architecture. It is ineligible by construction.

The final [nominal record](../results/runs/{BASE}/results.json) and [value-proposal record](../results/runs/{PROPOSAL}/results.json) use identical specification, model, test and source hashes. Each preserves {len(b['jobs'])} simulator jobs with decks/logs/raw evidence. All jobs complete; qualification failures below are retained.

| Metric | Nominal fixture | Numerical value proposal |
| --- | ---: | ---: |
{table}

Noise values integrate 20 Hz–20 kHz, with pressure and EIN conditional on the assumed capsule transfer. Capsule mechanical noise is excluded; no semiconductor noise model exists in this ideal fixture. Noise-power component sums close to total simulated noise within numerical precision. The scenario pass counts cover only initial DC/AC screens; **they are not manufacturing yield or all-requirement pass rates**.

![Final fixture response and passive noise spectra](../results/reports/initial_fixture_comparison.png)

The optimizer varied bias resistance, polarization resistance and output coupling capacitance within declared bounds. [202 recorded trials](../results/runs/{OPTIMIZATION}/trials.json) produced a proposal of 16.317 GΩ, 24.447 MΩ and 99.286 µF, respectively. The iteration budget expired before the optimizer's convergence criterion; global optimality is not claimed. Initial two-parameter and shorter searches failed feasibility and remain recorded.

The proposal improves nominal response and output impedance but worsens noise, impedance balance and startup settling. Its P48 current/response screens pass, yet realistic low-impedance output-load stress cases still fail response. The full suite rejects it. This verifies the optimizer-to-test-to-archive workflow and demonstrates why one-axis success cannot override other requirements. The current optimizer is a **nominal constrained control**; robust high-percentile/worst-case optimization is future work.

| Engineering check | Nominal | Proposal |
| --- | --- | --- |
{checks}

Passing distortion here validates the numerical harmonic extractor against ideal behavior. The headroom result is a right-censored lower bound at 112.468 Pa RMS and 1 kHz, with no observed clipping boundary; it is not a real microphone's maximum SPL. Temperature pass covers this ideal electrical network, not unknown capsule or semiconductor temperature laws. The stability check fails cable/load stress and has no return-ratio/Nyquist evidence; low HF peaking alone does not prove stability.

The [verification record](../{verification_relative}) and its `junit.xml` preserve {tests} passing software/physics regressions, raw controls and matching final source manifests. Controls include loaded P48 analytic behavior, charge-model AC/transient agreement, capacitance extraction, output-impedance deembedding, component-noise accounting including a generic BJT parser control, harmonic timestep refinement, specification integrity, incomplete-result rejection, structural novelty and diversity retention. A generic BJT control is not a qualified production device model.

## Diversity and research memory

[22 Inventor concepts](../search/concepts.yaml) cover all [14 required architectural families](../search/families.yaml). Twenty avoid a conventional JFET voltage-buffer input; multiple proposals borrow charge amplifiers, electrometer guarding, capacitance bridges, low-current transimpedance sensing and sensor-interface mechanisms. Each specifies the sensed quantity, loading, DC bias, gain, balanced output, likely noise/distortion, fatal flaw and fastest falsification experiment. The [cross-domain register](cross_domain/mechanisms.md) links primary application reports, datasheets and research.

Concepts are **proposals, not explored or validated circuits**. The Inventor proposes; the Engineer must preserve each defining mechanism while constructing a viable netlist; simulation decides. One charge-amplifier concept has an [Engineer handoff](../search/proposals/concept_0010/engineer_task.md). No nonideal research or benchmark netlist is implemented yet. The bounded search loop correctly returns `awaiting_engineer_netlists` instead of manufacturing performance claims.

The [archive](../results/archive.json) retains unsuccessful experiments and architectural niches. [Novelty](../search/novelty.py) is separate from performance; a value-only change is not a new architecture. Pareto comparisons require complete metrics and matching source/specification/backend cohorts. [Rejected ideas](rejected_ideas.md), [discoveries](discoveries.md) and the [experiment log](experiment_log.md) preserve implementation failures and numerical lessons, including a fresh [behavioral-derivative AC failure reproduction](probes/ddt_ac_reproducer/results.json). One run was invalidated by a concurrent proposal export; it was preserved and repeated with stable sources. A final reporting audit also caught adverse completed scenarios being excluded from metric percentiles. Corrected summaries include all finite completed pass/fail cases, explicitly count missing/error metrics and retain failures in the pass denominator. The final runs above use the corrected suite; earlier aggregate percentiles are superseded, with original raw cases preserved.

## Evidence needed before later phases

1. Phase 3: current, documented semiconductor types, model licences, manufacturer limits, noise/temperature behavior and defensible populations; then a strong fairly optimized no-selection JFET reference and several distinct controls.
2. Phase 4–7: Engineer netlists for diverse concepts, structural search, robust optimization, passive/semiconductor tolerance and correlation populations, full noise/distortion/environment coverage, meaningful loop injection and stability analysis, device power/SOA and statistically supported all-requirement yield. Current scenario Monte Carlo is only a screen.
3. Capsule characterization: safe polarization and lead isolation first; calibrated front/rear capacitance/parasitics, sensitivity/spectra, leakage versus humidity/temperature, noise/overload and angular response with the intended headbasket. Replace assumed model parameters without changing the software architecture.
4. Phase 8: the [patent track](patents/README.md) is prepared but has no screened patent claims yet. Relevant jurisdictions, priority/status/claims and uncertain cases require separate documented research; no freedom-to-manufacture conclusion is made.
5. Phase 9–10: compare several fundamental families before selecting prototypes; add RF/ESD/protection/humidity, connection transients and PCB parasitics; collect calibrated measurements through the [interchange](../measurement/README.md), compare with simulation and revise models from evidence.

Licensing update, 2026-10-05: project-authored software is GPL-3.0-or-later; hardware design sources and electrical netlists/models are CERN-OHL-S-2.0. See the [repository scope](../../../LICENSE). Third-party material retains its own terms; vendor-model redistribution review and engineering/patent release gates remain unresolved. No parts were purchased, suppliers contacted, PCB generated or physical prototype authorized by a simulated passing screen.
"""
    (ROOT / "research/phase0_report.md").write_text(report)
    inputs = [ROOT / "results/runs" / ident / "results.json" for ident in [BASE, PROPOSAL]] + [verification_path]
    overview = {
        "schema_version": 1, "scope": "phase_0_2_foundation", "candidate_kind": "ideal_infrastructure_fixture",
        "baseline_experiment": BASE, "value_proposal_experiment": PROPOSAL,
        "optimization_experiment": OPTIMIZATION, "numerical_trials": 202,
        "regression_tests": tests, "verification_record": verification_relative,
        "qualified_designs": 0, "architectural_concepts": 22, "persistent_families": 14,
        "implemented_nonideal_architectures": 0, "physical_measurements": 0,
        "same_specification": True, "same_suite": True,
        "spec_sha256": b["spec_sha256"], "suite_sha256": b["suite_sha256"],
        "report_inputs_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
        "outputs": ["research/phase0_report.md", "results/reports/initial_fixture_comparison.png", "results/reports/initial_fixture_comparison.svg"],
    }
    (output / "initial_environment.json").write_text(json.dumps(overview, indent=2) + "\n")
    print(json.dumps(overview, indent=2))


if __name__ == "__main__":
    main()
