# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison 001 from immutable records and original local waveforms.

No simulator, candidate, specification, archive or original result is modified.
Run from lab: .venv/bin/python research/compare_architectures.py
"""

from compare_architectures_support import OUT, ROOT, dump, sha


from meridian_lab.bounded import write_markdown


from pathlib import Path
import json
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import sys


def stage(context):
    actual_rows = context["actual_rows"]
    ax = context["ax"]
    bom = context["bom"]
    cfg = context["cfg"]
    cfg_path = context["cfg_path"]
    checked = context["checked"]
    details = context["details"]
    evidence = context["evidence"]
    family = context["family"]
    family_labels = context["family_labels"]
    fig = context["fig"]
    inputs = context["inputs"]
    nominal_rows = context["nominal_rows"]
    optimizers = context["optimizers"]
    part_register = context["part_register"]
    r = context["r"]
    records = context["records"]
    representative_records = context["representative_records"]
    source = context["source"]
    for family in ["conventional_jfet", "unconventional_jfet", "no_fet"]:
        points = [r for r in actual_rows if r["family"] == family]
        ax.scatter(
            [r["current_a"] * 1000 for r in points],
            [r["response_deviation_db"] for r in points],
            label=family_labels[family],
        )
        previous_label_y = 0
        for r in sorted(points, key=lambda r: r["response_deviation_db"]):
            label_y = max(r["response_deviation_db"], previous_label_y * 1.16)
            ax.annotate(
                r["candidate"].replace("candidate_", "") + f" ({r['installed_count']} parts)",
                (r["current_a"] * 1000, r["response_deviation_db"]),
                xytext=(r["current_a"] * 1000 + 0.035, label_y),
                textcoords="data",
                fontsize=7,
                arrowprops={"arrowstyle": "-", "color": "gray", "lw": 0.5},
            )
            previous_label_y = label_y
    ax.set(
        yscale="log",
        xlim=(4.0, 5.45),
        xlabel="Nominal modeled P48 current (mA)",
        ylabel="Response deviation (dB)",
    )
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    ax.set_title("Research projection: actual BOMs, matching cohort; qualified front empty")
    fig.savefig(OUT / "research-pareto.png", dpi=170)
    plt.close(fig)
    fig.savefig(OUT / "research-pareto.png", dpi=170)
    plt.close(fig)

    def num(value, scale=1):
        return "unknown" if value is None else f"{value * scale:.5g}"

    md = [
        "# Generated comparison tables",
        "",
        "Derived from immutable same-cohort records. Values are model-conditional; unknowns remain unknown.",
        "",
        "| Candidate | Current mA | Rail / polarization V | Sensitivity mV/Pa | Response dB | EIN µV / dBA | Zdiff Ω / mismatch % | Active / passive |",
        "| --- | ---: | --- | ---: | ---: | --- | --- | --- |",
    ]
    for r in nominal_rows:
        md.append(
            f"| {r['candidate']} | {num(r['current_a'], 1000)} | {num(r['rail_v'])} / {num(r['simulated_polarization_v'])} | {num(r['sensitivity_v_per_pa'], 1000)} | {num(r['response_deviation_db'])} | {num(r['ein_v_rms_conditional'], 1e6)} / {num(r['electronics_dba_conditional'])} | {num(r['z_diff_max_ohm'])} / {num(r['impedance_mismatch_fraction'], 100)} | {r['active_packages']} / {r['passive_parts']} |"
        )
    md += [
        "",
        "## Complete check statuses",
        "",
        "| Candidate | " + " | ".join(next(iter(representative_records.values()))["checks"]) + " |",
        "| --- | "
        + " | ".join(["---"] * len(next(iter(representative_records.values()))["checks"]))
        + " |",
    ]
    names = list(next(iter(representative_records.values()))["checks"])
    for c, r in representative_records.items():
        md.append("| " + c + " | " + " | ".join(r["checks"][k]["status"] for k in names) + " |")
    md += [
        "",
        "Carrier additionally has an errored carrier_mechanism check; ordinary columns are unsupported periodic analyses.",
        "",
        "## Exact BOM and sourcing observations",
        "",
        "All prices are incomplete catalogue scenarios. Every delivered total is unknown. Each source link retains exact variant, indexed age, MOQ/pack/lead and private-route limits. Nominal values and tolerances below come from the frozen BOM; original errors remain.",
        "",
    ]
    for d in details:
        c = d["candidate"]
        bom = d["bom"]
        md += [
            f"### {c}",
            "",
            f"[Frozen netlist](../../runs/{representative_records[c]['experiment_id']}/circuit.cir) · [Frozen BOM](../../runs/{representative_records[c]['experiment_id']}/bom.yaml) · [Connectivity diagram]({c}_connectivity.svg) · [Every node/element]({c}_connectivity.csv)",
            "",
            "| Exact MPN | Installed qty | Nominal / tolerance | Package | MOQ / retail pack / excess | Indexed stock / age | Net unit EUR scenario |",
            "| --- | ---: | --- | --- | --- | --- | ---: |",
        ]
        for q in bom["quantity_summary"]:
            source = part_register["parts"][q["exact_mpn"]]
            p = next(p for p in bom["physical_parts"] if p["part_id"] == q["exact_mpn"])
            md.append(
                f"| [{q['exact_mpn']}]({source['url']}) | {q['installed_quantity']} | {p['value']} {p['unit']} / {num(p['tolerance_fraction'], 100)}% | {p['package']} | {num(q.get('moq'))} / {num(q.get('retail_pack_size'))} / {num(q.get('unavoidable_pack_excess_scenario'))} | {num(source.get('stock_observed'))} / {source['reported_crawl_age']} | {num(q.get('unit_price_net_eur_observed'))} |"
            )
        md += [
            "",
            f"Priced net subtotal EUR {bom['electronics_cost']['priced_items_net_eur_scenario']:.4f}; confirmed delivered total unknown. Unpriced: {json.dumps(bom['electronics_cost']['unpriced_items'])}.",
            "Full supplier URLs, ratings/technology, lifecycle, exact lead-time fields, intended purchasing quantities and unknown fees are in bom_lines.csv and the machine-readable comparison. Documented dimensions conflict for EEU-FR1J470: frozen catalogue says 12.7mm body, newer primary record says 11.2mm; physical outline/lead allowance needs resolution. Factory packs are not private retail MOQs.",
            "",
        ]
    write_markdown((OUT / "tables.md"), "\n".join(md) + "\n")
    evidence(cfg_path)
    for path in [
        Path(__file__),
        ROOT / "src/meridian_lab/core.py",
        ROOT / "src/meridian_lab/metrics.py",
    ]:
        evidence(path)
    evidence(ROOT / "tests/test_comparison.py")
    outputs = {
        p.name: sha(p)
        for p in sorted(OUT.iterdir())
        if p.is_file() and p.name != "provenance.json" and p.suffix != ".log"
    }
    dump(
        OUT / "provenance.json",
        {
            "schema_version": 1,
            "date": cfg["date"],
            "status": "pass",
            "reporting_versions": {
                "python": sys.version,
                "numpy": np.__version__,
                "matplotlib": matplotlib.__version__,
                "graphviz": subprocess.run(
                    ["dot", "-V"], capture_output=True, text=True, check=True
                ).stderr.strip(),
            },
            "input_sha256": inputs,
            "verified_declared_files": checked,
            "output_sha256": outputs,
            "cohort_spec_sha256": next(iter(records.values()))["spec_sha256"],
            "cohort_suite_sha256": next(iter(records.values()))["suite_sha256"],
            "full_suite_records": len(records),
            "optimization_records": len(optimizers),
            "original_records_modified": False,
            "new_spice_evaluations": 0,
            "independent_backup_complete": False,
        },
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "full_suite_records": len(records),
                "optimization_records": len(optimizers),
                "verified_files": len(checked),
                "outputs": len(outputs),
                "production_front": [],
            }
        )
    )
    return {
        **context,
    }
