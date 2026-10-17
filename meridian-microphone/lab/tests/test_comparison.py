# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent guards for reporting scopes and contribution accounting."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

SPEC = importlib.util.spec_from_file_location(
    "comparison", Path(__file__).resolve().parents[1] / "tools/reporting/compare_architectures.py"
)
comparison = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comparison)


def test_disjoint_noise_power_and_unknown_roots():
    # Independent two-resistor oracle: RMS quadrature, not summed ASD.
    f = np.array([20.0, 20000.0])
    roots = {
        "onoise_r.xdut.rbias": np.array([3.0, 3.0]),
        "onoise_r.xdut.routp": np.array([4.0, 4.0]),
        "onoise_r.xcap.rfront": np.array([12.0, 12.0]),
    }
    groups, spectra, closure = comparison.verify_partition(f, roots, np.array([13.0, 13.0]))
    assert len(groups) == 3 and closure == 0
    assert np.all(spectra["input bias, reset and degeneration"] == 3)
    with pytest.raises(ValueError, match="Unclassified"):
        comparison.noise_group("onoise_r.xdut.unlisted")
    with pytest.raises(ValueError, match="does not close"):
        comparison.verify_partition(f, roots, np.array([14.0, 14.0]))


def test_pareto_missing_axes_and_no_scalar_winner():
    rows = [
        {"candidate": "unknown", "response": None, "current": 0},
        {"candidate": "flat", "response": 1, "current": 5},
        {"candidate": "low_power", "response": 2, "current": 3},
        {"candidate": "dominated", "response": 2, "current": 5},
    ]
    assert comparison.pareto(rows, ["response", "current"]) == ["flat", "low_power"]


def test_cohort_guard_checks_sources_and_backend():
    a = {
        "spec_sha256": "s",
        "suite_sha256": "t",
        "backend": "ngspice",
        "source_manifest": {"a": "h"},
    }
    comparison.require_common([a, dict(a)])
    for mutation in [
        {"source_manifest": {"a": "changed"}},
        {"backend": "physical_measurement"},
        {"spec_sha256": "different"},
        {"suite_sha256": "different"},
    ]:
        with pytest.raises(ValueError, match="cohorts"):
            comparison.require_common([a, {**a, **mutation}])


def test_connectivity_retains_macro_pin_order_and_ideals():
    lines = "VQ_0 rail q0 0\nXQ q0 base emitter BC846B\nR1 emitter g {R}\nEout out g VOL='2*v(mid,g)-v(audio,g)'\n"
    elements = comparison.parse_elements(lines, {"R": 1000})
    assert elements[1]["nodes"] == ["q0", "base", "emitter"]
    assert elements[2]["value_or_model"] == "1000"
    assert elements[3]["kind"] == "E" and elements[3]["nodes"] == ["out", "g"]


def test_realized_filter_inductor_and_disjoint_losses():
    elements = comparison.parse_elements(
        "Lback b cb_ind {L}\nRCbackfilterloss cb_ind cb_loss 0.8\n", {"L": 3e-8}
    )
    assert elements[0]["nodes"] == ["b", "cb_ind"]
    assert elements[0]["value_or_model"] == "3e-08"
    assert comparison.noise_group("onoise_r.xdut.rcbackfilterloss") == "polarization network"
    assert comparison.noise_group("onoise_r.xdut.rcbackfilterinsulation") == "polarization network"


def test_common_cohort_statistics_retain_errors_in_holdout_denominator():
    from comparison_002_tables import finite_summary

    rows = [
        {"candidate": "a", "holdout": True, "status": "pass", "response_deviation_db": 0.2},
        {"candidate": "a", "holdout": True, "status": "fail", "response_deviation_db": 40},
        {"candidate": "a", "holdout": True, "status": "error"},
    ]
    result = next(r for r in finite_summary(rows) if r["holdout"])
    assert result["attempts"] == 3 and result["screens_pass"] == 1
    assert result["error_count"] == 1 and result["worst_response_db"] == 40
    assert result["artificial_screen_fraction"] == 1 / 3
    assert result["all_requirement_yield"] is None
    lo, hi = result["exact_95percent_interval"]
    assert lo < 1 / 3 < hi


def test_input_admittance_uses_actual_servo_return_node():
    from comparison_002_recovery import input_admittance
    from meridian_lab.core import Raw

    f = np.array([1000.0])
    raw = Raw(
        {
            "frequency": f,
            "v(f)": np.array([1.0]),
            "v(mic_g)": np.array([0.0]),
            "v(xdut.servo)": np.array([0.75]),
            "i(v.xdut.vjinput_1)": np.array([2e-9]),
        },
        "AC",
    )
    result = input_admittance(
        raw,
        {"RBIAS_VALUE": 1e9, "CBIASSTRAY_VALUE": 4e-12},
        "Rbias f servo {RBIAS_VALUE}\nCbiasstray f servo {CBIASSTRAY_VALUE}\n",
    )
    assert result["actual_bias_return"] == "servo"
    assert result["real_s"] == pytest.approx(2.25e-9)
    assert result["equivalent_capacitance_f"] == pytest.approx(1e-12, abs=0)


def test_realized_filter_diagram_preserves_elements_within_text_budget(tmp_path, monkeypatch):
    import comparison_common
    from meridian_lab.core import ROOT, read_yaml

    folder = ROOT / "candidates/candidate_0025"
    params = {k: v["default"] for k, v in read_yaml(folder / "topology.yaml")["parameters"].items()}
    elements = comparison.parse_elements((folder / "circuit.cir").read_text(), params)
    monkeypatch.setattr(comparison_common, "OUT", tmp_path)
    comparison_common.diagram("candidate_0025", elements, compact=True)
    payload = (tmp_path / "candidate-0025-connectivity.dot").read_text()
    expected = sum(not (e["kind"] == "V" and e["value_or_model"] == "0") for e in elements)
    assert payload.count("[shape=box,") == expected
    assert "RCbackfilterloss" in payload and "Lbackfilter" in payload
    assert len(payload) <= 15000


def test_manifest_path_tree_retains_all_hashes_under_unchanged_page_limit(tmp_path):
    from compare_architectures_002 import hash_tree
    from meridian_lab.partition import bounded_data
    from meridian_lab.bounded import write_data
    from meridian_lab.core import read_yaml

    records = {
        f"results/runs/experiment_{i % 8}/source/research/long_documentary_subject_name/retained_original_references_with_exact_identity/files/file_{i:05}.py": f"{i:064x}"
        for i in range(12000)
    }
    with pytest.raises(ValueError, match="Too many include pages"):
        bounded_data(records, "manifest.json")
    tree = hash_tree(records)
    path = tmp_path / "manifest.json"
    write_data(path, tree)
    assert read_yaml(path) == tree
    assert all(len(p.read_text()) <= 15000 for p in tmp_path.rglob("*.json"))
    recovered = {}

    def visit(node, parts=()):
        for key, value in node.items():
            if isinstance(value, dict):
                visit(value, (*parts, key))
            else:
                recovered["/".join((*parts, key))] = value

    visit(read_yaml(path))
    assert recovered == records


def test_paired_endpoints_reject_missing_coverage_and_keep_unknowns():
    from comparison_metrics import paired_endpoints

    a = {"scenario": {"id": "same", "parameters": {"LEAK": 1e9}}, "status": "fail"}
    b = {**a, "response_deviation_db": 2.0}
    validation = {"candidate_0019": {"corners": [a]}, "candidate_0023": {"corners": [b]}}
    row = paired_endpoints(validation)[0]
    assert row["conventional_response_db"] is None
    assert row["smaller_response_deviation"] is None
    assert row["production_ranking"] is None
    validation["candidate_0023"]["corners"] = []
    with pytest.raises(ValueError, match="coverage"):
        paired_endpoints(validation)


def test_comparison_stages_accept_only_explicit_inputs_and_write_each_plot_once(
    tmp_path, monkeypatch
):
    from comparison_records import ComparisonData
    import comparison_tables as tables
    import comparison_outputs as outputs
    from matplotlib.figure import Figure

    data = ComparisonData(
        cfg={},
        cfg_path=tmp_path / "config.yaml",
        checked={},
        comparison_flags={},
        evidence=lambda path: path,
        index={"continuous": {}},
        inputs={},
        optimizers={},
        part_register={},
        patent_index={},
        records={},
        refresh={},
        robust_register={},
        validation={},
    )
    candidates = ["candidate_0019", "candidate_0023", "candidate_0012"]
    for candidate in candidates:
        data.contributions.append({"candidate": candidate, "group": "input", "output_v_rms": 1.0})
        data.nominal_rows.append({"candidate": candidate, "name": "Control"})
        data.representative_records[candidate] = {
            "checks": {
                "frequency_response": {
                    "metrics": {
                        "frequency_hz": [20, 1000, 20000],
                        "gain_v_per_pa": [0.02, 0.02, 0.02],
                    }
                },
                "noise": {"metrics": {}},
            }
        }
        data.spectra.extend(
            {"candidate": candidate, "frequency_hz": f, "electronics_pressure_asd_pa_sqrt_hz": 1e-5}
            for f in [20, 1000, 20000]
        )
    data.paired = [
        {"scenario": "LEAK_low", "conventional_response_db": 1.0, "servo_response_db": 2.0}
    ]
    data.actual_rows = [
        {
            "candidate": candidates[0],
            "family": "conventional_jfet",
            "current_a": 0.005,
            "response_deviation_db": 1.0,
            "installed_count": 10,
        }
    ]
    monkeypatch.setattr(tables, "OUT", tmp_path)
    monkeypatch.setattr(outputs, "OUT", tmp_path)
    saved = []
    savefig = Figure.savefig

    def record_save(figure, path, **kwargs):
        saved.append(path.name)
        return savefig(figure, path, **kwargs)

    monkeypatch.setattr(Figure, "savefig", record_save)
    tables.plot_response_noise(data)
    tables.plot_contributions(data)
    tables.plot_regions(data)
    outputs.plot_projection(data)
    assert sorted(saved) == [
        "noise-contributions.png",
        "research-pareto.png",
        "response-noise.png",
        "uncertainty-regions.png",
    ]
    assert all((tmp_path / name).stat().st_size > 0 for name in saved)
