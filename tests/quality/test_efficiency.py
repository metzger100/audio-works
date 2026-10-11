"""Fixtures for reading overhead, shared prose and recursive data folders."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from repo_quality.efficiency import inspect
from test_structure import MemoryView


class EfficiencyTests(unittest.TestCase):
    def inspect(self, files, **extra):
        register = {
            "common": [],
            "routes": {"orientation": list(files)},
            "modules": [],
            "classifications": [],
            "root_files": list(files),
            "generated": [],
            **extra,
        }
        return inspect(MemoryView(files), register)

    def test_route_boundary_counts_characters_and_shared_reading_once(self):
        files = {"one.md": "é" * 25000, "two.md": "ø" * 25000}
        report = self.inspect(files, common=["one.md"])
        self.assertEqual(report["reading_sizes"]["orientation"], 50000)
        self.assertEqual(report["errors"], [])
        report = self.inspect({**files, "two.md": files["two.md"] + "é"})
        self.assertIn("50001 > 50000", "\n".join(report["errors"]))

    def test_duplicates_normalize_links_and_skip_generated_and_originals(self):
        prose = "Evidence retains original failures, conditions and parent relationships. " * 3
        files = {
            "one.md": prose + "[Source](a.md)\n",
            "two.md": prose + "[Source](b.md)\n",
            "original.md": prose + "[Source](c.md)\n",
            "generated.md": prose + "[Source](d.md)\n",
        }
        report = self.inspect(
            files,
            original_files={"original.md": {}},
            classifications=[{"path": "generated.md", "role": "generated"}],
        )
        self.assertEqual(report["repeated_prose"][0]["files"], ["one.md", "two.md"])
        self.assertIn("Repeated prose across documents", "\n".join(report["errors"]))
        files["two.md"] = "[Shared conditions](one.md).\n"
        self.assertEqual(
            self.inspect(
                files,
                original_files={"original.md": {}},
                classifications=[{"path": "generated.md", "role": "generated"}],
            )["errors"],
            [],
        )

    def test_nested_data_layout_is_rejected_but_flat_pages_and_frozen_paths_pass(self):
        bad = "data-parts/metrics-parts/page-0001.json"
        report = self.inspect({bad: "{}\n", "data-pages/metrics-page-0001.json": "{}\n"})
        self.assertEqual(report["nested_data_partitions"], [bad])
        self.assertEqual(self.inspect({bad: "{}\n"}, original_files={bad: {}})["errors"], [])

    def test_page_containers_are_flat_and_folder_counts_exclude_originals(self):
        files = {
            "docs/data-pages/record-page-0001.json": "{}\n",
            "docs/index-pages/history-0001.md": "# History\n",
            "frozen/source/deep/original.json": "{}\n",
        }
        report = self.inspect(files, original_files={"frozen/source/deep/original.json": {}})
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["folders"]["maintained"], 3)
        self.assertEqual(report["folders"]["original_only"], 3)
        self.assertEqual(report["folders"]["page_containers"], 2)
        self.assertEqual(report["folders"]["data_page_containers"], 1)
        self.assertEqual(report["folders"]["navigation_page_containers"], 1)
        for path in (
            "docs/record-parts/page-0001.json",
            "docs/data-pages/record/page-0001.json",
            "docs/index-pages/history/page-0001.md",
        ):
            with self.subTest(path=path):
                self.assertIn(
                    "Redundant page directory", "\n".join(self.inspect({path: ""})["errors"])
                )
