from meridian_lab.core import read_yaml

# SPDX-License-Identifier: GPL-3.0-or-later
"""Render the initial infrastructure report from immutable experiment records.

This is reporting only: it changes no netlist, specification, result or archive.
Run from the lab: MPLCONFIGDIR=tools/cache/matplotlib .venv/bin/python tools/reporting/render_initial_report.py
"""
from initial_common import BASE, PROPOSAL, ROOT, metrics, read_run


import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt


def matching_verification(proposal):
    # Report the original cohort's verification, rather than an unrelated latest run.
    return next(
        path
        for path in reversed(sorted((ROOT / "results/verification").glob("*/verification.json")))
        if (record := read_yaml(path)).get("status") == "pass"
        and record.get("source_unchanged")
        and record["source_manifest"] == proposal["source_manifest"]
    )


def stage(context):
    baseline, proposal = read_run(BASE), read_run(PROPOSAL)
    assert baseline["spec_sha256"] == proposal["spec_sha256"]
    assert baseline["suite_sha256"] == proposal["suite_sha256"]
    assert not baseline["eligible"] and not proposal["eligible"]
    assert all(j["status"] == "ok" for r in [baseline, proposal] for j in r["jobs"])
    verification_path = matching_verification(proposal)
    verification = read_yaml(verification_path)
    assert verification["status"] == "pass" and verification["source_unchanged"]
    assert verification["source_manifest"] == proposal["source_manifest"]
    suite = ET.parse(verification_path.with_name("junit.xml")).getroot().find("testsuite")
    assert suite is not None and suite.get("failures") == "0" and suite.get("errors") == "0"
    tests = int(suite.get("tests"))
    output = ROOT / "results/reports"
    output.mkdir(exist_ok=True)
    plt.rcParams["svg.hashsalt"] = "meridian-initial-fixture"
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout="constrained")
    colors = ["#235789", "#bd5d1b"]
    for record, label, color in zip(
        [baseline, proposal], ["Nominal fixture", "Numerical value proposal"], colors
    ):
        response, noise = metrics(record, "frequency_response"), metrics(record, "noise")
        frequency = np.geomspace(20, 20000, 512)
        gain = np.exp(
            np.interp(
                np.log(frequency),
                np.log(response["frequency_hz"]),
                np.log(response["gain_v_per_pa"]),
            )
        )
        reference = response["sensitivity_v_per_pa_at_1khz"]
        axes[0].semilogx(
            frequency, 20 * np.log10(gain / reference), label=label, color=color, linewidth=2
        )
        axes[1].loglog(
            noise["frequency_hz"],
            np.array(noise["electronics_output_asd_v_per_sqrt_hz"]) * 1e9,
            label=label,
            color=color,
            linewidth=2,
        )
    axes[0].axhspan(-1, 1, color="#548c63", alpha=0.13, label="Provisional response limits")
    axes[0].axhline(-1, color="#548c63", linestyle=":", linewidth=1)
    axes[0].axhline(1, color="#548c63", linestyle=":", linewidth=1)
    axes[0].set(
        xlabel="Frequency (Hz)",
        ylabel="Response relative to 1 kHz (dB)",
        ylim=(-4.3, 1.35),
        title="Frequency response under nominal loading",
    )
    axes[1].set(
        xlabel="Frequency (Hz)",
        ylabel="Electronics output noise ASD (nV / √Hz)",
        title="Passive electronics noise; ideal buffers",
    )
    for ax in axes:
        ax.set_xlim(20, 20000)
        ax.grid(True, which="both", alpha=0.18)
        ax.legend(loc="best", fontsize=8)
    fig.suptitle("Infrastructure fixture only — both results are unqualified", fontsize=13)
    fig.savefig(output / "initial-fixture-comparison.png", dpi=180)
    fig.savefig(output / "initial-fixture-comparison.svg", metadata={"Date": None})
    plt.close(fig)
    b, p = baseline, proposal
    m = metrics
    rows = [
        (
            "Passive harvest current",
            f"{m(b, 'operating_point')['current_a'] * 1000:.3f} mA",
            f"{m(p, 'operating_point')['current_a'] * 1000:.3f} mA",
        ),
        (
            "Loaded internal rail",
            f"{m(b, 'operating_point')['internal_rail_v']:.3f} V",
            f"{m(p, 'operating_point')['internal_rail_v']:.3f} V",
        ),
        (
            "Simulated capsule polarization",
            f"{m(b, 'operating_point')['polarization_dc_v']:.3f} V",
            f"{m(p, 'operating_point')['polarization_dc_v']:.3f} V",
        ),
        (
            "Maximum audio response deviation",
            f"{m(b, 'frequency_response')['response_deviation_db']:.3f} dB",
            f"{m(p, 'frequency_response')['response_deviation_db']:.3f} dB",
        ),
        (
            "Electronics unweighted EIN, conditional",
            f"{m(b, 'noise')['electronics_ein_v_rms_conditional'] * 1e6:.3f} µV RMS",
            f"{m(p, 'noise')['electronics_ein_v_rms_conditional'] * 1e6:.3f} µV RMS",
        ),
        (
            "Electronics unweighted equivalent pressure",
            f"{m(b, 'noise')['electronics_noise_pa_rms'] * 1e6:.1f} µPa RMS",
            f"{m(p, 'noise')['electronics_noise_pa_rms'] * 1e6:.1f} µPa RMS",
        ),
        (
            "Electronics A-weighted noise, conditional",
            f"{m(b, 'noise')['electronics_noise_dba_conditional']:.2f} dBA",
            f"{m(p, 'noise')['electronics_noise_dba_conditional']:.2f} dBA",
        ),
        (
            "Worst differential output impedance",
            f"{m(b, 'output_impedance')['output_impedance_ohm']:.1f} Ω",
            f"{m(p, 'output_impedance')['output_impedance_ohm']:.1f} Ω",
        ),
        (
            "Worst diagonal impedance mismatch",
            f"{m(b, 'balance')['impedance_mismatch_fraction'] * 100:.2f}%",
            f"{m(p, 'balance')['impedance_mismatch_fraction'] * 100:.2f}%",
        ),
        (
            "Cold-start settling to 1%",
            f"{m(b, 'startup')['settling_to_1percent_s']:.3f} s",
            f"{m(p, 'startup')['settling_to_1percent_s']:.3f} s",
        ),
        (
            "DC/AC scenario screening",
            f"{m(b, 'monte_carlo')['passing']}/16 pass",
            f"{m(p, 'monte_carlo')['passing']}/16 pass",
        ),
        (
            "Scenario response median",
            f"{m(b, 'monte_carlo')['median']:.3f} dB",
            f"{m(p, 'monte_carlo')['median']:.3f} dB",
        ),
        (
            "Scenario response 95th / 99th percentile",
            f"{m(b, 'monte_carlo')['p95']:.3f} / {m(b, 'monte_carlo')['p99']:.3f} dB",
            f"{m(p, 'monte_carlo')['p95']:.3f} / {m(p, 'monte_carlo')['p99']:.3f} dB",
        ),
        (
            "Scenario response worst observed",
            f"{m(b, 'monte_carlo')['worst_observed']:.3f} dB",
            f"{m(p, 'monte_carlo')['worst_observed']:.3f} dB",
        ),
    ]
    table = "\n".join(f"| {name} | {before} | {after} |" for name, before, after in rows)
    checks = "\n".join(
        f"| {name} | {check['status']} | {p['checks'][name]['status']} |"
        for name, check in b["checks"].items()
    )
    verification_relative = verification_path.relative_to(ROOT).as_posix()
    return {
        **context,
        "b": b,
        "checks": checks,
        "output": output,
        "table": table,
        "tests": tests,
        "verification_path": verification_path,
        "verification_relative": verification_relative,
    }
