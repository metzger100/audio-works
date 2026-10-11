# SPDX-License-Identifier: GPL-3.0-or-later
"""Keep entry reading bounded, prose shared and data pagination shallow."""

from collections import defaultdict
from pathlib import PurePosixPath
import re

from .base import MAX_ROUTE
from .register import classify
from .structure import MD, original


def reading_sizes(view, register):
    return {
        route: sum(len(view.text(path)) for path in dict.fromkeys(register["common"] + paths))
        for route, paths in register["routes"].items()
    }


def inspect(view, register):
    errors = []
    paragraphs = defaultdict(set)
    nested = []
    depth = 0
    for path in sorted(view.paths):
        if original(path, register):
            continue
        parts = PurePosixPath(path).parts
        depth = max(depth, len(parts) - 1)
        if sum(part.endswith("-parts") for part in parts[:-1]) > 1:
            nested.append(path)
            errors.append(f"Nested data partition: {path}; use one parts directory per document")
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
        "repeated_prose": repeated,
        "nested_data_partitions": nested,
        "maximum_maintained_directory_depth": depth,
    }
