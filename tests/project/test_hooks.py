import subprocess

"""Repository gates and recovery cases; fixtures never touch lab evidence."""

from repo_fixture import RepositoryFixture, project


class TestHooks(RepositoryFixture):
    def test_folder_rename_preserves_immutable_bytes_and_staged_modes(self):
        path = "meridian-microphone/lab/results/runs/frozen/source/control.py"
        original = "# Original frozen source\n"
        self.put(path, original)
        self.run_git("add", ".")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Frozen source")
        (self.root / "meridian-microphone").rename(self.root / "meridian")
        self.run_git("add", "-A")
        self.run_git(
            "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Legacy folder fixture"
        )
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
        self.assertEqual(
            self.run_git("config", "--get", "core.hooksPath").stdout.strip(), "external-hooks"
        )

    def good_commit(self, message):
        self.refresh()
        self.run_git("add", ".")
        return self.run_git("commit", "--quiet", "-m", message, check=False)

    def test_successful_commit_partial_staging_and_selected_tools(self):
        project.install_hook(self.root)
        self.put("README.md", "# Valid staged content\n\nUseful staged content.\n")
        self.run_git("add", "README.md")
        self.put("README.md", "# Broken working content\n[bad](missing.md)\n")
        self.put("tools/project.py", "raise SystemExit(0)\n")
        before = self.run_git("diff", "--binary").stdout
        result = self.run_git("commit", "--quiet", "-m", "Only staged content")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(before, self.run_git("diff", "--binary").stdout)

    def test_merge_and_patch_application_are_blocked(self):
        base = self.run_git("rev-parse", "HEAD").stdout.strip()
        branch = self.run_git("branch", "--show-current").stdout.strip()
        self.run_git("checkout", "-b", "other")
        self.put("README.md", "# Broken incoming content\n[bad](missing.md)\n")
        self.run_git("add", ".")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Broken incoming")
        patch_file = self.parent / "change.patch"
        patch_file.write_text(self.run_git("format-patch", "-1", "--stdout").stdout)
        self.run_git("checkout", branch)
        project.install_hook(self.root)
        result = self.run_git("merge", "--no-ff", "other", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.run_git("rev-parse", "HEAD").stdout.strip(), base)
        self.assertIn("Broken local link", result.stdout + result.stderr)
        incoming = (self.root / "README.md").read_bytes()
        self.assertIn(b"missing.md", incoming)
        self.run_git("merge", "--abort")
        result = self.run_git("am", str(patch_file), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.run_git("rev-parse", "HEAD").stdout.strip(), base)
        self.assertEqual((self.root / "README.md").read_bytes(), incoming)
        self.run_git("am", "--abort")

    def test_multi_ref_push_checks_other_branches_and_preserved_evidence(self):
        remote = self.parent / "remote.git"
        subprocess.run(["git", "init", "--bare", "--quiet", str(remote)], check=True)
        self.run_git("remote", "add", "fixture", str(remote))
        project.install_hook(self.root)
        branch = self.run_git("branch", "--show-current").stdout.strip()
        self.run_git("push", "fixture", branch)
        self.run_git("checkout", "-b", "broken")
        self.put("README.md", "# Invalid outgoing branch\n[bad](missing.md)\n")
        self.run_git("add", ".")
        self.run_git("-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Must not push")
        self.run_git("checkout", branch)
        self.put("tools/hook_gate.py", "raise SystemExit(0)\n")
        before = self.run_git("status", "--porcelain").stdout
        result = self.run_git("push", "fixture", branch, "broken", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Broken local link", result.stdout + result.stderr)
        self.assertEqual(before, self.run_git("status", "--porcelain").stdout)
        listing = subprocess.check_output(["git", "--git-dir", str(remote), "show-ref"], text=True)
        self.assertNotIn("refs/heads/broken", listing)
        self.run_git("restore", "tools/hook_gate.py")
        self.run_git("checkout", "-b", "altered")
        self.put("branding/archive/2026-10-04-microphones/README.md", "# Altered frozen original\n")
        self.run_git("add", ".")
        self.run_git(
            "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Altered original"
        )
        self.run_git("checkout", branch)
        result = self.run_git("push", "fixture", "altered", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Changed immutable", result.stdout + result.stderr)
