# SPDX-License-Identifier: GPL-3.0-or-later
"""Keep entry reading bounded, prose shared and data pagination shallow."""

from collections import defaultdict
from pathlib import PurePosixPath
import re

from .base import MAX_ROUTE
from .register import classify
from .structure import MD, original
from .discovery import discovery_sizes


def folder_inventory(view, register):
    """Count directories in the selected Git view, excluding local runtimes/caches."""

    def parents(paths):
        return {
            str(parent)
            for path in paths
            for parent in PurePosixPath(path).parents
            if str(parent) != "."
        }

    maintained = parents(path for path in view.paths if not original(path, register))
    all_directories = parents(view.paths)
    pages = {
        path for path in maintained if PurePosixPath(path).name in {"data-pages", "index-pages"}
    }
    by_root = defaultdict(int)
    for path in maintained:
        by_root[path.split("/")[0]] += 1
    return {
        "maintained": len(maintained),
        "original_only": len(all_directories - maintained),
        "page_containers": len(pages),
        "data_page_containers": sum(PurePosixPath(path).name == "data-pages" for path in pages),
        "navigation_page_containers": sum(
            PurePosixPath(path).name == "index-pages" for path in pages
        ),
        "by_root": dict(sorted(by_root.items())),
    }


def reading_sizes(view, register):
    return {
        route: sum(len(view.text(path)) for path in dict.fromkeys(register["common"] + paths))
        for route, paths in register["routes"].items()
    }


def inspect(view, register):
    errors = []
    paragraphs = defaultdict(set)
    nested = []
    noncanonical = []
    depth = 0
    for path in sorted(view.paths):
        if original(path, register):
            continue
        parts = PurePosixPath(path).parts
        depth = max(depth, len(parts) - 1)
        if sum(part.endswith("-parts") for part in parts[:-1]) > 1:
            nested.append(path)
            errors.append(f"Nested data partition: {path}; use shared data-pages")
        if any(part.endswith("-parts") for part in parts[:-1]) or any(
            part == "index-pages"
            and index != len(parts) - 2
            or part == "data-pages"
            and parts[index + 1 : -1] not in {(), ("index-pages",)}
            for index, part in enumerate(parts[:-1])
        ):
            noncanonical.append(path)
            errors.append(f"Redundant page directory: {path}; use one flat container per parent")
        if not path.endswith(".md") or classify(path, register) == "generated":
            continue
        tokens = MD.parse(view.text(path))
        for index, token in enumerate(tokens):
            if token.type != "paragraph_open":
                continue
            # Compare rendered prose; different relative URLs do not disguise copies.
            inline = tokens[index + 1]
            visible = "".join(
                child.content if child.type not in {"softbreak", "hardbreak"} else " "
                for child in inline.children or []
                if child.type not in {"html_inline", "image"}
            )
            prose = re.sub(r"\s+", " ", visible).strip()
            if len(prose) >= 180:
                paragraphs[prose].add(path)
    repeated = [
        {"files": sorted(paths), "repeated_characters": len(prose) * (len(paths) - 1)}
        for prose, paths in paragraphs.items()
        if len(paths) > 1
    ]
    errors.extend(
        "Repeated prose across documents: " + ", ".join(item["files"]) for item in repeated
    )
    sizes = reading_sizes(view, register)
    errors.extend(
        f"Reading route {route}: {size} > {MAX_ROUTE} characters; scope references through hubs"
        for route, size in sizes.items()
        if size > MAX_ROUTE
    )
    return {
        "errors": errors,
        "reading_sizes": sizes,
        "discovery": discovery_sizes(view, register),
        "repeated_prose": repeated,
        "nested_data_partitions": nested,
        "noncanonical_page_directories": noncanonical,
        "folders": folder_inventory(view, register),
        "maximum_maintained_directory_depth": depth,
    }
