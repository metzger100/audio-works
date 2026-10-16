# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive bounded tables/plots; keep maintained findings and frozen bytes intact."""

import hashlib
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.bounded import write_csv, write_data, write_markdown


def render(batch):
    inputs = {}

    def load(relative):
        path = ROOT / relative

        # Include every shard that contributes to a resolved report input.
        def reader(name):
            source = path.parent / name
            inputs[str(source.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
            return source.read_text()

        from meridian_lab.data import load as resolve

        return resolve(reader, path.name)

    data = load(batch / "evaluation.json")
    search = load(batch / "search.json")["experiments"]
    proposals = {f: load(Path("results/runs") / e / "optimization.json") for f, e in search.items()}
    children = load(batch / "realization.json")["children"]
    ids = (
        list(data["baseline_experiments"].values())
        + [r["experiment"] for r in data["continuous"].values()]
        + [r["experiment"] for r in data["children"].values()]
    )
    records = {ident: load(Path("results/runs") / ident / "results.json") for ident in ids}
    suites = {r["suite_sha256"] for r in records.values()}
    specs = {r["spec_sha256"] for r in records.values()}
    if len(suites) != 1 or len(specs) != 1 or not data["source_unchanged"]:
        raise ValueError("Incomparable or changed frozen cohort")
    if any(r["eligible"] for r in records.values()):
        raise ValueError("This historical research report cannot promote eligibility")

    def metric(record, check, key):
        return record["checks"][check]["metrics"].get(key)

    budgets = [
        {
            "family": family,
            "evaluations": r["evaluations"],
            "reserved": r["budget_declared_before_run"],
            "scenario_attempts": r["scenario_attempts"],
            "analysis_errors": r["analysis_errors"],
            "runtime_s": r["runtime_s"],
            "termination": r["termination"],
            "experiment": r["experiment_id"],
        }
        for family, r in proposals.items()
    ]
    continuous = []
    for family, entry in data["continuous"].items():
        record = records[entry["experiment"]]
        validation = load(Path(entry["validation"]))
        random = validation["random_summary"]
        continuous.append(
            {
                "family": family,
                "experiment": entry["experiment"],
                "validation": entry["validation"],
                "baseline_response_db": metric(
                    records[data["baseline_experiments"][family]],
                    "frequency_response",
                    "response_deviation_db",
                ),
                "output_c_f": proposals[family]["best"]["design_values"]["OUTPUT_C"],
                "nominal_response_db": metric(
                    record, "frequency_response", "response_deviation_db"
                ),
                "trained_objective_db": proposals[family]["best"]["objective"]["value"],
                "withheld_worst_db": validation["corner_summary"]["worst_observed"],
                "random_passing": random["passing"],
                "random_samples": random["samples"],
                "sampler_95_interval": random["binomial_95_interval"],
            }
        )
    implementations = []
    plotted = {}
    for child in children:
        ident = child["candidate"]
        entry = data["children"][ident]
        record = records[entry["experiment"]]
        validation = load(Path(entry["validation"]))
        bom = load(Path("candidates") / ident / "bom.yaml")
        nominal = metric(record, "frequency_response", "response_deviation_db")
        parent = data["continuous"].get(child["family"])
        parent_nominal = (
            metric(records[parent["experiment"]], "frequency_response", "response_deviation_db")
            if parent
            else None
        )
        implementations.append(
            {
                "candidate": ident,
                "family": child["family"],
                "experiment": entry["experiment"],
                "validation": entry["validation"],
                "count_per_leg": child.get("count_per_leg"),
                "nominal_response_db": nominal,
                "parent_delta_db": nominal - parent_nominal
                if nominal is not None and parent_nominal is not None
                else None,
                "withheld_worst_db": validation["corner_summary"]["worst_observed"],
                "random_passing": validation["random_summary"]["passing"],
                "random_samples": validation["random_summary"]["samples"],
                "physical_parts": sum(p["quantity"] for p in bom["physical_parts"]),
                "net_eur_scenario": bom["electronics_cost"]["priced_items_net_eur_scenario"],
                "delivered_total_eur": None,
                "eligible": record["eligible"],
            }
        )
        if "count_per_leg" in child:
            plotted.setdefault(child["family"], []).append(
                (child["count_per_leg"], nominal, validation["corner_summary"]["worst_observed"])
            )
    output = ROOT / "results/reports/robust-optimization"
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in [
        ("budgets", budgets),
        ("continuous", continuous),
        ("implementations", implementations),
    ]:
        write_csv(output / (name + ".csv"), rows, list(rows[0]))
    write_markdown(
        output / "README.md",
        f"""# Robust optimization: derived evidence

[Maintained findings](../../../research/architectures/optimization/robust-optimization-report.md)
· [Frozen batch](../../optimization_batches/{batch.name}/evaluation.json)

[Budgets](budgets.csv) · [Continuous proposals](continuous.csv) · [Actual BOMs](implementations.csv)

Every implementation is unqualified. Random intervals describe an assumed sampler,
not production yield. Costs are incomplete catalogue scenarios; delivered totals remain unknown.

![Nominal and worst withheld response](response.png)
""",
    )
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for family, points in plotted.items():
        points.sort()
        label = "Conventional JFET" if family == "conventional_jfet" else "Servo JFET"
        for ax, index in zip(axes, [1, 2]):
            ax.plot([p[0] for p in points], [p[index] for p in points], marker="o", label=label)
    for ax, title in zip(axes, ["Nominal response screen", "Worst withheld finite scenario"]):
        ax.axhline(1, color="grey", linestyle="--", label="Frozen 1 dB limit")
        ax.set_title(title)
        ax.set_xlabel("47 µF capacitors per output leg")
        ax.set_ylabel("Response deviation (dB)")
        ax.set_xticks([1, 2, 3, 4])
        ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8)
    fig.suptitle("Model-conditional response; every BOM remains unqualified", fontsize=12)
    fig.savefig(output / "response.png", dpi=160)
    plt.close(fig)
    inputs[str(Path(__file__).relative_to(ROOT))] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    write_data(
        output / "provenance.json",
        {
            "input_sha256": inputs,
            "suite_sha256": sorted(suites),
            "spec_sha256": sorted(specs),
            "production_winner": None,
        },
    )


if __name__ == "__main__":
    render(Path(sys.argv[1]))
