# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison 001 from immutable records and original local waveforms.

No simulator, candidate, specification, archive or original result is modified.
Run from lab: .venv/bin/python tools/reporting/compare_architectures.py
"""

from comparison_common import OUT, ROOT, diagram, parse_elements, sha, table, verify_partition
from meridian_lab.core import read_yaml
from pathlib import Path
from meridian_lab.metrics import at_frequency
from meridian_lab.metrics import device_noise_totals
from meridian_lab.metrics import integrate_asd
import numpy as np
from meridian_lab.core import parse_raw


def candidate_bom(data, candidate, r, folder):
    bom = read_yaml(data.evidence(folder / "bom.yaml"))
    circuit = data.evidence(folder / "circuit.cir").read_text()
    elements = parse_elements(circuit, r["simulation_configuration"])
    table(OUT / f"{candidate.replace('_', '-')}-connectivity.csv", elements)
    diagram(candidate, elements)
    physical = bom["physical_parts"]
    refs = {e["reference"].lower() for e in elements}
    assert all(
        (p["reference"].lower() in refs or "x" + p["reference"].lower() in refs for p in physical)
    )
    for part in physical:
        source = dict(data.part_register["parts"][part["part_id"]])
        supplemental = data.robust_register["part"] if part["part_id"] == "EEU-FR1J470" else None
        data.boms.append(
            {
                "candidate": candidate,
                **part,
                "procurement_evidence": source,
                "supplemental_capacitor_evidence": supplemental,
            }
        )
    return bom


def nominal_metrics(candidate, choice, r, bom, folder):
    physical = bom["physical_parts"]
    active = sum((p["quantity"] for p in physical if p["unit"] == "device"))
    count = sum((p["quantity"] for p in physical))
    m = lambda check, r=r: r["checks"][check]["metrics"]
    op, ac, noise, port = [
        m(c) for c in ["operating_point", "frequency_response", "noise", "output_impedance"]
    ]
    row = {
        "candidate": candidate,
        "name": choice["name"],
        "family": r["topology"]["family"],
        "experiment": r["experiment_id"],
        "record": str((folder / "results.json").relative_to(ROOT)),
        "current_a": op.get("current_a"),
        "rail_v": op.get("internal_rail_v"),
        "simulated_polarization_v": op.get("polarization_dc_v"),
        "sensitivity_v_per_pa": ac.get("sensitivity_v_per_pa_at_1khz"),
        "response_deviation_db": ac.get("response_deviation_db"),
        "noise_pa_rms": noise.get("electronics_noise_pa_rms"),
        "noise_a_pa_rms": noise.get("electronics_noise_a_pa_rms"),
        "electronics_dba_conditional": noise.get("electronics_noise_dba_conditional"),
        "ein_v_rms_conditional": noise.get("electronics_ein_v_rms_conditional"),
        "output_noise_v_rms": noise.get("electronics_output_v_rms"),
        "z_diff_max_ohm": port.get("output_impedance_ohm"),
        "impedance_mismatch_fraction": port.get("impedance_mismatch_fraction"),
        "loading_loss_db": m("loading").get("loading_loss_db"),
        "startup_settling_s": m("startup").get("settling_to_1percent_s"),
        "startup_status": r["checks"]["startup"]["status"],
        "achieved_rail_settling_s": m("startup").get("settling_to_1percent_s")
        if r["checks"]["startup"]["status"] == "pass"
        else None,
        "hf_peaking_db": m("stability").get("hf_peaking_db"),
        "active_packages": active,
        "passive_parts": count - active,
        "installed_count": count,
        "count_and_power_complete": candidate != "candidate_0013",
        "priced_items_net_eur_scenario": bom["electronics_cost"]["priced_items_net_eur_scenario"],
        "confirmed_delivered_eur": None,
        "eligible": False,
        "physical_qualified": False,
        "patent_screening": "incomplete_phase8",
    }
    return row


def coverage(data, candidate, r):
    for name, check in r["checks"].items():
        data.statuses.append(
            {
                "candidate": candidate,
                "check": name,
                "status": check["status"],
                "reason": check.get("reason"),
                "coverage": check.get("coverage"),
            }
        )
    for metric in [
        "h2_percent",
        "h3_percent",
        "h4_to_h10_percent",
        "thd_percent",
        "clipping_v",
        "headroom_pa_rms",
    ]:
        data.harmonics.append(
            {
                "candidate": candidate,
                "metric": metric,
                "value": None,
                "status": r["checks"]["distortion"]["status"],
                "reason": r["checks"]["distortion"].get("reason"),
            }
        )


def candidate_detail(data, candidate, choice, r, bom, folder):
    patent = data.patent_index[candidate]
    assert patent.get("candidate_version_or_hash", patent.get("circuit_sha256")) == sha(
        folder / "circuit.cir"
    )
    corrections = []
    if candidate == "candidate_0013":
        corrections.append(
            "Original flag describes real outputs; exact descendant netlist has ideal Eoutp/Eoutn. Physical driver, oscillator and mixer classes remain unknown."
        )
    detail = {
        "candidate": candidate,
        "choice": choice,
        "identity": {
            "spec_sha256": r["spec_sha256"],
            "suite_sha256": r["suite_sha256"],
            "backend": r["backend"],
            "implementation_manifest": r["implementation_manifest"],
            "source_manifest": r["source_manifest"],
            "models": r["jobs"][0]["semiconductor_models"],
            "versions": r["versions"],
            "rng_seed": r["rng_seed"],
            "parent_candidates": r["parent_candidates"],
            "parent_experiments": r["parent_experiments"],
        },
        "checks": r["checks"],
        "bom": bom,
        "patent_original_feature_record": patent,
        "patent_comparison_review": data.comparison_flags,
        "patent_metadata_corrections": corrections,
        "claims_and_official_status_evidence": [],
        "prototype_manufacture_build_publication": "hold",
        "validation_summary": {
            k: data.validation[candidate][k]
            for k in ["corner_summary", "random_summary", "coverage"]
        }
        if candidate in data.validation
        else None,
    }
    return detail


def noise_metrics(data, candidate, r, row):
    noise = r["checks"]["noise"]["metrics"]
    if not noise:
        return
    raw_job = next((j for j in r["jobs"] if j["folder"].endswith("_noise")))
    raw = parse_raw(data.evidence(Path(raw_job["folder"]) / "noise.raw"))
    ac_job = next((j for j in r["jobs"] if j["folder"].endswith("_op_ac")))
    acraw = parse_raw(data.evidence(Path(ac_job["folder"]) / "ac.raw"))
    f = raw["frequency"].real
    gain = np.array(
        [abs(at_frequency(acraw["frequency"], acraw.voltage("pp", "pn"), x)) for x in f]
    )
    roots = device_noise_totals(raw)
    groups, densities, closure = verify_partition(f, roots, raw["onoise_spectrum"].real)
    electronics = np.sqrt(
        sum((v**2 for k, v in densities.items() if not k.endswith("(excluded)")), np.zeros_like(f))
    )
    np.testing.assert_allclose(
        electronics, noise["electronics_output_asd_v_per_sqrt_hz"], rtol=1e-10
    )
    np.testing.assert_allclose(
        integrate_asd(f, electronics / gain), row["noise_pa_rms"], rtol=1e-10
    )
    for group, density in densities.items():
        data.contributions.append(
            {
                "candidate": candidate,
                "group": group,
                "output_v_rms": integrate_asd(f, density),
                "pressure_pa_rms_conditional": integrate_asd(f, density / gain),
                "pressure_a_pa_rms_conditional": integrate_asd(f, density / gain, True),
                "vectors": groups[group],
                "power_closure_relative": closure,
            }
        )
    for i, frequency in enumerate(f):
        data.spectra.append(
            {
                "candidate": candidate,
                "frequency_hz": float(frequency),
                "electronics_output_asd_v_sqrt_hz": float(electronics[i]),
                "electronics_pressure_asd_pa_sqrt_hz": float(electronics[i] / gain[i]),
                **{g: float(d[i]) for g, d in densities.items()},
            }
        )


def paired_endpoints(validation):
    va, vb = [validation[c]["corners"] for c in ["candidate_0019", "candidate_0023"]]
    paired = []
    if len(va) != len(vb):
        raise ValueError("Different endpoint coverage; pairing would discard evidence")
    for a, b in zip(va, vb):
        sa, sb = (a["scenario"], b["scenario"])
        assert sa["id"] == sb["id"]
        if sa != sb:
            continue
        values = [a.get("response_deviation_db"), b.get("response_deviation_db")]
        winner = (
            None
            if any((x is None for x in values))
            else "tie"
            if values[0] == values[1]
            else ["candidate_0019", "candidate_0023"][int(values[1] < values[0])]
        )
        paired.append(
            {
                "scenario": sa["id"],
                "parameters": sa.get("parameters", {}),
                "conventional_response_db": values[0],
                "servo_response_db": values[1],
                "conventional_status": a["status"],
                "servo_status": b["status"],
                "smaller_response_deviation": winner,
                "production_ranking": None,
            }
        )
    return paired


def stage(data):
    for candidate, choice in data.cfg["representatives"].items():
        record = next(r for r in data.records.values() if r["candidate_id"] == candidate)
        data.representative_records[candidate] = record
        folder = ROOT / "results/runs" / record["experiment_id"]
        bom = candidate_bom(data, candidate, record, folder)
        row = nominal_metrics(candidate, choice, record, bom, folder)
        data.nominal_rows.append(row)
        coverage(data, candidate, record)
        data.details.append(candidate_detail(data, candidate, choice, record, bom, folder))
        noise_metrics(data, candidate, record, row)
    data.paired = paired_endpoints(data.validation)
    table(OUT / "paired-endpoints.csv", data.paired)
    return data
