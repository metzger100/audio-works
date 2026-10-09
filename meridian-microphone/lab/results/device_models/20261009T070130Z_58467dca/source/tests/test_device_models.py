# SPDX-License-Identifier: GPL-3.0-or-later
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
                     'models/semiconductor/vendor/acquisition/observation.json',
                     'requirements.txt','tools/ngspice-run']:
        p=tmp_path/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('control')
    monkeypatch.setattr(core,'ROOT',tmp_path)
    manifest=core.source_manifest()
    assert 'models/semiconductor/vendor/a.LIB' in manifest
    assert 'research/device_sources/local/evidence.json' in manifest
    assert 'models/semiconductor/vendor/acquisition/observation.json' in manifest

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

def test_model_external_dependencies_cannot_escape_frozen_provenance(tmp_path):
    root,path=library(tmp_path,'.include "/tmp/unregistered.lib"\n.model CONTROL NJF(BETA=.01 VTO=-1)\n')
    with pytest.raises(ValueError,match='external dependency'):resolve(root,['v1'])

def test_model_ancestry_preserves_vendor_identity_and_rejects_missing_cycles(tmp_path):
    root,path=library(tmp_path)
    p=path.parent/'registry.yaml';registry=read_yaml(p)
    parent=registry['devices'][0]['models'][0]
    child={**parent,'id':'child','version':'authored-hypothesis','parent_model_id':'v1'}
    registry['devices'][0]['models'].append(child);p.write_text(yaml.safe_dump(registry))
    found=resolve(root,['child'])[0]
    assert found['model_lineage'][0]['id']=='v1'
    assert found['model_lineage'][0]['sha256']==digest(path)
    child['parent_model_id']='absent';p.write_text(yaml.safe_dump(registry))
    with pytest.raises(ValueError,match='Missing or cyclic'):resolve(root,['child'])
    child['parent_model_id']='v1';parent['parent_model_id']='child';p.write_text(yaml.safe_dump(registry))
    with pytest.raises(ValueError,match='Missing or cyclic'):resolve(root,['child'])

@pytest.mark.parametrize('failure',['process_error','missing_output','os_error'])
def test_failed_jobs_retain_exact_semiconductor_provenance(tmp_path,monkeypatch,failure):
    (tmp_path/'models').mkdir()
    model_root,model=library(tmp_path/'models')
    candidate=tmp_path/'candidates/control';candidate.mkdir(parents=True)
    (candidate/'topology.yaml').write_text(yaml.safe_dump({'id':'control','semiconductor_models':['v1']}))
    (candidate/'circuit.cir').write_text('.subckt DUT f b rear p n g rail\n.ends DUT\n')
    monkeypatch.setattr(core,'ROOT',tmp_path)
    monkeypatch.setattr(core,'defaults',lambda:{'TEMP':25})
    monkeypatch.setattr(core,'verify_spec_lock',lambda:None)
    def failed_run(*args,**kwargs):
        if failure=='os_error':raise OSError('controlled unavailable simulator')
        return subprocess.CompletedProcess(args[0],1 if failure=='process_error' else 0,
                                           'Error: controlled failure' if failure=='process_error' else '', '')
    monkeypatch.setattr(core.subprocess,'run',failed_run)
    sim=core.Simulator('control',tmp_path/'jobs')
    with pytest.raises(core.SimulationError):sim.execute('failure','op',['op.raw'])
    job=sim.jobs[-1]
    assert job['status']=='error'
    assert job['semiconductor_models'][0]['version']=='test-r1'
    assert job['semiconductor_models'][0]['sha256']==digest(model)
    assert job['netlist_sha256']==digest(tmp_path/'jobs/0001_failure/job.cir')

def test_two_port_capacitance_extraction_has_correct_signs_and_no_double_count(tmp_path):
    # Independent physical oracle for the MOS Ciss/Coss/Crss fixtures.
    for drive in ['gate','drain']:
        p=tmp_path/drive;p.mkdir()
        (p/'job.cir').write_text(f'''* independent passive terminal-admittance control
Vg g 0 DC 0 AC {int(drive=='gate')}
Vd d 0 DC 25 AC {int(drive=='drain')}
Cgs g 0 20p
Cgd g d 3p
Cds d 0 4p
.control
set filetype=ascii
ac lin 1 1Meg 1Meg
write ac.raw i(vg) i(vd)
quit
.endc
.end
''')
        result=subprocess.run([str(ROOT/'tools/ngspice-run'),'-n','-b','job.cir'],cwd=p,capture_output=True,text=True,timeout=15)
        (p/'simulator.log').write_text(result.stdout+'\n'+result.stderr)
        assert result.returncode==0
        raw=core.parse_raw(p/'ac.raw');omega=2*np.pi*1e6
        if drive=='gate':assert -raw['i(vg)'][0].imag/omega==pytest.approx(23e-12,rel=1e-9)
        else:
            assert -raw['i(vd)'][0].imag/omega==pytest.approx(7e-12,rel=1e-9)
            assert raw['i(vg)'][0].imag/omega==pytest.approx(3e-12,rel=1e-9)
