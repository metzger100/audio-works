# SPDX-License-Identifier: GPL-3.0-or-later
"""Guard report output ownership and original-cohort comparisons."""

import importlib.util
import json
from pathlib import Path
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools/reporting"
sys.path.insert(0, str(TOOLS))


def module(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def put(root, relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content) if isinstance(content, dict) else content)
    return path


def test_initial_renderer_preserves_maintained_findings_and_originals(tmp_path, monkeypatch):
    receipt = module("initial_receipt")
    summary = module("initial_summary")
    monkeypatch.setattr(receipt, "ROOT", tmp_path)
    driver = put(tmp_path, "tools/reporting/initial_receipt.py", "driver")
    monkeypatch.setattr(receipt, "__file__", str(driver))
    put(tmp_path, "tools/reporting/render_initial_report.py", "entry")
    maintained = put(
        tmp_path, "research/architectures/initial/phase0-report.md", "Maintained findings\n"
    )
    baseline = put(tmp_path, f"results/runs/{receipt.BASE}/results.json", {"frozen": "baseline"})
    proposal = put(
        tmp_path, f"results/runs/{receipt.PROPOSAL}/results.json", {"frozen": "proposal"}
    )
    verification = put(
        tmp_path, "results/verification/original/verification.json", {"frozen": "verification"}
    )
    before = {p: p.read_bytes() for p in [maintained, baseline, proposal, verification]}
    output = tmp_path / "results/reports"
    output.mkdir()
    context = {
        "b": {"spec_sha256": "spec", "suite_sha256": "suite"},
        "output": output,
        "tests": 22,
        "verification_path": verification,
        "verification_relative": "results/verification/original/verification.json",
        "table": "| Independent metric | 3 | 4 |",
        "checks": "| response | failed | failed |",
    }
    receipt.stage(summary.stage(context))
    assert {p: p.read_bytes() for p in before} == before
    assert "Independent metric" in (output / "initial-summary.md").read_text()
    assert (
        "phase0-report.md"
        not in json.loads((output / "initial-environment.json").read_text())["outputs"]
    )


def test_initial_renderer_selects_original_matching_verification(tmp_path, monkeypatch):
    plots = module("initial_plots")
    monkeypatch.setattr(plots, "ROOT", tmp_path)
    good = {"status": "pass", "source_unchanged": True, "source_manifest": {"input": "original"}}
    expected = put(tmp_path, "results/verification/001/verification.json", good)
    put(
        tmp_path,
        "results/verification/002/verification.json",
        {**good, "source_manifest": {"input": "later"}},
    )
    put(tmp_path, "results/verification/003/verification.json", {**good, "source_unchanged": False})
    assert plots.matching_verification({"source_manifest": good["source_manifest"]}) == expected
    with pytest.raises(StopIteration):
        plots.matching_verification({"source_manifest": {"missing": "cohort"}})


def test_robust_renderer_rejects_incomparable_cohort_before_output(tmp_path, monkeypatch):
    renderer = module("render_robust_report")
    monkeypatch.setattr(renderer, "ROOT", tmp_path)
    put(
        tmp_path,
        "batch/evaluation.json",
        {
            "baseline_experiments": {"a": "one", "b": "two"},
            "continuous": {},
            "children": {},
            "source_unchanged": True,
        },
    )
    put(tmp_path, "batch/search.json", {"experiments": {}})
    put(tmp_path, "batch/realization.json", {"children": []})
    for ident, suite in [("one", "first"), ("two", "different")]:
        put(
            tmp_path,
            f"results/runs/{ident}/results.json",
            {"suite_sha256": suite, "spec_sha256": "same", "eligible": False},
        )
    with pytest.raises(ValueError, match="cohort"):
        renderer.render(Path("batch"))
    assert not (tmp_path / "results/reports").exists()


def test_derived_comparison_preserves_frozen_identities_and_provenance():
    from meridian_lab.core import ROOT, read_yaml

    comparison = read_yaml(
        ROOT / "results/reports/architecture-comparison-001/architecture-comparison-001.json"
    )
    index = read_yaml(
        ROOT / "results/optimization_batches/20261009T090126Z_4735cd2a/evaluation.json"
    )
    experiments = list(index["baseline_experiments"].values()) + [
        value["experiment"] for value in index["children"].values()
    ]
    records = [read_yaml(ROOT / "results/runs" / ident / "results.json") for ident in experiments]
    for detail in comparison["representatives"]:
        record = next(r for r in records if r["candidate_id"] == detail["candidate"])
        for key in (
            "source_manifest",
            "implementation_manifest",
            "parent_candidates",
            "parent_experiments",
        ):
            assert detail["identity"][key] == record[key]
        assert detail["checks"] == record["checks"]


def test_data_writer_replaces_only_prior_owned_pages(tmp_path):
    from meridian_lab.bounded import write_data
    from meridian_lab.data import load

    root = tmp_path / "report.json"
    old = tmp_path / "report-parts/metrics-parts/page-0001.json"
    old.parent.mkdir(parents=True)
    old.write_text('[{"value": "original"}]\n')
    (old.parent.parent / "metrics.json").write_text('{"$include":"metrics-parts/page-0001.json"}\n')
    root.write_text('{"$include":"report-parts/metrics.json"}\n')
    unrelated = old.parent.parent / "other-evidence.json"
    unrelated.write_text('{"original": true}\n')
    before = unrelated.read_bytes()
    value = {"cases": [{"id": f"case-{i}", "value": "é" * 800} for i in range(80)]}
    write_data(root, value)
    assert not old.exists()
    assert not old.parent.exists()
    assert unrelated.read_bytes() == before
    assert load(lambda name: (tmp_path / name).read_text(), "report.json") == value
    pages = set((tmp_path / "report-parts").glob("*.json")) - {unrelated}
    write_data(root, {"current": "compact"})
    assert all(not page.exists() for page in pages)
    assert unrelated.read_bytes() == before
    assert json.loads(root.read_text()) == {"current": "compact"}


def test_data_writer_rejects_unsafe_prior_include_before_writing(tmp_path):
    from meridian_lab.bounded import write_data

    root = tmp_path / "report.json"
    root.write_text('{"$include":"../outside.json"}\n')
    before = root.read_bytes()
    with pytest.raises(ValueError, match="Unsafe prior data include"):
        write_data(root, {"replacement": True})
    assert root.read_bytes() == before
