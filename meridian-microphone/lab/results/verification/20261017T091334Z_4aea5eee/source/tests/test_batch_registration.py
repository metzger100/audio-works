# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare registration requests with frozen source without creating candidates."""

from copy import deepcopy
import importlib.util
import sys

from meridian_lab.core import ROOT

sys.path.insert(0, str(ROOT / "search"))
import first_batch


def test_named_mechanism_builders_preserve_every_original_registration_request(monkeypatch):
    path = ROOT / "results/verification/20261011T122931Z_d7b00d15/source/search/first_batch.py"
    spec = importlib.util.spec_from_file_location("original_first_batch", path)
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    requests = []

    class Recorder:
        def __init__(self, *args, **kwargs):
            self.identity = (args, kwargs)
            self.meta = {"parameters": {}}
            self.lines = []
            self.calls = []

        def __getattr__(self, name):
            def record(*args, **kwargs):
                self.calls.append((name, args, kwargs))

            return record

        def finish(self):
            requests.append(deepcopy((self.identity, self.meta, self.lines, self.calls)))

    monkeypatch.setattr(original, "Attempt", Recorder)
    monkeypatch.setattr(first_batch, "Attempt", Recorder)
    original.main()
    expected = deepcopy(requests)
    requests.clear()
    first_batch.main()
    assert requests == expected
    assert [request[0][0][0] for request in requests] == list(range(1, 7))
