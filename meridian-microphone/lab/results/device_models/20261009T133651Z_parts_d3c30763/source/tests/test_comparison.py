# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent guards for reporting scopes and contribution accounting."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

SPEC = importlib.util.spec_from_file_location(
    'comparison', Path(__file__).resolve().parents[1] / 'research/compare_architectures.py')
comparison = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comparison)


def test_disjoint_noise_power_and_unknown_roots():
    # Independent two-resistor oracle: RMS quadrature, not summed ASD.
    f = np.array([20., 20000.])
    roots = {'onoise_r.xdut.rbias': np.array([3., 3.]),
             'onoise_r.xdut.routp': np.array([4., 4.]),
             'onoise_r.xcap.rfront': np.array([12., 12.])}
    groups, spectra, closure = comparison.verify_partition(f, roots, np.array([13., 13.]))
    assert len(groups) == 3 and closure == 0
    assert np.all(spectra['input bias, reset and degeneration'] == 3)
    with pytest.raises(ValueError, match='Unclassified'):
        comparison.noise_group('onoise_r.xdut.unlisted')
    with pytest.raises(ValueError, match='does not close'):
        comparison.verify_partition(f, roots, np.array([14., 14.]))


def test_pareto_missing_axes_and_no_scalar_winner():
    rows = [{'candidate': 'unknown', 'response': None, 'current': 0},
            {'candidate': 'flat', 'response': 1, 'current': 5},
            {'candidate': 'low_power', 'response': 2, 'current': 3},
            {'candidate': 'dominated', 'response': 2, 'current': 5}]
    assert comparison.pareto(rows, ['response', 'current']) == ['flat', 'low_power']


def test_cohort_guard_checks_sources_and_backend():
    a = {'spec_sha256': 's', 'suite_sha256': 't', 'backend': 'ngspice', 'source_manifest': {'a': 'h'}}
    comparison.require_common([a, dict(a)])
    for mutation in [{'source_manifest': {'a': 'changed'}}, {'backend': 'physical_measurement'},
                     {'spec_sha256': 'different'}, {'suite_sha256': 'different'}]:
        with pytest.raises(ValueError, match='cohorts'):
            comparison.require_common([a, {**a, **mutation}])


def test_connectivity_retains_macro_pin_order_and_ideals():
    lines = 'VQ_0 rail q0 0\nXQ q0 base emitter BC846B\nR1 emitter g {R}\nEout out g VOL=\'2*v(mid,g)-v(audio,g)\'\n'
    elements = comparison.parse_elements(lines, {'R': 1000})
    assert elements[1]['nodes'] == ['q0', 'base', 'emitter']
    assert elements[2]['value_or_model'] == '1000'
    assert elements[3]['kind'] == 'E' and elements[3]['nodes'] == ['out', 'g']
