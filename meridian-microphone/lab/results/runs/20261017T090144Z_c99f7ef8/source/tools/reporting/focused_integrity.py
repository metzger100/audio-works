# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify available Prompt9 bytes without reconstructing missing originals."""

from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(Path(__file__).resolve().parent)]
from meridian_lab.core import read_yaml, write_json, digest
from comparison_records import stage


def main():
    checked = {}

    def require(path, expected):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file() or digest(path) != expected:
            raise ValueError("Missing or damaged new evidence: " + str(path))
        checked[str(path.relative_to(ROOT))] = expected

    batches = []
    for folder in sorted((ROOT / "results/mechanism_controls").glob("*focused*")):
        ledger = folder / "batch.sha256"
        # Failed partial/preflight parents did not reach finalization. Add a
        # separate available-byte inventory; never alter their frozen files.
        if not ledger.exists():
            ledger.write_text(
                "".join(
                    f"{digest(p)}  {p.relative_to(ROOT)}\n"
                    for p in sorted(folder.rglob("*"))
                    if p.is_file()
                )
            )
        count = 0
        for line in ledger.read_text().splitlines():
            sha, name = line.split(None, 1)
            require(name, sha)
            count += 1
        batches.append(
            dict(
                batch=str(folder.relative_to(ROOT)),
                files=count,
                inventory_sha256=digest(ledger),
                damaged=0,
            )
        )

    def jobs(value):
        if isinstance(value, dict):
            if value.get("netlist_sha256") and "folder" in value:
                require(Path(value["folder"]) / "job.cir", value["netlist_sha256"])
                for n, h in value.get("files", {}).items():
                    require(Path(value["folder"]) / n, h)
            for x in value.values():
                jobs(x)
        elif isinstance(value, list):
            for x in value:
                jobs(x)

    primary = read_yaml(
        ROOT / "results/mechanism_controls/20261011T192308Z_focused_1992e85a/results.json"
    )
    suites = []
    for candidate, name in primary["full_suite"].items():
        folder = ROOT / "results/runs" / name
        record = read_yaml(folder / "results.json")
        for n, h in record["source_manifest"].items():
            require(folder / "source" / n, h)
        for n, h in record["implementation_manifest"].items():
            require(folder / n, h)
        jobs(record["jobs"])
        suites.append(
            dict(
                candidate=candidate,
                experiment=name,
                eligible=record["eligible"],
                spec_sha256=record["spec_sha256"],
                jobs=len(record["jobs"]),
            )
        )
    sources = read_yaml(ROOT / "research/architectures/focused-sources-001.json")
    retrievals = []
    for r in sources["retrievals"]:
        if r.get("private_path") and r.get("sha256"):
            require(r["private_path"], r["sha256"])
        retrievals.append({k: r.get(k) for k in ["id", "status", "sha256", "http_status"]})
    original = stage()
    verification = None
    if len(sys.argv) > 1:
        path = ROOT / sys.argv[1]
        v = read_yaml(path)
        for n, h in v["source_manifest"].items():
            require(path.parent / "source" / n, h)
        verification = dict(
            path=str(path.relative_to(ROOT)),
            status=v["status"],
            source_unchanged=v["source_unchanged"],
        )
    receipt = dict(
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        new_available_files_checked=len(checked),
        batches=batches,
        suites=suites,
        retrievals=retrievals,
        verification=verification,
        original_comparison_declared_hashes_checked=len(original.checked),
        damaged_new_files=0,
        global_original_evidence="Separate root preservation receipt; historical missing originals are not reconstructed",
        private_backup="Optional;no new private backup performed",
        publication=False,
    )
    write_json(ROOT / "research/architectures/focused-integrity-001.json", receipt)
    print(
        dict(checked=len(checked), batches=len(batches), original_comparison=len(original.checked))
    )


if __name__ == "__main__":
    main()
