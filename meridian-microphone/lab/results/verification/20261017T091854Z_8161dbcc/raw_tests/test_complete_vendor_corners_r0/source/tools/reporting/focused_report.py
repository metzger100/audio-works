# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive compact Prompt9 tables from preserved complete and failed records."""

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src")]
from meridian_lab.core import read_yaml, write_json, digest, parse_raw
from meridian_lab.bounded import write_csv

PARENT = "results/mechanism_controls/20261011T192308Z_focused_1992e85a"
FOLLOWUP = "results/mechanism_controls/20261011T192658Z_focused_followup_b5cac5a2"
OUT = ROOT / "results/reports/focused-hypotheses-001"


def csv_table(name, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    write_csv(OUT / name, rows, keys)


def figure(rows):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for c, label in [
        ("candidate_0019", "0019 fixed bias"),
        ("candidate_0023", "0023 servo"),
        ("candidate_0025", "0025 servo + filter"),
    ]:
        points = sorted(
            (float(r["declared_scenario"]["parameters"]["LEAK"]), r)
            for r in rows
            if r["candidate"] == c
            and r["scenario"] in ["leakage1G", "leakage10G", "leakage100G", "leakage100T"]
        )
        axes[0].loglog(
            [x for x, r in points],
            [r["noise_pa_rms_conditional"] * 1e6 for x, r in points],
            "o-",
            label=label,
        )
        axes[1].semilogx(
            [x for x, r in points], [r["response_db"] for x, r in points], "o-", label=label
        )
    axes[0].set_ylabel("Conditional electronics noise (µPa RMS)")
    axes[1].set_ylabel("Maximum normalized audio deviation (dB)")
    axes[1].axhline(1, color="black", linestyle=":", label="1 dB acceptance")
    for ax in axes:
        ax.set_xlabel("Separate diaphragm leakage resistance (Ω)")
        ax.grid(True, which="both", alpha=0.25)
        ax.legend(fontsize=8)
    fig.suptitle("Finite matched leakage cases — complete qualification remains failed")
    for extension in ["png", "svg"]:
        fig.savefig(OUT / ("leakage." + extension), dpi=180)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inputs = {}

    def load(name):
        p = ROOT / name
        inputs[name] = digest(p)
        return read_yaml(p)

    d, follow = load(PARENT + "/results.json"), load(FOLLOWUP + "/results.json")
    assert d["source_unchanged"] and follow["source_unchanged"]
    rows = d["rows"] + follow["rows"]
    # Preserve original failed board cells; their successor has its own identity.
    csv_table(
        "scenarios.csv",
        [
            {
                k: r.get(k)
                for k in [
                    "candidate",
                    "scenario",
                    "status",
                    "validation",
                    "current_a",
                    "polarization_v",
                    "response_db",
                    "sensitivity_v_per_pa",
                    "noise_pa_rms_conditional",
                    "reason",
                ]
            }
            for r in rows
        ],
    )
    full = {c: load("results/runs/" + n + "/results.json") for c, n in d["full_suite"].items()}
    checks = [
        {
            "candidate": c,
            "check": k,
            "status": x["status"],
            "reason": x.get("reason"),
            "coverage": x.get("coverage"),
            "experiment": r["experiment_id"],
        }
        for c, r in full.items()
        for k, x in r["checks"].items()
    ]
    csv_table("checks.csv", checks)
    nominal = {
        c: next(x for x in rows if x["candidate"] == c and x["scenario"] == "nominal") for c in full
    }
    child = next(c for c in full if c not in ["candidate_0019", "candidate_0023"])
    b = []
    for x in rows:
        if x["candidate"] != child:
            continue
        parent = next(
            y for y in rows if y["candidate"] == "candidate_0023" and y["scenario"] == x["scenario"]
        )
        b.append(
            dict(
                scenario=x["scenario"],
                parent_status=parent["status"],
                child_status=x["status"],
                response_change_db=x.get("response_db", np.nan) - parent.get("response_db", np.nan),
                noise_ratio=x["noise_pa_rms_conditional"] / parent["noise_pa_rms_conditional"]
                if "noise_pa_rms_conditional" in x and "noise_pa_rms_conditional" in parent
                else None,
            )
        )
    # Missing comparisons stay null, rather than serializing nonfinite evidence.
    for r in b:
        if not np.isfinite(r["response_change_db"]):
            r["response_change_db"] = None
    csv_table("filter-pairs.csv", b)
    driver = load(PARENT + "/driver-results.json")
    pairs, startup = [], []
    for r in driver["rows"]:
        base = next(
            x
            for x in driver["rows"]
            if x["model"] == "bc846b_emitter_r1"
            and (x["fixture"], x["temperature_c"]) == (r["fixture"], r["temperature_c"])
        )
        pairs.append(
            dict(
                model=r["model"],
                fixture=r["fixture"],
                temperature_c=r["temperature_c"],
                status=r["status"],
                output_noise_v_rms=r.get("native_output_noise_v_rms"),
                noise_ratio=r["native_output_noise_v_rms"] / base["native_output_noise_v_rms"],
                diagonal_mismatch_fraction=r["ports"]["diagonal_mismatch_fraction_max"],
                imbalance_ratio=r["ports"]["diagonal_mismatch_fraction_max"]
                / base["ports"]["diagonal_mismatch_fraction_max"],
                differential_ohm=r["ports"]["differential_ohm_max"],
                common_current_conversion_ohm=r["ports"]["common_current_to_diff_ohm_max"],
                common_rail_diff_gain=r["correlated_supply_diff_v_per_v_1khz"],
                inversion_phase_deg=r["inversion_phase_difference_deg"],
                native_power_closure=r["native_noise_power_closure"],
            )
        )
    csv_table("drivers.csv", pairs)
    for job in driver["jobs"]:
        if job["label"] != "cold_startup":
            continue
        mid = job["model"]["id"]
        raw = parse_raw(ROOT / PARENT / "driver" / job["directory"] / "start.raw")
        target = parse_raw(ROOT / PARENT / "driver" / mid / "high_source_impedance_25/op.raw")
        nodes = ["signal", "inverse", "outp", "outn"]
        residual = {n: float(raw[f"v({n})"][-1].real - target[f"v({n})"][0].real) for n in nodes}
        startup.append(
            dict(
                model=mid,
                job_status=job["status"],
                final_residual_v=residual,
                scope="Rail-only turn-on, raw already29.5293276V; high-source-impedance fixture,25C. Not P48 hot-plug/full-DUT startup qualification",
            )
        )
    refinement = []
    for c, n in nominal.items():
        r = full[c]
        refinement.append(
            dict(
                candidate=c,
                noise_64_to_128_relative=n["noise_pa_rms_conditional"]
                / r["checks"]["noise"]["metrics"]["electronics_noise_pa_rms"]
                - 1,
                response_32_to_64_change_db=n["response_db"]
                - r["checks"]["frequency_response"]["metrics"]["response_deviation_db"],
            )
        )
    dc_rows = [
        dict(candidate=x["candidate"], scenario=x["scenario"], **x["dc"]) for x in rows if "dc" in x
    ]
    write_json(OUT / "dc-authority.json", dc_rows)
    write_json(OUT / "driver-startup.json", startup)
    write_json(OUT / "refinement.json", refinement)
    contributions = [
        {"candidate": c, "source": k, "pressure_noise_pa_rms": v}
        for c, n in nominal.items()
        for k, v in n["contribution_pa_rms"].items()
    ]
    csv_table("nominal-noise-contributions.csv", contributions)
    holdouts = {
        c: dict(
            total=16,
            pass_count=sum(
                x["status"] == "pass" for x in rows if x["candidate"] == c and x["validation"]
            ),
            interpretation="Paired artificial external/shared-quantile specimens, not yield or probability",
        )
        for c in full
    }
    summary = dict(
        date="2026-10-12",
        primary_batch=PARENT,
        followup_batch=FOLLOWUP,
        children=load("research/architectures/focused-children-001.json"),
        hypotheses=[
            dict(
                id="A",
                state="full-envelope no-trim claim falsified; finite local useful cases",
                remedy_child=None,
            ),
            dict(
                id="B",
                state="resolved conditional nominal noise benefit; leakage/startup/qualification fail",
                child=child,
            ),
            dict(
                id="C",
                state="neither alternative improves all supported noise/port comparisons",
                integrated_child=None,
            ),
        ],
        checks=checks,
        holdouts=holdouts,
        refinement=refinement,
        nominal={
            c: {
                k: n[k]
                for k in ["current_a", "polarization_v", "response_db", "noise_pa_rms_conditional"]
            }
            for c, n in nominal.items()
        },
        oracles=driver["oracles"] + follow["oracles"],
        complete_execution=True,
        qualified=False,
        production_front=[],
        physical_front=[],
        all_families_retained=14,
        driver_boundary=dict(
            rail_v=13.5557796,
            raw_v=29.5293276,
            correction="Held diagnostic values near0019 operating point; raw equals rounded0019 backplate,0.000612V below actual raw. Original comment called this0023 incorrectly. No integrated operating-point or supply-feedback claim.",
        ),
    )
    write_json(OUT / "summary.json", summary)
    coverage = dict(
        A_B=dict(
            candidates=list(full),
            original_cells=len(d["rows"]),
            followup_cells=len(follow["rows"]),
            original_board_extraction_errors=3,
            board_successors=3,
            identical_external_conditions=True,
            shared_quantiles=True,
            differing_source_resistors_ohm={
                "candidate_0019": 3300,
                "candidate_0023": 1000,
                child: 1000,
            },
            full_suite_checks_per_candidate=14,
            independent_holdouts_per_candidate=16,
            temperature_endpoint_c=[-10, 50],
            original_full_spec_envelope_preserved=True,
        ),
        C=dict(
            exact_full_models=3,
            temperatures_c=[-10, 25, 50],
            fixtures=3,
            cells=27,
            jobs=60,
            startup_controls=3,
            finite_interface=True,
            noise_scope="Total native fixture-plus-driver PSD, missing full physical spectra",
            loaded_twoport=True,
            deembedded_DUT="Three complete microphone suites separately",
        ),
        loop=dict(
            voltage_orientation_checks=2,
            voltage_return_diagnostics=2,
            bilateral_current_injection=False,
            open_loop_RHP_poles_known=False,
            stability_proof=False,
        ),
        nonlinear="Full DUT distortion errors/headroom incomplete retained; Prompt8 isolated follower scope only",
        unsupported=[
            "joint process distribution",
            "complete noise spectra",
            "temperature dielectric/board leakage laws",
            "thermal/SOA",
            "hot_plug",
            "protection/ESD",
            "distributed_RF",
            "capsule safe bias",
            "mechanical acoustic measurements",
            "full candidate patent status",
            "delivered Germany basket",
        ],
    )
    write_json(OUT / "coverage.json", coverage)
    write_json(OUT / "inputs.json", inputs)
    figure(rows)
    print(
        dict(
            cells=len(rows),
            checks=len(checks),
            driver_cells=len(pairs),
            report=str(OUT.relative_to(ROOT)),
        )
    )


if __name__ == "__main__":
    main()
