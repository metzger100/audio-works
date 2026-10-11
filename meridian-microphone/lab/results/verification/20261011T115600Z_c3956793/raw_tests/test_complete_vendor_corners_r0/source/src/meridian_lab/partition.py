# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic bounded structured output, without dropping fields or precision."""

from pathlib import PurePosixPath
import hashlib
import posixpath
import re
import yaml

from .data import canonical

TARGET = 12000


def bounded_data(value, name):
    outputs = {}
    suffix = ".yaml" if PurePosixPath(name).suffix in {".yaml", ".yml"} else ".json"
    directory = str(PurePosixPath(name).with_suffix("")) + "-parts"

    def filename(crumbs):
        label = "-".join(
            re.sub(r"[^a-z0-9]+", "-", str(crumb).lower()).strip("-") or "value" for crumb in crumbs
        )
        # Long paths stay recognizable; the full identity prevents truncated collisions.
        if len(label) > 110:
            label = label[:95].rstrip("-") + "-" + hashlib.sha256(label.encode()).hexdigest()[:12]
        return directory + "/" + label + suffix

    def encode(node):
        return (
            yaml.safe_dump(node, allow_unicode=True, sort_keys=False).encode()
            if suffix == ".yaml"
            else canonical(node)
        )

    def emit(node, destination, crumbs):
        payload = encode(node)
        if len(payload.decode()) <= TARGET:
            outputs[destination] = payload
            return
        if not isinstance(node, (dict, list)):
            raise ValueError(f"Oversized scalar needs editorial restructuring: {destination}")
        entries = list(node.items()) if isinstance(node, dict) else list(enumerate(node))
        adjusted = []
        for index, (key, child) in enumerate(entries):
            if len(encode(child).decode()) > 8000:
                identity = (
                    next(
                        (child[k] for k in ("id", "candidate", "candidate_id") if child.get(k)), key
                    )
                    if isinstance(child, dict)
                    else key
                )
                child_crumbs = (*crumbs, f"{index:04d}", str(identity))
                child_name = filename(child_crumbs)
                emit(child, child_name, child_crumbs)
                child = {"$include": posixpath.relpath(child_name, posixpath.dirname(destination))}
            adjusted.append((key, child))
        groups = []
        current = {} if isinstance(node, dict) else []
        for key, child in adjusted:
            proposal = {**current, key: child} if isinstance(node, dict) else [*current, child]
            if current and len(encode(proposal).decode()) > 10000:
                groups.append(current)
                current = {} if isinstance(node, dict) else []
            if isinstance(node, dict):
                current[key] = child
            else:
                current.append(child)
        if current:
            groups.append(current)
        references = []
        for index, group in enumerate(groups):
            part = filename((*crumbs, f"page-{index + 1:04d}"))

            # References inside the group were relative to its original parent.
            def relocate(value):
                if isinstance(value, dict):
                    if "$include" in value:
                        old = value["$include"]
                        return {
                            "$include": posixpath.relpath(
                                posixpath.join(posixpath.dirname(destination), old), directory
                            )
                        }
                    return {k: relocate(v) for k, v in value.items()}
                return [relocate(v) for v in value] if isinstance(value, list) else value

            outputs[part] = encode(relocate(group))
            references.append(posixpath.relpath(part, posixpath.dirname(destination)))
        root = {"$include": references}
        if len(encode(root).decode()) > TARGET:
            raise ValueError(f"Too many include pages: {destination}; group records semantically")
        outputs[destination] = encode(root)

    emit(value, name, ())
    return outputs
