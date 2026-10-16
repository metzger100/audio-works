# SPDX-License-Identifier: GPL-3.0-or-later
"""Fail-closed checks; no working files, index entries or evidence are rewritten."""

import hashlib
import os
from datetime import date
from pathlib import Path
import subprocess

from .base import MAX_COMMON, MAX_ROUTE, View, git, tree
from .efficiency import inspect
from .data import load
from .evidence import archived_snapshot_gaps, preservation_status, snapshot_hashes
from .navigation import navigation_output, render
from .register import immutable
from .structure import validate, original
from .records import relationships
from .originals import declared_originals, original_destinations

HOOKS = ("pre-commit", "pre-merge-commit", "pre-applypatch", "pre-push")


def quality_metadata(view, change):
    if not change or change.get("decision") not in view.paths or not change.get("tests"):
        return ["Quality contract needs a dated decision and regression references"]
    errors = []
    stamp = change.get("date")
    try:
        if date.fromisoformat(stamp).isoformat() != stamp:
            raise ValueError("Use YYYY-MM-DD")
    except (TypeError, ValueError):
        errors.append("Quality decision needs a valid YYYY-MM-DD date")
    else:
        if stamp not in view.text(change["decision"]):
            errors.append("Quality decision text omits its registered date")
    if any(path not in view.paths for path in change["tests"]):
        errors.append("Quality regression reference missing")
    return errors


def check(view, register):
    structural = validate(view, register)
    errors = structural.pop("errors")
    efficiency = inspect(view, register)
    errors.extend(efficiency.pop("errors"))
    errors.extend(relationships(view))
    expected = render(view, register)
    stale = []
    for path, content in expected.items():
        if path not in view.paths or view.read(path) != content:
            stale.append(path)
            errors.append(f"Stale generated file: {path}; run refresh and stage the result")
    for path in view.paths:
        if navigation_output(path) and not original(path, register) and path not in expected:
            errors.append(f"Obsolete generated navigation: {path}; run refresh")
    common = list(dict.fromkeys(register["common"]))
    count = sum(len(view.text(path)) for path in common)
    if count > MAX_COMMON:
        errors.append(
            f"Common context {count} characters exceeds {MAX_COMMON}; shorten entry material without removing required policies"
        )
    words = len(expected["CURRENT.md"].decode().split())
    if words >= 300:
        errors.append(f"Current-state page has {words} words; must stay below 300")
    for stage in register["stages"]:
        if stage.get("state") not in {"planned", "partial", "complete", "blocked"}:
            errors.append(f"Unknown stage state: {stage.get('id')}")
        if stage.get("state") in {"partial", "complete"} and not stage.get("evidence"):
            errors.append(f"Stage {stage.get('id')} requires an evidence reference")
        if stage.get("evidence") and stage["evidence"] not in view.paths:
            errors.append(f"Missing stage evidence: {stage['evidence']}")
    baseline = tree(view.root, view.base)
    prior = register
    if "project.json" in baseline:
        prior_view = View(view.root, revision=view.base)
        prior = load(prior_view.text, "project.json")
    if prior.get("schema_version") == 2 and register.get("original_revision") != prior.get(
        "original_revision"
    ):
        errors.append("Original preservation baseline cannot be replaced")
    algorithm = git(view.root, "rev-parse", "--show-object-format").strip()
    relocations = original_destinations(register, prior)
    for path, (mode, oid) in baseline.items():
        if not (immutable(path, register) or immutable(path, prior)):
            continue
        from .base import current_path

        destination = current_path(relocations.get(path, path))
        if destination not in view.paths:
            errors.append(f"Deleted immutable evidence/history: {path}")
        elif view.staged or view.revision:
            if view.index[destination] != (mode, oid):
                errors.append(
                    f"Changed immutable evidence/history: {path}; create a descendant/correction"
                )
        else:
            data = view.read(destination)
            actual = hashlib.new(algorithm, f"blob {len(data)}\0".encode() + data).hexdigest()
            executable = bool((view.root / destination).stat().st_mode & 0o111)
            if actual != oid or executable != (mode == "100755"):
                errors.append(
                    f"Changed immutable evidence/history: {path}; create a descendant/correction"
                )
    errors.extend(declared_originals(view, register, prior, baseline))
    originals = register.get("original_files", {})
    external = register.get("external_files", {})
    if originals or external:
        revision = register.get("original_revision")
        if not revision:
            errors.append("Original exclusions need explicit baseline Git provenance")
        else:
            original_view = View(view.root, revision=revision)
            for path, declaration in {**originals, **external}.items():
                origin = declaration.get("original_path")
                if (
                    declaration.get("git_revision") != revision
                    or not origin
                    or origin not in original_view.paths
                ):
                    errors.append(f"Invalid original provenance: {path}")
                elif (
                    hashlib.sha256(original_view.read(origin)).hexdigest() != declaration["sha256"]
                ):
                    errors.append(f"Original provenance hash mismatch: {path}")
                if path in originals and not (
                    path.startswith(
                        (
                            "docs/history/",
                            "meridian-microphone/lab/research/",
                        )
                    )
                ):
                    errors.append(f"Original exclusion outside research/history scope: {path}")
                if path in external and not (path.startswith("LICENSES/") or "LICENSE" in path):
                    errors.append(f"External exclusion outside original licence scope: {path}")
    legacy = archived_snapshot_gaps(view)
    for path, expected_hash in snapshot_hashes(view).items():
        private_original = (
            "/source/models/semiconductor/vendor/" in path
            or "/source/research/device_sources/local/" in path
            or "/source/research/architecture_sources/local/" in path
            or "/source/tools/ngspice/" in path
            or path.endswith((".raw", ".raw.csv"))
        )
        if path in view.paths:
            if hashlib.sha256(view.read(path)).hexdigest() != expected_hash:
                errors.append(f"Changed source snapshot hash: {path}")
        elif not private_original and legacy.get(path) != expected_hash:
            errors.append(f"Missing required source snapshot: {path}")
    change = register.get("quality_change")
    if register.get("schema_version") == 2:
        errors.extend(quality_metadata(view, change))
        policy_paths = {"QUALITY.md", "AGENTS.md", "ruff.toml", "requirements-quality.txt"}
        changed = any(
            path in baseline
            and (
                view.index.get(path) != baseline[path]
                if view.staged or view.revision
                else hashlib.new(
                    algorithm, f"blob {len(view.read(path))}\0".encode() + view.read(path)
                ).hexdigest()
                != baseline[path][1]
            )
            for path in view.paths
            if not navigation_output(path)
            and (path in policy_paths or path.startswith(("tools/", ".githooks/")))
        )
        if changed and prior.get("schema_version") == 2 and change:
            decision = change["decision"]
            if (
                decision in baseline
                and hashlib.new(
                    algorithm, f"blob {len(view.read(decision))}\0".encode() + view.read(decision)
                ).hexdigest()
                == baseline[decision][1]
            ):
                errors.append(
                    "Quality/tooling changes need a new or updated dated decision with regression coverage"
                )
    return {
        "status": "fail" if errors else "pass",
        "errors": errors,
        "organization": "fail" if errors else "pass",
        **efficiency,
        "generated_files": len(expected),
        "enforcement": {
            "hooks": list(HOOKS),
            "installed": hook_installed(view.root),
            "ci": ".github/workflows/repository-quality.yml" in view.paths,
            "selected_content": "index"
            if view.staged
            else "committed"
            if view.revision
            else "working",
            "character_limit": 15000,
            "onboarding_limit": MAX_COMMON,
            "route_limit": MAX_ROUTE,
        },
        "common_characters": count,
        "estimated_tokens": round(count / 4),
        "current_words": words,
        "context_status": "pass" if count <= MAX_COMMON else "fail",
        "hook_installed": hook_installed(view.root),
        "continued_quality": "pass" if hook_installed(view.root) else "incomplete",
        "stale_generated": stale,
        **structural,
        "preservation": preservation_status(view.root, view, register),
        "note": "Repository checks do not establish scientific, procurement or legal qualification; character counts estimate tokens.",
    }


def hook_installed(root):
    result = subprocess.run(
        ["git", "-C", str(root), "config", "--local", "--get", "core.hooksPath"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == ".githooks" and all(
        (root / ".githooks" / name).is_file() and os.access(root / ".githooks" / name, os.X_OK)
        for name in HOOKS
    )


def install_hook(root):
    result = subprocess.run(
        ["git", "-C", str(root), "config", "--get", "core.hooksPath"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip() != ".githooks":
        raise ValueError(
            "Unrelated hook configuration exists; integrate it explicitly rather than overwrite it"
        )
    if result.returncode != 0:
        default = Path(git(root, "rev-parse", "--git-path", "hooks").strip())
        if not default.is_absolute():
            default = root / default
        if default.exists() and any(
            path.is_file() and not path.name.endswith(".sample") for path in default.iterdir()
        ):
            raise ValueError("Existing active default hooks require explicit integration")
    for name in HOOKS:
        hook = root / ".githooks" / name
        if not hook.is_file():
            raise ValueError(f"Managed hook source missing: {name}")
        hook.chmod(hook.stat().st_mode | 0o111)
    git(root, "config", "--local", "core.hooksPath", ".githooks")
    return {"status": "pass", "hook_installed": True, "hooks": list(HOOKS)}
