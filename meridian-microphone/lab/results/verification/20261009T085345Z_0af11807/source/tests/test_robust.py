# SPDX-License-Identifier: GPL-3.0-or-later
"""Adverse/error specimens, independent uncertainty, budgets and objective gates."""
from copy import deepcopy
import json
import numpy as np
import pytest
import yaml

from meridian_lab import robust
from meridian_lab.core import ROOT, Simulator, read_yaml


def test_missing_or_error_robust_objective_is_not_a_favorable_zero():
    rows = [{'status':'pass','m':1}, {'status':'fail','m':100}, {'status':'error'}]
    out = robust.aggregate(rows, 'm')
    assert not out['complete'] and out['value'] is None
    assert out['worst_observed'] == 100 and out['finite_samples']==2
    assert robust.aggregate(rows[:2], 'm', 'scenario_percentile')['value'] > 90
    assert robust.aggregate(rows[:2], 'm', direction='maximize')['value'] == 1


def test_periodic_and_missing_noise_never_rank_as_stationary_audio():
    assert not robust.audit({'analysis_domain':'periodic_mechanism_control'},'response')['allowed']
    assert not robust.audit({}, 'noise')['allowed']
    assert robust.audit({}, 'response')['allowed']
    assert not robust.audit({}, 'headroom')['allowed']
    with pytest.raises(ValueError):
        robust.audit({}, 'weighted_winner')


def test_seeded_holdout_keeps_original_capsule_bounds_and_cross_stray():
    meta=read_yaml(ROOT/'candidates/candidate_0015/topology.yaml')
    a=robust.random_scenarios(meta,84047,16)
    assert a == robust.random_scenarios(meta,84047,16)
    assert a != robust.random_scenarios(meta,94047,16)
    ranges=robust.uncertainty_ranges(meta)
    assert ranges['LEAK']==[1e9,1e14] and ranges['CF']==[45e-12,100e-12]
    assert ranges['CROSS']==[0,5e-12]
    corners=robust.corner_scenarios(meta)
    assert {c.get('model_replacement') for c in corners} >= {'jfe150_weak','jfe150_strong'}


def test_design_tolerance_is_centered_on_new_design_without_narrowing():
    meta=deepcopy(read_yaml(ROOT/'candidates/candidate_0015/topology.yaml'))
    meta['parameters']['COUTP_VALUE']['default']=188e-6
    definition={'OUTPUT_C':{'targets':['COUTP_VALUE'],'tolerance_fraction':.2}}
    assert robust.uncertainty_ranges(meta,definition)['COUTP_VALUE']==pytest.approx([150.4e-6,225.6e-6])


def test_small_sample_percentile_interval_has_unbounded_upper_tail():
    assert robust.percentile_interval(range(16))[1] is None
    assert robust.percentile_interval([])==[None,None]


def test_budget_counts_failures_and_unique_trials(monkeypatch,tmp_path):
    folder=tmp_path/'candidates/candidate_9999';folder.mkdir(parents=True)
    meta={'id':'candidate_9999','parameters':{'R':{'default':3}},'qualification_evidence':[]}
    (folder/'topology.yaml').write_text(yaml.safe_dump(meta))
    (folder/'circuit.cir').write_text('* analytic optimizer oracle\n')
    monkeypatch.setattr(robust,'ROOT',tmp_path)
    monkeypatch.setattr(robust,'source_manifest',lambda:{})
    monkeypatch.setattr(robust,'verify_spec_lock',lambda:None)
    monkeypatch.setattr(robust,'spec_digest',lambda:'frozen')
    monkeypatch.setattr(robust,'environment_versions',lambda:{})
    def oracle(candidate,directory,snapshot,overrides,scenarios,axis):
        # Independent convex physical-objective surrogate; a broad infeasible region
        # must not make the finite adverse trials disappear.
        v=abs(overrides['R']-7)/7
        return [{'status':'pass' if v<=.5 else 'fail','response_deviation_db':v,'current_a':.001} for _ in scenarios]
    monkeypatch.setattr(robust,'measure',oracle)
    record=robust.optimize('candidate_9999',{'R':{'targets':['R'],'range':[1,10],'rationale':'oracle'}},budget=9)
    assert record['evaluations']==9 and record['termination']=='evaluation_budget_exhausted'
    assert not record['scipy_success'] and not record['global_optimality']
    assert record['trial_failures']>0 and record['best'] is not None
    saved=json.loads((tmp_path/'results/runs'/record['experiment_id']/'trials.json').read_text())
    assert len(saved)==9 and record['scenario_attempts']==27


def test_parallel_capacitors_match_independent_admittance_oracle(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    for count in [1,4]:
        circuit='Vtest cap 0 AC 1\n'+''.join(f'Ctest{i} cap 0 47u\n' for i in range(count))
        data=sim.execute('parallel_control','ac lin 1 120 120\nwrite cap.raw all',['cap.raw'],extra=circuit)['cap.raw']
        assert -data['i(vtest)'][0].imag/(2*np.pi*120)==pytest.approx(count*47e-6,rel=1e-10)
