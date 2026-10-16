# SPDX-License-Identifier: GPL-3.0-or-later
"""Rebuild scoped behavior/coverage and independently check retained bytes/KCL."""

from pathlib import Path
import csv
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.core import digest, parse_raw, read_yaml, write_json
from meridian_lab.metrics import at_frequency

MAIN = "20261016T130909Z_diverse_00c8217a"
FOLLOW = "20261016T131328Z_diverse_followup_2834cfe4"
OUT = ROOT / "research/architectures"


def inventory_check(folder):
    checked = 0
    failures = []
    for line in (folder / "batch.sha256").read_text().splitlines():
        expected, name = line.split("  ", 1)
        p = ROOT / name
        if not p.is_file() or digest(p) != expected:
            failures.append(name)
        checked += 1
    return dict(checked=checked, failures=failures)


def kcl(folder, cid):
    path = folder / cid / "0001_nominal"
    op, a = parse_raw(path / "op.raw"), parse_raw(path / "ac.raw")
    f = a["frequency"].real
    s = 2j * np.pi * f
    vf, vb, vr, vg, vo = [a[k] for k in ["v(f)", "v(b)", "v(rear)", "v(mic_g)", "v(xdut.outa)"]]
    vpol = float(op["v(b)"][0] - op["v(f)"][0])
    yf = np.full(len(f), 2e-6, dtype=complex)
    if cid.endswith("0024"):
        ys = 1e-10 + 1 / (1.5915494309 + 1 / (s * 1e-10))
        yf += 1 / (1 / (s * 1e-7) + 1 / ys)
    else:
        yf += s * 1e-7
    # Capsule AC is a derivative about its real DC bias, not imposed40V.
    terms = dict(
        base=a["i(v.xdut.vqinput_1)"],
        feedback=(vf - vo) * yf,
        capsule=s * 70e-12 * (vf - vb - vpol * (0.02 / 60) * a["v(pressure)"]),
        leakage=(vf - vb) / 1e12,
        case=s * 2e-12 * (vf - vg),
        cross=s * 0.5e-12 * (vf - vr),
    )
    residual = sum(terms.values())
    scale = sum(abs(x) for x in terms.values())
    ratio = float(np.max(abs(residual) / np.maximum(scale, 1e-300)))
    qpa = 70e-12 * vpol * (0.02 / 60)
    response = a.voltage("pp", "pn")
    reference = float(abs(at_frequency(f, response, 1000)))
    band = (f >= 20) & (f <= 20000)
    edge_f = np.r_[20, f[band], 20000]
    edge_gain = np.array([abs(at_frequency(f, response, x)) for x in edge_f])
    deviation = float(np.max(abs(20 * np.log10(edge_gain / reference))))
    return dict(
        candidate=cid,
        polarization_v=vpol,
        motional_charge_c_per_pa=qpa,
        maximum_relative_input_kcl_residual=ratio,
        kcl_pass=ratio < 0.01,
        signal_conversion_1khz_v_per_c=reference / qpa,
        sensitivity_1khz_v_per_pa=reference,
        response_deviation_db=deviation,
        disclaimer="Macro base current is observed boundary data; KCL does not independently validate semiconductor laws",
    )


def main():
    mainfolder = ROOT / "results/mechanism_controls" / MAIN
    followfolder = ROOT / "results/mechanism_controls" / FOLLOW
    first, follow = read_yaml(mainfolder / "results.json"), read_yaml(followfolder / "results.json")
    rows = first["results"]
    parent_kcl = [kcl(followfolder, c) for c in ["candidate_0012", "candidate_0024"]]
    controls = []
    for job in first["jobs"]:
        controls.append(
            dict(
                cohort=MAIN,
                model=job["model"]["id"],
                label=job["label"],
                status=job["status"],
                reason=job.get("reason", ""),
            )
        )
    for cohort, parents in [(MAIN, rows["parents"]), (FOLLOW, follow["parents"])]:
        for p in parents:
            controls.append(
                dict(
                    cohort=cohort,
                    model=p["candidate"],
                    label="exact_parent_DC_AC",
                    status=p["status"],
                    reason=p.get("reason", ""),
                )
            )
    for job in follow["jobs"]:
        controls.append(
            dict(
                cohort=FOLLOW,
                model=job["model"]["id"],
                label=job["label"],
                status=job["status"],
                reason=job.get("reason", ""),
            )
        )
    with (OUT / "diverse-behavior-001.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(controls[0]))
        writer.writeheader()
        writer.writerows(controls)
    cm = rows["cmos"]["terminals"]
    translations = []
    for model in ["opa197_pspice", "opa928_vendor"]:
        baseline = next(x for x in cm if x.get("model") == model and x["kind"] == "follower_0")
        for x in cm:
            if x.get("model") == model and x["kind"] in ["follower_20", "follower_-20"]:
                item = dict(model=model, shift_v=x["shift_v"], status=x["status"])
                if "relative_output_v" in x:
                    delta = abs(x["relative_output_v"] - baseline["relative_output_v"])
                    currents = max(
                        abs(x["currents_a"][n] - baseline["currents_a"][n]) for n in ["vp", "vn"]
                    )
                    item.update(
                        relative_output_delta_v=delta,
                        maximum_supply_current_delta_a=currents,
                        finite_screen_pass=delta < 0.001
                        and currents / abs(baseline["currents_a"]["vp"]) < 0.01,
                    )
                translations.append(item)
    integrity = {
        name: inventory_check(ROOT / "results/mechanism_controls" / name) for name in [MAIN, FOLLOW]
    }
    signal = rows["island"]
    expected = signal[0]["expected_demod_peak_v"]
    recovery = [
        x["recovered_ratio"]
        for x in signal
        if x.get("pressure_peak_pa") == 1
        and x.get("carrier_peak_v") == 0.2
        and "recovered_ratio" in x
    ]
    off = follow["carrier_off"]["demod_peak_v"]["1000"] / expected
    carrier = dict(
        zero_ratio=signal[0]["recovered_ratio"],
        carrier_off_ratio=off,
        recovery_ratios=recovery,
        relative_timestep_change=abs(recovery[1] - recovery[0]),
        deterministic_oracle_pass=signal[0]["recovered_ratio"] < 0.01
        and off < 0.01
        and all(abs(x - 1) < 0.02 for x in recovery)
        and abs(recovery[1] - recovery[0]) < 0.005,
        seeded=rows["seeded"]["aggregate"],
        native_periodic_noise_supported=False,
        physical_integration_cohort="candidate0013 prior integrated P48 failure; no pooled ideal result",
    )
    coverage = [
        dict(
            behavior="BJT finite charge conversion",
            state="12 ideal KCL controls pass",
            missing="Actual open-stage two-port/capacitance population",
        ),
        dict(
            behavior="BJT reset authority",
            state="2 ideal reset controls; exact parents replay and KCL",
            missing="Real actuator and measured base/flicker noise; full no-selection envelope",
        ),
        dict(
            behavior="CMOS floating reference",
            state="OPA197 -20V local pass; +20V fails both; OPA928 -20V fails",
            missing="Full translation/nonlinear validity; no internal rewrite",
        ),
        dict(
            behavior="CMOS guard",
            state="Grounded OPA928 two-stage AC/load diagnostic",
            missing="CMOS noise, complete loops, translation and P48 loading",
        ),
        dict(
            behavior="CMOS charge/reset",
            state="Both grounded/translated charge fixtures unsupported; reset unsupported",
            missing="Grounded charge macro validation precedes structural child",
        ),
        dict(
            behavior="Carrier deterministic",
            state="Recovery/zero/off/refinement controls pass after retained timeout",
            missing="Integrated P48 demodulation, RF safety and real hardware",
        ),
        dict(
            behavior="Carrier ideal stochastic",
            state="32 seeded LPTV cells; covariance/PSD/Parseval and source calibration",
            missing="Native periodically biased device spectra/cross correlations/oscillator AM-PM",
        ),
        dict(
            behavior="Realized hardware and qualification",
            state="No new implementation/BOM or qualified front",
            missing="Complete applicable suite after actual structural realization; procurement/patents/physical gates",
        ),
    ]
    report = dict(
        main_cohort=MAIN,
        followup_cohort=FOLLOW,
        parent_kcl=parent_kcl,
        translations=translations,
        carrier=carrier,
        coverage=coverage,
        job_count=len(controls),
        execution_errors=sum(x["status"] in ["error", "unsupported"] for x in controls),
        integrity=integrity,
        prior=rows["prior"],
        qualified_front=[],
        spec_changes=False,
    )
    write_json(OUT / "diverse-analysis-001.json", report)
    text = "<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->\n# Diverse behavior coverage\n\n"
    text += "| Behavior | Observed scope | Missing prerequisite |\n| --- | --- | --- |\n"
    for row in coverage:
        text += f"|{row['behavior']}|{row['state']}|{row['missing']}|\n"
    (OUT / "diverse-coverage-001.md").write_text(text)
    print(
        json.dumps(
            dict(
                jobs=len(controls),
                errors=report["execution_errors"],
                kcl=parent_kcl,
                carrier_pass=carrier["deterministic_oracle_pass"],
                integrity=integrity,
            )
        )
    )


if __name__ == "__main__":
    main()
