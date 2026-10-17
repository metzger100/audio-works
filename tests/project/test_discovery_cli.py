# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise actual repository discovery commands and selected-content audits."""

import json
import subprocess

from repo_fixture import RepositoryFixture


class TestDiscoveryCLI(RepositoryFixture):
    def invoke(self, *args):
        return subprocess.run(
            [
                str(self.root / ".project-local/quality/bin/python"),
                str(self.root / "tools/project.py"),
                "--root",
                str(self.root),
                *args,
            ],
            text=True,
            capture_output=True,
        )

    def test_file_filters_and_search_keep_fragments_explicit(self):
        self.put("docs/discovery.json", '{"$include": "data-pages/discovery.json"}\n')
        self.put("docs/data-pages/discovery.json", '{"needle": true}\n')
        self.put(
            "meridian-microphone/lab/results/runs/discovery/data-pages/item.json",
            '{"needle": true}\n',
        )
        default = self.invoke("files", "--path", "docs")
        self.assertEqual(default.returncode, 0, default.stderr)
        self.assertIn("docs/discovery.json", default.stdout.splitlines())
        self.assertNotIn("docs/data-pages/discovery.json", default.stdout.splitlines())
        expanded = self.invoke("files", "--path", "docs", "--include-data-pages")
        self.assertIn("docs/data-pages/discovery.json", expanded.stdout.splitlines())
        hidden = self.invoke("search", "needle", "--path", "docs")
        self.assertEqual(hidden.returncode, 1, hidden.stderr)
        found = self.invoke(
            "search", "needle", "--path", "docs", "--include-data-pages", "--files-with-matches"
        )
        self.assertEqual(found.returncode, 0, found.stderr)
        self.assertEqual(found.stdout, "docs/data-pages/discovery.json\n")
        options = [
            "search",
            "needle",
            "--path",
            "meridian-microphone/lab/results/runs/discovery",
            "--include-evidence",
        ]
        self.assertEqual(self.invoke(*options).returncode, 1)
        self.assertEqual(self.invoke(*options, "--include-data-pages").returncode, 0)

    def test_exact_path_filename_output_errors_and_no_match(self):
        self.put("docs/notes.md", "# Notes\n\nneedle é\n")
        self.put("docs-old/notes.md", "needle sibling\n")
        found = self.invoke("search", "needle", "--path", "docs/notes.md")
        self.assertEqual(found.returncode, 0, found.stderr)
        self.assertEqual(found.stdout, "docs/notes.md:3:needle é\n")
        found = self.invoke("search", "needle", "--path", "docs", "--files-with-matches")
        self.assertEqual(found.stdout, "docs/notes.md\n")
        self.assertEqual(self.invoke("search", "absent", "--path", "docs").returncode, 1)
        self.assertEqual(self.invoke("search", "[", "--path", "docs").returncode, 2)
        empty = self.invoke("files", "--path", "missing")
        self.assertEqual((empty.returncode, empty.stdout), (0, ""))
        for path in ("/tmp", "../docs", "docs/../README.md"):
            result = self.invoke("files", "--path", path)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unsafe relative path", result.stderr)

    def test_engineering_context_retains_authority_in_both_formats(self):
        report = self.invoke("context", "reporting")
        self.assertEqual(report.returncode, 0, report.stderr)
        value = json.loads(report.stdout)
        compact = self.invoke("context", "reporting", "--format", "text")
        self.assertEqual(compact.returncode, 0, compact.stderr)
        self.assertLess(len(compact.stdout), len(report.stdout))
        for row in value["reading"]:
            self.assertEqual(
                compact.stdout.splitlines().count(f"{row['path']} ({row['characters']})"), 1
            )
        required = {
            "meridian-microphone/README.md",
            "meridian-microphone/DECISIONS.md",
            "meridian-microphone/lab/AGENTS.md",
            "meridian-microphone/lab/CONTRACT.md",
            "meridian-microphone/lab/research/reading.md",
            "meridian-microphone/lab/research/sources.yaml",
        }
        required.update(
            "meridian-microphone/lab/spec/" + name + ".yaml"
            for name in (
                "microphone-spec",
                "capsule-model",
                "design-constraints",
                "scoring",
                "lock",
            )
        )
        for route in ("device-models", "qualification", "topology", "optimization", "reporting"):
            self.assertTrue(required.issubset(self.register["routes"][route]))
        self.assertTrue(
            set(self.register["common"]).issubset(row["path"] for row in value["reading"])
        )

    def test_audit_discovery_metrics_read_index_bytes(self):
        page = "docs/data-pages/discovery.json"
        self.put("docs/discovery.json", '{"$include": "data-pages/discovery.json"}\n')
        self.put(page, '{"value": 1}\n')
        self.refresh()
        self.run_git("add", "-A")
        indexed = self.check(staged=True)
        self.assertEqual(indexed["status"], "pass", indexed["errors"])
        self.put(page, '{"value": "longer working content"}\n')
        working = self.check()
        self.assertGreater(
            working["discovery"]["data_pages"]["text_characters"],
            indexed["discovery"]["data_pages"]["text_characters"],
        )
        self.assertEqual(self.check(staged=True)["discovery"], indexed["discovery"])
