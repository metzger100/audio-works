# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent KCL oracles and finite isolated mechanisms, never device ratings."""

import numpy as np

from meridian_lab.metrics import at_frequency


def charge_transfer(f, cf, rf, ct, gain=10, pole=100000):
    s = 2j * np.pi * f
    a = gain / (1 + s / (2 * np.pi * pole))
    yf = 1 / rf + s * cf
    return -a * s / (s * ct + (1 + a) * yf)


def bjt_oracles(exp):
    rows = []
    for cf in [1e-7, 1 / (1 / 1e-7 + 1 / 1e-10)]:
        for rf in [5e5, 1e8]:
            for capsule in [45e-12, 70e-12, 100e-12]:
                ct = capsule + 2e-12
                circuit = (
                    f"Icharge 0 f AC 1\nCt f 0 {ct}\nRf out f {rf}\nCf out f {cf}\n"
                    "Ee pre 0 f 0 -10\nRp pre pole 1k\nCp pole 0 1.5915494309189535n\nEb out 0 pole 0 1"
                )
                label = f"charge_{cf:.8g}_{rf:.8g}_{capsule:.8g}"
                raw = exp.execute(
                    dict(id="charge_oracle"),
                    label,
                    circuit,
                    "ac dec 64 1 1Meg\nwrite ac.raw all",
                    ["ac.raw"],
                )
                row = dict(
                    cf_f=cf, rf_ohm=rf, capsule_f=capsule, scope="ideal finite-gain diagnostic"
                )
                if raw:
                    d = raw["ac.raw"]
                    f = d["frequency"].real
                    oracle = charge_transfer(f, cf, rf, ct)
                    observed = d["v(out)"] * (2j * np.pi * f)
                    error = float(np.max(abs(observed / oracle - 1)))
                    row.update(
                        error=error,
                        oracle_pass=error < 0.01,
                        conversion_v_per_c={
                            str(x): float(abs(at_frequency(f, observed, x)))
                            for x in [20, 1000, 20000]
                        },
                        reset_corner_hz=1 / (2 * np.pi * rf * cf),
                    )
                rows.append(row)
    resets = []
    for cf in [1e-7, 1 / (1 / 1e-7 + 1 / 1e-10)]:
        rf, ct = 5e5, 72e-12
        tau = rf * (ct + 11 * cf) / 11
        circuit = (
            f"Istep 0 f PULSE(0 1n {tau} 1n 1n {tau} {10 * tau})\n"
            f"Ct f 0 {ct}\nRf out f {rf}\nCf out f {cf}\nEe out 0 f 0 -10"
        )
        raw = exp.execute(
            dict(id="reset_oracle"),
            f"reset_{cf:.8g}",
            circuit,
            f"tran {tau / 100} {8 * tau} 0 {tau / 100}\nwrite tran.raw all",
            ["tran.raw"],
        )
        row = dict(cf_f=cf, tau_s=tau)
        if raw:
            d = raw["tran.raw"]
            t = d["time"].real
            # Superposition of two current steps; 1ns edge/width offsets are retained.
            amplitude = -10 / 11 * rf * 1e-9

            def step(delay, t=t, tau=tau):
                return np.where(t > delay, 1 - np.exp(-np.maximum(t - delay, 0) / tau), 0)

            expected = amplitude * (step(tau) - step(2 * tau + 1e-9))
            error = float(np.max(abs(d["v(out)"] - expected)))
            row.update(error_v=error, oracle_pass=error < 1e-5)
        resets.append(row)
    dc = []
    for rf in [5e5, 1e8]:
        raw = exp.execute(
            dict(id="dc_reset"),
            str(rf),
            f"Ib f 0 .5u\nRf out f {rf}\nEe out 0 f 0 -10",
            "op\nwrite op.raw all",
            ["op.raw"],
        )
        expected = 10 / 11 * rf * 0.5e-6
        dc.append(
            dict(
                rf_ohm=rf,
                assumed_ib_a=0.5e-6,
                expected_output_v=expected,
                observed_output_v=float(raw["op.raw"]["v(out)"][0]) if raw else None,
                physical_authority_pass=None,
                reason="Unlimited ideal output; compare demand with real rail",
            )
        )
    # Numerical integration independent of the SPICE noise implementation.
    f = np.geomspace(20, 20000, 20001)
    ib, q, k, temperature = 0.5e-6, 1.602176634e-19, 1.380649e-23, 298.15
    qpa = 70e-12 * 40 * (0.020 / 60)
    envelopes = []
    for rf in [5e5, 1e8]:
        for flicker_corner in [0, 100]:
            psd = 2 * q * ib * (1 + flicker_corner / f) + 4 * k * temperature / rf
            rms = float(np.sqrt(np.trapezoid(psd / (2 * np.pi * f * qpa) ** 2, f)))
            envelopes.append(
                dict(
                    rf_ohm=rf,
                    assumed_ib_a=ib,
                    assumed_current_flicker_corner_hz=flicker_corner,
                    conditional_pa_rms=rms,
                    population_or_device_rating=False,
                )
            )
    return dict(ac=rows, resets=resets, dc=dc, hypothetical_noise=envelopes)


def opa_circuit(model, shift=0, cm=8, charge=False, guard_load=None):
    pins = "ga gb " if model["device_id"] == "opa928" else ""
    sub = model["subcircuit"]
    base = f"Vg g 0 {shift}\nVp p g 16\nVn n g 0\nVm ref g {cm}\nRl out ref 10k\n"
    if charge:
        base += (
            "Ic g in DC 0 AC 1 PULSE(0 1p .01 1u 1u .01 2)\nCt in g 70p\n"
            "Rf out in 1G\nCf out in 100p\n"
            f"Xq ref in p n out {pins}{sub}"
        )
    else:
        base += f"Vin in ref DC 0 AC 1\nXq in out p n out {pins}{sub}"
    if guard_load is not None:
        gpins = "gc gd " if model["device_id"] == "opa928" else ""
        base += (
            f"\nXguard out go p n go {gpins}{sub}\nRiso go guard 1k\n"
            f"Cg guard g {max(guard_load, 1e-18)}\nCstray in guard 10p"
        )
    return base


def cmos_controls(exp, models):
    rows = []
    for shift in [0, 20, -20]:
        circuit = (
            f"Vg g 0 {shift}\nVin in g DC 8 AC 1\nEbuf out g in g 1\nVm ref g 8\nRl out ref 10k"
        )
        raw = exp.execute(
            dict(id="ideal_gauge"),
            str(shift),
            circuit,
            "op\nwrite op.raw all\nac lin 1 1k 1k\nwrite ac.raw all",
            ["op.raw", "ac.raw"],
        )
        rows.append(
            dict(
                kind="ideal_gauge",
                shift_v=shift,
                relative_output_v=float(raw["op.raw"].voltage("out", "g")[0]) if raw else None,
                no_cmos_power_or_noise_credit=True,
            )
        )
    for model in models:
        for label, shift, cm, charge, load in (
            [(f"follower_{x}", x, 8, False, None) for x in [0, 20, -20]]
            + [(f"cm_{x}", 0, x, False, None) for x in [0.1, 15.9]]
            + [(f"charge_{x}", x, 8, True, None) for x in [0, 20]]
            + [(f"guard_{x}", 0, 8, False, x) for x in [0, 100e-12, 1e-9]]
        ):
            raw = exp.execute(
                model,
                label,
                opa_circuit(model, shift, cm, charge, load),
                "op\nwrite op.raw all\nac dec 64 10 10Meg\nwrite ac.raw all",
                ["op.raw", "ac.raw"],
            )
            row = dict(
                model=model["id"],
                kind=label,
                shift_v=shift,
                cm_v=cm,
                status="supported_execution" if raw else "unsupported_execution",
            )
            if raw:
                d, a = raw["op.raw"], raw["ac.raw"]
                row.update(
                    relative_output_v=float(d.voltage("out", "g")[0]),
                    currents_a={v: float(d[f"i({v})"][0]) for v in ["vp", "vn", "vg", "vm"]},
                    ac_gain_1khz=float(abs(at_frequency(a["frequency"], a["v(out)"], 1000))),
                    rail_power_w=float(-16 * d["i(vp)"][0]),
                )
                if load is not None:
                    row.update(
                        guard_tracking_20khz=complex_record(
                            at_frequency(a["frequency"], a["v(guard)"] / a["v(in)"], 20000)
                        ),
                        input_admittance_20khz=complex_record(
                            -at_frequency(a["frequency"], a["i(vin)"], 20000)
                        ),
                    )
            rows.append(row)
    # Deliberately adverse positive-feedback controls, independently solved quadratic.
    guard = []
    for gain in [0, 0.99, 2]:
        ct, cg, rb, pole = 72e-12, 100e-12, 1e9, 1e4
        w = 2 * np.pi * pole
        roots = np.roots([(ct + cg) / w, ct + cg * (1 - gain) + 1 / (rb * w), 1 / rb])
        circuit = (
            f"Itest 0 f AC 1\nRb f 0 {rb}\nCt f 0 {ct}\nCg f guard {cg}\n"
            f"Eerr pre 0 f 0 {gain}\nRp pre pole 1k\nCp pole 0 {1 / (w * 1000)}\nEb guard 0 pole 0 1"
        )
        raw = exp.execute(
            dict(id="guard_oracle"),
            str(gain),
            circuit,
            "ac dec 64 1 10Meg\nwrite ac.raw all",
            ["ac.raw"],
        )
        row = dict(
            gain=gain,
            poles_per_s=[complex_record(z) for z in roots],
            stable_analytic=bool(np.all(roots.real < 0)),
        )
        if raw:
            d = raw["ac.raw"]
            s = 2j * np.pi * d["frequency"].real
            y = 1 / rb + s * (ct + cg * (1 - gain / (1 + s / w)))
            row["relative_error"] = float(np.max(abs(d["v(f)"] * y - 1)))
        guard.append(row)
    settling = []
    for shift in [0, 20]:
        m = models[0]
        raw = exp.execute(
            m,
            f"charge_reset_{shift}",
            opa_circuit(m, shift, charge=True),
            "tran 100u .8 0 100u\nwrite tran.raw time v(out) v(g)",
            ["tran.raw"],
        )
        row = dict(
            shift_v=shift,
            expected_tau_s=0.1,
            one_percent_s=0.460517,
            status="unsupported" if raw is None else "executed_not_yet_validated",
        )
        if raw:
            d = raw["tran.raw"]
            t = d["time"].real
            y = d.voltage("out", "g").real
            final = float(np.mean(y[t > 0.7]))
            expected_delta = -1e-3 * (1 - np.exp(-0.01 / 0.1)) * np.exp(-(t - 0.020002) / 0.1)
            mask = (t > 0.03) & (t < 0.5)
            error = float(np.max(abs(y[mask] - final - expected_delta[mask])))
            row.update(error_v=error, status="oracle_pass" if error < 1e-5 else "oracle_fail")
        settling.append(row)
    return dict(terminals=rows, guard_oracles=guard, reset=settling)


def complex_record(z):
    return [float(z.real), float(z.imag)]
