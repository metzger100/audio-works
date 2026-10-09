#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bootstrap selected Git content with installed dependencies; never change files."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def selected_check(root, revision=None, base=None):
    prefix = revision + ":" if revision else ":"
    with tempfile.TemporaryDirectory(prefix="audio-works-gate-") as directory:
        snapshot = Path(directory)
        if revision:
            names = git(root, "ls-tree", "-rz", "--name-only", revision).split(b"\0")
        else:
            names = git(root, "ls-files", "-z").split(b"\0")
        for raw in names:
            name = raw.decode()
            if not name.startswith("tools/") or not name.endswith(".py"):
                continue
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(root, "show", prefix + name))
        python = root / ".project-local/quality/bin/python"
        executable = str(python) if python.is_file() else sys.executable
        arguments = ["--ref", revision, "--base", base] if revision else ["--staged"]
        result = subprocess.run(
            [
                executable,
                str(snapshot / "tools/project.py"),
                "--root",
                str(root),
                "check",
                *arguments,
            ],
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )
        if result.returncode:
            raise ValueError("Repository quality gate rejected the selected content")


def main():
    root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    if sys.argv[1] != "push":
        selected_check(root)
        return
    rows = [line.split() for line in sys.stdin if line.strip()]
    seen = set()
    for local_ref, local_oid, remote_ref, remote_oid in rows:
        if set(local_oid) == {"0"}:
            continue  # Deletion introduces no content.
        tip = git(root, "rev-parse", local_oid + "^{commit}").decode().strip()
        if set(remote_oid) != {"0"}:
            base = git(root, "rev-parse", remote_oid + "^{commit}").decode().strip()
            revisions = git(root, "rev-list", "--reverse", tip, "^" + base).decode().splitlines()
        else:
            # A new ref must check all commits unique to the outgoing branch, plus its tip.
            revisions = (
                git(root, "rev-list", "--reverse", tip, "--not", "--remotes").decode().splitlines()
            )
            base = (
                git(root, "rev-parse", tip + "^").decode().strip()
                if git(root, "rev-list", "--parents", "-n", "1", tip).decode().count(" ")
                else tip
            )
        tip_register = json.loads(git(root, "show", tip + ":project.json"))
        original = tip_register.get("original_revision")
        for revision in dict.fromkeys([*revisions, tip]):
            if (
                original
                and subprocess.run(
                    ["git", "-C", str(root), "merge-base", "--is-ancestor", revision, original],
                    check=False,
                    capture_output=True,
                ).returncode
                == 0
            ):
                # Preserved pre-gate history is not rewritten or retroactively subjected to new budgets.
                base = revision
                continue
            if (revision, base) in seen:
                continue
            selected_check(root, revision, base)
            seen.add((revision, base))
            base = revision


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Quality gate: {error}", file=sys.stderr)
        raise SystemExit(1) from error
