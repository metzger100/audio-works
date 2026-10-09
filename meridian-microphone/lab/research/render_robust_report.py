# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive a scoped report from immutable search, full-suite and holdout records."""

import json
from pathlib import Path
import sys
import hashlib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.core import read_yaml


def _text(name):
    return (ROOT / "research/render-robust-report-text" / name).read_text()[:-1]


def load(p):
    return read_yaml(ROOT / p)


def link(id_):
    return f"[{id_}](../results/runs/{id_}/results.json)"


def num(v, scale=1):
    return "unknown" if v is None else f"{v * scale:.4g}"


def render(batch):
    data = load(batch / "evaluation.json")
    search = load(batch / "search.json")["experiments"]
    proposals = {f: load(Path("results/runs") / e / "optimization.json") for f, e in search.items()}
    realization = load(batch / "realization.json")["children"]
    ids = (
        list(data["baseline_experiments"].values())
        + [r["experiment"] for r in data["continuous"].values()]
        + [r["experiment"] for r in data["children"].values()]
    )
    records = {id_: load(Path("results/runs") / id_ / "results.json") for id_ in ids}
    suites = {r["suite_sha256"] for r in records.values()}
    specs = {r["spec_sha256"] for r in records.values()}
    assert len(suites) == len(specs) == 1 and data["source_unchanged"]
    assert not any(r["eligible"] for r in records.values())

    def m(r, check, key):
        return r["checks"][check]["metrics"].get(key)

    text = [
        "# Robust optimization research — 9 October 2026\n",
        _text("literal-0221.txt"),
        _text("literal-0222.txt"),
        "## Prerequisites and scope\n",
        _text("literal-0224.txt"),
        _text("literal-0225.txt"),
        "## Budget, parameters and termination\n",
        _text("literal-1074.txt")
        + str(batch / "plan.json")
        + ") and [search index](../"
        + str(batch / "search.json")
        + ") preserve the actual allocation.\n",
        _text("literal-0228.txt"),
        "| Family | Evaluations / reserved | Scenario attempts / errors | Runtime s | Outcome |\n| --- | ---: | ---: | ---: | --- |",
    ]
    for family, r in proposals.items():
        text.append(
            f"| {family} | {r['evaluations']} / {r['budget_declared_before_run']} | {r['scenario_attempts']} / {r['analysis_errors']} | {r['runtime_s']:.2f} | [{r['termination']}](../results/runs/{r['experiment_id']}/optimization.json) |"
        )
    text += [
        _text("literal-0237.txt"),
        "## Continuous proposals and withheld uncertainty\n",
        _text("literal-0239.txt"),
    ]
    for family, entry in data["continuous"].items():
        base = records[data["baseline_experiments"][family]]
        r = records[entry["experiment"]]
        v = load(Path(entry["validation"]))
        s = v["random_summary"]
        p = proposals[family]
        text.append(
            f"| {family} | {num(m(base, 'frequency_response', 'response_deviation_db'))} | {num(p['best']['design_values']['OUTPUT_C'], 1e6)} | {num(m(r, 'frequency_response', 'response_deviation_db'))} / {num(p['best']['objective']['value'])} | {num(v['corner_summary']['worst_observed'])} | {s['passing']}/{s['samples']}; 95% sampler interval [{num(s['binomial_95_interval'][0])}, {num(s['binomial_95_interval'][1])}] |"
        )
    text += [_text("literal-0257.txt"), _text("literal-0258.txt"), _text("literal-0259.txt")]
    for family, e in data["continuous"].items():
        text.append(
            f"- {family}: {link(data['baseline_experiments'][family])} → {link(e['experiment'])}; [withheld raw-case/interval record](../{e['validation']})."
        )
    text += [
        "\n## Actual BOM combinations and full-suite outcomes\n",
        "[Realizations](../" + str(batch / "realization.json") + _text("literal-0458.txt"),
        _text("literal-0269.txt"),
        _text("literal-0270.txt"),
    ]
    plotted = {}
    for child in realization:
        id_ = child["candidate"]
        entry = data["children"][id_]
        r = records[entry["experiment"]]
        v = load(Path(entry["validation"]))
        b = read_yaml(ROOT / "candidates" / id_ / "bom.yaml")
        nominal = m(r, "frequency_response", "response_deviation_db")
        parent_nom = (
            m(
                records[data["continuous"][child["family"]]["experiment"]],
                "frequency_response",
                "response_deviation_db",
            )
            if child["family"] in data["continuous"]
            else None
        )
        delta = nominal - parent_nom if nominal is not None and parent_nom is not None else None
        text.append(
            f"| [{id_}](../candidates/{id_}/bom.yaml) | {child['family']} | {child.get('count_per_leg', 'series Cf')} | {num(nominal)} | {num(delta)} | {num(v['corner_summary']['worst_observed'])} | {v['random_summary']['passing']} | {sum(p['quantity'] for p in b['physical_parts'])} | {num(b['electronics_cost']['priced_items_net_eur_scenario'])} |"
        )
        if "count_per_leg" in child:
            plotted.setdefault(child["family"], []).append(
                (child["count_per_leg"], nominal, v["corner_summary"]["worst_observed"])
            )
    text += [
        _text("literal-0772.txt") + str(batch / "evaluation.json") + _text("literal-0498.txt"),
        _text("literal-0296.txt"),
        "![Nominal improvement and adverse endpoint failures](robust_optimization_response.png)\n",
        "## Family-specific implications and next experiments\n",
        _text("literal-0299.txt"),
        _text("literal-0300.txt"),
        "3. BJT-only charge: the best tested continuous feedback C is about "
        + num(proposals["no_fet"]["diagnostic_best_infeasible"]["design_values"]["FEEDBACK_C"], 1e9)
        + " nF, with trained deviation "
        + num(proposals["no_fet"]["diagnostic_best_infeasible"]["objective"]["value"])
        + _text("literal-0501.txt"),
        _text("literal-0302.txt"),
        _text("literal-0303.txt"),
        _text("literal-0304.txt"),
        "## Procurement, patent and physical gates\n",
        _text("literal-0306.txt"),
        _text("literal-0307.txt"),
        _text("literal-0308.txt"),
        _text("literal-0309.txt"),
        "## Checks and preservation\n",
        _text("literal-0311.txt"),
        _text("literal-0312.txt"),
    ]
    (ROOT / "research/robust_optimization_report.md").write_text("\n".join(text) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for family, points in plotted.items():
        points.sort()
        label = "Conventional JFET" if family == "conventional_jfet" else "Servo JFET"
        axes[0].plot([p[0] for p in points], [p[1] for p in points], marker="o", label=label)
        axes[1].plot([p[0] for p in points], [p[2] for p in points], marker="o", label=label)
    for ax, title in zip(axes, ["Nominal response screen", "Worst withheld finite scenario"]):
        ax.axhline(1, color="grey", linestyle="--", label="Frozen 1 dB limit")
        ax.set_title(title)
        ax.set_xlabel("47 µF capacitors per output leg")
        ax.set_ylabel("Response deviation (dB)")
        ax.set_xticks([1, 2, 3, 4])
        ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8)
    fig.suptitle("Model-conditional response; every BOM remains unqualified", fontsize=12)
    fig.savefig(ROOT / "research/robust_optimization_response.png", dpi=160)
    plt.close(fig)
    (ROOT / "research/robust_optimization_plot_provenance.json").write_text(
        json.dumps(
            {
                "input_sha256": {
                    str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in [
                        ROOT / batch / "evaluation.json",
                        *[ROOT / "results/runs" / id_ / "results.json" for id_ in ids],
                    ]
                },
                "suite_sha256": list(suites),
                "spec_sha256": list(specs),
                "production_winner": None,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    render(Path(sys.argv[1]))
