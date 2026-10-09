# SPDX-License-Identifier: GPL-3.0-or-later
import importlib.util
from pathlib import Path
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('parts_controls',Path(__file__).resolve().parents[1]/'research/parts_controls_001.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_noise_figure_oracle_uses_power_and_bandwidth():
    f=np.linspace(900,1100,201); johnson=np.sqrt(4*1.380649e-23*298.15*2000)
    assert module.nf_db(f,np.full_like(f,johnson),2000,298.15)==pytest.approx(0,abs=1e-10)
    assert module.nf_db(f,np.full_like(f,2*johnson),2000,298.15)==pytest.approx(6.0205999133)
    with pytest.raises(ValueError):module.nf_db(f,np.ones_like(f),0,298.15)

def test_capacitance_observer_rejects_conductance_as_capacitance():
    assert module.capacitance(2e-6+2j*np.pi*1e6*17e-12,1e6)==pytest.approx(17e-12)

def test_derivative_audit_fails_if_original_or_child_changes(tmp_path):
    from acquire import audit_local_derivatives,sha
    original=tmp_path/'manufacturer.pdf';original.write_bytes(b'%PDF original')
    child=tmp_path/'literal.lib';child.write_bytes(b'.model Q NJF(VTO=-1)')
    entry={'id':'literal','path':child.name,'sha256':sha(child.read_bytes()),'ancestor_path':original.name,
           'ancestor_sha256':sha(original.read_bytes()),'operation':'literal transcription'}
    assert audit_local_derivatives([entry],tmp_path)[0]['status']=='ok'
    original.write_bytes(b'%PDF changed')
    assert audit_local_derivatives([entry],tmp_path)[0]['status']=='error'
    original.write_bytes(b'%PDF original');child.write_bytes(b'.model Q NJF(VTO=-2)')
    assert audit_local_derivatives([entry],tmp_path)[0]['status']=='error'
    entry['ancestor_path']='../escape.pdf'
    assert audit_local_derivatives([entry],tmp_path)[0]['status']=='error'
