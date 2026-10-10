# SPDX-License-Identifier: GPL-3.0-or-later
"""Preserve declared originals by Git identity through verified relocations."""

import hashlib


def identity(declaration):
    if isinstance(declaration, dict):
        return declaration.get("git_revision"), declaration.get("original_path")
    return None


def declared_originals(view, register, prior, baseline):
    errors = []
    for kind in ("original_files", "external_files"):
        current = register.get(kind, {})
        previous = prior.get(kind, {})
        origins = {}
        for path, declaration in current.items():
            origin = identity(declaration)
            if origin is not None:
                if origin in origins:
                    errors.append(f"Duplicate original identity: {origins[origin]} and {path}")
                origins[origin] = path
            expected = declaration["sha256"] if isinstance(declaration, dict) else declaration
            if path not in view.paths or hashlib.sha256(view.read(path)).hexdigest() != expected:
                errors.append(f"Changed or missing declared original: {path}")
        for path, declaration in previous.items():
            origin = identity(declaration)
            destination = origins.get(origin) if origin is not None else path
            expected = declaration["sha256"] if isinstance(declaration, dict) else declaration
            replacement = current.get(destination)
            actual = replacement.get("sha256") if isinstance(replacement, dict) else replacement
            if destination is None or actual != expected:
                errors.append(f"Deleted or changed original protection: {path}")
                continue
            if destination not in view.paths:
                continue  # Current declarations already report missing bytes.
            if path in baseline:
                expected_mode = baseline[path][0]
                if view.staged or view.revision:
                    mode = view.index[destination][0]
                else:
                    mode = (
                        "100755" if (view.root / destination).stat().st_mode & 0o111 else "100644"
                    )
                if mode != expected_mode:
                    errors.append(f"Changed original execute mode: {path} -> {destination}")
    return errors
