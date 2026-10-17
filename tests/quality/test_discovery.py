# SPDX-License-Identifier: GPL-3.0-or-later
"""Discovery filters, bounded search and compact context retain complete access."""

from contextlib import redirect_stdout
import io
import itertools
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from repo_quality import cli
from repo_quality.discovery import data_page, discovery_sizes, search, select_paths
from repo_quality.entry import render_root
from repo_quality.register import classify
from test_structure import MemoryView


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.view = MemoryView(
            {
                "README.md": "# Start\n",
                "docs/record.json": '{"$include": "data-pages/part.json"}\n',
                "docs/data-pages/part.json": '{"value": 1}\n',
                "docs-old/notes.md": "Other directory\n",
                "data-pages.txt": "Ordinary file\n",
                "evidence/item.json": "{}\n",
                "evidence/data-pages/item.json": "{}\n",
                "history/notes.md": "History\n",
                "history/data-pages/item.json": "{}\n",
                "generated/view.md": "Generated\n",
                "generated/data-pages/item.json": "{}\n",
            }
        )
        self.register = {
            "root_files": ["README.md", "data-pages.txt"],
            "common": ["README.md"],
            "routes": {"documentation": ["README.md", "docs/record.json"]},
            "modules": [{"prefix": "docs/"}, {"prefix": "docs-old/"}],
            "classifications": [
                {"prefix": prefix + "/", "role": role}
                for prefix, role in [
                    ("evidence", "evidence"),
                    ("history", "historical"),
                    ("generated", "generated"),
                ]
            ],
            "generated": [],
        }

    def test_visibility_switches_are_independent_and_keep_parent_records(self):
        flags = ["include_evidence", "include_history", "include_generated", "include_data_pages"]
        for values in itertools.product((False, True), repeat=4):
            options = dict(zip(flags, values))
            with self.subTest(**options):
                expected = []
                for path in sorted(self.view.paths):
                    role = classify(path, self.register)
                    allowed = {
                        "evidence": values[0],
                        "historical": values[1],
                        "generated": values[2],
                    }.get(role, True)
                    if allowed and (values[3] or not data_page(path)):
                        expected.append(path)
                self.assertEqual(select_paths(self.view, self.register, **options), expected)
        default = select_paths(self.view, self.register)
        self.assertIn("docs/record.json", default)
        self.assertIn("data-pages.txt", default)
        self.assertNotIn("docs/data-pages/part.json", default)

    def test_path_scopes_exact_files_and_descendants_without_bypassing_filters(self):
        for prefix in ("docs", "docs/"):
            self.assertEqual(
                select_paths(self.view, self.register, path=prefix), ["docs/record.json"]
            )
        self.assertEqual(select_paths(self.view, self.register, path="README.md"), ["README.md"])
        self.assertEqual(select_paths(self.view, self.register, path="evidence"), [])
        self.assertEqual(select_paths(self.view, self.register, path="absent"), [])
        for prefix in (
            "/tmp",
            "../docs",
            "docs/../README.md",
            "docs//record.json",
            "docs\\record.json",
            "",
            ".",
            "docs//",
        ):
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                select_paths(self.view, self.register, path=prefix)

    def test_search_batches_encoded_arguments_and_preserves_match_outcomes(self):
        paths = [f"docs/{i:03d}-é.md" for i in range(100)]
        for matched, expected in ((False, 1), (True, 0)):
            with (
                patch("repo_quality.discovery.SEARCH_ARGUMENT_BYTES", 400),
                patch(
                    "repo_quality.discovery.subprocess.run",
                    return_value=SimpleNamespace(returncode=int(not matched)),
                ) as run,
            ):
                self.assertEqual(
                    search(Path("/tmp"), paths, "-pattern", files_with_matches=True), expected
                )
            calls = run.call_args_list
            self.assertGreater(len(calls), 1)
            visited = []
            for call in calls:
                args = call.args[0]
                self.assertLessEqual(sum(len(os.fsencode(arg)) + 9 for arg in args), 400)
                marker = args.index("--")
                self.assertEqual(args[marker + 1], "-pattern")
                self.assertIn("--with-filename", args)
                self.assertIn("--files-with-matches", args)
                visited.extend(args[marker + 2 :])
            self.assertEqual(visited, paths)

    def test_search_errors_override_matches_and_empty_search_does_not_run(self):
        paths = [f"{i:03d}.md" for i in range(100)]
        for outcomes, expected in (([1, 0] + [1] * 100, 0), ([0, 2], 2), ([0, -9], 2)):
            with (
                patch("repo_quality.discovery.SEARCH_ARGUMENT_BYTES", 300),
                patch(
                    "repo_quality.discovery.subprocess.run",
                    side_effect=[SimpleNamespace(returncode=code) for code in outcomes],
                ),
            ):
                self.assertEqual(search(Path("/tmp"), paths, "needle"), expected)
        with patch("repo_quality.discovery.subprocess.run") as run:
            self.assertEqual(search(Path("/tmp"), [], "needle"), 1)
            run.assert_not_called()
        with (
            patch("repo_quality.discovery.SEARCH_ARGUMENT_BYTES", 5),
            self.assertRaises(ValueError),
        ):
            search(Path("/tmp"), paths, "needle")

    def test_context_text_and_default_json_share_deduplicated_reading_and_totals(self):
        outputs = []
        for options in ([], ["--format", "json"], ["--format", "text"]):
            output = io.StringIO()
            with (
                patch.object(cli, "View", return_value=self.view),
                patch.object(cli, "load_register", return_value=self.register),
                redirect_stdout(output),
            ):
                self.assertEqual(cli.main(["context", "documentation", *options]), 0)
            outputs.append(output.getvalue())
        self.assertEqual(outputs[0], outputs[1])
        report = json.loads(outputs[0])
        self.assertEqual(
            [row["path"] for row in report["reading"]], ["README.md", "docs/record.json"]
        )
        self.assertEqual(
            report["route_characters"],
            sum(len(self.view.text(path)) for path in ["README.md", "docs/record.json"]),
        )
        for row in report["reading"]:
            self.assertEqual(
                outputs[2].splitlines().count(f"{row['path']} ({row['characters']})"), 1
            )
        self.assertIn(
            f"Characters: {report['route_characters']} / {report['route_limit']}", outputs[2]
        )
        self.assertIn(report["note"], outputs[2])

    def test_audit_counts_unicode_characters_and_separates_binary_files(self):
        class BinaryView(MemoryView):
            def text(self, path):
                if path == "docs/image.png":
                    return b"\x89PNG".decode()
                return super().text(path)

        view = BinaryView({**self.view.content, "docs/image.png": "", "docs/unicode.md": "é\n"})
        report = discovery_sizes(view, self.register)
        visible = select_paths(view, self.register)
        self.assertEqual(report["default"]["files"], len(visible))
        self.assertEqual(report["default"]["binary_files"], 1)
        self.assertEqual(report["data_pages"]["files"], 1)
        self.assertEqual(
            report["default"]["text_characters"],
            sum(len(view.text(path)) for path in visible if path != "docs/image.png"),
        )

    def test_entry_groups_destinations_once_and_retains_unknown_files(self):
        outputs = {}
        render_root(
            outputs,
            {
                "README.md",
                "CURRENT.md",
                "QUALITY.md",
                "docs/start-here.md",
                "docs/current-evidence.md",
                "docs/future.md",
            },
            {"docs", "docs/decisions", "tools", "meridian-microphone"},
        )
        import re

        body = outputs["docs/INDEX.md"].decode()
        targets = re.findall(r"\]\(([^)]+)\)", body)
        self.assertEqual(len(targets), len(set(targets)))
        for target in (
            "../README.md",
            "../tools/INDEX.md",
            "../meridian-microphone/INDEX.md",
            "decisions/INDEX.md",
            "future.md",
            "current-evidence.md",
            "evidence.md",
        ):
            self.assertIn(target, targets)
        self.assertIn("## Maintenance and policies", body)
        self.assertIn("## Other references", body)

    def test_entry_pagination_keeps_headings_with_their_first_destination(self):
        from repo_quality.structure import markdown_health

        files = {f"docs/{i:03d}-{'x' * 90}.md" for i in range(200)}
        outputs = {}
        render_root(outputs, files, {"docs"})
        self.assertGreater(len(outputs), 1)
        for path, contents in outputs.items():
            text = contents.decode()
            self.assertLessEqual(len(text), 15000, path)
            self.assertEqual(markdown_health(text), [], path)
