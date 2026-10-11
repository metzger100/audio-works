# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import uuid

from .evidence import (
    backup_paths,
    ensure_idle,
    evidence_fingerprint,
    file_manifest,
    independent_storage,
    snapshot_hashes,
    verify_evidence,
    write_attestation,
    archived_snapshot_gaps,
)
from .base import View, canonical, git, now, private, safe_name, sha, tree
from .register import load_register


def create_backup(root, destination, independent=False):
    ensure_idle(root)
    view = View(root)
    r = load_register(view)
    verification = verify_evidence(root, view)
    legacy = archived_snapshot_gaps(view)
    declarations = snapshot_hashes(view)
    known_missing = all(
        p in legacy and legacy[p] == declarations.get(p) for p in verification["missing"]
    )
    if verification["damaged"] or verification["uninventoried"] or not known_missing:
        raise ValueError(
            "Original evidence verification failed; resolve damage, new missing files or undeclared inputs. Known legacy gaps remain explicit."
        )
    destination = Path(destination).resolve()
    if destination.is_relative_to(root):
        raise ValueError("Backup destination must be outside this checkout")
    if not destination.is_dir():
        raise ValueError("Destination must be an existing owner-chosen storage directory")
    if independent and not independent_storage(root, destination):
        raise ValueError(
            "Independent storage must be persistent, outside this checkout and on a different device"
        )
    id_ = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    partial = destination / (".audiotech-" + id_ + ".partial")
    output = destination / ("audiotech-" + id_)
    partial.mkdir(mode=0o700)
    try:
        paths = backup_paths(root, view, r)
        before = file_manifest(root, paths)
        revision = git(root, "rev-parse", "HEAD").strip()
        refs = git(root, "show-ref")
        git(root, "bundle", "create", str(partial / "repository.bundle"), "--all")
        with tarfile.open(partial / "files.tar", "w") as archive:
            for name in paths:
                archive.add(root / name, arcname="files/" + name, recursive=False)
        ensure_idle(root)
        after_view = View(root)
        if (
            backup_paths(root, after_view, load_register(after_view)) != paths
            or file_manifest(root, paths) != before
            or git(root, "rev-parse", "HEAD").strip() != revision
            or git(root, "show-ref") != refs
        ):
            raise ValueError("Inputs changed during capture; inconsistent backup rejected")
        # Verify the captured bytes rather than relying only on unchanged source files.
        verify_tar(partial / "files.tar", before)
        manifest = {
            "schema_version": 1,
            "backup_id": id_,
            "captured_at": now(),
            "revision": revision,
            "independent": independent,
            "files": before,
            "original_evidence_complete": not verification["missing"],
            "missing_original_sources": {p: declarations[p] for p in verification["missing"]},
            "archive_sha256": sha(partial / "files.tar"),
            "bundle_sha256": sha(partial / "repository.bundle"),
            "evidence_fingerprint": evidence_fingerprint(after_view),
        }
        (partial / "manifest.json").write_bytes(canonical(manifest))
        partial.rename(output)
        write_attestation(
            root,
            {
                "backup_id": id_,
                "source": str(output),
                "manifest_sha256": sha(output / "manifest.json"),
                "independent": independent,
                "restore_verified": False,
                "original_evidence_complete": manifest["original_evidence_complete"],
                "evidence_fingerprint": manifest["evidence_fingerprint"],
            },
        )
        return {
            "status": "pass" if manifest["original_evidence_complete"] else "incomplete",
            "capture_verified": True,
            "source": str(output),
            "file_count": len(paths),
            "independent": independent,
            "missing_original_sources": len(verification["missing"]),
            "note": "Capture verified. Restore verification and original-evidence completeness are reported separately.",
        }
    except BaseException:
        shutil.rmtree(partial, ignore_errors=True)
        raise


def verify_tar(path, files):
    seen = set()
    with tarfile.open(path, "r") as archive:
        for member in archive:
            safe_name(member.name)
            if not member.name.startswith("files/") or not member.isfile():
                raise ValueError("Only allowlisted regular-file archive members are accepted")
            name = member.name[len("files/") :]
            safe_name(name)
            if private(name) or name not in files or name in seen:
                raise ValueError(f"Unsafe, duplicate or undeclared archive member: {name}")
            seen.add(name)
            h = hashlib.sha256()
            stream = archive.extractfile(member)
            for block in iter(lambda stream=stream: stream.read(1024 * 1024), b""):
                h.update(block)
            if h.hexdigest() != files[name]["sha256"] or member.size != files[name]["size"]:
                raise ValueError(f"Captured evidence differs from its manifest: {name}")
    if seen != set(files):
        raise ValueError("Archive omits declared files")


def restore_backup(root, source, destination):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if (
        destination == root
        or destination.is_relative_to(root)
        or destination.is_relative_to(source)
        or source.is_relative_to(destination)
    ):
        raise ValueError("Restore destination must be separate from source and calling checkout")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("Restore destination must be empty")
    manifest = json.loads((source / "manifest.json").read_text())
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported backup manifest")
    if not re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", manifest.get("backup_id", "")):
        raise ValueError("Unsafe backup identifier")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", manifest.get("revision", "")):
        raise ValueError("Backup revision must be a Git object identifier")
    attestation = root / ".project-local/backups" / (manifest["backup_id"] + ".json")
    if attestation.exists():
        prior = json.loads(attestation.read_text())
        if prior.get("manifest_sha256") != sha(source / "manifest.json"):
            raise ValueError("Backup manifest differs from the locally recorded capture hash")
    for name in manifest["files"]:
        safe_name(name)
        if private(name):
            raise ValueError("Private/cache paths are not allowed in the archive")
    if (
        sha(source / "files.tar") != manifest["archive_sha256"]
        or sha(source / "repository.bundle") != manifest["bundle_sha256"]
    ):
        raise ValueError("Backup payload hash mismatch")
    verify_tar(source / "files.tar", manifest["files"])
    # Restore to a sibling first; an unsuccessful restore never populates the destination.
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".audiotech-restore-", dir=destination.parent))
    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                "--no-checkout",
                str(source / "repository.bundle"),
                str(staging),
            ],
            check=True,
            capture_output=True,
        )
        git(staging, "checkout", "--quiet", "--detach", manifest["revision"])
        with tarfile.open(source / "files.tar", "r") as archive:
            for member in archive:
                name = member.name[len("files/") :]
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if any(
                    p.is_symlink() for p in [target, *target.parents] if p.is_relative_to(staging)
                ):
                    raise ValueError("Restore would traverse a symlink from Git history")
                with archive.extractfile(member) as incoming, target.open("wb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
                target.chmod(0o755 if manifest["files"][name]["executable"] else 0o644)
        # Reproduce tracked deletions in the captured working state.
        for name in tree(staging):
            if name not in manifest["files"]:
                p = staging / name
                if p.is_file() or p.is_symlink():
                    p.unlink()
        restored = file_manifest(staging, sorted(manifest["files"]))
        if restored != manifest["files"]:
            raise ValueError("Restored bytes/modes differ from the original capture")
        restored_view = View(staging)
        verification = verify_evidence(staging, restored_view)
        declarations = snapshot_hashes(restored_view)
        missing = {p: declarations.get(p) for p in verification["missing"]}
        if (
            verification["damaged"]
            or verification["uninventoried"]
            or missing != manifest["missing_original_sources"]
            or manifest["original_evidence_complete"] != (not missing)
        ):
            raise ValueError(
                "Restored evidence contradicts the capture's completeness declarations"
            )
        if destination.exists():
            destination.rmdir()
        staging.rename(destination)
        independent = manifest.get("independent", False) and independent_storage(root, source)
        write_attestation(
            root,
            {
                "backup_id": manifest["backup_id"],
                "source": str(source),
                "manifest_sha256": sha(source / "manifest.json"),
                "independent": independent,
                "restore_verified": True,
                "restored_at": now(),
                "original_evidence_complete": manifest["original_evidence_complete"],
                "evidence_fingerprint": manifest["evidence_fingerprint"],
            },
        )
        return {
            "status": "pass",
            "destination": str(destination),
            "files_verified": len(restored),
            "independent": independent,
            "original_evidence_complete": manifest["original_evidence_complete"],
            "missing_original_sources": len(manifest["missing_original_sources"]),
        }
    finally:
        if staging.exists():
            shutil.rmtree(staging)
