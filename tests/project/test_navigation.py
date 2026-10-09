import hashlib
import subprocess
import sys
import os

"""Repository gates and recovery cases; fixtures never touch lab evidence."""

import json

from repo_fixture import RepositoryFixture, project, REPO


class TestNavigation(RepositoryFixture):
    def test_generation_is_deterministic_and_common_routes_include_contracts(self):
        first = {
            p: (self.root / p).read_bytes()
            for p in project.render(project.View(self.root), self.register)
        }
        self.refresh()
        self.assertEqual(
            first,
            {
                p: (self.root / p).read_bytes()
                for p in project.render(project.View(self.root), self.register)
            },
        )
        self.assertEqual(self.check()["status"], "pass")
        self.register["routes"]["topology"].remove("meridian-microphone/lab/CONTRACT.md")
        self.save_register()
        with self.assertRaisesRegex(ValueError, "scientific contract"):
            project.load_register(project.View(self.root))

    def test_broken_active_links_and_missing_headings_fail(self):
        self.put("README.md", "# Fixture\n[missing](missing.md)\n[heading](QUALITY.md#absent)\n")
        report = self.check()
        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("Broken local link" in e for e in report["errors"]))
        self.assertTrue(any("Broken heading" in e for e in report["errors"]))

    def test_new_unclassified_module_and_stale_generation_fail(self):
        self.put("unregistered/notes.md", "# New module\n")
        report = self.check()
        self.assertTrue(any("Unclassified" in e for e in report["errors"]))
        self.assertTrue(any("Stale generated" in e for e in report["errors"]))

    def test_context_growth_and_missing_mandatory_policy_fail(self):
        self.put("AGENTS.md", "x" * 33000)
        self.assertEqual(self.check()["context_status"], "fail")
        self.register["common"].remove("PATENTS.md")
        self.save_register()
        with self.assertRaisesRegex(ValueError, "mandatory"):
            project.load_register(project.View(self.root))
        self.register["common"].append("PATENTS.md")
        self.register["common"].remove("CONTRIBUTING.md")
        self.save_register()
        with self.assertRaisesRegex(ValueError, "mandatory"):
            project.load_register(project.View(self.root))

    def test_failed_and_interrupted_records_keep_status_and_parents(self):
        self.put(
            "meridian-microphone/lab/results/device_models/failed_child/results.json",
            json.dumps(
                {
                    "status": "failed_parent_and_scoped_subset_preserved",
                    "parent_experiments": ["original_parent"],
                    "eligible_for_production": False,
                }
            ),
        )
        self.put(
            "meridian-microphone/lab/results/device_models/interrupted/checkpoint.json",
            json.dumps({"complete": False}),
        )
        rows = project.record_index(project.View(self.root))["records"]
        child = next(r for r in rows if r["experiment_id"] == "failed_child")
        self.assertEqual(child["parent_experiments"], ["original_parent"])
        self.assertFalse(child["eligible_for_production"])
        self.assertEqual(child["status"], "failed_parent_and_scoped_subset_preserved")
        interrupted = next(r for r in rows if r["experiment_id"] == "interrupted")
        self.assertIsNone(interrupted["status"])
        self.assertTrue(any("Stale generated" in e for e in self.check()["errors"]))

    def test_original_history_cannot_be_changed_or_deleted(self):
        path = "branding/archive/2026-10-04-microphones/README.md"
        self.put(path, "# Rewritten historical data\n")
        self.assertTrue(any("Changed immutable" in e for e in self.check()["errors"]))
        (self.root / path).unlink()
        self.assertTrue(any("Deleted immutable" in e for e in self.check()["errors"]))

    def test_search_scopes_keep_explicit_history_and_evidence_options(self):
        self.put("README.md", "# NEEDLE-active\n")
        self.put("branding/archive/2026-10-04-microphones/README.md", "# NEEDLE-history\n")
        self.put("meridian-microphone/lab/results/runs/new/notes.md", "# NEEDLE-evidence\n")
        cmd = [
            "python3",
            str(REPO / "tools/project.py"),
            "--root",
            str(self.root),
            "search",
            "NEEDLE",
        ]
        default = subprocess.run(cmd, text=True, capture_output=True, check=True).stdout
        self.assertIn("NEEDLE-active", default)
        self.assertNotIn("NEEDLE-history", default)
        self.assertNotIn("NEEDLE-evidence", default)
        expanded = subprocess.run(
            cmd + ["--include-evidence", "--include-history"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        self.assertIn("NEEDLE-history", expanded)
        self.assertIn("NEEDLE-evidence", expanded)

    def test_refresh_preserves_new_frozen_indexes_and_requires_snapshot_files(self):
        path = "meridian-microphone/lab/results/verification/new/source/research/INDEX.md"
        contents = "# Original snapshot navigation\n"
        self.put(path, contents)
        self.put(
            "meridian-microphone/lab/results/verification/new/verification.json",
            json.dumps(
                {
                    "status": "pass",
                    "source_manifest": {
                        "research/INDEX.md": hashlib.sha256(contents.encode()).hexdigest()
                    },
                }
            )
            + "\n",
        )
        result = subprocess.run(
            [
                str(REPO / ".project-local/quality/bin/python")
                if (REPO / ".project-local/quality/bin/python").exists()
                else sys.executable,
                str(self.root / "tools/project.py"),
                "--root",
                str(self.root),
                "refresh",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / path).read_text(), contents)
        self.assertEqual(self.check()["status"], "pass")
        (self.root / path).unlink()
        self.assertIn("Missing required source snapshot", "\n".join(self.check()["errors"]))
