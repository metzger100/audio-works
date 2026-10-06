import copy
from pathlib import Path
import numpy as np
import pytest
import yaml
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
        assert 'noise' in c['not_covered'] and 'temperature' in c['not_covered']

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
