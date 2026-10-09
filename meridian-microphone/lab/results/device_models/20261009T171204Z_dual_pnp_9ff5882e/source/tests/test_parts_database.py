# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
import importlib.util,copy,subprocess,os
import pytest,re
spec=importlib.util.spec_from_file_location('parts_db',Path(__file__).resolve().parents[1]/'research/parts_database.py')
db=importlib.util.module_from_spec(spec);spec.loader.exec_module(db)

def fixture():
    return dict(measurement_state='No capsule or owned-stock measurements evidenced',role_gap_matrix=[{'id':'p48_power'}],parts=[
        dict(device_id='npn',manufacturer='Maker A',exact_mpn='2N5551',roles=['p48_power'],states=dict(investigated=True,acquired=True,characterized=False,candidate_combination_qualified=False,behavior_validated={}),models=[
            dict(id='v1',path='vendor/v1.lib',sha256='a'*64,acquisition='valid_spice'),
            dict(id='v2',path='vendor/v2.lib',sha256='b'*64,acquisition='valid_spice')])],research_leads=[dict(exact_mpn='MMBFJ113',roles=[],states=dict(investigated=True,acquired=False,characterized=False,candidate_combination_qualified=False))])

def test_search_keeps_exact_devices_variants_and_leads_separate():
    data=fixture();assert len(db.search(data,'5551',role='p48_power'))==1
    assert not db.search(data,'MMBFJ113',state='acquired')
    assert db.counts(data)['exact_semiconductor_devices']==1
    assert db.counts(data)['valid_spice_files']==2
    assert db.counts(data)['physical_owned_stock'] is None
    assert not db.audit(data)

def test_false_promotion_and_unconditioned_behavior_fail_closed():
    data=fixture();part=data['parts'][0]
    part['states']['candidate_combination_qualified']=True
    assert len(db.audit(data))==3
    part['states']['candidate_combination_qualified']=False
    part['states']['behavior_validated']=[dict(status='pass',condition='',evidence='guaranteed_limit')]
    assert 'lacks conditions' in db.audit(data)[0]
    part['states']['behavior_validated']=[];part['states']['acquired']=False;part['states']['characterized']=True
    assert 'without acquired' in db.audit(data)[0]

def test_wrapper_accepts_documented_modes_and_rejects_injected_mode(tmp_path):
    lab=Path(__file__).resolve().parents[1];backend=lab/'tools/ngspice/usr/bin/ngspice'
    if not backend.exists():pytest.skip('Local simulator not installed')
    deck=tmp_path/'unit.cir';deck.write_text('Compatibility control\nV1 n 0 1\nR1 n 0 1k\n.control\nop\nprint i(V1)\nquit\n.endc\n.end\n')
    for mode in ['ps','ltpsa']:
        result=subprocess.run([str(lab/'tools/ngspice-run'),'-n','-b',str(deck)],env={**os.environ,'MERIDIAN_NGSPICE_BEHAVIOR':mode},capture_output=True,text=True,timeout=15)
        assert result.returncode==0
        current=re.search(r'i\(v1\)\s*=\s*([-+0-9.eE]+)',result.stdout)
        assert current and float(current.group(1))==pytest.approx(-.001,rel=1e-6)
        assert ('ps lt a' if mode=='ltpsa' else 'ps') in result.stdout
    result=subprocess.run([str(lab/'tools/ngspice-run'),'-n','-b',str(deck)],env={**os.environ,'MERIDIAN_NGSPICE_BEHAVIOR':'ps\nquit'},capture_output=True,text=True,timeout=15)
    assert result.returncode==2;assert 'Unsupported explicit' in result.stderr
