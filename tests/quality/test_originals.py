"""Original relocation must preserve identity, bytes, modes and protection."""

import hashlib
import unittest

from repo_quality.originals import declared_originals


class OriginalView:
    staged = True
    revision = None

    def __init__(self, content, mode="100644"):
        self.content = content
        self.paths = set(content)
        self.index = {path: (mode, "unused") for path in content}

    def read(self, path):
        return self.content[path]


class OriginalTests(unittest.TestCase):
    def setUp(self):
        self.old = "project/research/survey.md"
        self.new = "project/lab/research/capsules/survey.md"
        self.payload = b"Original finding with retained uncertainty.\n"
        self.declaration = {
            "git_revision": "baseline",
            "original_path": self.old,
            "sha256": hashlib.sha256(self.payload).hexdigest(),
        }
        self.prior = {"original_files": {self.old: self.declaration}}
        self.register = {"original_files": {self.new: self.declaration}}
        self.baseline = {self.old: ("100644", "unused")}

    def errors(self, view, register=None):
        return declared_originals(view, register or self.register, self.prior, self.baseline)

    def test_relocation_keeps_original_identity_bytes_and_modes(self):
        self.assertEqual(self.errors(OriginalView({self.new: self.payload})), [])
        self.assertIn(
            "Changed or missing declared original",
            "\n".join(self.errors(OriginalView({self.new: self.payload + b"changed"}))),
        )
        self.assertIn(
            "Changed original execute mode",
            "\n".join(self.errors(OriginalView({self.new: self.payload}, "100755"))),
        )

    def test_removing_or_replacing_provenance_is_rejected(self):
        view = OriginalView({self.new: self.payload})
        for register in (
            {"original_files": {}},
            {"original_files": {self.new: {**self.declaration, "original_path": "other.md"}}},
            {"original_files": {self.new: {**self.declaration, "sha256": "0" * 64}}},
        ):
            self.assertIn("original protection", "\n".join(self.errors(view, register)))

    def test_duplicate_identity_and_missing_destination_are_rejected(self):
        register = {"original_files": {self.new: self.declaration, self.old: self.declaration}}
        self.assertIn(
            "Duplicate original identity",
            "\n".join(self.errors(OriginalView({self.new: self.payload}), register)),
        )
        self.assertIn(
            "Changed or missing declared original", "\n".join(self.errors(OriginalView({})))
        )
