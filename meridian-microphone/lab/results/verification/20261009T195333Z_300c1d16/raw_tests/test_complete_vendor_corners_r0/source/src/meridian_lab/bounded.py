# SPDX-License-Identifier: GPL-3.0-or-later
"""Bound mutable reports and tables; originals remain complete in frozen records."""

import csv
import io
import json
from pathlib import Path
import re

from .partition import bounded_data


def write_data(path, value):
    path = Path(path)
    for name, payload in bounded_data(value, path.name).items():
        target = path.parent / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)


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
