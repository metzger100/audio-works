import json
from pathlib import Path
import numpy as np
import pytest

from meridian_lab import core
from meridian_lab.archive import dominates, graph_features, novelty
from meridian_lab.core import ROOT, Raw, SimulationError, Simulator, parse_raw, read_yaml
from meridian_lab.metrics import harmonic_spectrum, population_summary


def test_invalid_spice_is_failure_even_with_zero_exit(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    with pytest.raises(SimulationError):
        sim.execute('invalid','op\nwrite op.raw all',['op.raw'],extra='Binvalid invalid 0 V=unsupported_function(v(f))')
    assert sim.jobs[-1]['status']=='error'


def test_missing_analysis_never_passes(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    with pytest.raises(SimulationError):
        sim.execute('missing','op',['missing.raw'])


def test_truncated_raw_rejected(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    sim.op_ac()
    source=next(tmp_path.glob('*/ac.raw'))
    broken=tmp_path/'truncated.raw'
    broken.write_text('\n'.join(source.read_text().splitlines()[:-10]))
    with pytest.raises(SimulationError):
        parse_raw(broken)


def test_silent_spec_changes_rejected(monkeypatch):
    monkeypatch.setattr(core,'spec_digest',lambda:'unexpected_change')
    with pytest.raises(ValueError,match='Specification changed'):
        core.verify_spec_lock()


def test_no_fundamental_is_not_zero_distortion_pass():
    t=np.linspace(0,.1,10000)
    with pytest.raises(ValueError,match='No measurable fundamental'):
        harmonic_spectrum(t,np.zeros_like(t),1000)


def test_failed_simulations_stay_in_population_denominator():
    m=population_summary([{'status':'pass','metric':1},{'status':'error'},{'status':'fail','metric':2}],'metric')
    assert m['observed_pass_fraction']==pytest.approx(1/3)
    assert not m['yield_claim']
    allpass=population_summary([{'status':'pass','metric':1}]*16,'metric')
    assert allpass['binomial_95_interval'][0]<0.8  # 16 successes cannot establish 99.9% yield.


def test_novelty_is_value_independent_and_does_not_grant_dominance(tmp_path):
    a=tmp_path/'a.cir'; b=tmp_path/'b.cir'
    a.write_text('R1 input output 1000\nC1 output 0 1n\n')
    b.write_text('Rother input output 12345\nCother output 0 500p\n')
    assert graph_features(a)['graph_signature']==graph_features(b)['graph_signature']
    base={'spec_sha256':'a','suite_sha256':'b','backend':'ngspice','metrics':{'noise':1}}
    challenger={**base,'metrics':{'noise':0.5}}
    assert dominates(challenger,base,{'noise':'minimize'})
    assert not dominates(challenger,base,{'noise':'minimize','yield':'maximize'})
    assert not dominates({**challenger,'spec_sha256':'changed'},base,{'noise':'minimize'})


def test_ideal_fixture_cannot_be_qualified():
    meta=read_yaml(ROOT/'candidates/fixture_0001/topology.yaml')
    assert meta['ideal_devices'] and not meta['eligible'] and meta['kind']=='infrastructure_fixture'


def test_spec_numeric_ranges_and_required_measurements():
    capsule=read_yaml(ROOT/'spec/capsule_model.yaml')
    for parameter in capsule['parameters'].values():
        if 'nominal' in parameter:
            assert isinstance(parameter['nominal'],(float,int))
        if 'range' in parameter:
            lo,hi=parameter['range']; assert isinstance(lo,(float,int)) and lo<=hi
    assert capsule['parameters']['maximum_safe_polarization_v']['value'] is None
    q=read_yaml(ROOT/'spec/microphone_spec.yaml')['qualification']
    assert 'physical_measurements' in q['evidence_required'] and not q['missing_or_error_is_pass']
