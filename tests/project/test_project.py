"""Repository gates and recovery cases; fixtures never touch lab evidence."""
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("project_tools", REPO / "tools/project.py")
project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(project)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="audiotech-quality-test-")
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / "repo"
        self.root.mkdir()
        self.run_git("init", "--quiet")
        self.run_git("config", "user.name", "Local test fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.register = json.loads((REPO / "project.json").read_text())
        paths = set(self.register["common"] + self.register["evidence"])
        for values in self.register["routes"].values():
            paths.update(values)
        paths.update({"meridian-microphone/lab/results/README.md", "meridian-microphone/research/reference-datasheets/README.md",
                      "branding/archive/2026-10-04-microphones/README.md", "branding/archive/2026-10-05-audio-proposal/README.md",
                      "QUALITY.md", "CONTRIBUTING.md"})
        for name in paths - project.GENERATED:
            self.put(name, "# Fixture\n\nRetained fixture content.\n")
        self.put(".gitignore", ".project-local/\n/meridian-microphone/lab/results/**/*.raw\n/meridian-microphone/lab/results/**/*.raw.csv\n/tools/__pycache__/\n")
        for name in ["tools/project.py", ".githooks/pre-commit"]:
            self.put(name, (REPO / name).read_text())
        for i, name in enumerate(["device_models", "qualification", "architectures", "robust_optimization", "comparative_report"], 1):
            self.put(f"meridian-microphone/lab/research/prompts/{i:02d}_{name}.md", f"# Prompt {i}\n\nPreserve the original evidence.\n")
        self.put(self.register["evidence"][1], json.dumps({"status": "pass", "source_manifest": {}}))
        self.save_register()
        self.refresh()
        self.run_git("add", ".")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Fixture baseline")

    def run_git(self, *args, check=True):
        return subprocess.run(["git", "-C", str(self.root), *args], text=True, capture_output=True, check=check)

    def put(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def save_register(self):
        self.put("project.json", json.dumps(self.register, indent=2) + "\n")

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
        self.put("meridian-microphone/lab/results/new-wave.sha256", hashlib.sha256((self.root / path).read_bytes()).hexdigest() + "  " + path.removeprefix("meridian-microphone/lab/") + "\n")
        self.refresh()
        return path

    def backup(self):
        self.add_wave()
        with patch.object(project, "ensure_idle"):
            result = project.create_backup(self.root, self.parent)
        return Path(result["source"])

    def test_generation_is_deterministic_and_common_routes_include_contracts(self):
        first = {p: (self.root / p).read_bytes() for p in project.GENERATED}
        self.refresh()
        self.assertEqual(first, {p: (self.root / p).read_bytes() for p in project.GENERATED})
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

    def test_failed_and_interrupted_records_keep_status_and_parents(self):
        self.put("meridian-microphone/lab/results/device_models/failed_child/results.json", json.dumps({
            "status": "failed_parent_and_scoped_subset_preserved", "parent_experiments": ["original_parent"],
            "eligible_for_production": False}))
        self.put("meridian-microphone/lab/results/device_models/interrupted/checkpoint.json", json.dumps({"complete": False}))
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

    def test_folder_rename_preserves_immutable_bytes_and_staged_modes(self):
        path = "meridian-microphone/lab/results/runs/frozen/source/control.py"
        original = "# Original frozen source\n"
        self.put(path, original)
        self.run_git("add", ".")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Frozen source")
        (self.root / "meridian-microphone").rename(self.root / "meridian")
        self.run_git("add", "-A")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Legacy folder fixture")
        (self.root / "meridian").rename(self.root / "meridian-microphone")
        self.assertEqual(self.check()["status"], "pass")
        self.run_git("add", "-A")
        self.assertEqual(self.check(staged=True)["status"], "pass")
        self.put(path, "# Rewritten frozen source\n")
        self.assertTrue(any("Changed immutable" in e for e in self.check()["errors"]))
        self.run_git("add", path)
        self.put(path, original)
        self.assertTrue(any("Changed immutable" in e for e in self.check(staged=True)["errors"]))
        self.run_git("add", path)
        (self.root / path).chmod(0o755)
        self.run_git("add", path)
        self.assertTrue(any("Changed immutable" in e for e in self.check(staged=True)["errors"]))
        (self.root / path).unlink()
        self.assertTrue(any("Deleted immutable" in e for e in self.check()["errors"]))

    def test_partial_staging_uses_index_not_working_content(self):
        original = (self.root / "README.md").read_text()
        self.put("README.md", "# Broken working file\n[bad](missing.md)\n")
        self.assertEqual(self.check(staged=True)["status"], "pass")
        self.assertEqual(self.check()["status"], "fail")
        self.run_git("add", "README.md")
        self.put("README.md", original)
        self.assertEqual(self.check(staged=True)["status"], "fail")
        self.assertEqual(self.check()["status"], "pass")

    def test_commit_hook_executes_staged_checker_and_does_not_edit_files(self):
        project.install_hook(self.root)
        self.put("README.md", "# Broken staged file\n[bad](missing.md)\n")
        self.run_git("add", "README.md")
        self.put("tools/project.py", "raise SystemExit(0)\n")
        before = self.run_git("diff", "--binary").stdout
        staged_before = self.run_git("diff", "--cached", "--binary").stdout
        result = self.run_git("commit", "-m", "Must be rejected", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Broken local link", result.stdout + result.stderr)
        self.assertEqual(before, self.run_git("diff", "--binary").stdout)
        self.assertEqual(staged_before, self.run_git("diff", "--cached", "--binary").stdout)

    def test_hook_install_is_idempotent_and_preserves_unrelated_hooks(self):
        project.install_hook(self.root)
        project.install_hook(self.root)
        self.assertTrue(project.hook_installed(self.root))
        self.run_git("config", "core.hooksPath", "external-hooks")
        with self.assertRaisesRegex(ValueError, "Unrelated hook"):
            project.install_hook(self.root)
        self.assertEqual(self.run_git("config", "--get", "core.hooksPath").stdout.strip(), "external-hooks")

    def test_missing_corrupt_and_uninventoried_waveforms_are_distinct(self):
        path = self.add_wave()
        self.assertEqual(project.verify_evidence(self.root, project.View(self.root))["status"], "pass")
        self.put(path, "corrupt\n")
        self.assertEqual(project.verify_evidence(self.root, project.View(self.root))["damaged"], [path])
        (self.root / path).unlink()
        report = project.verify_evidence(self.root, project.View(self.root))
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["missing"], [path])
        self.put("meridian-microphone/lab/results/runs/unregistered/job/new.raw", "new evidence")
        self.assertTrue(project.verify_evidence(self.root, project.View(self.root))["uninventoried"])

    def test_new_inventory_preserves_old_inventory(self):
        self.add_wave()
        old = (self.root / "meridian-microphone/lab/results/new-wave.sha256").read_bytes()
        self.put("meridian-microphone/lab/results/runs/newer/job/new.raw.csv", "time,value\n0,1\n")
        with patch.object(project, "ensure_idle"):
            result = project.new_inventory(self.root, project.View(self.root))
        self.assertEqual(result["new_files"], 1)
        self.assertEqual(old, (self.root / "meridian-microphone/lab/results/new-wave.sha256").read_bytes())
        self.assertEqual(project.verify_evidence(self.root, project.View(self.root))["status"], "pass")

    def test_backup_restores_working_changes_ignored_evidence_and_git_history(self):
        self.put("README.md", "# Uncommitted maintained content\n")
        source = self.backup()
        destination = self.parent / "restored"
        result = project.restore_backup(self.root, source, destination)
        self.assertFalse(result["independent"])
        self.assertEqual((destination / "README.md").read_bytes(), (self.root / "README.md").read_bytes())
        self.assertTrue((destination / "meridian-microphone/lab/results/runs/new_batch/job/ac.raw").exists())
        self.assertEqual(project.git(destination, "rev-parse", "HEAD"), self.run_git("rev-parse", "HEAD").stdout)
        report = project.verify_evidence(destination, project.View(destination))
        self.assertEqual(report["status"], "pass")
        self.assertEqual(self.check()["preservation"]["status"], "incomplete")

    def test_restore_refuses_nonempty_destination_and_corrupted_payload(self):
        source = self.backup()
        destination = self.parent / "occupied"
        destination.mkdir(); (destination / "owner-data").write_text("preserve")
        with self.assertRaisesRegex(ValueError, "empty"):
            project.restore_backup(self.root, source, destination)
        self.assertEqual((destination / "owner-data").read_text(), "preserve")
        with (source / "files.tar").open("ab") as f:
            f.write(b"corruption")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            project.restore_backup(self.root, source, self.parent / "must-remain-absent")
        self.assertFalse((self.parent / "must-remain-absent").exists())

    def test_unsafe_members_links_duplicates_and_omissions_are_rejected(self):
        declared = {"README.md": {"size": 1, "sha256": hashlib.sha256(b"x").hexdigest()}}
        for names, link in [(["files/../../outside"], False), (["files/README.md"], True),
                            (["files/README.md", "files/README.md"], False), ([], False)]:
            archive = self.parent / "malformed.tar"
            with tarfile.open(archive, "w") as output:
                for name in names:
                    member = tarfile.TarInfo(name); member.size = 1
                    if link:
                        member.type = tarfile.SYMTYPE; member.linkname = "../../outside"
                        output.addfile(member)
                    else:
                        output.addfile(member, io.BytesIO(b"x"))
            with self.assertRaises(ValueError):
                project.verify_tar(archive, declared)

    def test_capture_rejects_changing_inputs_and_cleans_partial_bundle(self):
        self.add_wave()
        original = project.file_manifest
        calls = 0
        def changing(root, paths):
            nonlocal calls
            result = original(root, paths); calls += 1
            if calls == 2:
                result["README.md"]["sha256"] = "0" * 64
            return result
        with patch.object(project, "ensure_idle"), patch.object(project, "file_manifest", side_effect=changing):
            with self.assertRaisesRegex(ValueError, "Inputs changed"):
                project.create_backup(self.root, self.parent)
        self.assertFalse(list(self.parent.glob(".audiotech-*.partial")))
        self.assertFalse(list(self.parent.glob("audiotech-*")))

    def test_known_legacy_gap_is_captured_as_incomplete_and_new_gaps_block(self):
        missing = "meridian-microphone/lab/results/runs/legacy/source/src/old.py"
        expected = hashlib.sha256(b"unavailable original code").hexdigest()
        self.put("meridian-microphone/lab/results/runs/legacy/results.json", json.dumps({"status": "failed", "source_manifest": {"src/old.py": expected}}))
        legacy_missing = missing.replace("meridian-microphone/", "meridian/", 1)
        self.put("docs/legacy-source-gaps.json", json.dumps({"schema_version": 1, "missing_sources": {legacy_missing: expected}}))
        self.refresh()
        with patch.object(project, "ensure_idle"):
            result = project.create_backup(self.root, self.parent)
        self.assertEqual(result["status"], "incomplete")
        self.assertTrue(result["capture_verified"])
        manifest = json.loads((Path(result["source"]) / "manifest.json").read_text())
        self.assertFalse(manifest["original_evidence_complete"])
        self.assertEqual(manifest["missing_original_sources"], {missing: expected})
        self.put("meridian-microphone/lab/results/runs/new_gap/results.json", json.dumps({"source_manifest": {"src/new.py": expected}}))
        with patch.object(project, "ensure_idle"):
            with self.assertRaisesRegex(ValueError, "new missing"):
                project.create_backup(self.root, self.parent)

    def test_capture_manifest_tampering_is_detected_before_restore(self):
        source = self.backup()
        manifest = json.loads((source / "manifest.json").read_text())
        manifest["captured_at"] = "changed observation"
        (source / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "locally recorded"):
            project.restore_backup(self.root, source, self.parent / "must-remain-absent")

    def test_backup_from_original_folder_remains_restorable(self):
        wave = self.add_wave().replace("meridian-microphone/", "meridian/", 1)
        (self.root / "meridian-microphone").rename(self.root / "meridian")
        legacy_register = json.loads(json.dumps(self.register).replace("meridian-microphone/", "meridian/"))
        self.put("project.json", json.dumps(legacy_register))
        # Capture a pre-rename fixture using its original register contract.
        with patch.object(project, "ensure_idle"), patch.object(project, "load_register", return_value=legacy_register):
            source = Path(project.create_backup(self.root, self.parent)["source"])
        destination = self.parent / "legacy-restore"
        with patch.object(project, "ensure_idle"):
            result = project.restore_backup(self.root, source, destination)
        self.assertEqual(result["status"], "pass")
        self.assertTrue((destination / wave).is_file())
        verification = project.verify_evidence(destination, project.View(destination))
        self.assertEqual(verification["status"], "pass")
        self.assertEqual(verification["declared_waveforms"], 1)

    def test_backup_identifier_cannot_escape_private_attestation_directory(self):
        with self.assertRaisesRegex(ValueError, "identifier"):
            project.write_attestation(self.root, {"backup_id": "../../outside"})
        self.assertFalse((self.root / "outside.json").exists())

    def test_restore_checks_completeness_against_original_declarations(self):
        source = self.backup()
        manifest = json.loads((source / "manifest.json").read_text())
        # Model an imported backup whose manifest is internally contradictory.
        (self.root / ".project-local/backups" / (manifest["backup_id"] + ".json")).unlink()
        manifest["original_evidence_complete"] = False
        (source / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "completeness declarations"):
            project.restore_backup(self.root, source, self.parent / "must-remain-absent")
        self.assertFalse((self.parent / "must-remain-absent").exists())

    def test_temporary_storage_cannot_be_asserted_independent(self):
        self.add_wave()
        with patch.object(project, "ensure_idle"):
            with self.assertRaisesRegex(ValueError, "Independent storage"):
                project.create_backup(self.root, self.parent, independent=True)

    def test_fresh_clone_is_usable_with_explicit_local_evidence_gap(self):
        self.add_wave()
        self.run_git("add", ".")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Declared local evidence")
        clone = self.parent / "clone"
        subprocess.run(["git", "clone", "--quiet", str(self.root), str(clone)], check=True)
        view = project.View(clone)
        self.assertEqual(project.check(view, project.load_register(view))["status"], "pass")
        self.assertEqual(project.verify_evidence(clone, view)["status"], "incomplete")
        project.install_hook(clone)
        self.assertTrue(project.hook_installed(clone))

    def test_search_scopes_keep_explicit_history_and_evidence_options(self):
        self.put("README.md", "# NEEDLE-active\n")
        self.put("branding/archive/2026-10-04-microphones/README.md", "# NEEDLE-history\n")
        self.put("meridian-microphone/lab/results/runs/new/notes.md", "# NEEDLE-evidence\n")
        cmd = ["python3", str(REPO / "tools/project.py"), "--root", str(self.root), "search", "NEEDLE"]
        default = subprocess.run(cmd, text=True, capture_output=True, check=True).stdout
        self.assertIn("NEEDLE-active", default)
        self.assertNotIn("NEEDLE-history", default)
        self.assertNotIn("NEEDLE-evidence", default)
        expanded = subprocess.run(cmd + ["--include-evidence", "--include-history"], text=True, capture_output=True, check=True).stdout
        self.assertIn("NEEDLE-history", expanded)
        self.assertIn("NEEDLE-evidence", expanded)


if __name__ == "__main__":
    unittest.main()
