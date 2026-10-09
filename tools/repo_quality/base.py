# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess


MAX_COMMON = 15000
MAX_FILE = 15000

MANDATORY = {
    "AGENTS.md",
    "README.md",
    "COMPONENTS.md",
    "PATENTS.md",
    "CURRENT.md",
    "QUALITY.md",
}

ENGINEERING = {"device-models", "qualification", "topology", "optimization", "reporting"}

ROUTES = ENGINEERING | {"orientation", "documentation", "branding"}

ROLES = {"active", "historical", "evidence", "generated", "proposal"}

RECORD_NAMES = {
    "results.json",
    "optimization.json",
    "verification.json",
    "failure.json",
    "checkpoint.json",
    "provenance_correction.json",
}

GENERATED = {
    "CURRENT.md",
    "docs/INDEX.md",
    "docs/evidence.md",
    "docs/evidence-index.json",
    "meridian-microphone/lab/research/prompts/prompt-pack.md",
}

PROTECTED_PREFIXES = (
    "branding/archive/",
    "meridian-microphone/lab/results/runs/",
    "meridian-microphone/lab/results/device_models/",
    "meridian-microphone/lab/results/verification/",
)

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
    if (
        not name
        or p.is_absolute()
        or any(s in {"", ".", ".."} for s in name.split("/"))
        or "\\" in name
    ):
        raise ValueError(f"Unsafe relative path: {name!r}")
    return name


def current_path(path):
    """Resolve the owner's folder rename without rewriting original records."""
    if path.startswith("meridian/"):
        return "meridian-microphone/" + path[len("meridian/") :]
    return path


def private(name):
    return any(
        p in PRIVATE_PARTS or p == ".env" or p.startswith(".env.") and p != ".env.example"
        for p in PurePosixPath(name).parts
    )


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

    def __init__(self, root, staged=False, revision=None, base=None):
        self.root = Path(root).resolve()
        self.staged = staged
        self.revision = revision
        self.base = base or "HEAD"
        self.index = {}
        self.cache = {}
        self._batch = None
        if staged and revision:
            raise ValueError("Choose either index or committed revision")
        if revision:
            git(root, "rev-parse", "--verify", revision + "^{commit}")
            self.index = tree(root, revision)
            self.paths = set(self.index)
        elif staged:
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
            names = git(
                root, "ls-files", "--cached", "--others", "--exclude-standard", "-z", binary=True
            )
            self.paths = {
                p.decode() for p in names.split(b"\0") if p and (self.root / p.decode()).is_file()
            }
        for p in self.paths:
            safe_name(p)

    def read(self, path):
        safe_name(path)
        if path not in self.cache:
            if path not in self.paths:
                raise ValueError(f"Required project file missing: {path}")
            if self.staged or self.revision:
                mode, oid = self.index[path]
                if mode == "120000":
                    raise ValueError(f"Symlink project inputs are unsupported: {path}")
                if self._batch is None:
                    self._batch = subprocess.Popen(
                        ["git", "-C", str(self.root), "cat-file", "--batch"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                    )
                self._batch.stdin.write((oid + "\n").encode())
                self._batch.stdin.flush()
                header = self._batch.stdout.readline().split()
                if len(header) != 3 or header[1] != b"blob":
                    raise ValueError(f"Index blob unavailable: {path}")
                size = int(header[2])
                data = self._batch.stdout.read(size)
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
                batch.stdin.close()
                batch.wait(timeout=1)
                batch.stdout.close()
            except (OSError, subprocess.TimeoutExpired):
                batch.kill()
                batch.wait()

    def text(self, path):
        return self.read(path).decode("utf-8")

    def exists(self, path):
        return path in self.paths or any(p.startswith(path.rstrip("/") + "/") for p in self.paths)
