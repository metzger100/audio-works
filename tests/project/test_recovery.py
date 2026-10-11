"""Repository gates and recovery cases; fixtures never touch lab evidence."""

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
from unittest.mock import patch

from repo_fixture import RepositoryFixture, project


class TestRecovery(RepositoryFixture):
    def test_missing_corrupt_and_uninventoried_waveforms_are_distinct(self):
        path = self.add_wave()
        self.assertEqual(
            project.verify_evidence(self.root, project.View(self.root))["status"], "pass"
        )
        self.put(path, "corrupt\n")
        self.assertEqual(
            project.verify_evidence(self.root, project.View(self.root))["damaged"], [path]
        )
        (self.root / path).unlink()
        report = project.verify_evidence(self.root, project.View(self.root))
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["missing"], [path])
        self.put("meridian-microphone/lab/results/runs/unregistered/job/new.raw", "new evidence")
        self.assertTrue(
            project.verify_evidence(self.root, project.View(self.root))["uninventoried"]
        )

    def test_new_inventory_preserves_old_inventory(self):
        self.add_wave()
        old = (self.root / "meridian-microphone/lab/results/new-wave.sha256").read_bytes()
        self.put("meridian-microphone/lab/results/runs/newer/job/new.raw.csv", "time,value\n0,1\n")
        with patch.object(project.evidence, "ensure_idle"):
            result = project.new_inventory(self.root, project.View(self.root))
        self.assertEqual(result["new_files"], 1)
        self.assertEqual(
            old, (self.root / "meridian-microphone/lab/results/new-wave.sha256").read_bytes()
        )
        self.assertEqual(
            project.verify_evidence(self.root, project.View(self.root))["status"], "pass"
        )

    def test_backup_restores_working_changes_ignored_evidence_and_git_history(self):
        self.put("README.md", "# Uncommitted maintained content\n")
        source = self.backup()
        destination = self.parent / "restored"
        result = project.restore_backup(self.root, source, destination)
        self.assertFalse(result["independent"])
        self.assertEqual(
            (destination / "README.md").read_bytes(), (self.root / "README.md").read_bytes()
        )
        self.assertTrue(
            (destination / "meridian-microphone/lab/results/runs/new_batch/job/ac.raw").exists()
        )
        self.assertEqual(
            project.git(destination, "rev-parse", "HEAD"), self.run_git("rev-parse", "HEAD").stdout
        )
        report = project.verify_evidence(destination, project.View(destination))
        self.assertEqual(report["status"], "pass")
        storage = self.check()["preservation"]
        self.assertEqual(storage["status"], "configured")
        self.assertEqual(storage["private_backups"], "optional")
        self.assertEqual(storage["remote_sync"], "not_checked")

    def test_restore_refuses_nonempty_destination_and_corrupted_payload(self):
        source = self.backup()
        destination = self.parent / "occupied"
        destination.mkdir()
        (destination / "owner-data").write_text("preserve")
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
        for names, link in [
            (["files/../../outside"], False),
            (["files/README.md"], True),
            (["files/README.md", "files/README.md"], False),
            ([], False),
        ]:
            archive = self.parent / "malformed.tar"
            with tarfile.open(archive, "w") as output:
                for name in names:
                    member = tarfile.TarInfo(name)
                    member.size = 1
                    if link:
                        member.type = tarfile.SYMTYPE
                        member.linkname = "../../outside"
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
            result = original(root, paths)
            calls += 1
            if calls == 2:
                result["README.md"]["sha256"] = "0" * 64
            return result

        with (
            patch.object(project.backup, "ensure_idle"),
            patch.object(project.backup, "file_manifest", side_effect=changing),
        ):
            with self.assertRaisesRegex(ValueError, "Inputs changed"):
                project.create_backup(self.root, self.parent)
        self.assertFalse(list(self.parent.glob(".audiotech-*.partial")))
        self.assertFalse(list(self.parent.glob("audiotech-*")))

    def test_known_legacy_gap_is_captured_as_incomplete_and_new_gaps_block(self):
        missing = "meridian-microphone/lab/results/runs/legacy/source/src/old.py"
        expected = hashlib.sha256(b"unavailable original code").hexdigest()
        self.put(
            "meridian-microphone/lab/results/runs/legacy/results.json",
            json.dumps({"status": "failed", "source_manifest": {"src/old.py": expected}}),
        )
        legacy_missing = missing.replace("meridian-microphone/", "meridian/", 1)
        self.put(
            "docs/legacy-source-gaps.json",
            json.dumps({"schema_version": 1, "missing_sources": {legacy_missing: expected}}),
        )
        self.refresh()
        with patch.object(project.backup, "ensure_idle"):
            result = project.create_backup(self.root, self.parent)
        self.assertEqual(result["status"], "incomplete")
        self.assertTrue(result["capture_verified"])
        manifest = json.loads((Path(result["source"]) / "manifest.json").read_text())
        self.assertFalse(manifest["original_evidence_complete"])
        self.assertEqual(manifest["missing_original_sources"], {missing: expected})
        self.put(
            "meridian-microphone/lab/results/runs/new_gap/results.json",
            json.dumps({"source_manifest": {"src/new.py": expected}}),
        )
        with patch.object(project.backup, "ensure_idle"):
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
        legacy_register = json.loads(
            json.dumps(self.register).replace("meridian-microphone/", "meridian/")
        )
        self.put("project.json", json.dumps(legacy_register))
        # Capture a pre-rename fixture using its original register contract.
        with (
            patch.object(project.backup, "ensure_idle"),
            patch.object(project.backup, "load_register", return_value=legacy_register),
        ):
            source = Path(project.create_backup(self.root, self.parent)["source"])
        destination = self.parent / "legacy-restore"
        with patch.object(project.backup, "ensure_idle"):
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
        with patch.object(project.backup, "ensure_idle"):
            with self.assertRaisesRegex(ValueError, "Independent storage"):
                project.create_backup(self.root, self.parent, independent=True)

    def test_fresh_clone_is_usable_with_explicit_local_evidence_gap(self):
        self.add_wave()
        self.run_git("add", ".")
        self.run_git(
            "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Declared local evidence"
        )
        clone = self.parent / "clone"
        subprocess.run(["git", "clone", "--quiet", str(self.root), str(clone)], check=True)
        view = project.View(clone)
        register = project.load_register(view)
        report = project.check(view, register)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["preservation"]["authority"], "github")
        self.assertEqual(report["preservation"]["private_backups"], "optional")
        self.assertEqual(project.verify_evidence(clone, view)["status"], "incomplete")
        register.pop("storage_policy")
        self.assertEqual(project.check(view, register)["preservation"]["status"], "incomplete")
        project.install_hook(clone)
        self.assertTrue(project.hook_installed(clone))
