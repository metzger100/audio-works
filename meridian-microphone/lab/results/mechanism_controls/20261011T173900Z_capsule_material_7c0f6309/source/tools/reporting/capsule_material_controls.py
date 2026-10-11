# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite annular-membrane/material controls; no selected-capsule model."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid

import numpy as np
from scipy.integrate import quad
import yaml

from capsule_envelope_math import EPS as EPS0, write_csv

LAB = Path(__file__).resolve().parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    inputs = [Path(__file__), Path(__file__).with_name("capsule_envelope_math.py")]
    inputs += [
        LAB / "research/capsules" / name
        for name in [
            "material-controls-001.yaml",
            "sources-001.yaml",
            "retrieval-001-part-3.json",
        ]
    ]
    hashes = {str(p.relative_to(LAB)): sha(p) for p in inputs}
    plan = yaml.safe_load(inputs[2].read_text())
    records = json.loads(inputs[-1].read_text())
    for row in records:
        original = LAB.parents[1] / row["private_root"] / row["private_file"]
        assert sha(original) == row["sha256"]
    out = (
        LAB
        / "results/mechanism_controls"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_capsule_material_"
            + uuid.uuid4().hex[:8]
        )
    )
    out.mkdir(parents=True, exist_ok=False)
    for name in hashes:
        target = out / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(LAB / name, target)
    (out / "plan.json").write_text(
        json.dumps({"plan": plan, "input_hashes": hashes}, indent=2) + "\n"
    )
    a = plan["assumed"]["outer_radius_m"]
    eta = plan["assumed"]["electrode_fraction"]
    k0 = 0.020 / 60
    # Manufacturer kg/mm2 means kilogram-force/mm2, not mass/area.
    f5 = 10 * 9.80665e6
    ultimate = 20 * 9.80665e6
    disk_gap = EPS0 * eta * np.pi * a * a / 70e-12
    disk_tension = a * a / (8 * k0 * disk_gap)
    disk_stress = disk_tension / 3e-6
    assert disk_stress > ultimate  # Retain failed analogy, not a capsule rejection.
    gap_rows = []
    sensitivity_rows = []
    for construction in plan["constructions"]:
        beta = construction["inner_outer_radius_ratio"]
        b = beta * a
        fraction = 1 - beta * beta
        shape = 1 + beta * beta - fraction / np.log(1 / beta)
        thickness = construction["film_thickness_m"]
        for c in plan["per_side_C_F"]:
            sref = 0.020 * c / 70e-12
            gap = EPS0 * eta * np.pi * (a * a - b * b) / c
            tension = a * a * shape / (8 * (sref / 60) * gap)
            stress = tension / thickness

            def displacement(r, t=tension, b=b):
                return (a * a - r * r - (a * a - b * b) * np.log(a / r) / np.log(a / b)) / (4 * t)

            numerical = quad(
                lambda r: displacement(r) * 2 * r / (a * a - b * b),
                b,
                a,
                epsabs=1e-22,
                epsrel=1e-10,
            )[0]
            analytical = a * a * shape / (8 * tension)
            assert np.isclose(numerical, analytical, rtol=1e-10, atol=0)
            assert abs(displacement(a)) < 1e-20 and abs(displacement(b)) < 1e-20
            assert np.min(displacement(np.linspace(b, a, 100))) > -1e-20
            assert stress < f5
            gap_rows.append(
                dict(
                    construction=construction["id"],
                    C_F=c,
                    Sref_V_per_Pa=sref,
                    gap_m=gap,
                    tension_N_per_m=tension,
                    film_stress_Pa=stress,
                    mean_compliance_m_per_Pa=analytical,
                    material_comparison="below grade92A F5 typical; NOT allowable stress",
                )
            )
            if c == 70e-12:
                for s in plan["sensitivity_endpoints_V_per_Pa"]:
                    scaled_stress = stress * 0.020 / s
                    sensitivity_rows.append(
                        dict(
                            construction=construction["id"],
                            Sref_V_per_Pa=s,
                            film_stress_Pa=scaled_stress,
                            comparator_status="above typical ultimate"
                            if scaled_stress > ultimate
                            else "below F5 typical",
                        )
                    )
    assert len(gap_rows) == plan["budget"]["gap_rows"]
    assert len(sensitivity_rows) == plan["budget"]["sensitivity_rows"]
    write_csv(out / "annular.csv", gap_rows)
    write_csv(out / "sensitivity-material.csv", sensitivity_rows)
    unchanged = all(
        sha(LAB / name) == h and sha(out / "source" / name) == h for name, h in hashes.items()
    )
    controls = {
        "source_unchanged": unchanged,
        "frozen_source_matches": unchanged,
        "original_sources_reverified": sha(original) == records[-1]["sha256"],
        "gap_rows": len(gap_rows),
        "sensitivity_rows": len(sensitivity_rows),
        "disk_stress_Pa_at_3um": disk_stress,
        "grade92A_F5_Pa": f5,
        "grade92A_MD_ultimate_Pa": ultimate,
        "physical_measurements": [],
        "eligible": False,
    }
    (out / "integrity.json").write_text(json.dumps(controls, indent=2) + "\n")
    files = sorted(p for p in out.rglob("*") if p.is_file())
    (out / "batch.sha256").write_text("".join(f"{sha(p)}  {p.relative_to(LAB)}\n" for p in files))
    print(out.relative_to(LAB))
    if not unchanged:
        raise RuntimeError("Changed inputs; preserve failed batch")


if __name__ == "__main__":
    run()
