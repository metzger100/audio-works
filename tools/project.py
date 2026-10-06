#!/usr/bin/env python3
"""Local project navigation and evidence preservation; standard library only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid
from urllib.parse import quote, unquote, urlsplit

MAX_COMMON = 32000
MANDATORY = {
    "AGENTS.md", "README.md", "COMPONENTS.md", "PATENTS.md", "CURRENT.md",
    "meridian-microphone/README.md", "meridian-microphone/DECISIONS.md", "meridian-microphone/lab/AGENTS.md",
}
ENGINEERING = {"device-models", "qualification", "topology", "optimization", "reporting"}
ROUTES = ENGINEERING | {"orientation", "documentation", "branding"}
ROLES = {"active", "historical", "evidence", "generated", "proposal"}
RECORD_NAMES = {"results.json", "optimization.json", "verification.json", "failure.json",
                "checkpoint.json", "provenance_correction.json"}
GENERATED = {"CURRENT.md", "docs/INDEX.md", "docs/EVIDENCE.md", "docs/evidence-index.json",
             "meridian-microphone/lab/research/prompts/prompt_pack.md"}
PROTECTED_PREFIXES = ("branding/archive/", "meridian-microphone/lab/results/runs/",
                      "meridian-microphone/lab/results/device_models/", "meridian-microphone/lab/results/verification/")
PRIVATE_PARTS = {".git", ".aws", ".codex", ".agents", ".project-local", ".venv", "__pycache__"}


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_name(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or any(s in {"", ".", ".."} for s in name.split("/")) or "\\" in name:
        raise ValueError(f"Unsafe relative path: {name!r}")
    return name


def current_path(path):
    """Resolve the owner's folder rename without rewriting original records."""
    if path.startswith("meridian/"):
        return "meridian-microphone/" + path[len("meridian/"):]
    return path


def private(name):
    return any(p in PRIVATE_PARTS or p == ".env" or p.startswith(".env.") and p != ".env.example"
               for p in PurePosixPath(name).parts)


def git(root, *args, binary=False):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode()


def tree(root, revision="HEAD"):
    try:
        raw = git(root, "ls-tree", "-rz", revision, binary=True)
    except subprocess.CalledProcessError:
        return {}
    result = {}
    for item in raw.split(b"\0"):
        if item:
            meta, name = item.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            if kind == "blob":
                result[name.decode()] = (mode, oid)
    return result


class View:
    """Read either working files or index blobs; never substitute unstaged bytes."""
    def __init__(self, root, staged=False):
        self.root = Path(root).resolve()
        self.staged = staged
        self.index = {}
        self.cache = {}
        self._batch = None
        if staged:
            for item in git(root, "ls-files", "--stage", "-z", binary=True).split(b"\0"):
                if not item:
                    continue
                meta, name = item.split(b"\t", 1)
                mode, oid, stage = meta.decode().split()
                if stage != "0":
                    raise ValueError("Resolve unmerged index entries before checking")
                self.index[name.decode()] = (mode, oid)
            self.paths = set(self.index)
        else:
            names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z", binary=True)
            self.paths = {p.decode() for p in names.split(b"\0") if p and (self.root / p.decode()).is_file()}
        for p in self.paths:
            safe_name(p)

    def read(self, path):
        safe_name(path)
        if path not in self.cache:
            if path not in self.paths:
                raise ValueError(f"Required project file missing: {path}")
            if self.staged:
                mode, oid = self.index[path]
                if mode == "120000":
                    raise ValueError(f"Symlink project inputs are unsupported: {path}")
                if self._batch is None:
                    self._batch = subprocess.Popen(["git", "-C", str(self.root), "cat-file", "--batch"],
                                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                self._batch.stdin.write((oid + "\n").encode()); self._batch.stdin.flush()
                header = self._batch.stdout.readline().split()
                if len(header) != 3 or header[1] != b"blob":
                    raise ValueError(f"Index blob unavailable: {path}")
                size = int(header[2]); data = self._batch.stdout.read(size)
                if len(data) != size or self._batch.stdout.read(1) != b"\n":
                    raise ValueError(f"Truncated index blob: {path}")
                self.cache[path] = data
            else:
                if (self.root / path).is_symlink():
                    raise ValueError(f"Symlink project inputs are unsupported: {path}")
                self.cache[path] = (self.root / path).read_bytes()
        return self.cache[path]

    def __del__(self):
        batch = getattr(self, "_batch", None)
        if batch is not None:
            try:
                batch.stdin.close(); batch.wait(timeout=1); batch.stdout.close()
            except (OSError, subprocess.TimeoutExpired):
                batch.kill(); batch.wait()

    def text(self, path):
        return self.read(path).decode("utf-8")

    def exists(self, path):
        return path in self.paths or any(p.startswith(path.rstrip("/") + "/") for p in self.paths)


def load_register(view):
    r = json.loads(view.text("project.json"))
    if r.get("schema_version") != 1:
        raise ValueError("Unsupported project register schema")
    for key in ("as_of", "phase", "readiness", "blockers", "next_action", "evidence", "stages",
                "common", "routes", "modules", "classifications", "root_files", "generated"):
        if key not in r:
            raise ValueError(f"Register missing {key}")
    if set(r["generated"]) != GENERATED:
        raise ValueError("Generated destinations must match the canonical tooling contract")
    if not MANDATORY.issubset(r["common"]):
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
    for rule in r["classifications"]:
        target = rule.get("path", rule.get("prefix"))
        if not target or rule.get("role") not in ROLES:
            raise ValueError("Classification rules need an explicit path/prefix and role")
        safe_name(target.rstrip("/"))
    for p in r["common"] + [p for ps in r["routes"].values() for p in ps] + r["evidence"]:
        safe_name(p)
        if p not in view.paths and p not in GENERATED:
            raise ValueError(f"Registered reading/evidence file missing: {p}")
    return r


def classify(path, r):
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


def record_index(view):
    rows = []
    for p in sorted(view.paths):
        m = re.fullmatch(r"meridian-microphone/lab/results/(runs|device_models|verification)/([^/]+)/([^/]+\.json)", current_path(p))
        if not m or m[3] not in RECORD_NAMES:
            continue
        d = json.loads(view.text(p))
        manifest = d.get("source_manifest")
        rows.append({"path": p, "kind": m[1], "record_type": m[3],
                     "experiment_id": d.get("experiment_id", m[2]),
                     "timestamp_utc": d.get("timestamp_utc"), "status": d.get("status"),
                     "eligible": d.get("eligible"), "eligible_for_production": d.get("eligible_for_production"),
                     "candidate_id": d.get("candidate_id"), "parent_experiments": d.get("parent_experiments"),
                     "parent_candidates": d.get("parent_candidates"), "spec_sha256": d.get("spec_sha256"),
                     "suite_sha256": d.get("suite_sha256"), "source_unchanged": d.get("source_unchanged"),
                     "source_manifest_sha256": hashlib.sha256(canonical(manifest)).hexdigest() if manifest else None})
    return {"schema_version": 1, "note": "Original statuses retained; null means unavailable legacy metadata, not pass.", "records": rows}


def render(view, r):
    current = ["<!-- Generated by tools/project.py refresh; edit project.json. -->", "# Current project state", "",
               f"As of {r['as_of']}: **{r['phase']}**.", ""]
    for category, state in r["readiness"].items():
        current.append(f"- **{category.capitalize()}:** {state}")
    current += ["", "**Blockers:** " + " ".join(r["blockers"]), "", "**Next:** " + r["next_action"], "", "Evidence:", ""]
    current += [f"- [{Path(p).name}]({link(p, 'CURRENT.md')})" for p in r["evidence"]]
    current += ["", "[Decisions](meridian-microphone/DECISIONS.md) · [Navigation](docs/INDEX.md) · [Quality contract](QUALITY.md)", ""]
    catalog = ["<!-- Generated; edit project.json and source files. -->", "# Project module index", "",
               "Active means maintained source; proposal means unqualified work; generated means rebuildable output; historical/evidence material retains its original context.", "",
               "[Current state](../CURRENT.md) · [Quality contract](../QUALITY.md) · [Experiment index](EVIDENCE.md)", ""]
    paths = view.paths | GENERATED
    groups = {"Repository": []}
    for m in r["modules"]:
        groups[m["name"]] = []
    for p in sorted(paths):
        role = classify(p, r)
        if role == "evidence" or role == "historical" and Path(p).name != "README.md":
            continue
        matching = [m for m in r["modules"] if p.startswith(m["prefix"])]
        group = max(matching, key=lambda m: len(m["prefix"]))["name"] if matching else "Repository"
        groups[group].append(f"- [{p}]({link(p)}) — {role or 'UNCLASSIFIED'}")
    for name, entries in groups.items():
        catalog += [f"## {name}", ""]
        purpose = next((m["purpose"] for m in r["modules"] if m["name"] == name), "Canonical policies, current facts and maintenance instructions.")
        catalog += [purpose, ""] + entries + [""]
    catalog += ["## Evidence and historical collections", "",
                "- [Simulation storage](../meridian-microphone/lab/results/README.md); original runs, device experiments and verification snapshots retain their bytes and relative laboratory layout.",
                "- [Capsule reference archive](../meridian-microphone/research/reference-datasheets/README.md).",
                "- [Historical microphone identity](../branding/archive/2026-10-04-microphones/README.md).",
                "- [Historical AUDIO proposal](../branding/archive/2026-10-05-audio-proposal/README.md).", ""]
    index = record_index(view)
    evidence = ["<!-- Generated from original records; never edit experiments to fix this view. -->", "# Experiment evidence index", "",
                "Each row links original metadata, including failures, interruptions and corrections. Statuses are preserved verbatim; unknown means absent legacy metadata. Numerical verification is separate from production, procurement, patent and physical qualification.", "",
                "[Machine-readable index](evidence-index.json) · [Storage/restoration boundary](../meridian-microphone/lab/results/README.md)", "",
                "| Kind / record | Experiment | Original status |", "| --- | --- | --- |"]
    for e in index["records"]:
        status = str(e["status"] if e["status"] is not None else "unknown").replace("|", "\\|")
        evidence.append(f"| {e['kind']} / {e['record_type']} | [{e['experiment_id']}]({link(e['path'], 'docs/EVIDENCE.md')}) | {status} |")
    evidence += ["", "Original parent fields, cohorts and missing metadata are retained in the JSON index. Leaf job evidence remains reachable from each original experiment directory.", ""]
    prompts = [p for p in sorted(view.paths) if re.fullmatch(r"meridian-microphone/lab/research/prompts/\d\d_[^/]+\.md", p)]
    pack = "<!-- Generated from individual phase prompts by tools/project.py refresh. Load one representation. -->\n# Phase prompt pack\n\n" + "\n\n---\n\n".join(view.text(p).strip() for p in prompts) + "\n"
    return {"CURRENT.md": ("\n".join(current)).encode(), "docs/INDEX.md": ("\n".join(catalog)).encode(),
            "docs/EVIDENCE.md": ("\n".join(evidence)).encode(), "docs/evidence-index.json": canonical(index),
            "meridian-microphone/lab/research/prompts/prompt_pack.md": pack.encode()}


def headings(text):
    seen = {}; anchors = set()
    for line in text.splitlines():
        if not re.match(r"^#{1,6}\s", line):
            continue
        slug = re.sub(r"[^\w\s-]", "", re.sub(r"^#+\s*", "", line).lower()).strip().replace(" ", "-")
        n = seen.get(slug, 0); seen[slug] = n + 1
        anchors.add(slug + (f"-{n}" if n else ""))
    return anchors


def immutable(path, r):
    path = current_path(path)
    return path == "docs/legacy-source-gaps.json" or path.startswith(PROTECTED_PREFIXES) or path.startswith(tuple(r.get("immutable_prefixes", []))) or path in r.get("immutable_files", []) or path.startswith("meridian-microphone/lab/results/") and path.endswith(".sha256")


def check(view, r):
    errors = []
    expected = render(view, r)
    for p, content in expected.items():
        if p not in view.paths or view.read(p) != content:
            errors.append(f"Stale generated file: {p}; run refresh and stage the result")
    for p in sorted(view.paths):
        role = classify(p, r)
        if private(p):
            errors.append(f"Private/cache path included in project files: {p}")
        if role is None:
            errors.append(f"Unclassified file: {p}; register its module/role")
        if not p.endswith(".md") or role == "evidence" or role == "historical" and Path(p).name != "README.md":
            continue
        text = re.sub(r"```.*?```", "", view.text(p), flags=re.S)
        for m in re.finditer(r"\[[^\]\n]*\]\(([^)\n]+)\)", text):
            raw = m[1].strip().strip("<>")
            u = urlsplit(raw)
            if u.scheme or u.netloc:
                continue
            target = unquote(u.path)
            if target.startswith("/"):
                errors.append(f"Nonportable absolute local link in {p}: {target}")
                continue
            destination = posixpath.normpath(posixpath.join(posixpath.dirname(p), target)) if target else p
            if destination.startswith("../") or not view.exists(destination):
                errors.append(f"Broken local link in {p}: {raw}")
            elif u.fragment and destination.endswith(".md") and destination in view.paths:
                if unquote(u.fragment) not in headings(view.text(destination)):
                    errors.append(f"Broken heading link in {p}: {raw}")
    common = list(dict.fromkeys(r["common"]))
    count = sum(len(view.text(p)) for p in common)
    if count > MAX_COMMON:
        errors.append(f"Common context {count} characters exceeds {MAX_COMMON}; shorten entry material without removing required evidence")
    words = len(expected["CURRENT.md"].decode().split())
    if words >= 300:
        errors.append(f"Current-state page has {words} words; must stay below 300")
    for s in r["stages"]:
        if s.get("state") not in {"planned", "partial", "complete", "blocked"}:
            errors.append(f"Unknown stage state: {s.get('id')}")
        if s.get("state") in {"partial", "complete"} and not s.get("evidence"):
            errors.append(f"Stage {s.get('id')} requires an evidence reference")
        if s.get("evidence") and s["evidence"] not in view.paths:
            errors.append(f"Missing stage evidence: {s['evidence']}")
    # Historical blobs are immutable once committed; new experiment IDs remain allowed.
    algorithm = git(view.root, "rev-parse", "--show-object-format").strip()
    for p, (mode, oid) in tree(view.root).items():
        if not immutable(p, r):
            continue
        destination = current_path(p)
        if destination not in view.paths:
            errors.append(f"Deleted immutable evidence/history: {p}")
        elif view.staged:
            if view.index[destination] != (mode, oid):
                errors.append(f"Changed immutable evidence/history: {p}; create a descendant/correction")
        else:
            data = view.read(destination)
            actual = hashlib.new(algorithm, f"blob {len(data)}\0".encode() + data).hexdigest()
            if actual != oid:
                errors.append(f"Changed immutable evidence/history: {p}; create a descendant/correction")
    return {"status": "fail" if errors else "pass", "errors": errors,
            "organization": "fail" if any("context" not in e.lower() for e in errors) else "pass",
            "common_characters": count, "estimated_tokens": round(count / 4), "current_words": words,
            "context_status": "pass" if count <= MAX_COMMON else "fail",
            "hook_installed": hook_installed(view.root),
            "continued_quality": "pass" if hook_installed(view.root) else "incomplete",
            "preservation": preservation_status(view.root, view, r),
            "note": "Repository checks do not establish scientific, procurement or legal qualification; token counts are character-based estimates."}


def hook_installed(root):
    r = subprocess.run(["git", "-C", str(root), "config", "--local", "--get", "core.hooksPath"], capture_output=True, text=True)
    return r.stdout.strip() == ".githooks" and (root / ".githooks/pre-commit").is_file() and os.access(root / ".githooks/pre-commit", os.X_OK)


def install_hook(root):
    r = subprocess.run(["git", "-C", str(root), "config", "--get", "core.hooksPath"], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip() != ".githooks":
        raise ValueError("Unrelated hook configuration exists; integrate it explicitly rather than overwrite it")
    if r.returncode != 0:
        default = Path(git(root, "rev-parse", "--git-path", "hooks").strip())
        if not default.is_absolute():
            default = root / default
        if default.exists() and any(p.is_file() and not p.name.endswith(".sample") for p in default.iterdir()):
            raise ValueError("Existing active default hooks require explicit integration")
    hook = root / ".githooks/pre-commit"
    if not hook.is_file():
        raise ValueError("Managed hook source missing")
    hook.chmod(hook.stat().st_mode | 0o111)
    git(root, "config", "--local", "core.hooksPath", ".githooks")
    return {"status": "pass", "hook_installed": True}


def inventory(view):
    hashes = {}
    for p in sorted(view.paths):
        if not current_path(p).startswith("meridian-microphone/lab/results/") or not p.endswith(".sha256"):
            continue
        for line in view.text(p).splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            h, relative = line.split(None, 1)
            relative = relative.lstrip("*")
            safe_name(relative)
            if not re.fullmatch(r"[0-9a-f]{64}", h):
                raise ValueError(f"Invalid SHA256 in {p}")
            path = posixpath.dirname(posixpath.dirname(p)) + "/" + relative
            if path in hashes and hashes[path] != h:
                raise ValueError(f"Conflicting immutable inventory declarations: {path}")
            hashes[path] = h
    return hashes


def original_waveforms(root):
    folders = [root / name / "lab/results" for name in ("meridian-microphone", "meridian")]
    return {p.relative_to(root).as_posix() for folder in folders for p in folder.rglob("*")
            if p.is_file() and not p.is_symlink() and p.name.endswith((".raw", ".raw.csv"))}


def snapshot_hashes(view):
    expected = {}
    for p in sorted(view.paths):
        if not re.fullmatch(r"meridian-microphone/lab/results/(runs|device_models|verification)/[^/]+/[^/]+\.json", current_path(p)) or Path(p).name not in RECORD_NAMES:
            continue
        d = json.loads(view.text(p))
        for relative, h in d.get("source_manifest", {}).items():
            safe_name(relative)
            name = posixpath.dirname(p) + "/source/" + relative
            if name in expected and expected[name] != h:
                raise ValueError(f"Conflicting source snapshot declarations: {name}")
            expected[name] = h
    return expected


def verify_evidence(root, view):
    declared = inventory(view)
    expected = {**snapshot_hashes(view), **declared}
    missing = []; damaged = []
    for name, h in sorted(expected.items()):
        p = root / name
        if not p.is_file() or p.is_symlink():
            missing.append(name)
        elif sha(p) != h:
            damaged.append(name)
    extra = sorted(original_waveforms(root) - declared.keys())
    return {"status": "pass" if not (missing or damaged or extra) else "incomplete" if missing and not (damaged or extra) else "fail",
            "declared_waveforms": len(declared), "snapshot_files": len(expected) - len(declared),
            "missing": missing, "damaged": damaged, "uninventoried": extra,
            "note": "Missing original local bytes require restoration; reruns or reacquisition do not recover original evidence."}


def ensure_idle(root):
    proc = Path("/proc")
    if not proc.exists():
        raise ValueError("Cannot establish evaluator idleness on this platform; capture on a supported idle Linux host")
    markers = ("meridian_lab.cli", "characterize.py", "optimize_values.py", "search/loop.py", "ngspice")
    for p in proc.iterdir():
        if not p.name.isdigit() or int(p.name) == os.getpid():
            continue
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            cwd = (p / "cwd").resolve()
        except (OSError, RuntimeError):
            continue
        if (str(root) in cmd or cwd.is_relative_to(root)) and any(m in cmd for m in markers):
            raise ValueError("An evaluator/simulator is active; wait for stable idle sources before capture")


def backup_paths(root, view, r):
    paths = set(view.paths)
    for prefix in r["backup_evidence_prefixes"]:
        safe_name(prefix.rstrip("/"))
        paths.update(p.relative_to(root).as_posix() for p in (root / prefix).rglob("*") if p.is_file())
    paths.update(original_waveforms(root))
    for p in (root / "meridian-microphone/lab/results").rglob("*"):
        relative = p.relative_to(root).as_posix()
        if p.is_file() and ("/source/models/semiconductor/vendor/" in relative or "/source/research/device_sources/local/" in relative):
            paths.add(relative)
    for p in paths:
        safe_name(p)
        if private(p) or classify(p, r) is None:
            raise ValueError(f"Unapproved backup input: {p}")
        if (root / p).is_symlink() or not (root / p).is_file():
            raise ValueError(f"Backup inputs must be regular files: {p}")
    return sorted(paths)


def file_manifest(root, paths):
    return {p: {"size": (root / p).stat().st_size, "sha256": sha(root / p),
                "executable": bool((root / p).stat().st_mode & 0o111)} for p in paths}


def evidence_fingerprint(view):
    # Coverage of declared original evidence, independent of generated navigation.
    paths = [p for p in view.paths if current_path(p).startswith("meridian-microphone/lab/results/") or p.startswith("branding/archive/")]
    hashes = {p: hashlib.sha256(view.read(p)).hexdigest() for p in sorted(paths)}
    return hashlib.sha256(canonical(hashes)).hexdigest()


def independent_storage(root, destination):
    destination = destination.resolve()
    volatile = (Path("/tmp"), Path("/dev/shm"), Path("/run"))
    if destination.is_relative_to(root) or any(destination.is_relative_to(p) for p in volatile):
        return False
    if destination.stat().st_dev == root.stat().st_dev:
        return False
    # Different device alone is insufficient for tmpfs/ramfs mounts.
    if Path("/proc/mounts").exists():
        matches = []
        for line in Path("/proc/mounts").read_text().splitlines():
            fields = line.split()
            mount = Path(fields[1].replace("\\040", " "))
            if destination.is_relative_to(mount):
                matches.append((len(str(mount)), fields[2]))
        if matches and max(matches)[1] in {"tmpfs", "ramfs"}:
            return False
    return True


def write_attestation(root, data):
    if not re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", data.get("backup_id", "")):
        raise ValueError("Unsafe backup identifier")
    folder = root / ".project-local/backups"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    p = folder / (data["backup_id"] + ".json")
    p.write_bytes(canonical(data)); p.chmod(0o600)


def preservation_status(root, view, r):
    fingerprint = evidence_fingerprint(view)
    folder = root / ".project-local/backups"
    for p in sorted(folder.glob("*.json"), reverse=True):
        d = json.loads(p.read_text())
        if d.get("independent") and d.get("restore_verified") and d.get("evidence_fingerprint") == fingerprint:
            source = Path(d["source"])
            manifest = source / "manifest.json"
            if manifest.is_file() and sha(manifest) == d.get("manifest_sha256"):
                if not d.get("original_evidence_complete", False):
                    return {"status": "incomplete", "restored_at": d["restored_at"],
                            "note": "Independent available-byte backup restored; declared original source gaps remain."}
                return {"status": "attested", "restored_at": d["restored_at"],
                        "note": "Independent restored backup covers declared evidence. Run evidence verify for current local-byte integrity."}
    return {"status": "incomplete", "note": "No independent restored backup covering the current declared evidence is attested. Local bytes are not hashed by the fast gate."}


def create_backup(root, destination, independent=False):
    ensure_idle(root)
    view = View(root); r = load_register(view)
    verification = verify_evidence(root, view)
    legacy = {}
    if "docs/legacy-source-gaps.json" in view.paths:
        legacy = {current_path(p): h for p, h in json.loads(view.text("docs/legacy-source-gaps.json"))["missing_sources"].items()}
    declarations = snapshot_hashes(view)
    known_missing = all(p in legacy and legacy[p] == declarations.get(p) for p in verification["missing"])
    if verification["damaged"] or verification["uninventoried"] or not known_missing:
        raise ValueError("Original evidence verification failed; resolve damage, new missing files or undeclared inputs. Known legacy gaps remain explicit.")
    destination = Path(destination).resolve()
    if destination.is_relative_to(root):
        raise ValueError("Backup destination must be outside this checkout")
    if not destination.is_dir():
        raise ValueError("Destination must be an existing owner-chosen storage directory")
    if independent and not independent_storage(root, destination):
        raise ValueError("Independent storage must be persistent, outside this checkout and on a different device")
    id_ = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    partial = destination / (".audiotech-" + id_ + ".partial")
    output = destination / ("audiotech-" + id_)
    partial.mkdir(mode=0o700)
    try:
        paths = backup_paths(root, view, r)
        before = file_manifest(root, paths)
        revision = git(root, "rev-parse", "HEAD").strip()
        refs = git(root, "show-ref")
        git(root, "bundle", "create", str(partial / "repository.bundle"), "--all")
        with tarfile.open(partial / "files.tar", "w") as archive:
            for name in paths:
                archive.add(root / name, arcname="files/" + name, recursive=False)
        ensure_idle(root)
        after_view = View(root)
        if backup_paths(root, after_view, load_register(after_view)) != paths or file_manifest(root, paths) != before or git(root, "rev-parse", "HEAD").strip() != revision or git(root, "show-ref") != refs:
            raise ValueError("Inputs changed during capture; inconsistent backup rejected")
        # Verify the captured bytes rather than relying only on unchanged source files.
        verify_tar(partial / "files.tar", before)
        manifest = {"schema_version": 1, "backup_id": id_, "captured_at": now(), "revision": revision,
                    "independent": independent, "files": before,
                    "original_evidence_complete": not verification["missing"],
                    "missing_original_sources": {p: declarations[p] for p in verification["missing"]},
                    "archive_sha256": sha(partial / "files.tar"), "bundle_sha256": sha(partial / "repository.bundle"),
                    "evidence_fingerprint": evidence_fingerprint(after_view)}
        (partial / "manifest.json").write_bytes(canonical(manifest))
        partial.rename(output)
        write_attestation(root, {"backup_id": id_, "source": str(output), "manifest_sha256": sha(output / "manifest.json"),
                               "independent": independent, "restore_verified": False,
                               "original_evidence_complete": manifest["original_evidence_complete"],
                               "evidence_fingerprint": manifest["evidence_fingerprint"]})
        return {"status": "pass" if manifest["original_evidence_complete"] else "incomplete", "capture_verified": True,
                "source": str(output), "file_count": len(paths), "independent": independent,
                "missing_original_sources": len(verification["missing"]),
                "note": "Capture verified. Full preservation also requires independent persistent storage and a successful restore."}
    except BaseException:
        shutil.rmtree(partial, ignore_errors=True)
        raise


def verify_tar(path, files):
    seen = set()
    with tarfile.open(path, "r") as archive:
        for member in archive:
            safe_name(member.name)
            if not member.name.startswith("files/") or not member.isfile():
                raise ValueError("Only allowlisted regular-file archive members are accepted")
            name = member.name[len("files/"):]
            safe_name(name)
            if private(name) or name not in files or name in seen:
                raise ValueError(f"Unsafe, duplicate or undeclared archive member: {name}")
            seen.add(name)
            h = hashlib.sha256()
            stream = archive.extractfile(member)
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
            if h.hexdigest() != files[name]["sha256"] or member.size != files[name]["size"]:
                raise ValueError(f"Captured evidence differs from its manifest: {name}")
    if seen != set(files):
        raise ValueError("Archive omits declared files")


def restore_backup(root, source, destination):
    source = Path(source).resolve(); destination = Path(destination).resolve()
    if destination == root or destination.is_relative_to(root) or destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError("Restore destination must be separate from source and calling checkout")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("Restore destination must be empty")
    manifest = json.loads((source / "manifest.json").read_text())
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported backup manifest")
    if not re.fullmatch(r"\d{8}T\d{6}Z_[0-9a-f]{8}", manifest.get("backup_id", "")):
        raise ValueError("Unsafe backup identifier")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", manifest.get("revision", "")):
        raise ValueError("Backup revision must be a Git object identifier")
    attestation = root / ".project-local/backups" / (manifest["backup_id"] + ".json")
    if attestation.exists():
        prior = json.loads(attestation.read_text())
        if prior.get("manifest_sha256") != sha(source / "manifest.json"):
            raise ValueError("Backup manifest differs from the locally recorded capture hash")
    for name in manifest["files"]:
        safe_name(name)
        if private(name):
            raise ValueError("Private/cache paths are not allowed in the archive")
    if sha(source / "files.tar") != manifest["archive_sha256"] or sha(source / "repository.bundle") != manifest["bundle_sha256"]:
        raise ValueError("Backup payload hash mismatch")
    verify_tar(source / "files.tar", manifest["files"])
    # Restore to a sibling first; an unsuccessful restore never populates the destination.
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".audiotech-restore-", dir=destination.parent))
    try:
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", str(source / "repository.bundle"), str(staging)], check=True, capture_output=True)
        git(staging, "checkout", "--quiet", "--detach", manifest["revision"])
        with tarfile.open(source / "files.tar", "r") as archive:
            for member in archive:
                name = member.name[len("files/"):]
                target = staging / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if any(p.is_symlink() for p in [target, *target.parents] if p.is_relative_to(staging)):
                    raise ValueError("Restore would traverse a symlink from Git history")
                with archive.extractfile(member) as incoming, target.open("wb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
                target.chmod(0o755 if manifest["files"][name]["executable"] else 0o644)
        # Reproduce tracked deletions in the captured working state.
        for name in tree(staging):
            if name not in manifest["files"]:
                p = staging / name
                if p.is_file() or p.is_symlink():
                    p.unlink()
        restored = file_manifest(staging, sorted(manifest["files"]))
        if restored != manifest["files"]:
            raise ValueError("Restored bytes/modes differ from the original capture")
        restored_view = View(staging)
        verification = verify_evidence(staging, restored_view)
        declarations = snapshot_hashes(restored_view)
        missing = {p: declarations.get(p) for p in verification["missing"]}
        if verification["damaged"] or verification["uninventoried"] or missing != manifest["missing_original_sources"] or manifest["original_evidence_complete"] != (not missing):
            raise ValueError("Restored evidence contradicts the capture's completeness declarations")
        if destination.exists():
            destination.rmdir()
        staging.rename(destination)
        independent = manifest.get("independent", False) and independent_storage(root, source)
        write_attestation(root, {"backup_id": manifest["backup_id"], "source": str(source),
                               "manifest_sha256": sha(source / "manifest.json"), "independent": independent,
                               "restore_verified": True, "restored_at": now(),
                               "original_evidence_complete": manifest["original_evidence_complete"],
                               "evidence_fingerprint": manifest["evidence_fingerprint"]})
        return {"status": "pass", "destination": str(destination), "files_verified": len(restored), "independent": independent,
                "original_evidence_complete": manifest["original_evidence_complete"],
                "missing_original_sources": len(manifest["missing_original_sources"])}
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def new_inventory(root, view):
    ensure_idle(root)
    declared = inventory(view)
    damaged = [p for p, h in declared.items() if not (root / p).is_file() or sha(root / p) != h]
    if damaged:
        raise ValueError("Resolve existing inventory damage before recording new evidence")
    new = sorted(original_waveforms(root) - declared.keys())
    if not new:
        return {"status": "pass", "new_files": 0, "note": "All existing original waveforms already inventoried."}
    lines = [sha(root / p) + "  " + p.removeprefix("meridian-microphone/lab/") for p in new]
    name = "evidence-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8] + ".sha256"
    destination = root / "meridian-microphone/lab/results" / name
    # Retain the observation only if the new evidence remained stable during hashing.
    ensure_idle(root)
    if sorted(original_waveforms(root) - declared.keys()) != new:
        raise ValueError("Evidence set changed while creating its inventory")
    for line, p in zip(lines, new):
        if sha(root / p) != line.split()[0]:
            raise ValueError("Evidence bytes changed while creating their inventory")
    with destination.open("x") as f:
        f.write("\n".join(lines) + "\n")
    return {"status": "pass", "new_files": len(new), "inventory": str(destination.relative_to(root))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="command", required=True)
    context = sub.add_parser("context"); context.add_argument("route", choices=sorted(ROUTES))
    for cmd in ("files", "search"):
        p = sub.add_parser(cmd); p.add_argument("--include-evidence", action="store_true"); p.add_argument("--include-history", action="store_true"); p.add_argument("--include-generated", action="store_true")
        if cmd == "search":
            p.add_argument("pattern")
    sub.add_parser("refresh")
    p = sub.add_parser("check"); p.add_argument("--staged", action="store_true")
    p = sub.add_parser("hooks"); p.add_argument("action", choices=["install"])
    e = sub.add_parser("evidence").add_subparsers(dest="action", required=True)
    e.add_parser("verify"); e.add_parser("inventory")
    p = e.add_parser("backup"); p.add_argument("--destination", required=True, type=Path); p.add_argument("--independent", action="store_true")
    p = e.add_parser("restore"); p.add_argument("--source", required=True, type=Path); p.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args(argv); root = args.root.resolve()
    try:
        if args.command == "hooks":
            result = install_hook(root)
        elif args.command == "evidence" and args.action == "backup":
            result = create_backup(root, args.destination, args.independent)
        elif args.command == "evidence" and args.action == "restore":
            result = restore_backup(root, args.source, args.destination)
        else:
            view = View(root, getattr(args, "staged", False)); r = load_register(view)
            if args.command == "check":
                result = check(view, r)
            elif args.command == "refresh":
                changed = []
                for p, data in render(view, r).items():
                    target = root / p
                    if not target.exists() or target.read_bytes() != data:
                        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data); changed.append(p)
                result = {"status": "pass", "updated": changed}
            elif args.command == "context":
                paths = list(dict.fromkeys(r["common"] + r["routes"][args.route]))
                common_count = sum(len(view.text(p)) for p in dict.fromkeys(r["common"]))
                result = {"route": args.route, "common_characters": common_count,
                          "estimated_common_tokens": round(common_count / 4),
                          "reading": [{"path": p, "role": classify(p, r), "purpose": "Mandatory entry context" if p in r["common"] else "Task-specific contract/evidence", "characters": len(view.text(p))} for p in paths],
                          "note": "Read the listed material before affected work; inspect additional relevant code/evidence on demand. Load one prompt representation."}
            elif args.command in {"files", "search"}:
                paths = [p for p in sorted(view.paths) if (classify(p, r) != "evidence" or args.include_evidence) and (classify(p, r) != "historical" or args.include_history) and (classify(p, r) != "generated" or args.include_generated)]
                if args.command == "files":
                    print("\n".join(paths)); return 0
                if not paths:
                    return 1
                return subprocess.run(["rg", "-n", "--", args.pattern, *paths], cwd=root).returncode
            elif args.command == "evidence":
                result = verify_evidence(root, view) if args.action == "verify" else new_inventory(root, view)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("status", "pass") == "pass" else 1
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError, subprocess.CalledProcessError, tarfile.TarError) as error:
        print(json.dumps({"status": "fail", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
