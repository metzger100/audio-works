# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic bounded structured output, without dropping fields or precision."""

from pathlib import PurePosixPath
import posixpath
import re
import yaml

from .data import canonical

TARGET = 12000


def bounded_data(value, name):
    outputs = {}
    suffix = ".yaml" if PurePosixPath(name).suffix in {".yaml", ".yml"} else ".json"

    def encode(node):
        return (
            yaml.safe_dump(node, allow_unicode=True, sort_keys=False).encode()
            if suffix == ".yaml"
            else canonical(node)
        )

    def emit(node, destination):
        payload = encode(node)
        if len(payload.decode()) <= TARGET:
            outputs[destination] = payload
            return
        if not isinstance(node, (dict, list)):
            raise ValueError(f"Oversized scalar needs editorial restructuring: {destination}")
        directory = str(PurePosixPath(destination).with_suffix("")) + "-parts"
        entries = list(node.items()) if isinstance(node, dict) else list(enumerate(node))
        adjusted = []
        for index, (key, child) in enumerate(entries):
            if len(encode(child).decode()) > 8000:
                label = child.get("id", key) if isinstance(child, dict) else key
                label = re.sub(r"[^a-z0-9]+", "-", str(label).lower()).strip("-")[:64] or "value"
                child_name = f"{directory}/{index:04d}-{label}{suffix}"
                emit(child, child_name)
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
            part = f"{directory}/page-{index + 1:04d}{suffix}"

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

    emit(value, name)
    return outputs
