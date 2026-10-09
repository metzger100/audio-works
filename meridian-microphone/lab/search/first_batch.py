# SPDX-License-Identifier: GPL-3.0-or-later
"""One-time registration of six reviewed mechanisms; refuses existing identities.

The generator is provenance, not an optimizer or performance declaration.
Run from the lab with .venv/bin/python search/first_batch.py.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def main():
    shared_output = "Real output devices and two 47 ohm/47 uF legs; harvest/cable/load coupling measured, symmetry not presumed"
    a = Attempt(
        1,
        "conventional_jfet",
        "Conventional degenerated JFET reference",
        "concept_0001",
        "voltage",
        "source_degeneration",
        questions(
            "front open-circuit voltage",
            "JFE input C, 1 GOhm gate bias; source follower reduces Cgs loading",
            "gate at rail/4; 3.3 kohm source degeneration; fixed parts across device spread",
            "source follower then AC coupling into real CMOS differential driver",
            shared_output,
            "JFE voltage/current/flicker plus gate/polarization resistors and both output opamps",
            "source-follower curvature, drain modulation and output clipping",
            "production corner bias/noise/model coverage",
            "DC current/VGS/VDS across weak/strong proposals, then loading/noise",
            "A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.",
        ),
        ["S14", "S15"],
    )
    for i in range(3):
        a.resistor(
            f"Rgatetop{i}",
            "rail" if i == 0 else f"gate_div{i - 1}",
            "gatebias" if i == 2 else f"gate_div{i}",
            10000,
        )
    a.resistor("Rgatebottom", "gatebias", "g", 10000)
    a.capacitor("Cgatebias", "gatebias", "g", 47e-6)
    a.resistor("Rbias", "f", "gatebias", 1e9, high=True)
    a.resistor("Rrear", "rear", "g", 1000)
    a.device(
        "Jinput", "JFE150", ["rail", "f", "source", "rail", "g"], "JFE150DBVR", "jfe150_pspice"
    )
    a.resistor("Rsource", "source", "g", 3300)
    a.capacitor("Caudio", "source", "signal", 1e-6)
    a.resistor("Rsignal", "signal", "mid", 1000000)
    a.output("signal")
    a.finish()

    a = Attempt(
        2,
        "unconventional_jfet",
        "JFET slow source-current servo",
        "concept_0015",
        "voltage",
        "slow_source_current_servo",
        questions(
            "front voltage above the slow servo bandwidth",
            "1 GOhm gate servo injection; finite input C",
            "filtered source compared with rail/10; servo sets source current through 1 kohm",
            "audio source follower; DC loop has separate authority and bandwidth",
            shared_output,
            "servo voltage noise through gate resistor, JFE flicker/current noise and output noise",
            "servo/audio interaction, rail-dependent reference and clipping",
            "insufficient servo authority or loop instability",
            "source-current DC, leakage extremes, startup and audio/servo return ratio",
            "A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.",
        ),
        ["S06", "S14", "S15"],
    )
    previous = "rail"
    for i in range(9):
        node = "setpoint" if i == 8 else f"set_div{i}"
        a.resistor(f"Rsettop{i}", previous, node, 10000)
        previous = node
    a.resistor("Rsetbottom", "setpoint", "g", 10000)
    a.capacitor("Cset", "setpoint", "g", 47e-6)
    a.resistor("Rsense", "source", "slow", 1000000)
    a.capacitor("Csense", "slow", "g", 1e-6)
    a.opamp("Uservo", "setpoint", "slow", "servo")
    a.resistor("Rbias", "f", "servo", 1e9, high=True)
    a.resistor("Rrear", "rear", "g", 1000)
    a.device(
        "Jinput", "JFE150", ["rail", "f", "source", "rail", "g"], "JFE150DBVR", "jfe150_pspice"
    )
    a.resistor("Rsource", "source", "g", 1000)
    a.capacitor("Caudio", "source", "signal", 1e-6)
    a.resistor("Rsignal", "signal", "mid", 1000000)
    a.output("signal")
    a.finish()

    a = Attempt(
        3,
        "bootstrap",
        "CMOS voltage input with driven guard",
        "concept_0005",
        "voltage",
        "unity_voltage_guard",
        questions(
            "front voltage",
            "finite CMOS Cin; guard follows front; bias return bootstrapped in audio",
            "midrail through 1 GOhm; guard DC anchored by 1 Mohm",
            "OPA197 follower plus finite-bandwidth guard buffer",
            shared_output,
            "input CMOS en/in/1f, guard coupling and both output channels",
            "common-mode crossover and positive-feedback tracking error",
            "guard noise or instability exceeds loading benefit",
            "compare guarded/untracked admittance and noise with assumed 0.5-10 pF geometry",
            "A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.",
        ),
        ["S06", "S16"],
    )
    a.resistor("Rbias", "f", "boot", 1e9, high=True)
    a.resistor("Rbootdc", "boot", "mid", 1000000)
    a.opamp("Uinput", "f", "outp", "outp")
    a.opamp("Uguard", "outp", "guard", "guard")
    a.capacitor("Cboot", "guard", "boot", 1e-6)
    a.capacitor("Cguard", "f", "guard", 5e-12, assumed=True)
    a.resistor("Rguardleak", "f", "guard", 1e12, parasitic=True)
    a.resistor("Rrear", "rear", "g", 1000)
    a.output("outp", buffer=False)
    a.finish()

    a = Attempt(
        4,
        "charge",
        "CMOS charge feedback with resistive reset",
        "concept_0010",
        "charge",
        "capacitive_feedback",
        questions(
            "front displacement charge",
            "virtual midrail at front; 100 pF feedback capacitor sets conversion",
            "1 GOhm feedback bleed supplies input bias and capsule leakage; DC authority explicitly finite",
            "Q/Cfb then real inverted output",
            shared_output,
            "feedback thermal/excess noise, CMOS en times noise gain and in, output driver noise",
            "finite loop gain, DC leakage saturation and rail clipping",
            "leakage times 1 GOhm exhausts swing",
            "DC at LEAK=1G then charge transfer/noise across C/leakage corners",
            "Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.",
        ),
        ["S05", "S07", "S16"],
    )
    a.opamp("Uinput", "mid", "f", "outp")
    a.resistor("Rfeedback", "outp", "f", 1e9, high=True)
    a.capacitor("Cfeedback", "outp", "f", 1e-10)
    a.resistor("Rrear", "rear", "g", 1000)
    a.output("outp", buffer=False)
    a.finish()

    a = Attempt(
        5,
        "no_fet",
        "BJT-only discrete charge-feedback input",
        "concept_0007",
        "charge",
        "bipolar_capacitive_feedback",
        questions(
            "front displacement charge at a bipolar summing input",
            "finite differential-pair loop; base shot noise remains",
            "fixed midrail pair and degenerated tail; 1 Mohm DC feedback supplies base current",
            "discrete differential error amplifier, 100 nF feedback and emitter followers",
            shared_output,
            "base-current shot noise, feedback resistor and collector/output noise; missing KF explicitly unknown",
            "differential pair curvature, finite loop gain, unequal follower bias",
            "low reset resistance requires very large Cfb and loses sensitivity/SNR",
            "base current/feedback authority, pressure-referred shot noise and finite-loop response",
            "An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.",
        ),
        ["S05", "S07", "S17"],
    )
    a.resistor("Rreftop", "rail", "ref", 10000)
    a.resistor("Rrefbottom", "ref", "g", 10000)
    a.capacitor("Cref", "ref", "g", 47e-6)
    a.device("Qinput", "BC846B", ["outa", "f", "e1"], "BC846B,215", "bc846b_emitter_r1")
    a.device("Qreference", "BC846B", ["outb", "ref", "e2"], "BC846B,215", "bc846b_emitter_r1")
    a.resistor("Remitter1", "e1", "tail", 1000)
    a.resistor("Remitter2", "e2", "tail", 1000)
    a.resistor("Rtail", "tail", "g", 10000)
    a.resistor("Rcollector1", "rail", "outa", 10000)
    a.resistor("Rcollector2", "rail", "outb", 10000)
    a.resistor("Rfeedback", "outa", "f", 1000000)
    a.capacitor("Cfeedback", "outa", "f", 1e-7)
    a.device("Qoutp", "BC846B", ["rail", "outa", "outp"], "BC846B,215", "bc846b_emitter_r1")
    a.device("Qoutn", "BC846B", ["rail", "outb", "outn"], "BC846B,215", "bc846b_emitter_r1")
    a.resistor("Routloadp", "outp", "g", 10000)
    a.resistor("Routloadn", "outn", "g", 10000)
    a.resistor("Rrear", "rear", "g", 1000)
    a.coupling()
    a.finish()

    a = Attempt(
        6,
        "floating",
        "Floating carrier bridge mechanism control",
        "concept_0019",
        "carrier_capacitance",
        "synchronous_demodulation_control",
        questions(
            "front/rear capacitance modulation of an anti-phase analog carrier",
            "floating capacitor bridge; 100 pF fixed references; both input buffer loads explicit",
            "filtered DC backplate and midrail electrode returns; no physical safe RF/DC rating inferred",
            "bridge sidebands then synchronous product and two-pole RC low-pass",
            shared_output,
            "periodic device noise, oscillator AM/PM and mixer folding; ordinary DC noise is invalid",
            "bridge imbalance, product/filters, force/back-action absent from capsule model",
            "unimplemented oscillator/mixer power/noise and unvalidated periodic protocol",
            "carrier on/off pressure sidebands, demodulation phase, step refinement and analytic charge-control oracle",
            "A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.",
        ),
        ["S09", "S16"],
    )
    a.meta.update(
        ideal_devices=True,
        analysis_domain="periodic_mechanism_control",
        carrier_protocol="deterministic_r1_noise_unimplemented",
    )
    for key, value in [("CARRIER_HZ", 100000), ("CARRIER_PEAK", 0.2)]:
        a.meta["parameters"][key] = dict(
            default=value,
            range=[value / 2, value * 2],
            scale="linear",
            provenance="explicit unsourced oscillator control, not device rating",
        )
    a.lines += [
        "Bcarrier excite pol V={CARRIER_PEAK*sin(2*PI*CARRIER_HZ*time)}",
        "Banti anti pol V={-CARRIER_PEAK*sin(2*PI*CARRIER_HZ*time)}",
    ]
    a.capacitor("Cexcite", "excite", "b", 1e-7)
    a.capacitor("Cbridgef", "f", "anti", 1e-10)
    a.capacitor("Cbridger", "rear", "anti", 1e-10)
    a.resistor("Rbias", "f", "mid", 1e9, high=True)
    a.resistor("Rrearbias", "rear", "mid", 1e9, high=True)
    a.opamp("Ufront", "f", "frontbuf", "frontbuf")
    a.opamp("Urear", "rear", "rearbuf", "rearbuf")
    a.lines.append("Bdemod demod mid V={(v(frontbuf,rearbuf))*2*sin(2*PI*CARRIER_HZ*time)}")
    a.resistor("Rfilter1", "demod", "lp1", 1000)
    a.capacitor("Cfilter1", "lp1", "mid", 1e-7)
    a.resistor("Rfilter2", "lp1", "audio", 1000)
    a.capacitor("Cfilter2", "audio", "mid", 1e-7)
    a.output("audio")
    a.finish()


from batch_attempt import Attempt as Attempt, questions as questions

if __name__ == "__main__":
    main()
