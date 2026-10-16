# SPDX-License-Identifier: GPL-3.0-or-later
"""Full-file isolated driver alternatives, before any integrated substitution."""

from copy import deepcopy
import numpy as np
from meridian_lab.core import ROOT, read_yaml
from meridian_lab.device_models import resolve
from meridian_lab.metrics import at_frequency, device_noise_totals, integrate_asd
from focused_math import port_metrics
from simulation_prerequisites import Suite


def fixtures(out, plan):
    suite = Suite(out, plan)
    oracles = []
    for step in [0.001, 0.0005]:
        circuit = "Vin in 0 DC 0 AC 1 PWL(0 0 .001 0 .001000001 1 1 1)\nR1 in b 1Meg\nC1 b 0 100n"
        raw = suite.execute(
            dict(id="filter_oracle"),
            f"rc_{step}",
            circuit,
            f"ac dec 128 20 20k\nwrite ac.raw all\ntran {step} 1 0 {step}\nwrite tran.raw all",
            ["ac.raw", "tran.raw"],
        )
        if raw:
            a, t = raw["ac.raw"], raw["tran.raw"]
            expected = 1 / (1 + 2j * np.pi * a["frequency"].real * 0.1)
            elapsed = np.maximum(t["time"].real - 0.001, 0)
            error = float(max(abs(t["v(b)"].real - (1 - np.exp(-elapsed / 0.1)))))
            oracles.append(
                dict(
                    kind="one_pole",
                    step_s=step,
                    ac_relative_error=float(max(abs(a["v(b)"] / expected - 1))),
                    transient_max_error_v=error,
                    pass_oracle=error < 1e-4,
                )
            )
    raw = suite.execute(
        dict(id="port_oracle"),
        "bilateral",
        "Rp p 0 100\nRn n 0 130\nRx p n 2k\nIp 0 p AC 1\nIn 0 n AC 0",
        "ac lin 1 1k 1k\nwrite p.raw all\nalter Ip ac=0\nalter In ac=1\nac lin 1 1k 1k\nwrite n.raw all",
        ["p.raw", "n.raw"],
    )
    if raw:
        from focused_math import passive_twoport_oracle

        z = np.array([[raw[x][f"v({n})"][0] for x in ["p.raw", "n.raw"]] for n in ["p", "n"]])
        error = float(max(abs(z - np.array(passive_twoport_oracle()["z_ohm"])).ravel()))
        oracles.append(
            dict(kind="bilateral_twoport", max_error_ohm=error, pass_oracle=error < 1e-9)
        )
    parent = read_yaml(ROOT / "candidates/candidate_0023/topology.yaml")
    params = {k: v["default"] for k, v in parent["parameters"].items()}
    original = (ROOT / "candidates/candidate_0023/circuit.cir").read_text()
    body = original[original.index("VQoutp_0") : original.index(".ends DUT")]
    body = "Routp outp cp {ROUTP_VALUE}\nRoutn outn cn {ROUTN_VALUE}\n" + body
    defs = "\n".join(f".param {k}={v:.16g}" for k, v in params.items())
    rows = []
    for model_id in plan["hypotheses"]["C"]["models"]:
        model = deepcopy(resolve(ROOT / "models", [model_id])[0])
        model["file"] = "models/" + model["path"]
        model.pop("resolved_path")
        frozen = out / "source" / model["file"]
        frozen.parent.mkdir(parents=True, exist_ok=True)
        frozen.write_bytes((out.parent / "source" / model["file"]).read_bytes())
        for temp in plan["hypotheses"]["C"]["temperature_c"]:
            for name in plan["hypotheses"]["C"]["fixtures"]:
                rs = 100000 if name == "high_source_impedance" else 1000
                zp, zn = (300, 315) if name == "asymmetric_load" else (1000, 1000)
                # Rail/raw held at observed servo-parent values, an explicit
                # isolation boundary. Integrated supply feedback is not credited.
                network = (
                    f"Vrail rail 0 DC 13.5557796 AC 0\nVraw raw 0 29.5293276\n"
                    f"Vsignal in 0 DC 0 AC 1\nRsrc in src {rs}\nCaudio src signal 1u\n"
                    "Rsignal signal mid 1Meg\nRmidtop rail mid 10k\nRmidbottom mid 0 10k\nCmid mid 0 47u\n"
                    "Vphantom feed 0 48\nRfeedp feed p 6813.6\nRfeedn feed n 6786.4\n"
                    "Rharvestp p raw 2200\nRharvestn n raw 2200\n"
                    f"Rwp p xp 10\nRwn n xn 10\nCdiff p n 6n\nCp p 0 8n\nCn n 0 8n\n"
                    f"Cpreamp_p xp pp 22u\nCpreamp_n xn pn 22u\nRloadp pp 0 {zp}\nRloadn pn 0 {zn}\n"
                    "Iportp 0 p DC 0 AC 0\nIportn 0 n DC 0 AC 0\n"
                )
                circuit = defs + "\n" + network + body.replace("BC846B", model["subcircuit"])
                # Local circuit reference is global0; exact parent symbols kept.
                import re

                circuit = re.sub(r"\bg\b", "0", circuit)
                label = f"{name}_{temp}"
                row = dict(
                    model=model_id,
                    temperature_c=temp,
                    fixture=name,
                    status="error",
                    source_resistance_ohm=rs,
                    load_legs_ohm=[zp, zn],
                    model_sha256=model["sha256"],
                )
                raw = suite.execute(
                    model,
                    label,
                    circuit,
                    "op\nwrite op.raw all\nac dec 64 20 20k\nwrite audio.raw all\n"
                    "noise v(pp,pn) Vsignal dec 128 20 20k 1\nsetplot noise1\nwrite noise.raw all\n"
                    "alter Vsignal ac=0\nalter Vrail ac=1\nac dec 64 20 20k\nwrite supply.raw all",
                    ["op.raw", "audio.raw", "noise.raw", "supply.raw"],
                    temp,
                )
                ports = suite.execute(
                    model,
                    label + "_ports",
                    circuit,
                    "alter Vsignal ac=0\nalter Iportp ac=1\nac dec 64 20 20k\nwrite p.raw all\n"
                    "alter Iportp ac=0\nalter Iportn ac=1\nac dec 64 20 20k\nwrite n.raw all",
                    ["p.raw", "n.raw"],
                    temp,
                )
                if raw and ports:
                    a, n = raw["audio.raw"], raw["noise.raw"]
                    roots = device_noise_totals(n)
                    power = sum((x * x for x in roots.values()), np.zeros_like(n["frequency"].real))
                    closure = float(
                        np.max(
                            abs(power - n["onoise_spectrum"].real ** 2)
                            / np.maximum(n["onoise_spectrum"].real ** 2, 1e-300)
                        )
                    )
                    columns = [
                        np.column_stack([ports[k]["v(p)"], ports[k]["v(n)"]])
                        for k in ["p.raw", "n.raw"]
                    ]
                    z = np.stack(columns, axis=-1)
                    # Exact known passive load network is present. This is loaded
                    # two-port behavior; integrated harness separately deembeds.
                    row.update(
                        status="ok",
                        ports=port_metrics(z),
                        native_noise_power_closure=closure,
                        native_output_noise_v_rms=integrate_asd(
                            n["frequency"].real, n["onoise_spectrum"].real
                        ),
                        differential_gain_1khz=abs(
                            complex(at_frequency(a["frequency"], a.voltage("pp", "pn"), 1000))
                        ),
                        inversion_phase_difference_deg=float(
                            np.angle(
                                at_frequency(a["frequency"], a["v(outn)"] / a["v(outp)"], 1000),
                                deg=True,
                            )
                        ),
                        correlated_supply_diff_v_per_v_1khz=float(
                            abs(
                                at_frequency(
                                    raw["supply.raw"]["frequency"],
                                    raw["supply.raw"].voltage("pp", "pn"),
                                    1000,
                                )
                            )
                        ),
                        signal_dc_v=float(raw["op.raw"]["v(signal)"][0]),
                        inverse_dc_v=float(raw["op.raw"]["v(inverse)"][0]),
                        base_currents_a=[
                            float(raw["op.raw"][f"i(vq{x}_1)"][0])
                            for x in ["outp", "invert", "outn"]
                        ],
                        noise_behavior_qualification="missing flicker/joint process; native numeric power only",
                        z_real=z.real.tolist(),
                        z_imag=z.imag.tolist(),
                        frequency_hz=ports["p.raw"]["frequency"].real.tolist(),
                    )
                rows.append(row)
                print("C", model_id, label, row["status"], flush=True)
        # Same finite turn-on observation; no cold-start result at an arbitrary
        # 64ms horizon earns the microphone's5s qualification.
        startup = circuit.replace(
            "Vrail rail 0 DC 13.5557796 AC 0",
            "Vrail rail 0 PWL(0 0 .001 0 .002 13.5557796 5 13.5557796)",
        )
        suite.execute(
            model, "cold_startup", startup, "tran 1m 5 0 1m\nwrite start.raw all", ["start.raw"], 25
        )
    return dict(
        rows=rows,
        jobs=suite.jobs,
        oracles=oracles,
        integrated_substitution_performed=False,
        qualification="Incomplete full-model spectra/process/thermal/protection; no production alternative pass",
    )
