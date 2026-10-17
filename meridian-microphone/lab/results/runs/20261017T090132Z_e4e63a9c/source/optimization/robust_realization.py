# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit phases keep source cohorts idle/stable between evaluations.

search -> realize -> evaluate; each phase writes a new record, refuses overwrite.
"""

from copy import deepcopy
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "search"))
from meridian_lab.core import ROOT, digest, read_yaml, write_json
from first_batch_children import clone, finish
from first_batch_realization import c0g_realization


from meridian_lab.bounded import write_data


def output_child(parent, number, count, continuous_experiment):
    a = clone(parent, number, f"{count} parallel output capacitors per leg, explicit loss/leakage")
    for leg, from_, to_ in [("p", "p", "cp"), ("n", "n", "cn")]:
        name = "Cout" + leg
        a.lines = [l for l in a.lines if not l.startswith(name + " ")]
        a.bom = [p for p in a.bom if p["reference"] != name]
        a.meta["parameters"].pop(name.upper() + "_VALUE")
        a.meta["population"].pop(name.upper() + "_VALUE")
        for i in range(count):
            c = name + str(i)
            internal = c.lower() + "_loss"
            a.capacitor(c, internal, to_, 47e-6)
            a.resistor(
                "R" + c + "loss", from_, internal, 0.09 / (2 * np.pi * 120 * 47e-6), parasitic=True
            )
            a.resistor("R" + c + "leak", from_, to_, 1e14, parasitic=True)
            for suffix, range_, dist in [
                ("loss", [0.01, 0.09 / (2 * np.pi * 120 * 47e-6)], "uniform"),
                ("leak", [63 / 29.6e-6, 1e14], "log_uniform"),
            ]:
                key = ("R" + c + suffix).upper() + "_VALUE"
                a.meta["parameters"][key].update(
                    range=range_,
                    provenance="S26 Panasonic FR-A DF/leakage anchor; explicit constant-law scenario only, not validated broadband/temperature/noise behavior",
                )
                a.meta["population"][key].update(
                    range=range_,
                    distribution=dist,
                    provenance=a.meta["parameters"][key]["provenance"],
                )
    a.meta["continuous_parent_experiment"] = continuous_experiment
    a.meta["questions"]["hypothesis"] = (
        f"{count} parallel documented 47uF output parts per leg may retain continuous LF benefit under independent/correlated capacitance, leakage and loss stress; no source/model/production qualification follows."
    )
    a.meta["patent_record"] = "../../research/patents/robust_optimization_2026-10-09.yaml"
    finish(
        a,
        "Realize output capacitance with actual parallel EEU-FR1J470 parts; count each part and add individually recorded series-loss and leakage controls. Preserve conversion and fixed bias; all gates held. Complete suite and holdout scenarios required.",
    )
    folder = ROOT / "candidates" / a.id
    b = read_yaml(folder / "bom.yaml")
    parent_bom = read_yaml(ROOT / "candidates" / parent / "bom.yaml")
    template = next(p for p in parent_bom["physical_parts"] if p["part_id"] == "EEU-FR1J470")
    for p in b["physical_parts"]:
        if p["part_id"] == "EEU-FR1J470":
            ref = p["reference"]
            p.update(deepcopy(template), reference=ref)
            p["source_record"] = "../../research/procurement/robust_parts_2026-10-09.yaml#part"
    delta = 2 * (count - 1)
    for row in b["quantity_summary"]:
        if row["exact_mpn"] == "EEU-FR1J470":
            row["installed_quantity"] += delta
            row["purchase_quantity_scenario"] += delta
            row["extended_net_eur_scenario"] = row["installed_quantity"] * 0.4
    b["electronics_cost"]["priced_items_net_eur_scenario"] = round(
        parent_bom["electronics_cost"]["priced_items_net_eur_scenario"] + 0.4 * delta, 4
    )
    b["electronics_cost"]["priced_items_vat_inclusive_eur_scenario"] = round(
        b["electronics_cost"]["priced_items_net_eur_scenario"] * 1.19, 6
    )
    b.update(
        continuous_parent_experiment=continuous_experiment,
        parallel_output_count_per_leg=count,
        implementation_qualification="Full suite/holdouts pending; ESR/leakage are explicit source-anchored stress assumptions; cap nonlinear/frequency/temperature noise and layout unknown",
        substitutes_qualified=[],
        build_ready=False,
    )
    write_data(folder / "bom.yaml", b)
    return a.id


def realize(batch):
    searches = read_yaml(batch / "search.json")["experiments"]
    children = []
    for family, first in [("conventional_jfet", 16), ("unconventional_jfet", 20)]:
        experiment = searches[family]
        proposal = read_yaml(ROOT / "results/runs" / experiment / "optimization.json")
        if proposal["best"] is None:
            continue
        for count in range(1, 5):
            children.append(
                {
                    "candidate": output_child(
                        proposal["candidate_id"], first + count - 1, count, experiment
                    ),
                    "parent": proposal["candidate_id"],
                    "continuous_parent_experiment": experiment,
                    "count_per_leg": count,
                    "family": family,
                }
            )
    # One structural no-FET hypothesis, within the explicitly reserved slot.
    a = clone("candidate_0012", 24, "BJT series feedback capacitance child")
    a.lines = [l.replace("Cfeedback outa f", "Cfeedback outa feedback_series") for l in a.lines]
    a.capacitor("Cfeedbackseries", "feedback_series", "f", 1e-10)
    c0g_realization(a)
    a.meta["questions"]["hypothesis"] = (
        "A series 100pF C0G caps the effective feedback capacitance instead of an unavailable arbitrary optimized value; unchanged 500kohm DC reset retains BJT base-current authority. It may expose whether the frequency/noise limitation is reset conductance or large feedback C."
    )
    a.meta["patent_record"] = "../../research/patents/robust_optimization_2026-10-09.yaml"
    finish(
        a,
        "Add sourced 100pF C0G in series with preserved 100nF feedback; include separately documented IR/DF controls; unchanged DC reset/device bias, no trimming. A structural child, not a family rescue or a qualified substitute.",
    )
    bpath = ROOT / "candidates" / a.id / "bom.yaml"
    b = read_yaml(bpath)
    part_record = read_yaml(ROOT / "research/procurement/architecture_parts_2026-10-09.yaml")[
        "parts"
    ]["CC0603JRNPO0BN101"]
    for part in b["physical_parts"]:
        if part["reference"] == "Cfeedbackseries":
            part.update(
                technology=part_record["technology"],
                package=part_record["package"],
                ratings=part_record["ratings"],
                source_record="../../research/procurement/architecture_parts_2026-10-09.yaml#parts/CC0603JRNPO0BN101",
                source_date="2026-10-09",
                manufacturer_document=part_record["manufacturer_document"],
            )
    b["quantity_summary"].append(
        {
            "exact_mpn": "CC0603JRNPO0BN101",
            "installed_quantity": 1,
            "purchase_quantity_scenario": None,
            "moq": None,
            "retail_pack_size": None,
            "unavoidable_pack_excess_scenario": None,
            "unit_price_net_eur_observed": 0.08,
            "extended_net_eur_scenario": 0.08,
            "seller": "DigiKey Germany",
            "evidence_limit": "Parent register exact private MOQ/dispatch unresolved",
        }
    )
    b["electronics_cost"]["priced_items_net_eur_scenario"] += 0.08
    b["electronics_cost"]["priced_items_vat_inclusive_eur_scenario"] = round(
        b["electronics_cost"]["priced_items_net_eur_scenario"] * 1.19, 6
    )
    b.update(
        build_ready=False,
        implementation_qualification="Series feedback C0G child unqualified; full suite required, missing nonlinear/noise/process/loss laws remain",
    )
    write_data(bpath, b)
    children.append(
        {
            "candidate": a.id,
            "parent": "candidate_0012",
            "family": "no_fet",
            "structural_slot": "underexplored",
        }
    )
    write_json(
        batch / "realization.json",
        {
            "children": children,
            "hypothesis_budget_used": {"improve": 8, "underexplored": 1, "assumption_breaking": 2},
            "new_concepts_used": 0,
            "held_tasks": {"underexplored": 4, "new_concepts": 3},
            "note": "Eight discrete combinations, two common leakage/loss extremes. Validation uses remaining two improve slots. Reservations do not imply 20 simulations performed.",
        },
    )
    flags = []
    for child in children:
        meta = read_yaml(ROOT / "candidates" / child["candidate"] / "topology.yaml")
        flags.append(
            {
                **child,
                "circuit_sha256": digest(ROOT / "candidates" / child["candidate"] / "circuit.cir"),
                "state": "unscreened_no_clearance",
                "parent_flags": "first_architecture_batch_2026-10-09.yaml",
                "features": [
                    "fixed P48 common-mode power extraction",
                    "differential real-device output",
                    "capacitor combination/loss/leakage realization",
                    meta["niche"]["feedback"],
                ],
                "change_review": "Values and parallel/series passive substitutions do not establish a design-around; preserve all prior feature holds and recheck actual claims before affected gates.",
                "claims": None,
                "official_status": None,
                "territories": ["DE", "applicable EP states"],
                "prototype_gate": "hold",
                "manufacture_gate": "hold",
                "build_publication_gate": "hold",
            }
        )
    write_data(
        ROOT / "research/patents/robust_optimization_2026-10-09.yaml",
        {
            "schema_version": 1,
            "date": "2026-10-09",
            "scope": "Internal optimization/realization research; no selection or publication",
            "candidates": flags,
            "professional_review": "Material claim/status uncertainty before any held gate; no legal non-infringement guarantee",
        },
    )
    print(str(batch / "realization.json"))
