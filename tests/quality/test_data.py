"""Lossless includes, bounded writes and hostile structured inputs."""

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from repo_quality.data import load, parse
from repo_quality.partition import bounded_data


class DataTests(unittest.TestCase):
    def test_boundary_and_lossless_nested_yaml(self):
        data = {
            "entries": [
                {"id": f"item-{i}", "value": "é" * 600, "numeric_keys": {1: [2, 3]}}
                for i in range(80)
            ]
        }
        outputs = bounded_data(data, "data.yaml")
        self.assertTrue(all(len(value.decode()) <= 15000 for value in outputs.values()))
        self.assertEqual(data, load(lambda path: outputs[path].decode(), "data.yaml"))
        self.assertEqual(outputs, bounded_data(data, "data.yaml"))

    def test_duplicate_keys_and_nonfinite(self):
        for text, suffix in [
            ('{"a":1,"a":2}', ".json"),
            ("a: 1\na: 2\n", ".yaml"),
            ("a: .nan\n", ".yaml"),
            ('{"v":NaN}', ".json"),
        ]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse(text, suffix)

    def test_include_escape_cycle_missing_and_duplicate_id(self):
        for files in [
            {"a.json": '{"$include":"../b.json"}'},
            {"a.json": '{"$include":"a.json"}'},
            {"a.json": '{"$include":"missing.json"}'},
            {
                "a.json": '{"$include":["b.json","c.json"]}',
                "b.json": '[{"id":"same"}]',
                "c.json": '[{"id":"same"}]',
            },
        ]:
            with self.subTest(files=files), self.assertRaises((ValueError, KeyError)):
                load(files.__getitem__, "a.json")

    def test_portable_parser_is_identical(self):
        root = Path(__file__).resolve().parents[2]
        for name in ("data.py", "partition.py"):
            self.assertEqual(
                (root / "tools/repo_quality" / name).read_bytes(),
                (root / "meridian-microphone/lab/src/meridian_lab" / name).read_bytes(),
            )
