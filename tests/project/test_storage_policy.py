# SPDX-License-Identifier: GPL-3.0-or-later
"""GitHub storage authority, historical archival and optional recovery."""

import hashlib
import json

from repo_fixture import RepositoryFixture, project


class TestStoragePolicy(RepositoryFixture):
    def test_storage_policy_cannot_claim_github_covers_ignored_evidence(self):
        for key, value in (
            ("scope", "all_evidence"),
            ("private_backups", "verified"),
            ("authority", "unknown"),
        ):
            with self.subTest(key=key):
                self.register["storage_policy"] = {
                    "authority": "github",
                    "scope": "versioned_repository",
                    "private_backups": "optional",
                    key: value,
                }
                self.save_register()
                with self.assertRaisesRegex(ValueError, "Storage policy must name"):
                    project.load_register(project.View(self.root))

    def test_protected_audit_can_be_archived_but_staged_rewrites_and_new_gaps_fail(self):
        old = "docs/legacy-source-gaps.json"
        new = "docs/history/2026-10-11/legacy-source-gaps.json"
        missing = "meridian-microphone/lab/results/runs/old/source/src/old.py"
        expected = hashlib.sha256(b"missing historical source").hexdigest()
        payload = json.dumps({"missing_sources": {missing: expected}}) + "\n"
        self.put(old, payload)
        self.put(
            "meridian-microphone/lab/results/runs/old/results.json",
            json.dumps({"status": "failed", "source_manifest": {"src/old.py": expected}}),
        )
        self.run_git("add", "-A")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Old audit")
        revision = self.run_git("rev-parse", "HEAD").stdout.strip()
        self.register["original_revision"] = revision
        self.save_register()
        self.refresh()
        self.run_git("add", "-A")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Anchor")
        (self.root / new).parent.mkdir(parents=True, exist_ok=True)
        (self.root / old).rename(self.root / new)
        self.register["original_files"] = {
            new: {
                "git_revision": revision,
                "original_path": old,
                "sha256": hashlib.sha256(payload.encode()).hexdigest(),
            }
        }
        self.save_register()
        self.refresh()
        self.run_git("add", "-A")
        report = self.check(staged=True)
        self.assertEqual(report["status"], "pass", report["errors"])
        self.put(new, json.dumps({"missing_sources": {missing: "0" * 64}}) + "\n")
        self.run_git("add", new)
        self.put(new, payload)
        self.assertIn("Changed immutable", "\n".join(self.check(staged=True)["errors"]))
        self.run_git("add", new)
        self.put(
            "meridian-microphone/lab/results/runs/new/results.json",
            json.dumps({"source_manifest": {"src/new.py": expected}}),
        )
        self.refresh()
        self.assertIn("Missing required source snapshot", "\n".join(self.check()["errors"]))

    def test_archived_declarations_keep_optional_restore_honest(self):
        missing = "meridian-microphone/lab/results/runs/old/source/src/old.py"
        expected = hashlib.sha256(b"original unavailable code").hexdigest()
        self.put(
            "meridian-microphone/lab/results/runs/old/results.json",
            json.dumps({"status": "failed", "source_manifest": {"src/old.py": expected}}),
        )
        self.put(
            "docs/history/2026-10-11/legacy-source-gaps.json",
            json.dumps({"missing_sources": {missing: expected}}),
        )
        self.refresh()
        source = self.backup()
        result = project.restore_backup(self.root, source, self.parent / "archived-restore")
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["original_evidence_complete"])
        self.assertEqual(result["missing_original_sources"], 1)
        report = self.check()
        self.assertEqual(report["status"], "pass", report["errors"])
        self.assertEqual(report["preservation"]["status"], "configured")
        self.assertNotIn("known_legacy_source_gaps", report)
