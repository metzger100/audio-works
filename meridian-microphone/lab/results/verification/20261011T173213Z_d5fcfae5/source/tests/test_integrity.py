import numpy as np
import pytest

from meridian_lab import core
from meridian_lab.archive import dominates, graph_features
from meridian_lab.core import ROOT, SimulationError, Simulator, parse_raw, read_yaml
from meridian_lab.metrics import harmonic_spectrum, population_summary


def test_invalid_spice_is_failure_even_with_zero_exit(tmp_path):
    sim = Simulator("fixture_0001", tmp_path)
    with pytest.raises(SimulationError):
        sim.execute(
            "invalid",
            "op\nwrite op.raw all",
            ["op.raw"],
            extra="Binvalid invalid 0 V=unsupported_function(v(f))",
        )
    assert sim.jobs[-1]["status"] == "error"


def test_missing_analysis_never_passes(tmp_path):
    sim = Simulator("fixture_0001", tmp_path)
    with pytest.raises(SimulationError):
        sim.execute("missing", "op", ["missing.raw"])


def test_truncated_raw_rejected(tmp_path):
    sim = Simulator("fixture_0001", tmp_path)
    sim.op_ac()
    source = next(tmp_path.glob("*/ac.raw"))
    broken = tmp_path / "truncated.raw"
    broken.write_text("\n".join(source.read_text().splitlines()[:-10]))
    with pytest.raises(SimulationError):
        parse_raw(broken)


def test_silent_spec_changes_rejected(monkeypatch):
    monkeypatch.setattr(core, "spec_digest", lambda: "unexpected_change")
    with pytest.raises(ValueError, match="Specification changed"):
        core.verify_spec_lock()


def test_no_fundamental_is_not_zero_distortion_pass():
    t = np.linspace(0, 0.1, 10000)
    with pytest.raises(ValueError, match="No measurable fundamental"):
        harmonic_spectrum(t, np.zeros_like(t), 1000)


def test_failed_simulations_stay_in_population_denominator():
    m = population_summary(
        [
            {"status": "pass", "metric": 1},
            {"status": "error", "metric": 1000},
            {"status": "fail", "metric": 2},
        ],
        "metric",
    )
    assert m["observed_pass_fraction"] == pytest.approx(1 / 3)
    assert not m["yield_claim"]
    assert m["worst_observed"] == 2  # Never omit a completed but unfavorable specimen.
    assert m["median"] == pytest.approx(1.5)
    assert m["p95"] > 1.9 and m["p99"] > 1.98
    assert m["metric_sample_count"] == 2 and m["missing_metric_count"] == 1
    assert m["simulation_error_count"] == 1 and m["statistics_include_requirement_failures"]
    allpass = population_summary([{"status": "pass", "metric": 1}] * 16, "metric")
    assert allpass["binomial_95_interval"][0] < 0.8  # 16 successes cannot establish 99.9% yield.


def test_novelty_is_value_independent_and_does_not_grant_dominance(tmp_path):
    a = tmp_path / "a.cir"
    b = tmp_path / "b.cir"
    a.write_text("R1 input output 1000\nC1 output 0 1n\n")
    b.write_text("Rother input output 12345\nCother output 0 500p\n")
    assert graph_features(a)["graph_signature"] == graph_features(b)["graph_signature"]
    base = {"spec_sha256": "a", "suite_sha256": "b", "backend": "ngspice", "metrics": {"noise": 1}}
    challenger = {**base, "metrics": {"noise": 0.5}}
    assert dominates(challenger, base, {"noise": "minimize"})
    assert not dominates(challenger, base, {"noise": "minimize", "yield": "maximize"})
    assert not dominates({**challenger, "spec_sha256": "changed"}, base, {"noise": "minimize"})


def test_ideal_fixture_cannot_be_qualified():
    meta = read_yaml(ROOT / "candidates/fixture_0001/topology.yaml")
    assert (
        meta["ideal_devices"] and not meta["eligible"] and meta["kind"] == "infrastructure_fixture"
    )


def test_spec_numeric_ranges_and_required_measurements():
    capsule = read_yaml(ROOT / "spec/capsule-model.yaml")
    for parameter in capsule["parameters"].values():
        if "nominal" in parameter:
            assert isinstance(parameter["nominal"], (float, int))
        if "range" in parameter:
            lo, hi = parameter["range"]
            assert isinstance(lo, (float, int)) and lo <= hi
    assert capsule["parameters"]["maximum_safe_polarization_v"]["value"] is None
    q = read_yaml(ROOT / "spec/microphone-spec.yaml")["qualification"]
    assert "physical_measurements" in q["evidence_required"] and not q["missing_or_error_is_pass"]


def test_memory_advisory_with_complete_real_spice_output_is_recorded(tmp_path, monkeypatch):
    original = core.subprocess.run

    def with_advisory(*a, **kw):
        run = original(*a, **kw)
        run.stderr += "\nWarning: memory required (374.06 MB), made of\n       38 nodes and approximately 1.29024e6 time steps,\n       is more than the DRAM memory available (248.73 MB)!\n       Swapping data to SSD may slow down the simulation.\n"
        return run

    monkeypatch.setattr(core.subprocess, "run", with_advisory)
    sim = Simulator("fixture_0001", tmp_path)
    data = sim.op_ac()
    assert len(data["ac.raw"]["frequency"]) > 100 and sim.jobs[-1]["status"] == "ok"
    assert len(sim.jobs[-1]["advisories"]) == 1


def test_unknown_warning_is_still_a_failure(tmp_path, monkeypatch):
    original = core.subprocess.run

    def with_warning(*a, **kw):
        run = original(*a, **kw)
        run.stderr += "\nWarning: unrecognized device behavior\n"
        return run

    monkeypatch.setattr(core.subprocess, "run", with_warning)
    with pytest.raises(SimulationError):
        Simulator("fixture_0001", tmp_path).op_ac()


def test_partitioned_candidate_data_and_snapshot_manifest(tmp_path):
    from meridian_lab import cli
    from meridian_lab.bounded import write_data
    from meridian_lab.core import read_yaml

    original = {
        "id": "candidate_9999",
        "population": [{"id": str(i), "notes": "é" * 700} for i in range(40)],
    }
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    write_data(candidate / "topology.yaml", original)
    (candidate / "circuit.cir").write_text(".subckt DUT a b\n.ends DUT\n")
    assert read_yaml(candidate / "topology.yaml") == original
    manifest = cli.implementation_manifest(candidate)
    assert "topology.yaml" in manifest
    assert any(path.startswith("data-pages/") for path in manifest)
    snapshot = tmp_path / "snapshot"
    for path in manifest:
        target = snapshot / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((candidate / path).read_bytes())
    assert read_yaml(snapshot / "topology.yaml") == original
    assert cli.implementation_manifest(snapshot) == manifest


def test_verification_rejects_a_changed_source_snapshot(monkeypatch, tmp_path):
    import sys
    import json
    import pytest
    from meridian_lab import cli
    from meridian_lab.core import digest

    lab = tmp_path / "lab"
    (lab / "src").mkdir(parents=True)
    source = lab / "src/control.py"
    source.write_text("original = True\n")
    (lab / "results/verification").mkdir(parents=True)
    monkeypatch.setattr(cli, "ROOT", lab)
    monkeypatch.setattr(cli, "source_manifest", lambda: {"src/control.py": digest(source)})
    monkeypatch.setattr(cli, "spec_digest", lambda: "unchanged-spec")
    monkeypatch.setattr(cli, "environment_versions", lambda: {"fixture": "controlled"})
    monkeypatch.setattr(sys, "argv", ["lab", "verify"])

    def passing_tests_with_source_change(arguments):
        source.write_text("original = False\n")
        return 0

    monkeypatch.setattr(pytest, "main", passing_tests_with_source_change)
    with pytest.raises(SystemExit) as exit_code:
        cli.main()
    assert exit_code.value.code == 2
    record = next((lab / "results/verification").glob("*/verification.json"))
    value = json.loads(record.read_text())
    assert value["status"] == "fail"
    assert value["source_unchanged"] is False
    assert (record.parent / "source/src/control.py").read_text() == "original = True\n"
