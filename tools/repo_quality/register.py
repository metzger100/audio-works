# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations
import posixpath
import re
from urllib.parse import quote

from .base import (
    ENGINEERING,
    GENERATED,
    MANDATORY,
    PROTECTED_PREFIXES,
    ROLES,
    ROUTES,
    current_path,
    safe_name,
)
from .data import load


def load_register(view):
    r = load(view.text, "project.json")
    if r.get("schema_version") not in {1, 2}:
        raise ValueError("Unsupported project register schema")
    for key in (
        "as_of",
        "phase",
        "readiness",
        "blockers",
        "next_action",
        "evidence",
        "stages",
        "common",
        "routes",
        "modules",
        "classifications",
        "root_files",
        "generated",
    ):
        if key not in r:
            raise ValueError(f"Register missing {key}")
    if r.get("schema_version") == 1 and set(r["generated"]) != GENERATED:
        raise ValueError("Generated destinations must match the canonical tooling contract")
    mandatory = MANDATORY | ({"CONTRIBUTING.md"} if r["schema_version"] == 2 else set())
    if not mandatory.issubset(r["common"]):
        raise ValueError("Common reading omits mandatory policies/instructions/decisions")
    if set(r["routes"]) != ROUTES:
        raise ValueError("Register must retain all eight reading routes")
    for name, paths in r["routes"].items():
        if name in ENGINEERING and "meridian-microphone/lab/CONTRACT.md" not in paths:
            raise ValueError(f"Engineering route {name} omits the scientific contract")
    for module in r["modules"]:
        prefix = module["prefix"]
        if not prefix.endswith("/") or not module.get("name") or not module.get("purpose"):
            raise ValueError("Modules need a directory prefix, name and purpose")
        safe_name(prefix.rstrip("/"))
        if r["schema_version"] == 2:
            if not module.get("index") or not module["index"].startswith(prefix):
                raise ValueError(f"Module needs its own index: {prefix}")
            safe_name(module["index"])
    prefixes = [module["prefix"] for module in r["modules"]]
    if len(set(prefixes)) != len(prefixes):
        raise ValueError("Duplicate module prefix")
    registrations = set()
    for rule in r["classifications"]:
        if ("path" in rule) == ("prefix" in rule):
            raise ValueError("Classification needs exactly one path or prefix")
        identity = ("path" if "path" in rule else "prefix", rule.get("path", rule.get("prefix")))
        if identity in registrations:
            raise ValueError("Duplicate classification registration")
        registrations.add(identity)
        target = rule.get("path", rule.get("prefix"))
        if not target or rule.get("role") not in ROLES:
            raise ValueError("Classification rules need an explicit path/prefix and role")
        safe_name(target.rstrip("/"))
    for p in r["common"] + [p for ps in r["routes"].values() for p in ps] + r["evidence"]:
        safe_name(p)
        if p not in view.paths and p not in r["generated"] and not p.endswith("/INDEX.md"):
            raise ValueError(f"Registered reading/evidence file missing: {p}")
    allowed_scopes = {
        "branding/archive/",
        "meridian-microphone/lab/results/runs/",
        "meridian-microphone/lab/results/device_models/",
        "meridian-microphone/lab/results/verification/",
        "meridian-microphone/lab/results/mechanism_controls/",
        "meridian-microphone/lab/results/optimization_batches/",
        "docs/history/",
        "meridian-microphone/lab/research/probes/",
    }
    if set(r.get("immutable_prefixes", [])) - allowed_scopes:
        raise ValueError("Immutable exclusions are limited to original evidence/history scopes")
    for path in r.get("immutable_files", []):
        inventory = path.startswith("meridian-microphone/lab/results/") and path.endswith(".sha256")
        source = (
            path.startswith("meridian-microphone/lab/research/")
            and re.search(r"\d{4}-\d{2}-\d{2}", path)
            and path.endswith((".yaml", ".json"))
        )
        if not (inventory or source or path == "docs/legacy-source-gaps.json"):
            raise ValueError("No general-purpose immutable file waiver: " + path)
    return r


def classify(path, r):
    if path in r.get("original_files", {}):
        return "historical"
    if immutable(path, r):
        return (
            "historical"
            if path.startswith(
                ("branding/archive/", "docs/history/", "meridian-microphone/lab/research/probes/")
            )
            else "evidence"
        )
    if path in r.get("external_files", {}):
        return "evidence"
    from .navigation import navigation_output

    if navigation_output(path):
        return "generated"
    if path in r["generated"]:
        return "generated"
    for rule in r["classifications"]:
        if rule.get("role") not in ROLES:
            raise ValueError("Unknown document role")
        if path == rule.get("path") or path.startswith(rule.get("prefix", "\0")):
            return rule["role"]
    if path in r["root_files"]:
        return "active"
    if any(path.startswith(m["prefix"]) for m in r["modules"]):
        return "active"
    return None


def link(path, origin="docs/INDEX.md"):
    return quote(posixpath.relpath(path, posixpath.dirname(origin) or "."), safe="/")


def headings(text):
    seen = {}
    anchors = set()
    for line in text.splitlines():
        if not re.match(r"^#{1,6}\s", line):
            continue
        slug = (
            re.sub(r"[^\w\s-]", "", re.sub(r"^#+\s*", "", line).lower()).strip().replace(" ", "-")
        )
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        anchors.add(slug + (f"-{n}" if n else ""))
    return anchors


def immutable(path, r):
    path = current_path(path)
    return (
        path == "docs/legacy-source-gaps.json"
        or path.startswith(PROTECTED_PREFIXES)
        or path.startswith(tuple(r.get("immutable_prefixes", [])))
        or path in r.get("immutable_files", [])
        or path.startswith("meridian-microphone/lab/results/")
        and path.endswith(".sha256")
    )
