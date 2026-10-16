# SPDX-License-Identifier: GPL-3.0-or-later
"""Supplementary analytic loss/current spectra with frozen source inputs."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad

from capsule_envelope_math import KB, TEMP, write_csv

LAB = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    out = (
        LAB
        / "results/mechanism_controls"
        / (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_capsule_excess_"
            + uuid.uuid4().hex[:8]
        )
    )
    out.mkdir(parents=True, exist_ok=False)
    inputs = [
        Path(__file__),
        Path(__file__).with_name("capsule_envelope_math.py"),
        LAB / "research/capsules/parameters-001.yaml",
        LAB / "research/capsules/sources-001.yaml",
        LAB / "research/capsules/scenarios-001.yaml",
        LAB / "spec/capsule-model.yaml",
    ]
    manifest = {str(p.relative_to(LAB)): sha(p) for p in inputs}
    for name in manifest:
        target = out / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(LAB / name, target)
    (out / "plan.json").write_text(
        json.dumps(
            {
                "input_hashes": manifest,
                "budget": 12,
                "optimizations": 0,
                "assumed_C_F": 70e-12,
                "R_ohm": 1e12,
                "case_C_F": 2e-12,
                "mathematical_bias_V": 40,
                "Sref_values_V_per_Pa": [0.005, 0.020, 0.040],
                "supplementary_terms": ["loss_tangent", "excess_current"],
                "interpretation": "Isolated grounded-backplate node diagnostic; no candidate noise or acoustic rating",
            },
            indent=2,
        )
        + "\n"
    )
    freq = np.geomspace(20, 20000, 1000)
    c = 70e-12
    total_c = 72e-12
    resistance = 1e12
    entries = []
    fig, ax = plt.subplots(figsize=(8, 4))
    for kind, values in [("loss_tangent", [1e-4, 1e-3]), ("excess_current", [1e-15, 1e-14])]:
        for value in values:

            def variance_density(f, v=value, mode=kind):
                impedance = 1 / (1 / resistance + 2j * np.pi * f * total_c)
                spectrum = (
                    4 * KB * TEMP * 2 * np.pi * f * c * v
                    if mode == "loss_tangent"
                    else v * v * 100 / f
                )
                return spectrum * abs(impedance) ** 2

            numeric = quad(
                lambda u: variance_density(np.exp(u)) * np.exp(u),
                np.log(20),
                np.log(20000),
                epsabs=1e-25,
                epsrel=1e-9,
            )[0]
            sampled = variance_density(freq)
            refined = np.trapezoid(sampled, freq)
            assert abs(refined / numeric - 1) < 1e-4
            ax.loglog(freq, np.sqrt(sampled) * 1e9, label=f"{kind}={value:g}")
            for sref in [0.005, 0.020, 0.040]:
                sensitivity = sref * 40 / 60 * c / total_c
                entries.append(
                    dict(
                        term=kind,
                        assumed_value=value,
                        Sref_V_per_Pa=sref,
                        node_V_rms=np.sqrt(numeric),
                        isolated_pressure_equivalent_Pa_rms=np.sqrt(numeric) / sensitivity,
                        numerical_refinement_relative=refined / numeric - 1,
                    )
                )
    assert len(entries) == 12
    write_csv(out / "supplementary.csv", entries)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Isolated node ASD (nV/sqrt(Hz))")
    ax.set_title("Hypothetical loss/excess current; 70 pF + 2 pF, 1 Tohm")
    ax.grid(alpha=0.3, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "supplementary.png", dpi=160)
    plt.close(fig)
    unchanged = all(sha(LAB / name) == value for name, value in manifest.items())
    (out / "integrity.json").write_text(
        json.dumps(
            {
                "source_unchanged": unchanged,
                "rows": 12,
                "physical_measurements": [],
                "eligible": False,
            },
            indent=2,
        )
        + "\n"
    )
    files = sorted(p for p in out.rglob("*") if p.is_file())
    (out / "batch.sha256").write_text("".join(f"{sha(p)}  {p.relative_to(LAB)}\n" for p in files))
    print(out.relative_to(LAB))
    if not unchanged:
        raise RuntimeError("Sources changed; preserve failed batch")


if __name__ == "__main__":
    run()
