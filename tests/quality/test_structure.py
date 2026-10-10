"""Small rejection fixtures used by every blocking gate."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from repo_quality.structure import validate


class MemoryView:
    def __init__(self, content):
        self.content = content
        self.paths = set(content)

    def text(self, path):
        return self.content[path]


def report(content):
    return validate(
        MemoryView(content),
        {
            "modules": [{"prefix": "docs/", "index": "docs/INDEX.md"}],
            "classifications": [],
            "root_files": list(content),
            "generated": [],
        },
    )


class StructureTests(unittest.TestCase):
    def test_one_research_root_per_project(self):
        view = MemoryView(
            {
                "docs/INDEX.md": "# Hub\n\n[Project](project/INDEX.md)\n",
                "docs/project/INDEX.md": "# Project\n\n[Research](research/notes.md)\n",
                "docs/project/research/notes.md": "# Notes\n\nEvidence.\n",
            }
        )
        register = {
            "modules": [
                {
                    "prefix": "docs/project/",
                    "index": "docs/project/INDEX.md",
                    "research_root": "docs/project/lab/research/",
                }
            ],
            "root_files": list(view.paths),
            "classifications": [],
            "generated": [],
        }
        errors = "\n".join(validate(view, register)["errors"])
        self.assertIn("Competing research root: docs/project/research/", errors)
        register["modules"][0]["research_root"] = "docs/project/research/"
        self.assertEqual(validate(view, register)["errors"], [])

    def test_empty_sections_and_repeated_prose_are_rejected(self):
        from repo_quality.structure import markdown_health

        prose = (
            "Evidence retains the original conditions, failures, hashes and parent relationships. "
            * 3
        )
        errors = markdown_health(f"# Findings\n\n{prose}\n\n{prose}\n\n## Next actions\n")
        self.assertIn("Repeated substantial paragraph", errors)
        self.assertIn("Empty Markdown section: Next actions", errors)
        self.assertEqual(markdown_health("# Hub\n\n## Child\n\nUseful material.\n"), [])

    def test_exact_character_boundary(self):
        for length, passes in [(15000, True), (15001, False)]:
            result = report(
                {
                    "docs/INDEX.md": "# Hub\n\n[x](notes.md)\n",
                    "docs/notes.md": "é" * (length - 1) + "\n",
                }
            )
            self.assertEqual(not result["oversized"], passes)

    def test_links_reference_links_images_and_anchors(self):
        content = {
            "docs/INDEX.md": '# Hub\n\n[x][r]\n\n[r]: notes.md#missing\n\n<img src="absent.svg">\n',
            "docs/notes.md": "# Present\n",
        }
        errors = "\n".join(report(content)["errors"])
        self.assertIn("Broken heading", errors)
        self.assertIn("absent.svg", errors)

    def test_names_private_conflicts_and_unreachable(self):
        content = {
            "docs/INDEX.md": "# Hub\n",
            "Bad Name.md": "<<<<<<< ours\n",
            "bad name.md": "\n",
            ".env": "secret\n",
        }
        errors = "\n".join(report(content)["errors"])
        for expected in [
            "Invalid maintained filename",
            "Case-colliding",
            "Private/cache",
            "merge conflict",
            "Unreachable",
        ]:
            self.assertIn(expected, errors)

    def test_missing_index_and_duplicate_toml(self):
        errors = "\n".join(report({"data.toml": "a=1\na=2\n"})["errors"])
        self.assertIn("Missing module index", errors)
        self.assertIn("Malformed", errors)

    def test_names_validate_suffixes_and_directory_components(self):
        from repo_quality.structure import valid_component

        for name in ("notes.draft v2.md", "notes..md", "notes.bad_suffix.md"):
            self.assertFalse(valid_component(name), name)
        self.assertFalse(valid_component("research.drafts", directory=True))
        self.assertTrue(valid_component("source_manifest.py", python=True))
        self.assertTrue(valid_component("research-memory", directory=True))
        self.assertTrue(valid_component("measurements.raw.csv"))

    def test_quality_decisions_require_valid_dates_and_existing_regressions(self):
        from repo_quality.checks import quality_metadata

        view = MemoryView({"decision.md": "# Decision, 2026-10-10\n", "test.py": "\n"})
        change = {"date": "2026-10-10", "decision": "decision.md", "tests": ["test.py"]}
        self.assertEqual(quality_metadata(view, change), [])
        for stamp in (None, "2026-02-30", "20261010"):
            self.assertIn(
                "valid YYYY-MM-DD", "\n".join(quality_metadata(view, {**change, "date": stamp}))
            )
        self.assertIn(
            "omits its registered date",
            "\n".join(quality_metadata(view, {**change, "date": "2026-10-09"})),
        )
        self.assertIn(
            "regression reference missing",
            "\n".join(quality_metadata(view, {**change, "tests": ["missing.py"]})),
        )

    def test_generated_pages_keep_external_links_and_rebase_local_links(self):
        from repo_quality.navigation import pages

        outputs = {}
        pages(
            outputs,
            "docs/INDEX.md",
            "Hub",
            "[Site](https://example.com)",
            ["- [Local](notes.md) " + "x" * 1000] * 25,
        )
        self.assertGreater(len(outputs), 1)
        for path, payload in outputs.items():
            self.assertLessEqual(len(payload.decode()), 15000)
            self.assertIn("https://example.com", payload.decode())
            if path != "docs/INDEX.md":
                self.assertIn("../../notes.md", payload.decode())

    def test_unsupported_evidence_promotion(self):
        from repo_quality.records import relationships
        import json

        view = MemoryView(
            {
                "meridian-microphone/lab/candidates/candidate_0001/topology.yaml": "id: candidate_0001\nparents: []\n",
                "meridian-microphone/lab/candidates/candidate_0001/results.json": json.dumps(
                    {
                        "latest_experiment": "a",
                        "result_file": "results/runs/a/results.json",
                        "status": "pass",
                        "eligible": True,
                    }
                ),
                "meridian-microphone/lab/results/runs/a/results.json": json.dumps(
                    {"experiment_id": "a", "status": "failed", "eligible": False}
                ),
            }
        )
        self.assertIn("Unsupported evidence promotion", "\n".join(relationships(view)))
