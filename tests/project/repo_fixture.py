"""Repository gates and recovery cases; fixtures never touch lab evidence."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("project_tools", REPO / "tools/project.py")
project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)


class RepositoryFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="audiotech-quality-test-")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / "repo"
        self.root.mkdir()
        self.run_git("init", "--quiet")
        self.run_git("config", "user.name", "Local test fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.register = project.load_register(project.View(REPO))
        self.register["original_files"] = {}
        self.register["external_files"] = {}
        self.register = json.loads(
            json.dumps(self.register).replace(
                "architecture_comparison_001_2026-10-09.yaml", "comparison-2026-10-09.yaml"
            )
        )
        paths = set(
            self.register["common"]
            + self.register["evidence"]
            + [stage["evidence"] for stage in self.register["stages"]]
        )
        for values in self.register["routes"].values():
            paths.update(values)
        paths.update(
            {
                "meridian-microphone/lab/results/README.md",
                "meridian-microphone/research/reference-datasheets/README.md",
                "branding/archive/2026-10-04-microphones/README.md",
                "branding/archive/2026-10-05-audio-proposal/README.md",
                "QUALITY.md",
                "CONTRIBUTING.md",
            }
        )
        for name in paths - project.GENERATED:
            self.put(name, "# Fixture\n\nRetained fixture content.\n")
        self.put(
            ".gitignore",
            ".project-local/\n/meridian-microphone/lab/results/**/*.raw\n/meridian-microphone/lab/results/**/*.raw.csv\n/tools/__pycache__/\n__pycache__/\n",
        )
        for name in (
            [
                str(p.relative_to(REPO))
                for base in [
                    REPO / "tools",
                    REPO / "tests/quality",
                    REPO / "meridian-microphone/lab/src/meridian_lab",
                ]
                for p in base.rglob("*.py")
                if "__pycache__" not in p.parts
                and (base.name != "meridian_lab" or p.name in {"data.py", "partition.py"})
            ]
            + [
                ".githooks/" + name
                for name in ("pre-commit", "pre-merge-commit", "pre-applypatch", "pre-push")
            ]
            + ["ruff.toml", "requirements-quality.txt"]
        ):
            self.put(name, (REPO / name).read_text())
            if name.startswith(".githooks/"):
                (self.root / name).chmod(0o755)
        for i, name in enumerate(
            [
                "device_models",
                "qualification",
                "architectures",
                "robust_optimization",
                "comparative_report",
            ],
            1,
        ):
            self.put(
                f"meridian-microphone/lab/research/prompts/{i:02d}-{name.replace(chr(95), chr(45))}.md",
                f"# Prompt {i}\n\nPreserve the original evidence.\n",
            )
        self.put(
            self.register["evidence"][1],
            json.dumps({"status": "pass", "source_manifest": {}}) + "\n",
        )
        self.put(
            "docs/history/2026-10-09/meridian-microphone/lab/research/experiment_log.md",
            "# Original fixture memory\n",
        )
        self.register["quality_change"] = {
            "date": "2026-10-10",
            "decision": "docs/decisions/2026-10-09-repository-structure.md",
            "tests": ["tests/quality/test_data.py", "tests/quality/test_structure.py"],
        }
        self.put(
            self.register["quality_change"]["decision"],
            "# Dated fixture decision, 2026-10-10\n\nPreserve gate regression coverage.\n",
        )
        self.put("tests/project/test_hooks.py", "# Fixture regression pointer\n")
        local = self.root / ".project-local"
        local.mkdir()
        (local / "quality").symlink_to(REPO / ".project-local/quality", target_is_directory=True)
        self.save_register()
        self.refresh()
        self.run_git("add", ".")
        self.run_git(
            "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Fixture baseline"
        )

    def run_git(self, *args, check=True):
        return subprocess.run(
            ["git", "-C", str(self.root), *args], text=True, capture_output=True, check=check
        )

    def put(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def save_register(self):
        from repo_quality.partition import bounded_data

        register = dict(self.register)
        for key in ("modules", "routes", "classifications"):
            name = "docs/config/" + key + ".json"
            for path, data in bounded_data(register[key], name).items():
                self.put(path, data.decode())
            register[key] = {"$include": name}
        self.put("project.json", json.dumps(register, indent=2) + "\n")

    def refresh(self):
        view = project.View(self.root)
        for name, data in project.render(view, project.load_register(view)).items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)

    def check(self, staged=False):
        view = project.View(self.root, staged)
        return project.check(view, project.load_register(view))

    def add_wave(self):
        path = "meridian-microphone/lab/results/runs/new_batch/job/ac.raw"
        self.put(path, "original failed waveform\n")
        self.put(
            "meridian-microphone/lab/results/new-wave.sha256",
            hashlib.sha256((self.root / path).read_bytes()).hexdigest()
            + "  "
            + path.removeprefix("meridian-microphone/lab/")
            + "\n",
        )
        self.refresh()
        return path

    def backup(self):
        self.add_wave()
        with patch.object(project.backup, "ensure_idle"):
            result = project.create_backup(self.root, self.parent)
        return Path(result["source"])
