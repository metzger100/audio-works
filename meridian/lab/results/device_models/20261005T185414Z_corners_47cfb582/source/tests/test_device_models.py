import copy
from pathlib import Path
import numpy as np
import pytest
import yaml
import subprocess
from meridian_lab import core
from meridian_lab.core import ROOT, digest, read_yaml
from meridian_lab.device_models import resolve, candidate_models

def library(tmp_path,content='* test\n.model CONTROL NJF(BETA=.01 VTO=-1)\n'):
    p=tmp_path/'semiconductor';p.mkdir()
    model=p/'test.lib';model.write_text(content)
    registry={'devices':[{'id':'control','manufacturer':'test','models':[{'id':'v1','path':'semiconductor/test.lib',
        'sha256':digest(model),'acquisition_status':'valid_spice','version':'test-r1'}]}]}
    (p/'registry.yaml').write_text(yaml.safe_dump(registry))
    return tmp_path,model

def test_vendor_version_and_hash_are_resolved_and_tampering_fails(tmp_path):
    root,path=library(tmp_path)
    found=resolve(root,['v1'])[0]
    assert found['version']=='test-r1' and found['sha256']==digest(path)
    path.write_text(path.read_text()+'* change\n')
    with pytest.raises(ValueError,match='changed'):resolve(root,['v1'])

def test_html_and_missing_vendor_models_cannot_satisfy_provenance(tmp_path):
    root,path=library(tmp_path,'<html>challenge</html>\n')
    with pytest.raises(ValueError,match='Non-SPICE'):resolve(root,['v1'])
    path.unlink()
    with pytest.raises(ValueError,match='Missing'):resolve(root,['v1'])

def test_external_candidate_include_is_rejected(tmp_path):
    root,path=library(tmp_path)
    with pytest.raises(ValueError,match='registered'):candidate_models(root,{},'.include "/tmp/whatever.lib"')
    found,text=candidate_models(root,{'semiconductor_models':['v1']},'.subckt DUT a b\n.ends')
    assert str(path) in text and len(found)==1

def test_coupled_jfet_dc_bound_controls_obey_terminal_limits():
    corners=read_yaml(ROOT/'models/semiconductor/corners.yaml')
    assert corners['probability_distribution'] is None
    for c in corners['coupled_dc_controls']:
        assert c['beta_a_per_v2']*c['vto_v']**2==pytest.approx(c['idss_a'],rel=1e-12)
        assert -2*c['beta_a_per_v2']*c['vto_v']==pytest.approx(c['gfs_s'],rel=1e-12)
        assert .024<=c['idss_a']<=.046 and .055<=c['gfs_s']<=.080
        assert -1.1<=c['vgs_at_2ma_v']<=-.5
        assert -1.3<=c['vgs_at_100ua_v']<=-.7
        assert -1.5<=c['vgs_at_100na_v']<=-.9
        assert 'noise' in c['not_covered'] and 'temperature' in c['not_covered']
    failed=corners['level1_feasibility_gap']['failed_parent_tuple']
    cutoff=failed['vto_v']*(1-np.sqrt(1e-7/failed['idss_a']))
    assert cutoff>-.9
    assert corners['manufacturer_ranges']['idss_25c_a'][0]==.024

def test_duplicate_vendor_subcircuits_cannot_silently_override_models(tmp_path):
    root,path=library(tmp_path)
    registry=read_yaml(path.parent/'registry.yaml')
    registry['devices'][0]['models'].append({**registry['devices'][0]['models'][0],'id':'v2'})
    (path.parent/'registry.yaml').write_text(yaml.safe_dump(registry))
    with pytest.raises(ValueError,match='Duplicate SPICE definition'):
        candidate_models(root,{'semiconductor_models':['v1','v2']},'.subckt DUT a b\n.ends')

def test_local_model_definitions_in_different_subcircuits_are_allowed(tmp_path):
    root,path=library(tmp_path,'.subckt A a b\n.model SW SW(RON=1)\n.ends\n.subckt B a b\n.model SW SW(RON=2)\n.ends\n')
    models,_=candidate_models(root,{'semiconductor_models':['v1']},'.subckt DUT a b\n.ends')
    assert len(models)==1

def test_source_manifest_includes_vendor_bytes_and_public_evidence(tmp_path,monkeypatch):
    for relative in ['models/semiconductor/vendor/a.LIB','research/device_sources/local/evidence.json',
                     'requirements.txt','tools/ngspice-run']:
        p=tmp_path/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('control')
    monkeypatch.setattr(core,'ROOT',tmp_path)
    manifest=core.source_manifest()
    assert 'models/semiconductor/vendor/a.LIB' in manifest
    assert 'research/device_sources/local/evidence.json' in manifest

def test_failed_acquisition_and_missing_flicker_are_explicit_in_registry():
    registry=read_yaml(ROOT/'models/semiconductor/registry.yaml')
    devices={d['id']:d for d in registry['devices']}
    assert devices['2n7002']['models'][0]['acquisition_status']=='invalid_html_challenge'
    assert 'KF absent' in devices['bc856b']['represented_behavior']['noise']
    assert all(m['redistribution']['status']=='not_established_do_not_redistribute'
               for d in devices.values() for m in d.get('models',[]))

def test_coupled_dc_controls_match_native_spice_physics(tmp_path):
    controls=read_yaml(ROOT/'models/semiconductor/corners.yaml')['coupled_dc_controls']
    models=(ROOT/'models/semiconductor/dc_bound_controls.cir').read_text()
    devices='\n'.join(f'Vd{i} d{i} 0 10\nVg{i} g{i} 0 DC 0 AC 1\nJq{i} d{i} g{i} 0 DC_BOUND_{i}' for i in range(3))
    (tmp_path/'job.cir').write_text('* independently derived native DC controls\n'+models+'\n'+devices+
        '\n.temp 25\n.options tnom=25 reltol=1e-8\n.control\nset filetype=ascii\nop\nwrite op.raw all\nac lin 1 1000 1000\nwrite ac.raw all\nquit\n.endc\n.end\n')
    run=subprocess.run([str(ROOT/'tools/ngspice-run'),'-n','-b','job.cir'],cwd=tmp_path,capture_output=True,text=True,timeout=15)
    (tmp_path/'simulator.log').write_text(run.stdout+'\n'+run.stderr)
    assert run.returncode==0
    op=core.parse_raw(tmp_path/'op.raw');ac=core.parse_raw(tmp_path/'ac.raw')
    for i,c in enumerate(controls):
        assert -op[f'i(vd{i})'][0]==pytest.approx(c['idss_a'],rel=1e-6)
        assert abs(ac[f'i(vd{i})'][0])==pytest.approx(c['gfs_s'],rel=1e-6)
