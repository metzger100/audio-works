# SPDX-License-Identifier: GPL-3.0-or-later
"""Run lint and fast regressions against the selected content, never unstaged code."""

from pathlib import Path
import os
import subprocess
import sys
import tempfile

from .structure import original


def executable(root):
    local = root / ".project-local/quality/bin/python"
    return str(local) if local.is_file() else sys.executable


def fast_checks(view, register):
    with tempfile.TemporaryDirectory(prefix="audio-works-quality-") as directory:
        snapshot = Path(directory)
        sources = []
        for name in sorted(view.paths):
            if original(name, register):
                continue
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(view.read(name))
            if name.endswith(".py") or name == ".githooks/pre-push":
                sources.append(name)
        python = executable(view.root)
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        environment.pop("PYTHONPATH", None)
        dependency_probe = (
            "import importlib.metadata as m; expected="
            + repr(
                dict(
                    line.split("==")
                    for line in view.text("requirements-quality.txt").splitlines()
                    if "==" in line
                )
            )
            + "; assert all(m.version(k)==v for k,v in expected.items()), 'Install the pinned quality dependencies before using the gate'"
        )
        commands = [
            [python, "-c", dependency_probe],
            [python, "-m", "ruff", "check", "--no-cache", "--config", "ruff.toml", *sources],
            [
                python,
                "-m",
                "ruff",
                "format",
                "--check",
                "--no-cache",
                "--config",
                "ruff.toml",
                *sources,
            ],
            [python, "-m", "unittest", "discover", "-s", "tests/quality", "-q"],
        ]
        records = []
        for command in commands:
            result = subprocess.run(
                command, cwd=snapshot, env=environment, text=True, capture_output=True, timeout=120
            )
            records.append(
                {
                    "check": " ".join(command[2:5]),
                    "status": "pass" if result.returncode == 0 else "fail",
                    "output": (result.stdout + result.stderr)[-8000:],
                }
            )
        return {
            "status": "pass" if all(row["status"] == "pass" for row in records) else "fail",
            "checks": records,
        }
