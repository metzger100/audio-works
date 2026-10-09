from __future__ import annotations

from itertools import product
import numpy as np

from .core import ROOT, SimulationError, read_yaml
from .metrics import at_frequency, db, population_summary


def result(status, metrics=None, reason=None, coverage=None):
    return {"status": status, "metrics": metrics or {}, "reason": reason, "coverage": coverage}


def thresholds():
    return read_yaml(ROOT / "spec/microphone-spec.yaml")["requirements"]


def scenario_ranges():
    c = read_yaml(ROOT / "spec/capsule-model.yaml")["parameters"]
    d = read_yaml(ROOT / "spec/design-constraints.yaml")
    p = d["power"]
    e = d["environment"]
    return {
        "VS": p["supply_v"]["range"],
        "FT": p["feed_absolute_tolerance_fraction"]["range"],
        "FM": p["feed_pair_mismatch_fraction"]["range"],
        "CF": c["front_capacitance_f"]["range"],
        "CR": c["rear_capacitance_f"]["range"],
        "LEAK": c["leakage_resistance_ohm"]["range"],
        "PAR": c["parasitic_to_case_f"]["range"],
        "SREF": c["sensitivity_at_reference_v_per_pa"]["range"],
        "LEN": e["cable_length_m"]["range"],
        "RW": e["cable_resistance_ohm_per_m_per_conductor"]["range"],
        "CD": e["cable_direct_capacitance_f_per_m"]["range"],
        "CS": e["cable_each_leg_to_shield_f_per_m"]["range"],
        "ZIN": e["preamp_differential_load_ohm"]["range"],
        "ZM": e["preamp_leg_mismatch_fraction"]["range"],
        "TEMP": e["temperature_c"]["range"],
    }


def current(raw):
    return float(-raw["i(v.xenv.vphantom)"][0].real)


def response(raw):
    f = raw["frequency"].real
    gain = raw.voltage("pp", "pn")
    ref = abs(at_frequency(f, gain, 1000))
    if ref < 1e-9:
        raise SimulationError("Missing useful pressure-to-output transfer")
    mask = (f >= 20) & (f <= 20000)
    # Include exact band edges; logarithmic sweep need not land on 20 Hz or 20 kHz.
    frequencies = np.r_[20, f[mask], 20000]
    band = np.array([at_frequency(f, gain, x) for x in frequencies])
    relative = 20 * np.log10(np.maximum(np.abs(band) / ref, 1e-300))
    return {
        "sensitivity_v_per_pa_at_1khz": float(ref),
        "response_deviation_db": float(np.max(np.abs(relative))),
        "lf_db": db(at_frequency(f, gain, 20) / ref),
        "hf_db": db(at_frequency(f, gain, 20000) / ref),
        "phase_1khz_deg": float(np.angle(at_frequency(f, gain, 1000), deg=True)),
        "frequency_hz": f.tolist(),
        "gain_v_per_pa": abs(gain).tolist(),
        "phase_deg": np.rad2deg(np.unwrap(np.angle(gain))).tolist(),
    }


def operating_point(sim, ctx):
    raw = ctx["nominal"]["op.raw"]
    p = sim.params
    i = current(raw)
    vp = float(raw.voltage("p", "mic_g")[0])
    vn = float(raw.voltage("n", "mic_g")[0])
    rail = float(raw.voltage("rail", "mic_g")[0])
    pol = float(raw.voltage("b", "f")[0])
    xp = float(raw["v(xenv.xp)"][0])
    xn = float(raw["v(xenv.xn)"][0])
    ip = (p["VS"] - xp) / (6800 * (1 + p["FT"]) * (1 + p["FM"] / 2))
    inn = (p["VS"] - xn) / (6800 * (1 + p["FT"]) * (1 - p["FM"] / 2))
    mismatch = abs(ip - inn) / max(abs((ip + inn) / 2), 1e-20)
    ok = 0 < i <= thresholds()["current_max_a"]["value"] and 0 < rail < p["VS"] and pol > 0
    ctx["polarization_dc_v"] = pol
    m = {
        "current_a": i,
        "current_per_leg_a": [ip, inn],
        "conductor_current_mismatch_fraction": mismatch,
        "mic_terminal_v": [vp, vn],
        "internal_rail_v": rail,
        "polarization_dc_v": pol,
        "supplied_power_w": p["VS"] * i,
        "terminal_power_w": vp * ip + vn * inn,
        "device_power_qualification": "pending part ratings/SOA; ideal fixture energy not accounted",
        "safe_capsule_bias": "unknown; simulated voltage is not approved for hardware",
    }
    if sim.meta.get("power_devices"):
        from .architectures import dc_accounting

        m["dc_energy_accounting"] = dc_accounting(sim, raw, m["terminal_power_w"])
        m["device_power_qualification"] = (
            "Terminal currents/powers recorded; thermal/SOA and vendor power-block fidelity remain unqualified"
        )
        if m["dc_energy_accounting"]["relative_residual"] > 1e-4:
            ok = False
    return result(
        "pass" if ok else "fail",
        m,
        coverage="DC feasibility screen; device safe operating area remains a separate evidence gate",
    )


def frequency_response(sim, ctx):
    m = response(ctx["nominal"]["ac.raw"])
    return result(
        "pass"
        if m["response_deviation_db"] <= thresholds()["electronics_response_db"]["value"]
        else "fail",
        m,
        coverage="1 Hz to 10 MHz, nominal environment; electrical model only",
    )


def phantom_supply(sim, ctx):
    ranges = scenario_ranges()
    rows = [
        screen(sim, "p48_corner", dict(VS=v, FT=t, FM=m))
        for v, t, m in product(ranges["VS"], ranges["FT"], ranges["FM"])
    ]
    return result(
        "pass" if all(x["status"] == "pass" for x in rows) else "fail",
        {"cases": rows},
        coverage="8 DC/AC supply/feed extremes. Noise/distortion/abuse at corners pending.",
    )


def temperature(sim, ctx):
    lo, hi = scenario_ranges()["TEMP"]
    rows = [screen(sim, "temperature", {"TEMP": t}) for t in [lo, sim.params["TEMP"], hi]]
    return result(
        "pass" if all(x["status"] == "pass" for x in rows) else "fail",
        {"cases": rows, "capsule_temperature_law_known": False},
        coverage="3 electrical temperatures; no validated mechanical or leakage temperature law",
    )


def semiconductor_corners(sim, ctx):
    corners = sim.meta.get("device_corners", [])
    if not corners:
        return result(
            "incomplete",
            reason="No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield",
        )
    rows = [screen(sim, "device_corner", r["parameters"]) for r in corners]
    qualified = all(
        r.get("provenance") in {"manufacturer_bound", "measured_bound"} for r in corners
    )
    return result(
        "pass"
        if qualified and all(x["status"] == "pass" for x in rows)
        else "fail"
        if any(x["status"] != "pass" for x in rows)
        else "incomplete",
        {"cases": rows},
        coverage="DC/AC only; full noise/distortion/stability corners pending",
    )


def monte_carlo(sim, ctx):
    rng = np.random.default_rng(ctx["seed"])
    rows = []
    for _ in range(ctx["samples"]):
        # Scenario uncertainty is not a production population. All distributions are explicit here.
        overrides = {
            k: float(np.exp(rng.uniform(np.log(lo), np.log(hi))))
            if k == "LEAK"
            else float(rng.uniform(lo, hi))
            for k, (lo, hi) in scenario_ranges().items()
        }
        for k, definition in sim.meta.get("population", {}).items():
            lo, hi = definition["range"]
            if definition["distribution"] == "uniform":
                overrides[k] = float(rng.uniform(lo, hi))
            elif definition["distribution"] == "log_uniform":
                overrides[k] = float(np.exp(rng.uniform(np.log(lo), np.log(hi))))
            else:
                raise ValueError("Unsupported or undocumented population distribution")
        rows.append(screen(sim, "monte_carlo", overrides))
    summary = population_summary(rows, "response_deviation_db")
    summary.update(
        seed=ctx["seed"],
        distributions="Independent uniform scenario ranges; leakage log-uniform; not manufacturer distributions",
        cases=rows,
        all_requirements_pass_fraction=None,
        screened_requirements=["current", "positive_polarization", "frequency_response"],
    )
    return result(
        "incomplete",
        summary,
        reason="Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established",
    )


from .qualification_signal import noise as noise, distortion as distortion, headroom as headroom
from .qualification_ports import (
    port_matrix as port_matrix,
    output_impedance as output_impedance,
    balance as balance,
    screen as screen,
    loading as loading,
    startup as startup,
    stability as stability,
)


CHECKS = {
    name: globals()[name]
    for name in [
        "operating_point",
        "frequency_response",
        "noise",
        "distortion",
        "headroom",
        "output_impedance",
        "balance",
        "phantom_supply",
        "temperature",
        "semiconductor_corners",
        "monte_carlo",
        "loading",
        "startup",
        "stability",
    ]
}


def evaluate(sim, seed=34047, samples=16, checks=None):
    selected = checks or list(CHECKS)
    ctx = {"seed": seed, "samples": samples, "checks": {}}
    try:
        ctx["nominal"] = sim.execute("operating_point", "op\nwrite op.raw all", ["op.raw"])
    except Exception as exc:
        return {n: result("error", reason=str(exc)) for n in selected}
    # Establish DC/current/energy before any transfer or noise analysis, including
    # selected subsets that need actual polarization for their interpretation.
    try:
        dc = operating_point(sim, ctx)
    except Exception as exc:
        return {n: result("error", reason=f"{type(exc).__name__}: {exc}") for n in selected}
    if "operating_point" in selected:
        ctx["checks"]["operating_point"] = dc
    if selected == ["operating_point"]:
        return ctx["checks"]
    if sim.meta.get("analysis_domain") == "periodic_mechanism_control":
        from .architectures import carrier_control

        try:
            control = carrier_control(sim)
            ctx["checks"]["carrier_mechanism"] = result(
                "incomplete",
                control,
                reason="Deterministic control; periodic noise/physical oscillator/mixer remain unsupported",
            )
        except Exception as exc:
            ctx["checks"]["carrier_mechanism"] = result(
                "error", reason=f"{type(exc).__name__}: {exc}"
            )
        for name in selected:
            if name != "operating_point":
                ctx["checks"][name] = result(
                    "incomplete",
                    reason="Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior",
                )
        return ctx["checks"]
    try:
        ctx["nominal"].update(sim.op_ac())
    except Exception as exc:
        for n in selected:
            if n != "operating_point":
                ctx["checks"][n] = result("error", reason=str(exc))
        return ctx["checks"]
    for name in selected:
        if name == "operating_point":
            continue
        try:
            ctx["checks"][name] = CHECKS[name](sim, ctx)
        except Exception as exc:
            ctx["checks"][name] = result("error", reason=f"{type(exc).__name__}: {exc}")
    return ctx["checks"]
