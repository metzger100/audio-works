# SPDX-License-Identifier: GPL-3.0-or-later
"""Bound mutable reports and tables; originals remain complete in frozen records."""

import csv
import io
import json
from pathlib import Path
import re

from .partition import bounded_data, page_namespace
from .data import parse


def owned_parts(path):
    """Find include-owned pages; shared pages must belong to this document's namespace."""
    path = Path(path)
    directory = path.parent / (path.stem + "-parts")
    shared = path.parent / "data-pages"
    suffix = ".yaml" if path.suffix in {".yaml", ".yml"} else ".json"
    found = set()

    def visit(source):
        if source.is_symlink() or any(
            parent.is_symlink()
            for parent in source.parents
            if parent != path.parent and parent.is_relative_to(path.parent)
        ):
            raise ValueError("Symlink data pages are unsupported")
        node = parse(source.read_text(), source.suffix)

        def includes(value):
            if isinstance(value, dict):
                if "$include" in value:
                    refs = value["$include"]
                    for ref in [refs] if isinstance(refs, str) else refs:
                        target = source.parent / ref
                        if Path(ref).is_absolute() or ".." in Path(ref).parts:
                            raise ValueError("Unsafe prior data include")
                        if target.is_relative_to(shared) and (
                            target.parent != shared
                            or not target.name.startswith(page_namespace(path.name) + "-")
                            or target.suffix != suffix
                        ):
                            raise ValueError("Data page belongs to another document")
                        if (
                            target.is_relative_to(directory) or target.is_relative_to(shared)
                        ) and target not in found:
                            found.add(target)
                            visit(target)
                else:
                    for child in value.values():
                        includes(child)
            elif isinstance(value, list):
                for child in value:
                    includes(child)

        includes(node)

    if path.exists():
        visit(path)
    return found


def write_data(path, value):
    path = Path(path)
    previous = owned_parts(path)
    outputs = bounded_data(value, path.name)
    if (path.parent / "data-pages").is_symlink() or any(
        (path.parent / name).is_symlink() for name in outputs
    ):
        raise ValueError("Symlink data pages are unsupported")
    for name, payload in outputs.items():
        target = path.parent / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    for obsolete in previous - {path.parent / name for name in outputs}:
        obsolete.unlink()
    parents = {
        parent
        for page in previous
        for parent in page.parents
        if parent != path.parent and parent.is_relative_to(path.parent)
    }
    for parent in sorted(parents, key=lambda item: len(item.parts), reverse=True):
        try:
            parent.rmdir()
        except OSError:
            pass  # Remaining pages, navigation or unrelated evidence still own this directory.


def write_markdown(path, text):
    path = Path(path)
    if len(text) <= 12000:
        path.write_text(text.rstrip() + "\n")
        return
    groups = []
    current = []
    # Line boundaries retain all data, including large tables; each page repeats its header.
    for line in text.splitlines():
        if len(line) > 11000:
            raise ValueError("Oversized report line needs semantic restructuring")
        if current and len("\n".join([*current, line])) > 11000:
            groups.append(current)
            current = []
        current.append(line)
    if current:
        groups.append(current)
    directory = path.parent / (path.stem + "-pages")
    directory.mkdir(exist_ok=True)
    links = []
    for i, group in enumerate(groups, 1):
        name = f"page-{i:04d}.md"
        body = "\n".join(group)
        # Pages are one directory below their original report.
        body = re.sub(r"\]\((?![a-z]+:|#|/)([^)]+)\)", lambda m: "](../" + m[1] + ")", body)
        (directory / name).write_text(
            "# Report detail\n\n[Report hub](../" + path.name + ")\n\n" + body + "\n"
        )
        links.append(f"- [Detail {i}]({directory.name}/{name})")
    first = text.split("\n\n", 2)[:2]
    path.write_text("\n\n".join(first) + "\n\n" + "\n".join(links) + "\n")


def write_csv(path, rows, fields):
    path = Path(path)
    rows = list(rows)

    def encode(part):
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in part:
            writer.writerow(
                {
                    key: json.dumps(value) if isinstance(value, (dict, list)) else value
                    for key, value in row.items()
                }
            )
        return stream.getvalue()

    payload = encode(rows)
    if len(payload) <= 12000:
        path.write_text(payload)
        return
    directory = path.parent / (path.stem + "-pages")
    directory.mkdir(exist_ok=True)
    pages = []
    current = []

    def emit(part):
        name = f"page-{len(pages) + 1:04d}.csv"
        (directory / name).write_text(encode(part))
        pages.append(directory.name + "/" + name)

    for row in rows:
        if current and len(encode([*current, row])) > 12000:
            emit(current)
            current = []
        if len(encode([row])) > 15000:
            raise ValueError("Oversized CSV row needs semantic restructuring")
        current.append(row)
    if current:
        emit(current)
    path.with_suffix(".json").write_text(
        json.dumps(
            {"format": "csv-pages", "columns": fields, "row_count": len(rows), "pages": pages},
            indent=2,
        )
        + "\n"
    )
    path.unlink(missing_ok=True)
