# SPDX-License-Identifier: GPL-3.0-or-later
"""Recheck acquired originals, duplicate cores, frozen batches and current runtime."""

from datetime import datetime, timezone
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.core import digest, read_yaml, write_json


def nominal_definitions(path):
    text = re.sub(r"\n\s*\+", " ", path.read_text().lower())
    found = {}
    for name, definition in re.findall(r"(?m)^\s*\.model\s+(\S+)\s+([^\n]+)", text):
        if name in {"njfe150", "djfe150", "esd_sw"}:
            value = " ".join(definition.split())
            if name in found and found[name] != value:
                raise ValueError("Conflicting repeated nominal definition")
            found[name] = value
    if len(found) != 3:
        raise ValueError("Incomplete nominal core")
    return found


def main():
    ledger = read_yaml(ROOT / "research/devices/simulation-prerequisites-sources-001.json")
    behavior = read_yaml(ROOT / "research/devices/simulation-prerequisites-behavior-001.json")
    rows, total = [], 0
    for record in behavior["cohorts"]:
        batch = ROOT / "results/device_models" / record["cohort"]
        count = 0
        for line in (batch / "batch.sha256").read_text().splitlines():
            sha, name = line.split("  ", 1)
            if digest(ROOT / name) != sha:
                raise ValueError(f"Damaged or missing frozen byte: {name}")
            count += 1
        total += count
        rows.append(
            dict(
                cohort=record["cohort"],
                declared_files=count,
                damaged=0,
                inventory_sha256=digest(batch / "batch.sha256"),
            )
        )
    acquired = ROOT / "research/device_sources/local/20261011T175127Z_prerequisites_40132801"
    originals, members = [], 0
    for receipt in sorted(acquired.glob("*/receipt.json")):
        record = read_yaml(receipt)
        if digest(receipt.parent / "response.bin") != record["sha256"]:
            raise ValueError("Damaged acquired response")
        for index, member in enumerate(record.get("members", []), 1):
            if digest(receipt.parent / f"member_{index:03}") != member["sha256"]:
                raise ValueError("Damaged archive member")
            members += 1
        originals.append(
            dict(
                id=record["id"],
                status=record["status"],
                sha256=record["sha256"],
                members=len(record.get("members", [])),
            )
        )
    comparisons = []
    generic = nominal_definitions(ROOT / ledger["model_comparison"][0]["path"])
    for item in ledger["model_comparison"]:
        path = ROOT / item["path"]
        core = nominal_definitions(path)
        if digest(path) != item["file_sha256"] or core != item["normalized_nominal_definitions"]:
            raise ValueError("Model comparison ledger changed")
        comparisons.append(
            dict(
                id=item["id"],
                sha256=digest(path),
                nominal_core_equal=core == generic,
                byte_identical_to_generic=digest(path)
                == ledger["model_comparison"][0]["file_sha256"],
            )
        )
    web = ROOT / "research/device_sources/local/20261011_prerequisite_web"
    queries = read_yaml(ROOT / "research/devices/simulation-prerequisites-queries-001.json")
    for row in queries["retained_raw_responses"]:
        if digest(ROOT / row["path"]) != row["sha256"]:
            raise ValueError("Web response changed")
    result = dict(
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        batch_inventories=rows,
        checked_batch_files=total,
        originals=originals,
        archive_members_checked=members,
        model_comparison=comparisons,
        current_runtime_hashes={
            str(p.relative_to(ROOT)): digest(p)
            for p in [
                ROOT / "tools/ngspice/usr/bin/ngspice",
                ROOT / "tools/ngspice-run",
                *sorted((ROOT / "tools/ngspice/usr/lib/ngspice").glob("*.cm")),
            ]
        },
        runtime_scope="Current bytes only; initial cohort did not freeze individual .cm libraries",
        private_web_response_hashes={
            str(p.relative_to(ROOT)): digest(p) for p in sorted(web.iterdir()) if p.is_file()
        },
        original_evidence_completeness="Separate root evidence verify receipt; historical missing originals not reconstructed",
    )
    write_json(ROOT / "research/devices/simulation-prerequisites-integrity-001.json", result)
    print(f"{total} batch files, {len(originals)} responses, {members} archive members verified")


if __name__ == "__main__":
    main()
