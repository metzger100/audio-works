# SPDX-License-Identifier: GPL-3.0-or-later
"""Functional views supplement full ordered-pin connectivity, including ideals."""

import json
import subprocess


def functional(out, candidate, circuit):
    jfets = {"candidate_0017", "candidate_0019", "candidate_0023", "candidate_0025"}
    labels = {
        "power": "P48 pins 2/3 → two 2.2kΩ paths\nFiltered raw; divider/NPN rail; midpoint",
        "capsule": "K47FRB electrical scenario\nFront/backplate/rear; mechanics and safe bias unknown",
        "polar": "Raw → resistor chain/filter → Rback\nBackplate bias; rear return to local ground",
    }
    edges = [("power", "polar", "raw"), ("polar", "capsule", "simulated DC")]
    if candidate in jfets:
        assert "XJinput" in circuit
        labels["input"] = "JFE150 source follower\nNo selection or hidden trimming"
        labels["bias"] = (
            "Fixed divider → 1GΩ input return\n3.3kΩ source degeneration"
            if candidate in {"candidate_0017", "candidate_0019"}
            else "Two-BJT source-voltage servo → 1GΩ gate return\n1kΩ source degeneration; finite authority"
        )
        labels["output"] = (
            "AC coupling; inverter + two NPN drivers\n47Ω legs; parallel 47µF output capacitors"
        )
        edges += [("bias", "input", "bias return"), ("power", "bias", "rail/reference")]
        if candidate in {"candidate_0023", "candidate_0025"}:
            edges.append(("input", "bias", "source sense"))
        if candidate == "candidate_0025":
            assert "Lbackfilter b cb_ind" in circuit
            labels["filter"] = "Final backplate → local ground\n100nF PP; IR/ESR/assumed ESL"
            edges.append(("polar", "filter", "backplate branch"))
    elif candidate == "candidate_0012":
        assert "Cfeedback" in circuit
        labels["input"] = "BJT differential charge stage\n100nF feedback; parallel 1MΩ reset paths"
        labels["output"] = "Opposed pair outputs → two NPN followers\nAC coupling to pins 2/3"
        edges.append(("input", "input", "finite charge/reset feedback"))
    elif candidate in {"candidate_0010", "candidate_0014"}:
        labels["input"] = (
            "OPA197 follower + separate OPA197 guard\nAC bootstrap of high-resistance return"
            if candidate == "candidate_0010"
            else "OPA197 charge input\n100pF C0G feedback; 1GΩ reset"
        )
        labels["output"] = (
            "Inverter + two NPN drivers; AC output coupling\nFloating/charge integration held"
        )
        edges.append(("input", "input", "guard/bootstrap or charge/reset feedback"))
    else:
        assert candidate == "candidate_0013" and "Eoutp" in circuit and "Eoutn" in circuit
        labels["input"] = (
            "Ideal anti-phase carrier → floating bridge\nIdeal buffers; RF permission unknown"
        )
        labels["output"] = (
            "Ideal synchronous product → passive lowpasses\nIdeal Eoutp/Eoutn; no real carrier BOM"
        )
    edges += [("capsule", "input", "electrical conversion"), ("input", "output", "signal")]
    if candidate != "candidate_0013":
        edges.append(("power", "output", "loaded rail/reference"))
    lines = [
        "digraph functional {",
        'rankdir=LR;graph[bgcolor="white",pad=.2,nodesep=.4,ranksep=.6];',
        'node[shape=box,style="rounded,filled",fillcolor="#edf3f5",fontname="sans",fontsize=11];',
        'edge[fontname="sans",fontsize=9];',
        f"label={json.dumps(candidate + ': functional research view; full connectivity supplied separately')};labelloc=t;",
    ]
    lines += [f"{n}[label={json.dumps(v, ensure_ascii=False)}];" for n, v in labels.items()]
    lines += [f"{a}->{b}[label={json.dumps(v, ensure_ascii=False)}];" for a, b, v in edges]
    path = out / (candidate.replace("_", "-") + "-functional.dot")
    path.write_text("\n".join([*lines, "}"]) + "\n")
    for ext in ["svg", "png"]:
        subprocess.run(
            ["dot", "-T" + ext, str(path), "-o", str(path.with_suffix("." + ext))], check=True
        )
