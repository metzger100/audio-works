# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent loaded node equations, RC quadrature and port transformations."""

import numpy as np
from scipy.integrate import quad


def filter_calculation():
    k, t, r, c = 1.380649e-23, 298.15, 1e6, 1e-7
    # Independent analytic integral versus adaptive quadrature, one resistor pole.
    exact = (
        2
        * k
        * t
        / (np.pi * c)
        * (np.arctan(2 * np.pi * r * c * 20000) - np.arctan(2 * np.pi * r * c * 20))
    )
    numeric = quad(
        lambda x: 4 * k * t * r / (1 + (2 * np.pi * x * r * c) ** 2),
        20,
        20000,
        epsabs=1e-30,
        epsrel=1e-10,
    )[0]
    return dict(
        R_ohm=r,
        C_f=c,
        pole_hz=1 / (2 * np.pi * r * c),
        attenuation_20hz_db=float(-10 * np.log10(1 + (2 * np.pi * 20 * r * c) ** 2)),
        resistor_noise_band_v_rms=float(np.sqrt(exact)),
        quadrature_relative_error=abs(numeric / exact - 1),
        energy_30v_j=0.5 * c * 30**2,
        unloaded_1percent_s=-r * c * np.log(0.01),
        interpretation="One-pole Rback diagnostic; actual two-pole/capsule/servo transfer is measured separately",
    )


def dc_oracle(raw, params, servo, filtered, board=None):
    def v(node):
        if node == "g":
            return 0.0
        name = node if node in ["f", "b", "rear", "rail"] else "xdut." + node
        return float(raw.voltage(name, "mic_g")[0].real)

    ig = float(raw["i(v.xdut.vjinput_1)"][0].real)
    leak, bias = params["LEAK"], params["RBIAS_VALUE"]
    rpol = sum(params[f"RPOLAR{i}_VALUE"] for i in range(10)) + params["RBACK_VALUE"]
    ir = params["RCBACKFILTERINSULATION_VALUE"] if filtered else float("inf")
    gb = 1 / board if board else 0
    # Unknowns b,f,rear,u. Actual nonlinear JFE terminal current and supply are
    # retained as boundary observations, not replaced by a Shockley fitted model.
    a = np.zeros((4, 4))
    rhs = np.zeros(4)
    a[0] = [1 / rpol + 2 / leak + 1 / ir, -1 / leak, -1 / leak, 0]
    rhs[0] = v("raw") / rpol
    a[1] = [-1 / leak, 1 / leak + 1 / bias + gb, 0, -1 / bias]
    rhs[1] = -ig
    a[2] = [-1 / leak, 0, 1 / leak + 1 / params["RREAR_VALUE"], 0]
    if servo:
        a[3, 3] = 1
        rhs[3] = v("servo")
    else:
        rt = sum(params[f"RGATETOP{i}_VALUE"] for i in range(3))
        rb = params["RGATEBOTTOM_VALUE"]
        a[3] = [0, -1 / bias, 0, 1 / rt + 1 / rb + 1 / bias]
        rhs[3] = v("rail") / rt
    solved = np.linalg.solve(a, rhs)
    observed = np.array([v("b"), v("f"), v("rear"), v("servo" if servo else "gatebias")])
    source = v("source")
    source_residual = source / params["RSOURCE_VALUE"] + float(raw["i(v.xdut.vjinput_2)"][0].real)
    extra = {}
    if servo:
        rs = sum(params[f"RSERVOSENSE{i}_VALUE"] for i in range(3))
        rr = sum(params[f"RSERVOREF{i}_VALUE"] for i in range(15))
        ibsense = float(raw["i(v.xdut.vqservoerror_1)"][0].real)
        ibref = float(raw["i(v.xdut.vqservoref_1)"][0].real)
        source_residual += (source - v("slow")) / rs
        extra = dict(
            slow_v=v("slow"),
            setpoint_v=v("setpoint"),
            servo_v=v("servo"),
            source_target_unloaded_v=v("rail") / 4,
            source_error_unloaded_v=source - v("rail") / 4,
            sense_base_current_a=ibsense,
            reference_base_current_a=ibref,
            sense_kcl_a=(v("slow") - source) / rs
            + v("slow") / params["RSERVOSENSEGROUND_VALUE"]
            + ibsense,
            reference_kcl_a=(v("setpoint") - v("rail")) / rr
            + v("setpoint") / params["RSERVOREFGROUND_VALUE"]
            + ibref,
            error_vce_v=v("servo") - v("se"),
            reference_vce_v=v("rail") - v("se"),
        )
    ibreg = float(raw["i(v.xdut.vqreg_1)"][0].real)
    extra.update(
        regbase_v=v("regbase"),
        regulator_base_current_a=ibreg,
        regulator_kcl_a=(v("regbase") - v("raw")) / params["RREGTOP_VALUE"]
        + v("regbase") / params["RREGBOTTOM_VALUE"]
        + ibreg,
    )
    return dict(
        independent_linear_solution_v=solved.tolist(),
        simulated_nodes_v=observed.tolist(),
        max_node_error_v=float(np.max(abs(solved - observed))),
        gate_terminal_current_a=ig,
        gate_bias_path_current_a=(v("f") - observed[3]) / bias,
        front_leakage_current_a=(v("b") - v("f")) / leak,
        rear_leakage_current_a=(v("b") - v("rear")) / leak,
        filter_dc_current_a=v("b") / ir,
        board_dc_current_a=v("f") * gb,
        source_current_a=source / params["RSOURCE_VALUE"],
        source_kcl_a=source_residual,
        vds_v=v("rail") - source,
        vgs_v=v("f") - source,
        rail_v=v("rail"),
        polarization_v=v("b") - v("f"),
        terminal_static_limits_pass=(
            -40 <= v("rail") - source <= 40 and -40 <= v("f") - source <= 0.9
        ),
        active_channel_authority=(v("rail") > source and v("f") < source),
        **extra,
    )


def port_metrics(z):
    d = np.array([1, -1])
    cm = np.ones(2)
    diff = np.einsum("i,nij,j->n", d, z, d)
    balance = np.abs(z[:, 0, 0] - z[:, 1, 1]) / ((abs(z[:, 0, 0]) + abs(z[:, 1, 1])) / 2)
    return dict(
        differential_ohm_max=float(max(abs(diff))),
        diagonal_mismatch_fraction_max=float(max(balance)),
        cross_port_ohm_max=float(max(np.maximum(abs(z[:, 0, 1]), abs(z[:, 1, 0])))),
        common_current_to_diff_ohm_max=float(max(abs(np.einsum("i,nij,j->n", d, z, cm)))),
    )


def passive_twoport_oracle():
    # Exact bilateral resistor network; independent nodal inversion and hand
    # determinant. Symmetric series labels cannot force equal diagonal elements.
    gp, gn, gx = 1 / 100, 1 / 130, 1 / 2000
    y = np.array([[gp + gx, -gx], [-gx, gn + gx]])
    det = gp * gn + gx * (gp + gn)
    hand = np.array([[gn + gx, gx], [gx, gp + gx]]) / det
    return dict(
        z_ohm=hand.tolist(),
        max_error=float(np.max(abs(hand - np.linalg.inv(y)))),
        differential_ohm=float(np.array([1, -1]) @ hand @ np.array([1, -1])),
    )
