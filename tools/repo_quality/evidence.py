# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import uuid

from .base import RECORD_NAMES, canonical, current_path, private, safe_name, sha
from .register import classify
from .data import load


def archived_snapshot_gaps(view):
    """Read retained historical declarations, including the old checkout layout."""
    for path in (
        "docs/history/2026-10-11/legacy-source-gaps.json",
        "docs/legacy-source-gaps.json",
    ):
        if path in view.paths:
            return {
                current_path(name): expected
                for name, expected in load(view.text, path).get("missing_sources", {}).items()
            }
    return {}


def inventory(view):
    hashes = {}
    for p in sorted(view.paths):
        if not current_path(p).startswith("meridian-microphone/lab/results/") or not p.endswith(
            ".sha256"
        ):
            continue
        for line in view.text(p).splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            h, relative = line.split(None, 1)
            relative = relative.lstrip("*")
            safe_name(relative)
            if not re.fullmatch(r"[0-9a-f]{64}", h):
                raise ValueError(f"Invalid SHA256 in {p}")
            path = posixpath.dirname(posixpath.dirname(p)) + "/" + relative
            if path in hashes and hashes[path] != h:
                raise ValueError(f"Conflicting immutable inventory declarations: {path}")
            hashes[path] = h
    return hashes


def original_waveforms(root):
    folders = [root / name / "lab/results" for name in ("meridian-microphone", "meridian")]
    return {
        p.relative_to(root).as_posix()
        for folder in folders
        for p in folder.rglob("*")
        if p.is_file() and not p.is_symlink() and p.name.endswith((".raw", ".raw.csv"))
    }


def snapshot_hashes(view):
    expected = {}
    for p in sorted(view.paths):
        if (
            not re.fullmatch(
                r"meridian-microphone/lab/results/(runs|device_models|verification)/[^/]+/[^/]+\.json",
                current_path(p),
            )
            or Path(p).name not in RECORD_NAMES
        ):
            continue
        d = json.loads(view.text(p))
        for relative, h in d.get("source_manifest", {}).items():
            safe_name(relative)
            name = posixpath.dirname(p) + "/source/" + relative
            if name in expected and expected[name] != h:
                raise ValueError(f"Conflicting source snapshot declarations: {name}")
            expected[name] = h
    return expected


def verify_evidence(root, view):
    declared = inventory(view)
    expected = {**snapshot_hashes(view), **declared}
    missing = []
    damaged = []
    for name, h in sorted(expected.items()):
        p = root / name
        if not p.is_file() or p.is_symlink():
            missing.append(name)
        elif sha(p) != h:
            damaged.append(name)
    extra = sorted(original_waveforms(root) - declared.keys())
    return {
        "status": "pass"
        if not (missing or damaged or extra)
        else "incomplete"
        if missing and not (damaged or extra)
        else "fail",
        "declared_waveforms": len(declared),
        "snapshot_files": len(expected) - len(declared),
        "missing": missing,
        "damaged": damaged,
        "uninventoried": extra,
        "note": "Missing original local bytes require restoration; reruns or reacquisition do not recover original evidence.",
    }


def ensure_idle(root):
    proc = Path("/proc")
    if not proc.exists():
        raise ValueError(
            "Cannot establish evaluator idleness on this platform; capture on a supported idle Linux host"
        )
    markers = (
        "meridian_lab.cli",
        "characterize.py",
        "optimize_values.py",
        "search/loop.py",
        "ngspice",
    )
    for p in proc.iterdir():
        if not p.name.isdigit() or int(p.name) == os.getpid():
            continue
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            cwd = (p / "cwd").resolve()
        except (OSError, RuntimeError):
            continue
        if (str(root) in cmd or cwd.is_relative_to(root)) and any(m in cmd for m in markers):
            raise ValueError(
                "An evaluator/simulator is active; wait for stable idle sources before capture"
            )


def backup_paths(root, view, r):
    paths = set(view.paths)
    for prefix in r["backup_evidence_prefixes"]:
        safe_name(prefix.rstrip("/"))
        paths.update(
            p.relative_to(root).as_posix() for p in (root / prefix).rglob("*") if p.is_file()
        )
    paths.update(original_waveforms(root))
    for p in (root / "meridian-microphone/lab/results").rglob("*"):
        relative = p.relative_to(root).as_posix()
        if p.is_file() and (
            "/source/models/semiconductor/vendor/" in relative
            or "/source/research/device_sources/local/" in relative
        ):
            paths.add(relative)
    for p in paths:
        safe_name(p)
        if private(p) or classify(p, r) is None:
            raise ValueError(f"Unapproved backup input: {p}")
        if (root / p).is_symlink() or not (root / p).is_file():
            raise ValueError(f"Backup inputs must be regular files: {p}")
    return sorted(paths)


def file_manifest(root, paths):
    return {
        p: {
            "size": (root / p).stat().st_size,
            "sha256": sha(root / p),
            "executable": bool((root / p).stat().st_mode & 0o111),
        }
        for p in paths
    }


def evidence_fingerprint(view):
    # Coverage of declared original evidence, independent of generated navigation.
    paths = [
        p
        for p in view.paths
        if current_path(p).startswith("meridian-microphone/lab/results/")
        or p.startswith("branding/archive/")
    ]
    hashes = {p: hashlib.sha256(view.read(p)).hexdigest() for p in sorted(paths)}
    return hashlib.sha256(canonical(hashes)).hexdigest()


def independent_storage(root, destination):
    destination = destination.resolve()
    volatile = (Path("/tmp"), Path("/dev/shm"), Path("/run"))
    if destination.is_relative_to(root) or any(destination.is_relative_to(p) for p in volatile):
        return False
    if destination.stat().st_dev == root.stat().st_dev:
        return False
    # Different device alone is insufficient for tmpfs/ramfs mounts.
    if Path("/proc/mounts").exists():
        matches = []
        for line in Path("/proc/mounts").read_text().splitlines():
            fields = line.split()
            mount = Path(fields[1].replace("\\040", " "))
            if destination.is_relative_to(mount):
                matches.append((len(str(mount)), fields[2]))
        if matches and max(matches)[1] in {"tmpfs", "ramfs"}:
            return False
    return True


def write_attestation(root, data):
    if not re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", data.get("backup_id", "")):
        raise ValueError("Unsafe backup identifier")
    folder = root / ".project-local/backups"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    p = folder / (data["backup_id"] + ".json")
    p.write_bytes(canonical(data))
    p.chmod(0o600)


def preservation_status(root, view, r):
    if r.get("storage_policy", {}).get("authority") == "github":
        return {
            "status": "configured",
            "authority": "github",
            "repository": r["repository"],
            "scope": "versioned_repository",
            "private_backups": "optional",
            "remote_sync": "not_checked",
            "note": "GitHub is canonical for committed files. This local gate does not verify remote synchronization or preservation of ignored evidence.",
        }
    fingerprint = evidence_fingerprint(view)
    folder = root / ".project-local/backups"
    for p in sorted(folder.glob("*.json"), reverse=True):
        d = json.loads(p.read_text())
        if (
            d.get("independent")
            and d.get("restore_verified")
            and d.get("evidence_fingerprint") == fingerprint
        ):
            source = Path(d["source"])
            manifest = source / "manifest.json"
            if manifest.is_file() and sha(manifest) == d.get("manifest_sha256"):
                if not d.get("original_evidence_complete", False):
                    return {
                        "status": "incomplete",
                        "restored_at": d["restored_at"],
                        "note": "Independent available-byte backup restored; declared original source gaps remain.",
                    }
                return {
                    "status": "attested",
                    "restored_at": d["restored_at"],
                    "note": "Independent restored backup covers declared evidence. Run evidence verify for current local-byte integrity.",
                }
    return {
        "status": "incomplete",
        "note": "No independent restored backup covering the current declared evidence is attested. Local bytes are not hashed by the fast gate.",
    }


def new_inventory(root, view):
    ensure_idle(root)
    declared = inventory(view)
    damaged = [p for p, h in declared.items() if not (root / p).is_file() or sha(root / p) != h]
    if damaged:
        raise ValueError("Resolve existing inventory damage before recording new evidence")
    new = sorted(original_waveforms(root) - declared.keys())
    if not new:
        return {
            "status": "pass",
            "new_files": 0,
            "note": "All existing original waveforms already inventoried.",
        }
    lines = [sha(root / p) + "  " + p.removeprefix("meridian-microphone/lab/") for p in new]
    name = (
        "evidence-"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid.uuid4().hex[:8]
        + ".sha256"
    )
    destination = root / "meridian-microphone/lab/results" / name
    # Retain the observation only if the new evidence remained stable during hashing.
    ensure_idle(root)
    if sorted(original_waveforms(root) - declared.keys()) != new:
        raise ValueError("Evidence set changed while creating its inventory")
    for line, p in zip(lines, new):
        if sha(root / p) != line.split()[0]:
            raise ValueError("Evidence bytes changed while creating their inventory")
    with destination.open("x") as f:
        f.write("\n".join(lines) + "\n")
    return {
        "status": "pass",
        "new_files": len(new),
        "inventory": str(destination.relative_to(root)),
    }
