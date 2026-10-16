# SPDX-License-Identifier: GPL-3.0-or-later
"""One-time registration of six reviewed mechanisms; refuses existing identities.

The generator is provenance, not an optimizer or performance declaration.
Run from the lab with .venv/bin/python search/first_batch.py.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from meridian_lab.core import ROOT
from mutate import register


from meridian_lab.bounded import write_data


class Attempt:
    def __init__(self, number, family, title, concept, sensing, feedback, questions, sources):
        self.id = f"candidate_{number:04d}"
        self.title = title
        self.lines = [
            "* SPDX-License-Identifier: CERN-OHL-S-2.0",
            "* Internal research; no build recommendation.",
            ".subckt DUT f b rear p n g rail",
        ]
        self.bom = []
        self.meta = dict(
            family=family,
            concept_parent=concept,
            ideal_devices=False,
            semiconductor_models=["bc846b_emitter_r1"],
            parameters={},
            population={},
            device_models=[],
            qualification_evidence=[],
            noise_groups={},
            dc_probes=[],
            loop_probes=[],
            power_devices=[],
            power_resistors=[],
            questions=questions,
            sources=sources,
            input_device_class="JFET" if number < 3 else "BJT" if number == 5 else "CMOS",
            fet_audio_path=number != 5,
            fet_power_circuitry=False,
            internal_device_classes="CMOS per OPA197 datasheet; macro internals are behavioral, not transistor evidence"
            if number != 5
            else "NPN only",
            procurement_state="research_BOM_live_orderability_and_delivered_quote_unverified",
            patent_state="unscreened_no_clearance",
            prototype_gate="hold",
            manufacture_gate="hold",
            build_publication_gate="hold",
            niche=dict(
                input_device="JFET" if number < 3 else "BJT" if number == 5 else "CMOS",
                sensing=sensing,
                reference="floating_bridge" if number == 6 else "single_ended",
                feedback=feedback,
                bias="source_servo" if number == 2 else "fixed_parts",
                active_device_count=0,
                servo=number == 2,
                output="differential_real_devices",
                common_mode="divider",
                bootstrap=number == 3,
            ),
        )
        self.power()

    def parameter(self, name, value, tolerance, provenance):
        key = name.upper() + "_VALUE"
        self.meta["parameters"][key] = dict(
            default=value,
            range=[value * (1 - tolerance), value * (1 + tolerance)],
            scale="log",
            provenance=provenance,
        )
        self.meta["population"][key] = dict(
            range=[value * (1 - tolerance), value * (1 + tolerance)],
            distribution="uniform",
            provenance=provenance,
            interpretation="independent tolerance stress, not a measured production distribution",
        )
        return key

    def resistor(self, name, a, b, value, high=False, parasitic=False):
        part = (
            "HVA12JA1G00"
            if high
            else {
                47: "RC0603FR-0747RL",
                1000: "RC0603FR-071KL",
                2200: "RC0603FR-072K2L",
                3300: "RC0603FR-073K3L",
                10000: "RC0603FR-0710KL",
                100000: "RC0603FR-07100KL",
                1000000: "RC0603FR-071ML",
            }[value]
            if not parasitic
            else None
        )
        tol = 0.05 if high else 0.01
        if parasitic:
            key = self.parameter(
                name, value, 0.9, "assumed board leakage; broader capsule range remains unchanged"
            )
        else:
            key = self.parameter(
                name,
                value,
                tol,
                f"BOM {part}; catalogue tolerance; excess noise/voltage coefficient unqualified",
            )
            self.bom.append(
                dict(
                    reference=name,
                    part_id=part,
                    quantity=1,
                    value=value,
                    unit="ohm",
                    tolerance_fraction=tol,
                )
            )
        self.lines.append(f"{name} {a} {b} {{{key}}}")
        self.meta["power_resistors"].append(dict(reference=name, nodes=[a, b], parameter=key))
        if high:
            self.capacitor("C" + name[1:] + "stray", a, b, 2e-13, assumed=True)

    def capacitor(self, name, a, b, value, assumed=False):
        part = {
            47e-6: "EEU-FR1J470",
            1e-6: "R82EC4100DQ70J",
            1e-7: "R82EC3100DQ70J",
            1e-10: "C0603C101J1GACTU",
        }.get(value)
        tol = 0.20 if value == 47e-6 else 0.05
        key = self.parameter(
            name,
            value,
            0.9 if assumed else tol,
            "assumed geometry/parasitic; not a purchasable part or measured bound"
            if assumed
            else f"BOM {part}; capacitance tolerance; dielectric/leakage/ESR coverage partial",
        )
        self.lines.append(f"{name} {a} {b} {{{key}}}")
        if not assumed:
            if part is None:
                raise ValueError("Unsourced nominal capacitor")
            self.bom.append(
                dict(
                    reference=name,
                    part_id=part,
                    quantity=1,
                    value=value,
                    unit="F",
                    tolerance_fraction=tol,
                )
            )
            # Explicit conservative ESR and insulation controls, separately labelled assumptions.
            # Bulk storage and film loss need measured frequency/temperature-dependent models.

    def device(self, name, model, nodes, part, model_id):
        currents = []
        internals = []
        for i, node in enumerate(nodes):
            sense = f"V{name}_{i}"
            inside = f"{name}_t{i}"
            self.lines.append(f"{sense} {node} {inside} 0")
            currents.append(f"i(v.xdut.{sense.lower()})")
            internals.append(inside)
        self.lines.append(f"X{name} " + " ".join(internals) + " " + model)
        self.meta["power_devices"].append(
            dict(instance=name, model_id=model_id, nodes=nodes, currents=currents)
        )
        if model_id not in self.meta["semiconductor_models"]:
            self.meta["semiconductor_models"].append(model_id)
        self.bom.append(
            dict(
                reference=name,
                part_id=part,
                quantity=1,
                value=model,
                unit="device",
                tolerance_fraction=None,
            )
        )
        self.meta["niche"]["active_device_count"] += 1

    def power(self):
        self.resistor("Rharvestp", "p", "raw", 2200)
        self.resistor("Rharvestn", "n", "raw", 2200)
        self.capacitor("Craw", "raw", "g", 47e-6)
        self.resistor("Rregtop", "raw", "regbase", 100000)
        self.resistor("Rregbottom", "regbase", "g", 100000)
        self.capacitor("Cregbase", "regbase", "g", 1e-6)
        self.device("Qreg", "BC846B", ["raw", "regbase", "rail"], "BC846B,215", "bc846b_emitter_r1")
        self.capacitor("Crail", "rail", "g", 47e-6)
        self.resistor("Rmidtop", "rail", "mid", 10000)
        self.resistor("Rmidbottom", "mid", "g", 10000)
        self.capacitor("Cmid", "mid", "g", 47e-6)
        # 10 MOhm realized as ten standard 1 MOhm parts, not an ideal unavailable value.
        previous = "raw"
        for i in range(10):
            node = "pol" if i == 9 else f"pol_{i}"
            self.resistor(f"Rpolar{i}", previous, node, 1000000)
            previous = node
        self.capacitor("Cpol", "pol", "g", 1e-7)
        self.resistor("Rback", "pol", "b", 1000000)

    def opamp(self, name, positive, negative, output):
        self.device(
            name,
            "OPAx197",
            [positive, negative, "rail", "g", output],
            "OPA197IDBVR",
            "opa197_pspice",
        )

    def output(self, signal, buffer=True):
        if buffer:
            self.opamp("Uoutp", signal, "outp", "outp")
        elif signal != "outp":
            self.lines.append(f"Voutlink {signal} outp 0")
        self.resistor("Rinvertin", "outp", "inv", 10000)
        self.resistor("Rinvertfb", "outn", "inv", 10000)
        self.opamp("Uoutn", "mid", "inv", "outn")
        self.coupling()

    def coupling(self):
        # Positive electrolytic terminal belongs to the higher P48 pin; power-off reversal unqualified.
        self.resistor("Routp", "outp", "cp", 47)
        self.resistor("Routn", "outn", "cn", 47)
        self.capacitor("Coutp", "p", "cp", 47e-6)
        self.capacitor("Coutn", "n", "cn", 47e-6)

    def finish(self):
        self.lines.append(".ends DUT")
        folder = ROOT / "search/proposals" / self.id
        folder.mkdir(exist_ok=False)
        circuit = folder / "circuit.cir"
        circuit.write_text("\n".join(self.lines) + "\n")
        metadata = folder / "topology.yaml"
        write_data(metadata, self.meta)
        hypothesis = self.meta["questions"]["hypothesis"]
        dest = register(
            "fixture_0001",
            self.id,
            circuit,
            metadata,
            hypothesis,
            f"Independent {self.title} mechanism child of interface fixture; not a copied production microphone.",
        )
        bom = dict(
            schema_version=1,
            candidate=self.id,
            intended_equipment="one possible finished microphone; alternatives are not a shopping list",
            capsule=dict(
                mpn="K47FRB",
                quantity=1,
                safe_polarization="unknown",
                included_in_electronics_cost=False,
            ),
            procurement_register="../../research/procurement/architecture_parts_2026-10-09.yaml",
            physical_parts=self.bom,
            simulation_only="Zero-volt current observers and explicit geometry/leakage controls are not purchases",
            substitutes_qualified=[],
            build_ready=False,
        )
        if self.meta["ideal_devices"]:
            bom["missing_implementation_parts"] = [
                "carrier oscillator/anti-phase excitation and its power/noise",
                "synchronous analog demodulator and its power/noise",
            ]
        write_data(dest / "bom.yaml", bom)
        (dest / "notes.md").write_text(
            f"# {self.title}\n\nInventor: see the nine questions and falsifiable hypothesis in [metadata](topology.yaml).\n\nEngineer: fixed ordinary nominal parts, NPN divider-fed rail, filtered polarization and real output terminals. No selection or trimming. [BOM](bom.yaml) is an intended-quantity research BOM; live availability, delivered costs, parasitic/leakage/excess-noise and full production device behavior remain unqualified. Board parasitics are assumptions, not purchased components. All qualification and patent gates remain held.\n\nRun `./run evaluate {self.id}`. Sources are frozen per experiment. No optimization or substitute credit is claimed.\n"
        )
        return dest


def questions(quantity, loading, bias, gain, output, noise, distortion, fatal, test, hypothesis):
    return dict(
        sensed_quantity=quantity,
        loading=loading,
        dc_bias=bias,
        gain_or_impedance_transformation=gain,
        balanced_output=output,
        expected_noise=noise,
        expected_distortion=distortion,
        likely_fatal_flaw=fatal,
        quickest_falsification=test,
        hypothesis=hypothesis,
    )
