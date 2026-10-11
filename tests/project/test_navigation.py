import hashlib
import subprocess
import sys
import os

"""Repository gates and recovery cases; fixtures never touch lab evidence."""

import json

from repo_fixture import RepositoryFixture, project, REPO


class TestNavigation(RepositoryFixture):
    def test_multiple_index_hubs_share_one_flat_page_folder(self):
        from repo_quality.navigation import pages

        outputs = {}
        entries = [f"- [Entry {i}](../README.md) " + "x" * 5500 for i in range(6)]
        for destination in ("docs/first.md", "docs/second.md"):
            pages(outputs, destination, "Bounded hub", "[Source](../QUALITY.md)", entries)
        children = [p for p in outputs if "/index-pages/" in p]
        self.assertEqual(len(children), 6)
        self.assertTrue(all(p.count("/") == 2 for p in children))
        self.assertIn(b"[Source](../../QUALITY.md)", outputs[children[0]])
        self.assertIn(b"[Entry 0](../../README.md)", outputs[children[0]])
        self.assertTrue(all(len(content.decode()) <= 15000 for content in outputs.values()))

    def test_commit_rejects_document_specific_page_folders_without_changing_content(self):
        project.install_hook(self.root)
        self.put("docs/record-parts/page-0001.json", "{}\n")
        self.refresh()
        self.run_git("add", "-A")
        before = self.run_git("diff", "--binary").stdout
        staged_before = self.run_git("diff", "--cached", "--binary").stdout
        result = self.run_git("commit", "-m", "Reject redundant page folder", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Redundant page directory", result.stdout + result.stderr)
        self.assertEqual(before, self.run_git("diff", "--binary").stdout)
        self.assertEqual(staged_before, self.run_git("diff", "--cached", "--binary").stdout)

    def test_refresh_prunes_empty_obsolete_hubs_and_preserves_unrelated_material(self):
        directory = "docs/obsolete-parts/metrics-parts"
        self.put(directory + "/INDEX.md", "# Obsolete generated hub\n\nOld pages.\n")
        self.put("docs/other-parts/INDEX.md", "# Obsolete hub\n\nOld pages.\n")
        self.put("docs/other-parts/retained.log", "Retained independent output.\n")
        result = subprocess.run(
            [
                str(REPO / ".project-local/quality/bin/python"),
                str(self.root / "tools/project.py"),
                "--root",
                str(self.root),
                "refresh",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.root / directory).exists())
        self.assertEqual(
            (self.root / "docs/other-parts/retained.log").read_text(),
            "Retained independent output.\n",
        )

    def test_commit_rejects_cross_file_prose_from_index_and_leaves_content_untouched(self):
        project.install_hook(self.root)
        prose = (
            "Preserve original evidence, failures, conditions, seeds and parent relationships. " * 3
        )
        self.put("docs/first.md", "# First\n\n" + prose + "[Evidence](../README.md)\n")
        self.put("docs/second.md", "# Second\n\n" + prose + "[Evidence](../QUALITY.md)\n")
        self.refresh()
        self.run_git("add", "-A")
        self.put("docs/second.md", "# Second\n\n[Shared conditions](first.md).\n")
        self.assertEqual(self.check()["status"], "pass")
        self.assertIn(
            "Repeated prose across documents", "\n".join(self.check(staged=True)["errors"])
        )
        before = self.run_git("diff", "--binary").stdout
        staged_before = self.run_git("diff", "--cached", "--binary").stdout
        result = self.run_git("commit", "-m", "Reject staged duplication", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Repeated prose across documents", result.stdout + result.stderr)
        self.assertEqual(before, self.run_git("diff", "--binary").stdout)
        self.assertEqual(staged_before, self.run_git("diff", "--cached", "--binary").stdout)

    def test_declared_original_relocation_checks_staged_bytes(self):
        old = "meridian-microphone/research/survey first.md"
        new = "meridian-microphone/lab/research/capsules/survey first.md"
        payload = "# Original survey\n\nMeasured uncertainty is retained.\n"
        self.put(old, payload)
        self.run_git("add", old)
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Original")
        revision = self.run_git("rev-parse", "HEAD").stdout.strip()
        self.register["original_revision"] = revision
        declaration = {
            "git_revision": revision,
            "original_path": old,
            "sha256": hashlib.sha256(payload.encode()).hexdigest(),
        }
        self.register["original_files"] = {old: declaration}
        self.save_register()
        self.refresh()
        self.run_git("add", "-A")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Protection")
        (self.root / old).rename(self.root / new)
        self.register["original_files"] = {new: declaration}
        self.save_register()
        self.refresh()
        history = (self.root / "docs/history.md").read_text()
        self.assertIn("capsules/survey%20first.md", history)
        self.assertIn(declaration["sha256"], history)
        self.assertEqual(self.check()["status"], "pass")
        self.run_git("add", "-A")
        self.assertEqual(self.check(staged=True)["status"], "pass")
        project.install_hook(self.root)
        self.put(new, payload + "Changed finding.\n")
        self.run_git("add", new)
        self.put(new, payload)
        errors = "\n".join(self.check(staged=True)["errors"])
        self.assertIn("Changed or missing declared original", errors)
        before = self.run_git("diff", "--binary").stdout
        staged_before = self.run_git("diff", "--cached", "--binary").stdout
        result = self.run_git("commit", "-m", "Reject changed relocated original", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Changed or missing declared original", result.stdout + result.stderr)
        self.assertEqual(before, self.run_git("diff", "--binary").stdout)
        self.assertEqual(staged_before, self.run_git("diff", "--cached", "--binary").stdout)
        self.assertEqual(self.check()["status"], "pass")

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
        self.register["routes"]["topology"].append("meridian-microphone/lab/CONTRACT.md")
        self.register["routes"]["topology"].remove("meridian-microphone/lab/spec/scoring.yaml")
        self.save_register()
        with self.assertRaisesRegex(ValueError, "specifications"):
            project.load_register(project.View(self.root))
        self.register["routes"]["topology"].append("meridian-microphone/lab/spec/scoring.yaml")
        self.register["routes"]["topology"].remove("meridian-microphone/lab/research/reading.md")
        self.save_register()
        with self.assertRaisesRegex(ValueError, "authority/specifications"):
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
