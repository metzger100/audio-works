# SPDX-License-Identifier: GPL-3.0-or-later
"""Audit later children and register exactly one planned final-backplate child."""

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "search")]
from meridian_lab.core import read_yaml, digest, write_json, verify_spec_lock
from meridian_lab.bounded import write_data
from mutate import register


def main():
    verify_spec_lock()
    target = ROOT / "research/architectures/focused-children-001.json"
    if target.exists():
        raise ValueError("Audit exists; inspect retained child rather than repeat registration")
    inventory = []
    for folder in sorted((ROOT / "candidates").glob("candidate_*")):
        m = read_yaml(folder / "topology.yaml")
        inventory.append(
            dict(
                id=m["id"],
                parents=m.get("parents", []),
                circuit_sha256=digest(folder / "circuit.cir"),
                final_backplate_filter="Cbackfilter" in (folder / "circuit.cir").read_text(),
                hypothesis=m["hypothesis"],
            )
        )
    existing = [
        r for r in inventory if "candidate_0023" in r["parents"] and r["final_backplate_filter"]
    ]
    partial = (
        existing[0]["id"]
        if len(existing) == 1
        and not (ROOT / "candidates" / existing[0]["id"] / "bom.yaml").exists()
        else None
    )
    if existing and not partial:
        raise ValueError("Existing filtered 0023 descendant; inspect rather than duplicate")
    parent = ROOT / "candidates/candidate_0023"
    mid = partial or "candidate_%04d" % (1 + max(int(r["id"].split("_")[1]) for r in inventory))
    work = ROOT / "search/proposals" / mid
    if not partial:
        work.mkdir(exist_ok=False)
    circuit = (
        (parent / "circuit.cir")
        .read_text()
        .replace(
            ".ends DUT",
            "Cbackfilter cb_loss g {CBACKFILTER_VALUE}\n"
            "RCbackfilterloss cb_ind cb_loss {RCBACKFILTERLOSS_VALUE}\n"
            "Lbackfilter b cb_ind {LBACKFILTER_VALUE}\n"
            "RCbackfilterinsulation b g {RCBACKFILTERINSULATION_VALUE}\n.ends DUT",
        )
    )
    if not partial:
        (work / "circuit.cir").write_text(circuit)
    m = read_yaml(parent / "topology.yaml")
    new = {
        "CBACKFILTER_VALUE": (1e-7, [9e-8, 1.1e-7]),
        "RCBACKFILTERLOSS_VALUE": (0.7957747154594768, [0.01, 0.7957747154594768]),
        "RCBACKFILTERINSULATION_VALUE": (1e11, [1e11, 1e14]),
        "LBACKFILTER_VALUE": (3e-8, [1e-8, 5e-8]),
    }
    for key, (value, bounds) in new.items():
        source = "focused-plan-001 B; WIMA 20C discrete IR/DF anchors; constant law/ESL assumptions"
        m["parameters"][key] = dict(default=value, range=bounds, scale="log", provenance=source)
        m["population"][key] = dict(
            range=bounds,
            distribution="log_uniform" if "INSULATION" in key else "uniform",
            provenance=source,
            interpretation="assumption stress, not a production distribution",
        )
    m["niche"]["reference"] = "single_ended_final_backplate_filtered"
    m["sources"] = [*m["sources"], "S33"]
    m["patent_record"] = "../../research/patents/focused-hypotheses-001.yaml"
    for ref, nodes, key in [
        ("RCbackfilterloss", ["cb_ind", "cb_loss"], "RCBACKFILTERLOSS_VALUE"),
        ("RCbackfilterinsulation", ["b", "g"], "RCBACKFILTERINSULATION_VALUE"),
    ]:
        m["power_resistors"].append(dict(reference=ref, nodes=nodes, parameter=key))
    hypothesis = "One actual 100nF PP filter at final b path may reduce servo backplate noise; test authority, response, startup and loop limitations independently."
    changes = "Add WIMA MKP2D031001F00KSSD at b-g, with explicit IR, series loss and assumed ESL. Preserve all original parts/models and unfiltered parent."
    m["questions"]["hypothesis"] = hypothesis
    m["questions"]["quickest_falsification"] = (
        "Matched retained adverse DC/AC/noise plus unchanged complete suite; no noise or physical eligibility inheritance"
    )
    if partial:
        folder = ROOT / "candidates" / mid
        if (folder / "circuit.cir").read_text() != circuit:
            raise ValueError("Partial child differs; preserve and stop")
        write_json(
            work / "registration-failure.json",
            dict(
                status="error",
                reason="Initial BOM finalization attempted append on inherited string field",
                recovery="Complete missing BOM only; registered circuit and topology remain unchanged",
            ),
        )
    else:
        write_data(work / "topology.yaml", m)
        folder = register(
            "candidate_0023", mid, work / "circuit.cir", work / "topology.yaml", hypothesis, changes
        )
    bom = deepcopy(read_yaml(parent / "bom.yaml"))
    bom.update(candidate=mid, parent_bom="../candidate_0023/bom.yaml", build_ready=False)
    bom["physical_parts"].append(
        dict(
            reference="Cbackfilter",
            part_id="MKP2D031001F00KSSD",
            quantity=1,
            value=1e-7,
            unit="F",
            tolerance_fraction=0.10,
            technology="metallized polypropylene",
            package="radial5x10x7.2mm,5mm pitch",
            ratings=dict(
                voltage_v=100,
                temperature_C=[-55, 100],
                insulation_resistance_min_ohm=1e11,
                dissipation_factor_max_at_1khz_20C=0.0005,
            ),
            source_record="../../research/procurement/focused-parts-001.yaml",
            source_date="2026-10-11",
            manufacturer_document="https://www.wima.de/wp-content/uploads/media/e_WIMA_MKP_2.pdf",
        )
    )
    bom["inherited_simulation_only"] = bom["simulation_only"]
    bom["simulation_only"] = [
        dict(
            reference="RCbackfilterloss/insulation,Lbackfilter",
            purpose="Equivalent film loss/IR/ESL; not three extra physical parts",
            temperature_and_excess_noise="unvalidated",
        )
    ]
    bom["quantity_summary"].append(
        dict(
            exact_mpn="MKP2D031001F00KSSD",
            installed_quantity=1,
            purchase_quantity_scenario=None,
            moq=None,
            retail_pack_size=None,
            confirmed_delivered_eur=None,
        )
    )
    bom["electronics_cost"].update(
        confirmed_delivered_eur=None,
        child_added_price_eur=None,
        scope="Inherited dated partial scenario; child delivered cost and full basket unknown",
    )
    bom["implementation_qualification"] = (
        "Full suite and matched adverse validation required; no inherited qualification"
    )
    write_data(folder / "bom.yaml", bom)
    originals = []
    for c, exp in [
        ("candidate_0019", "20261009T090737Z_40e6a493"),
        ("candidate_0023", "20261009T090930Z_1acba093"),
    ]:
        run = ROOT / "results/runs" / exp
        r = read_yaml(run / "results.json")
        originals.append(
            dict(
                candidate=c,
                experiment=exp,
                results_sha256=digest(run / "results.json"),
                frozen_netlist_sha256=digest(run / "circuit.cir"),
                current_matches=digest(run / "circuit.cir")
                == digest(ROOT / "candidates" / c / "circuit.cir"),
                checks={k: v["status"] for k, v in r["checks"].items()},
                job_count=len(r["jobs"]),
            )
        )
    write_json(
        target,
        dict(
            schema_version=1,
            date="2026-10-11",
            inventory=inventory,
            original_comparison=originals,
            B_child=mid,
            B_parent="candidate_0023",
            child_circuit_sha256=digest(folder / "circuit.cir"),
            C_integrated_children=[],
            A_structural_children=[],
            complete=False,
            reason="Finite execution remains required",
        ),
    )
    print(mid)


if __name__ == "__main__":
    main()
