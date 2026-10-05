import importlib.util
from pathlib import Path
import numpy as np
import pytest

from meridian_lab.core import ROOT, Simulator, read_yaml
from meridian_lab.metrics import at_frequency, harmonic_spectrum


def test_distortion_numerical_refinement_matches_linear_ac_oracle(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    nominal=sim.op_ac()
    pol=float(nominal['op.raw'].voltage('b','f')[0])
    gain=abs(at_frequency(nominal['ac.raw']['frequency'],nominal['ac.raw'].voltage('pp','pn'),1000))
    results=[]
    for samples in [128,256]:
        wave=sim.transient(1000,np.sqrt(2),samples=samples,settling=.5,overrides={'LIN':1,'POLDC':pol})
        results.append(harmonic_spectrum(wave['time'],wave.voltage('pp','pn'),1000))
    for r in results:
        assert r['harmonics_v_rms'][0]==pytest.approx(gain,rel=.002)
        assert r['thd_percent']<.001
    assert abs(results[0]['harmonics_v_rms'][0]/results[1]['harmonics_v_rms'][0]-1)<.001


def test_all_requested_families_have_proposals_and_nine_physical_questions():
    families=read_yaml(ROOT/'search/families.yaml')['families']
    concepts=read_yaml(ROOT/'search/concepts.yaml')['concepts']
    assert len(families)>=14 and len(concepts)>=20
    assert {f['id'] for f in families}<=set(x for c in concepts for x in c['families'])
    assert sum(c['nonconventional_jfet_buffer'] for c in concepts)>=len(concepts)/2
    assert sum(c['scientific_transfer'] for c in concepts)>=5
    for c in concepts:
        for key in ['sensed_quantity','loading_control','dc_bias','gain_or_impedance_transformation','balanced_output','expected_dominant_noise','expected_dominant_distortion','likely_fatal_flaw','fastest_falsification']:
            assert c[key]
        assert c['status']=='proposed_not_simulated' and not c['performance_claim']


def test_exploration_allocator_tracks_requested_proportions():
    path=ROOT/'search/selection.py'
    spec=importlib.util.spec_from_file_location('meridian_selection_test',path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    counts={}
    for _ in range(100):
        chosen=module.next_allocation(counts); counts[chosen]=counts.get(chosen,0)+1
    assert counts=={'improve':50,'underexplored':25,'new_concepts':15,'assumption_breaking':10}
