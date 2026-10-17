# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only successor extraction; retain optional-diagnostic errors and all cases."""

from copy import deepcopy
from pathlib import Path
import numpy as np

from meridian_lab.core import parse_raw, read_yaml, digest
from meridian_lab.metrics import at_frequency
from meridian_lab.qualification import response
from meridian_lab.bounded import write_data
from comparison_common import parse_elements


def hash_tree(mapping):
    tree = {}
    for name, sha in sorted(mapping.items()):
        cursor = tree
        parts = Path(name).parts
        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[parts[-1]] = sha
    return tree


def input_admittance(raw, parameters, circuit):
    elements = {e["reference"].lower(): e for e in parse_elements(circuit, parameters)}
    resistor, capacitor = elements["rbias"], elements["cbiasstray"]
    assert resistor["nodes"] == capacitor["nodes"]
    assert resistor["nodes"][0] == "f"
    reference = resistor["nodes"][1]
    ref = raw.voltage("xdut." + reference, "mic_g") if reference != "g" else 0
    voltage = raw.voltage("f", "mic_g")
    frequency = raw["frequency"].real
    y = raw["i(v.xdut.vjinput_1)"] / voltage + (voltage - ref) / voltage * (
        1 / parameters["RBIAS_VALUE"] + 2j * np.pi * frequency * parameters["CBIASSTRAY_VALUE"]
    )
    yy = at_frequency(frequency, y, 1000)
    return dict(
        real_s=float(yy.real),
        imag_s=float(yy.imag),
        equivalent_capacitance_f=float(yy.imag / (2 * np.pi * 1000)),
        actual_bias_return=reference,
        boundary="Observed gate and actual Rbias/Cbiasstray moving return; driven capsule boundary; not independent port",
    )


def recover(root, out, batch, rows, evidence):
    # The finite successor plan is written before reading any affected traces.
    source = Path(__file__)
    plan = dict(
        date="2026-10-17",
        parent=str(batch),
        scope="Optional input-admittance node lookup only",
        source_sha256=digest(source),
        source=str(source.relative_to(root)),
        hypotheses="Servo uses f-servo Rbias/Cbiasstray; fixed bias uses f-gatebias. Saved DC/AC/noise completed before diagnostic exception.",
        simulations=0,
        threshold_changes=False,
        stopping="Read all203 original rows once; recover only exact known missing-node error when every job succeeded and independent response reconstruction agrees. Preserve all original states/reasons/denominators.",
    )
    write_data(out / "recovery-plan.json", plan)
    corrected = []
    changes = []
    for original in rows:
        row = deepcopy(original)
        row["original_status"] = original["status"]
        if (
            original["status"] == "error"
            and original.get("reason")
            == "SimulationError: Missing required vector v(xdut.gatebias); never treated as a pass"
        ):
            assert all(j["status"] == "ok" for j in row["jobs"])
            assert "noise_pa_rms" in row and row["noise_partition_closure"] < 1e-5
            job = row["jobs"][0]
            ac = parse_raw(evidence(Path(job["folder"]) / "ac.raw"))
            params = read_yaml(evidence(Path(job["folder"]) / "parameters.json"))
            check = response(ac)
            np.testing.assert_allclose(
                check["response_deviation_db"], row["response_deviation_db"], rtol=1e-12, atol=0
            )
            circuit = evidence(
                batch / "implementations" / row["candidate"] / "circuit.cir"
            ).read_text()
            row["input_diagnostic_1khz"] = input_admittance(ac, params, circuit)
            row["original_error"] = row.pop("reason")
            row["status"] = (
                "pass" if row["dc"]["status"] == row["ac"]["status"] == "pass" else "fail"
            )
            row["recovery_scope"] = (
                "Read-only annotation correction; original error retained; no new simulator result"
            )
            changes.append(
                dict(
                    candidate=row["candidate"],
                    scenario=row["scenario"],
                    original_status="error",
                    original_error=row["original_error"],
                    successor_screen=row["status"],
                    raw_ac_sha256=digest(root / Path(job["folder"]) / "ac.raw"),
                    input_diagnostic=row["input_diagnostic_1khz"],
                )
            )
        corrected.append(row)
    write_data(
        out / "recovery.json",
        dict(
            plan=plan,
            recovered=changes,
            original_attempts=len(rows),
            original_errors=sum(r["status"] == "error" for r in rows),
            successor_errors=sum(r["status"] == "error" for r in corrected),
            same_scenarios=True,
            original_bytes_modified=False,
        ),
    )
    return corrected
