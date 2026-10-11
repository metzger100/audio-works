# SPDX-License-Identifier: GPL-3.0-or-later
"""Replay frozen MOS evidence to protect the control sequence and failure paths."""

import importlib.util
from functools import lru_cache
import sys

import pytest

from meridian_lab.core import ROOT, digest, parse_raw, read_yaml

MODELS = ROOT / "models/semiconductor"
sys.path.insert(0, str(MODELS))
from characterize_mos import mosfet

COHORT = ROOT / "results/device_models/20261009T070419Z_3bd1122a"
ORIGINAL = (
    ROOT
    / "results/verification/20261011T122931Z_d7b00d15/source"
    / "models/semiconductor/characterize_mos.py"
)


@lru_cache
def waveform(path):
    return parse_raw(path)


class Replay:
    def __init__(self, failed, cohort=COHORT, model_id="vishay_2n7002k_ps"):
        self.failed = failed
        self.cohort = cohort
        self.refs = read_yaml(cohort / "source/models/semiconductor/references.yaml")
        self.partial = {}
        self.calls = []
        self.jobs = {
            j["label"]: j
            for j in read_yaml(cohort / "results.json")["jobs"]
            if j["model_id"] == model_id
        }

    def execute(self, model, label, circuit, commands, outputs, temp=25, refine=False):
        # Compare complete requested decks, outputs, temperatures and refinements.
        self.calls.append((model, label, circuit, commands, outputs, temp, refine))
        job = self.jobs[label]
        assert job["temperature_c"] == temp and job["refinement"] == refine
        if label == self.failed or job["status"] != "ok":
            return None
        directory = self.cohort / job["directory"]
        for name in outputs:
            assert digest(directory / name) == job["raw_data_hashes"][name]
        return {name: waveform(directory / name) for name in outputs}


@pytest.mark.parametrize(
    "failed",
    [None, "transfer_25", "transfer_noise_bias_5v", "capacitance_refined_gate", "clipping_1e-06"],
)
def test_mos_control_refactor_preserves_decks_results_and_partial_failures(failed):
    # The oracle is the retained pre-refactor source and its original waveforms.
    spec = importlib.util.spec_from_file_location("original_mos_controls", ORIGINAL)
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    model = {"id": "vishay_2n7002k_ps", "subcircuit": "2N7002K"}
    expected, actual = Replay(failed), Replay(failed)

    def outcome(characterizer, replay):
        try:
            return characterizer(replay, model)
        except ValueError as error:
            return {"error": str(error), "partial": replay.partial}

    assert outcome(mosfet, actual) == outcome(original.mosfet, expected)
    assert actual.calls == expected.calls
    assert actual.partial == expected.partial


@pytest.mark.parametrize("kind,model_id", [("jfet", "jfe150_generic"), ("opa", "opa197_pspice")])
@pytest.mark.parametrize("failed", [None, "transfer_25", "small_25"])
def test_other_device_step_refactors_preserve_original_controls(kind, model_id, failed):
    cohort = ROOT / "results/device_models/20261005T185102Z_95a6dda5"
    path = ORIGINAL.with_name("characterize_" + kind + ".py")
    spec = importlib.util.spec_from_file_location("original_" + kind, path)
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    current = __import__("characterize_" + kind)
    registry = read_yaml(cohort / "source/models/semiconductor/registry.yaml")
    model = next(m for d in registry["devices"] for m in d["models"] if m["id"] == model_id)
    expected, actual = Replay(failed, cohort, model_id), Replay(failed, cohort, model_id)
    assert getattr(current, kind)(actual, model) == getattr(original, kind)(expected, model)
    assert actual.calls == expected.calls
    assert actual.partial == expected.partial
