# SPDX-License-Identifier: GPL-3.0-or-later
"""Scoped discovery without expanding evidence or internal data pages by default."""

import os
from pathlib import PurePosixPath
import subprocess

from .base import safe_name
from .register import classify

SEARCH_ARGUMENT_BYTES = 32000


def data_page(path):
    return "data-pages" in PurePosixPath(path).parts[:-1]


def select_paths(
    view,
    register,
    *,
    include_evidence=False,
    include_history=False,
    include_generated=False,
    include_data_pages=False,
    path=None,
):
    prefix = safe_name(path.removesuffix("/")) if path is not None else None
    excluded = set()
    for role, included in (
        ("evidence", include_evidence),
        ("historical", include_history),
        ("generated", include_generated),
    ):
        if not included:
            excluded.add(role)
    return [
        name
        for name in sorted(view.paths)
        if (prefix is None or name == prefix or name.startswith(prefix + "/"))
        and (include_data_pages or not data_page(name))
        and classify(name, register) not in excluded
    ]


def search(root, paths, pattern, *, files_with_matches=False):
    """Preserve ripgrep's 0/1/2 outcomes across bounded, explicitly named batches."""
    command = [
        "rg",
        "--with-filename",
        "--no-heading",
        "--color=never",
        "--sort=path",
        "--files-with-matches" if files_with_matches else "--line-number",
        "--",
        pattern,
    ]
    overhead = sum(len(os.fsencode(arg)) + 9 for arg in command)
    if overhead >= SEARCH_ARGUMENT_BYTES:
        raise ValueError("Search pattern exceeds the argument batch size")
    batches = []
    current = []
    size = overhead
    for path in paths:
        weight = len(os.fsencode(path)) + 9
        if overhead + weight > SEARCH_ARGUMENT_BYTES:
            raise ValueError("Search path exceeds the argument batch size")
        if size + weight > SEARCH_ARGUMENT_BYTES:
            batches.append(current)
            current = []
            size = overhead
        current.append(path)
        size += weight
    if current:
        batches.append(current)
    matched = False
    for batch in batches:
        code = subprocess.run([*command, *batch], cwd=root).returncode
        if code not in {0, 1}:
            return 2
        matched |= code == 0
    return 0 if matched else 1


def discovery_sizes(view, register):
    groups = {"default": [], "data_pages": []}
    for path in select_paths(view, register, include_data_pages=True):
        groups["data_pages" if data_page(path) else "default"].append(path)
    report = {}
    for group, paths in groups.items():
        characters = binary = 0
        for path in paths:
            try:
                characters += len(view.text(path))
            except UnicodeDecodeError:
                binary += 1
        report[group] = {
            "files": len(paths),
            "text_characters": characters,
            "estimated_tokens": round(characters / 4),
            "binary_files": binary,
        }
    report["note"] = "Text characters / 4 estimates tokens; binary files are counted separately."
    return report
