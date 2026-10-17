# SPDX-License-Identifier: GPL-3.0-or-later
"""Task-oriented repository entry with complete, unique destinations."""

from pathlib import PurePosixPath

from .navigation import pages
from .register import link


def render_root(outputs, files, directories):
    """Group entry tasks and retain every immediate destination exactly once."""
    destinations = {
        path for path in files if "/" not in path or str(PurePosixPath(path).parent) == "docs"
    }
    destinations.update(
        directory + "/INDEX.md"
        for directory in directories
        if ("/" not in directory and directory != "docs")
        or str(PurePosixPath(directory).parent) == "docs"
    )
    destinations.add("docs/evidence.md")
    groups = {
        "Start here": [
            "docs/start-here.md",
            "README.md",
            "CURRENT.md",
            "docs/repository-layout.md",
        ],
        "Projects and artwork": sorted(
            path
            for path in destinations
            if path.endswith("/INDEX.md")
            and path.count("/") == 1
            and path.split("/")[0] not in {".githooks", ".github", "LICENSES", "tests", "tools"}
        ),
        "Maintenance and policies": [
            "CONTRIBUTING.md",
            "AGENTS.md",
            "COMPONENTS.md",
            "PATENTS.md",
            "QUALITY.md",
            "docs/maintaining-repository.md",
            "docs/documenting-hardware.md",
            "docs/quality-rules.md",
            "LICENSE",
            "project.json",
            "docs/config/INDEX.md",
            "tools/INDEX.md",
            "tests/INDEX.md",
            ".githooks/INDEX.md",
            ".github/INDEX.md",
            ".gitignore",
            "requirements-quality.txt",
            "ruff.toml",
        ],
        "Evidence, decisions and history": [
            "docs/current-evidence.md",
            "docs/evidence.md",
            "docs/history.md",
            "docs/decisions/INDEX.md",
            "docs/validation.md",
            "docs/validation/INDEX.md",
            "LICENSES/INDEX.md",
        ],
    }
    used = set()
    root_entries = []
    groups["Other references"] = sorted(
        destinations - {p for paths in groups.values() for p in paths}
    )
    labels = {
        "docs/start-here.md": "Task guide",
        "README.md": "Audio Works",
        "CURRENT.md": "Current state",
        "docs/repository-layout.md": "Folder map",
        "docs/current-evidence.md": "Current supporting records",
        "docs/evidence.md": "Original experiment metadata",
        "docs/history.md": "Preserved history",
        "docs/validation.md": "Earlier layout validation",
    }
    for title, paths in groups.items():
        selected = [path for path in paths if path in destinations and path not in used]
        if not selected:
            continue
        for index, path in enumerate(selected):
            label = labels.get(
                path, path.removesuffix("/INDEX.md") + "/" if path.endswith("/INDEX.md") else path
            )
            heading = f"\n## {title}\n\n" if index == 0 else ""
            root_entries.append(f"{heading}- [{label}]({link(path)})")
            used.add(path)
    pages(
        outputs,
        "docs/INDEX.md",
        "Repository index",
        "Choose a task or subject below. Child indexes expose complete contents; read detailed evidence when needed.",
        root_entries,
    )
