# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison 001 from immutable records and original local waveforms.

No simulator, candidate, specification, archive or original result is modified.
Run from lab: .venv/bin/python tools/reporting/compare_architectures.py
"""

from comparison_common import OUT, ROOT, dump, pareto, table

from meridian_lab.core import read_yaml


from meridian_lab.metrics import at_frequency
import numpy as np
import matplotlib.pyplot as plt


def stage(context):
    ac = context["ac"]
    bom = context["bom"]
    boms = context["boms"]
    candidate = context["candidate"]
    cfg = context["cfg"]
    contributions = context["contributions"]
    details = context["details"]
    evidence = context["evidence"]
    f = context["f"]
    gain = context["gain"]
    group = context["group"]
    groups = context["groups"]
    harmonics = context["harmonics"]
    index = context["index"]
    nominal_rows = context["nominal_rows"]
    optimizers = context["optimizers"]
    paired = context["paired"]
    r = context["r"]
    records = context["records"]
    refresh = context["refresh"]
    representative_records = context["representative_records"]
    row = context["row"]
    sensitivity = context["sensitivity"]
    spectra = context["spectra"]
    statuses = context["statuses"]
    values = context["values"]
    for row in nominal_rows:
        if row["electronics_dba_conditional"] is None:
            continue
        for sref in [0.005, 0.020, 0.040]:
            sensitivity.append(
                {
                    "candidate": row["candidate"],
                    "sref_v_per_pa_at_60v": sref,
                    "derived_electronics_dba_conditional": row["electronics_dba_conditional"]
                    + 20 * np.log10(0.020 / sref),
                    "derived_noise_pa_rms": row["noise_pa_rms"] * 0.020 / sref,
                    "assumption": "Linear pressure-transfer scaling; unchanged DC/stationary noise. No physical noise qualification.",
                }
            )
    table(OUT / "sensitivity-rescaling.csv", sensitivity)
    projection_rows = []
    for r in records.values():
        if r["topology"]["family"] not in {"conventional_jfet", "unconventional_jfet", "no_fet"}:
            continue
        # Continuous proposals share a candidate identity; explicitly distinguish.
        label = r["candidate_id"]
        if r["experiment_id"] in {e["experiment"] for e in index["continuous"].values()}:
            label += ":continuous"
        bom = read_yaml(evidence(ROOT / "results/runs" / r["experiment_id"] / "bom.yaml"))
        projection_rows.append(
            {
                "candidate": label,
                "experiment": r["experiment_id"],
                "family": r["topology"]["family"],
                "response_deviation_db": r["checks"]["frequency_response"]["metrics"].get(
                    "response_deviation_db"
                ),
                "current_a": r["checks"]["operating_point"]["metrics"].get("current_a"),
                "installed_count": sum(p["quantity"] for p in bom["physical_parts"]),
                "implementation": "continuous proposal"
                if label.endswith(":continuous")
                else "actual research BOM",
            }
        )
    actual_rows = [r for r in projection_rows if r["implementation"] == "actual research BOM"]
    fronts = {
        "scope": "Model-conditional nominal DC/AC projection only; no architecture qualification",
        "axes_all_minimize": ["response_deviation_db", "current_a", "installed_count"],
        "matching_spec_suite_source_backend": True,
        "actual_bom_projection": pareto(
            actual_rows, ["response_deviation_db", "current_a", "installed_count"]
        ),
        "continuous_proposals_separate_projection": pareto(
            [r for r in projection_rows if r["implementation"] != "actual research BOM"],
            ["response_deviation_db", "current_a"],
        ),
        "excluded_axes": [
            "unvalidated noise",
            "unsupported nonlinear",
            "manufacturing yield",
            "unknown delivered cost",
            "carrier power",
        ],
        "production_front": [],
        "physical_qualified_front": [],
        "rows": projection_rows,
    }
    dump(OUT / "research-pareto.json", fronts)
    dump(
        OUT / "production-front.json",
        {
            "front": [],
            "physical_qualified_front": [],
            "scope": "Requires complete existing qualification, physical evidence and separate sourcing/patent gates",
            "gates_relaxed": False,
        },
    )
    table(OUT / "nominal-metrics.csv", nominal_rows)
    table(OUT / "qualification-coverage.csv", statuses)
    table(OUT / "bom-lines.csv", boms)
    table(OUT / "noise-contributions.csv", contributions)
    table(OUT / "noise-spectra.csv", spectra, sorted({k for r in spectra for k in r}))
    table(OUT / "harmonics-headroom.csv", harmonics)
    dump(
        OUT / "architecture-comparison-001.json",
        {
            "schema_version": 1,
            "date": cfg["date"],
            "scope": cfg["scope"],
            "representatives": details,
            "nominal_metrics": nominal_rows,
            "optimizers": optimizers,
            "paired_endpoints": paired,
            "noise_contributions": contributions,
            "current_procurement_refresh": refresh,
            "sensitivity_scaling": sensitivity,
            "research_pareto": fronts,
            "physical_measurements": [],
            "all_requirement_yield": None,
            "claims_screened": [],
            "production_selection": None,
        },
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout="constrained")
    for row in nominal_rows:
        r = representative_records[row["candidate"]]
        ac, _noise = r["checks"]["frequency_response"]["metrics"], r["checks"]["noise"]["metrics"]
        if not ac:
            continue
        label = row["candidate"].replace("candidate_", "") + " " + row["name"]
        f, gain = np.array(ac["frequency_hz"]), np.array(ac["gain_v_per_pa"])
        axes[0].semilogx(f, 20 * np.log10(gain / abs(at_frequency(f, gain, 1000))), label=label)
        nrows = [s for s in spectra if s["candidate"] == row["candidate"]]
        axes[1].loglog(
            [s["frequency_hz"] for s in nrows],
            [s["electronics_pressure_asd_pa_sqrt_hz"] for s in nrows],
            label=label,
        )
    axes[0].set(
        xlim=(20, 20000),
        ylim=(-10, 24),
        xlabel="Frequency (Hz)",
        ylabel="Response relative to 1 kHz (dB)",
    )
    axes[0].axhline(1, color="gray", ls="--")
    axes[0].axhline(-1, color="gray", ls="--")
    axes[0].axhline(1, color="gray", ls="--")
    axes[0].axhline(-1, color="gray", ls="--")
    axes[1].set(xlabel="Frequency (Hz)", ylabel="Conditional electronics pressure ASD (Pa/√Hz)")
    for ax in axes:
        ax.grid(alpha=0.2)
        ax.legend(fontsize=7)
    fig.suptitle(
        "Recorded models only; semiconductor noise unvalidated; capsule mechanics excluded"
    )
    fig.savefig(OUT / "response-noise.png", dpi=170)
    plt.close(fig)
    fig.savefig(OUT / "response-noise.png", dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4.8), layout="constrained")
    groups = sorted({r["group"] for r in contributions if not r["group"].endswith("(excluded)")})
    x = np.arange(3)
    bottom = np.zeros(3)
    x = np.arange(3)
    bottom = np.zeros(3)
    candidates = ["candidate_0019", "candidate_0023", "candidate_0012"]
    for group in groups:
        values = []
        for candidate in candidates:
            rows = [r for r in contributions if r["candidate"] == candidate and r["group"] == group]
            total = sum(
                r["output_v_rms"] ** 2
                for r in contributions
                if r["candidate"] == candidate and not r["group"].endswith("(excluded)")
            )
            values.append(100 * sum(r["output_v_rms"] ** 2 for r in rows) / total)
        ax.bar(x, values, bottom=bottom, label=group)
        bottom += values
    ax.set(
        xticks=x,
        xticklabels=[c.replace("candidate_", "") for c in candidates],
        ylabel="Unweighted output noise power (%)",
        ylim=(0, 100),
    )
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    ax.set_title("Raw root contributions; model-conditional, 20 Hz–20 kHz")
    fig.savefig(OUT / "noise-contributions.png", dpi=170)
    plt.close(fig)
    fig.savefig(OUT / "noise-contributions.png", dpi=170)
    plt.close(fig)
    region = [
        r
        for r in paired
        if r["scenario"].startswith(
            ("CF_", "CR_", "PAR_", "LEAK_", "CROSS_", "SREF_", "LEN_", "ZIN_")
        )
    ]
    fig, ax = plt.subplots(figsize=(11, 5.5), layout="constrained")
    x = np.arange(len(region))
    width = 0.4
    x = np.arange(len(region))
    width = 0.4
    ax.bar(
        x - width / 2,
        [r["conventional_response_db"] for r in region],
        width,
        label="0019 fixed-bias JFET",
    )
    ax.bar(x + width / 2, [r["servo_response_db"] for r in region], width, label="0023 servo JFET")
    ax.set(
        yscale="log",
        xticks=x,
        xticklabels=[r["scenario"] for r in region],
        ylabel="Response deviation (dB, logarithmic axis)",
    )
    ax.tick_params(axis="x", rotation=65)
    ax.axhline(1, color="gray", ls="--", label="Frozen limit")
    ax.tick_params(axis="x", rotation=65)
    ax.axhline(1, color="gray", ls="--", label="Frozen limit")
    ax.legend(fontsize=8)
    ax.set_title("Shared external endpoints; smaller deviation changes with assumptions")
    ax.legend(fontsize=8)
    ax.set_title("Shared external endpoints; smaller deviation changes with assumptions")
    fig.savefig(OUT / "uncertainty-regions.png", dpi=170)
    plt.close(fig)
    fig.savefig(OUT / "uncertainty-regions.png", dpi=170)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5.3), layout="constrained")
    family_labels = {
        "conventional_jfet": "Fixed-bias JFET",
        "unconventional_jfet": "Servo JFET",
        "no_fet": "BJT charge",
    }
    return {
        **context,
        "actual_rows": actual_rows,
        "ax": ax,
        "bom": bom,
        "family_labels": family_labels,
        "fig": fig,
        "r": r,
    }
