# SPDX-License-Identifier: GPL-3.0-or-later
"""Strict structured records with explicit, bounded, relative includes."""

from pathlib import PurePosixPath
import json
import math
import posixpath

import yaml


def canonical(value):
    return (
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate mapping key: {key}")
        result[key] = value
    return result


class StrictLoader(yaml.SafeLoader):
    pass


def mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    return unique_pairs(
        (loader.construct_object(key, deep=deep), loader.construct_object(value, deep=deep))
        for key, value in node.value
    )


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def parse(text, suffix):
    if suffix == ".json":
        return json.loads(
            text,
            object_pairs_hook=unique_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"Nonfinite JSON: {value}")
            ),
        )
    value = yaml.load(text, Loader=StrictLoader)

    def finite(node):
        if isinstance(node, float) and not math.isfinite(node):
            raise ValueError("Nonfinite YAML number")
        if isinstance(node, dict):
            for key, child in node.items():
                finite(key)
                finite(child)
        elif isinstance(node, list):
            for child in node:
                finite(child)

    finite(value)
    return value


def load(read, name, *, boundary="", seen=None):
    """Read a JSON/YAML node; a sole $include key substitutes another node."""
    seen = set() if seen is None else seen
    if name in seen:
        raise ValueError(f"Include cycle: {name}")
    seen = seen | {name}
    value = parse(read(name), PurePosixPath(name).suffix)

    def resolve(node):
        if isinstance(node, dict):
            if "$include" in node:
                targets = node["$include"]
                if len(node) != 1 or not isinstance(targets, (str, list)) or not targets:
                    raise ValueError(f"$include must be a sole relative reference: {name}")
                values = []
                for target in [targets] if isinstance(targets, str) else targets:
                    if not isinstance(target, str) or not target:
                        raise ValueError(f"Invalid include reference: {name}")
                    parts = PurePosixPath(target)
                    if parts.is_absolute() or ".." in parts.parts or "\\" in target:
                        raise ValueError(f"Unsafe include: {name}: {target}")
                    destination = posixpath.normpath(
                        posixpath.join(posixpath.dirname(name), target)
                    )
                    if boundary and not destination.startswith(boundary.rstrip("/") + "/"):
                        raise ValueError(f"Include escapes boundary: {destination}")
                    values.append(load(read, destination, boundary=boundary, seen=seen))
                if isinstance(targets, str):
                    return values[0]
                if all(isinstance(value, dict) for value in values):
                    return unique_pairs(
                        (key, value) for part in values for key, value in part.items()
                    )
                if all(isinstance(value, list) for value in values):
                    return resolve([child for part in values for child in part])
                raise ValueError(
                    f"Includes must concatenate lists or merge disjoint mappings: {name}"
                )
            return {key: resolve(child) for key, child in node.items()}
        if isinstance(node, list):
            resolved = [resolve(child) for child in node]
            identities = [
                child.get("id") for child in resolved if isinstance(child, dict) and "id" in child
            ]
            if len(identities) != len(set(identities)):
                raise ValueError(f"Duplicate record identity: {name}")
            return resolved
        return node

    return resolve(value)
