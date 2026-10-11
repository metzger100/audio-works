# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent amplitude, window, drift and timeout preservation regressions."""

import signal
import subprocess
import sys

import numpy as np
import pytest

from meridian_lab.core import ROOT, Simulator, SimulationError
from meridian_lab.nonlinear import settled_spectrum

sys.path.insert(0, str(ROOT / "tools/controls"))
from prerequisite_math import synthetic, synthetic_rms


@pytest.mark.parametrize("phase", [0, 0.37, 1.91])
@pytest.mark.parametrize("samples", [128, 256, 512])
def test_h1_h10_against_product_to_sum_oracle(phase, samples):
    rng = np.random.default_rng(34047)
    t = np.r_[0, np.sort(rng.uniform(0, 0.064, 64000)), 0.064]
    h = settled_spectrum(t, synthetic(t, phase), 1000, 0.032, samples_per_cycle=samples)
    assert h["harmonics_v_rms"] == pytest.approx(synthetic_rms(), rel=1e-5, abs=1e-10)
    expected = 100 * np.linalg.norm(synthetic_rms()[1:]) / synthetic_rms()[0]
    assert h["thd_percent"] == pytest.approx(expected, rel=1e-7)
    assert h["output_peak_v"] > h["harmonics_v_rms"][0]


def test_stable_fundamental_does_not_hide_drifting_h2_or_dc():
    t = np.linspace(0, 0.064, 64001)
    angle = 2 * np.pi * 1000 * t
    for y in [np.sin(angle) + 2 * t * np.sin(2 * angle), np.sin(angle) + 2 * t]:
        with pytest.raises(ValueError, match="Unsettled"):
            settled_spectrum(t, y, 1000, 0.032)


def test_partial_or_startup_discarded_waveforms_are_rejected():
    for t, reason in [
        (np.linspace(0.032, 0.064, 10000), "Startup"),
        (np.linspace(0, 0.050, 10000), "Two complete"),
    ]:
        with pytest.raises(ValueError, match=reason):
            settled_spectrum(t, np.sin(2 * np.pi * 1000 * t), 1000, 0.032)


def test_headroom_refinement_rejects_h2_drift_with_stable_fundamental():
    from meridian_lab.qualification_signal import headroom, thresholds

    t = np.linspace(0, 0.54, 138241)
    angle = 2 * np.pi * 1000 * t

    class Wave:
        def __getitem__(self, key):
            assert key == "time"
            return t

        def voltage(self, *nodes):
            return np.sin(angle) + 2 * t * np.sin(2 * angle)

    class Sim:
        def transient(self, *args, **kwargs):
            return Wave()

    limit = thresholds()["thd_at_135db_percent"]["value"]
    rows = [
        dict(frequency_hz=1000, pressure_pa_rms=level, thd_percent=thd)
        for level, thd in [(1, limit / 2), (2, limit * 2)]
    ]
    ctx = dict(checks=dict(distortion=dict(metrics=dict(cases=rows))), polarization_dc_v=40)
    with pytest.raises(SimulationError, match="Unsettled"):
        headroom(Sim(), ctx)


def test_timeout_retains_complete_solver_prefix_and_kills_group(tmp_path, monkeypatch):
    calls = []

    class TimedProcess:
        pid = 876543

        def __init__(self, *args, **kwargs):
            assert kwargs["start_new_session"]

        def communicate(self, timeout=None):
            calls.append(timeout)
            if timeout is not None:
                raise subprocess.TimeoutExpired("test", timeout)
            return "original stdout before timeout", "original stderr before timeout"

    monkeypatch.setattr(subprocess, "Popen", TimedProcess)
    kills = []
    monkeypatch.setattr("meridian_lab.core.os.killpg", lambda pid, sig: kills.append((pid, sig)))
    sim = Simulator("fixture_0001", tmp_path)
    with pytest.raises(SimulationError, match="60s"):
        sim.execute("timeout", "op", ["op.raw"])
    log = (tmp_path / "0001_timeout/simulator.log").read_text()
    assert "original stdout" in log and "original stderr" in log
    assert calls == [60, None] and kills == [(876543, signal.SIGKILL)]
    assert sim.jobs[0]["status"] == "error"


def test_transient_keeps_startup_without_changing_duration_or_timestep(tmp_path, monkeypatch):
    sim = Simulator("fixture_0001", tmp_path)
    captured = []

    def execute(label, commands, files, overrides):
        captured.append(commands)
        return {"tran.raw": object()}

    monkeypatch.setattr(sim, "execute", execute)
    sim.transient(1000, 1, settling=0.5)
    tokens = captured[0].splitlines()[0].split()
    assert float(tokens[2]) == 0.54
    assert float(tokens[3]) == 0
    assert float(tokens[1]) == float(tokens[4]) == 1 / 1000 / 256
