# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent energy/sideband oracles and rejection of invalid carrier scoring."""
from types import SimpleNamespace
import numpy as np
import pytest
from meridian_lab.core import Raw, Simulator, SimulationError
from meridian_lab.architectures import coherent_amplitudes, dc_accounting
from meridian_lab.qualification import evaluate
from meridian_lab.cli import implementation_manifest


def test_bom_changes_invalidate_implementation_snapshot(tmp_path):
    (tmp_path/'circuit.cir').write_text('* DUT')
    (tmp_path/'bom.yaml').write_text('part: original')
    original=implementation_manifest(tmp_path)
    (tmp_path/'results.json').write_text('{}')
    assert implementation_manifest(tmp_path)==original
    (tmp_path/'bom.yaml').write_text('part: substitute')
    assert implementation_manifest(tmp_path)!=original


def test_coherent_sidebands_do_not_confuse_baseline_imbalance_with_motion():
    t=np.linspace(.02,.03,64001)
    carrier=100000; audio=1000
    # Independent product-to-sum oracle, known AM index and arbitrary phase/DC.
    y=3.1 + .4*np.sin(2*np.pi*carrier*t+.3)*(1+.002*np.cos(2*np.pi*audio*t))
    peaks=coherent_amplitudes(t,y,[carrier-audio,carrier,carrier+audio])
    assert peaks[str(carrier)]==pytest.approx(.4,rel=1e-8)
    assert peaks[str(carrier-audio)]==pytest.approx(.0004,rel=1e-8)
    assert peaks[str(carrier+audio)]==pytest.approx(.0004,rel=1e-8)


def test_carrier_fit_rejects_truncated_or_duplicate_frequency_data():
    with pytest.raises(SimulationError): coherent_amplitudes([0,1],[0,0],[1])
    with pytest.raises(ValueError): coherent_amplitudes(np.linspace(0,1,100),np.zeros(100),[1,1])


def test_terminal_energy_accounts_for_device_and_resistor_power():
    raw=Raw({k:np.array([v]) for k,v in {
        'v(mic_g)':.01,'v(rail)':10.01,'v(f)':.01,'v(b)':.01,'v(rear)':.01,
        'i(v.xdut.vpower)':.002,'i(v.xdut.vreturn)':-.002}.items()},'Operating Point')
    sim=SimpleNamespace(meta={'power_devices':[dict(instance='load',model_id='oracle',nodes=['rail','g'],
                         currents=['i(v.xdut.vpower)','i(v.xdut.vreturn)'])],
                         'power_resistors':[dict(reference='Rload',nodes=['rail','g'],parameter='R')]},
                        params={'R':10000,'LEAK':1e12})
    out=dc_accounting(sim,raw,.03)
    assert out['summed_absorbed_power_w']==pytest.approx(.03)
    assert out['relative_residual']<1e-12
    assert out['devices'][0]['terminal_kcl_residual_a']==0


def test_periodic_backend_never_invokes_dc_audio_noise(monkeypatch):
    import meridian_lab.qualification as q
    import meridian_lab.architectures as a
    sim=SimpleNamespace(meta={'analysis_domain':'periodic_mechanism_control'},
                        execute=lambda *args,**kwargs:{'op.raw':'oracle'})
    monkeypatch.setattr(q,'operating_point',lambda sim,ctx:q.result('pass',{'current_a':.002}))
    monkeypatch.setattr(a,'carrier_control',lambda sim:{'periodic_noise':'incomplete'})
    out=evaluate(sim,checks=['operating_point','noise','distortion'])
    assert out['operating_point']['status']=='pass'
    assert out['noise']['status']==out['distortion']['status']=='incomplete'
    assert out['carrier_mechanism']['status']=='incomplete'


def test_capsule_carrier_sidebands_match_independent_charge_conservation(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    # Independent island: no amplifier, no P48 carrier power claim, zero parasitic
    # analytic control only. Application sweeps retain the full original envelope.
    extra='''Vrf bb 0 DC 40 SIN(40 .2 100k)
Vanti aa 0 DC 40 SIN(40 -.2 100k)
Vpressure pf 0 SIN(0 1 1k)
Vrearpressure pr 0 0
Xisland ff bb rr pf pr 0 FLAT_K47 CF=70p CR=70p PAR=1f CROSS=1f LEAK=1e14
Ccomparef ff aa 100p
Ccomparer rr aa 100p
Rreturnf ff 0 1e12
Rreturnr rr 0 1e12'''
    rows=[]
    for step in [1/(100000*32),1/(100000*64)]:
        raw=sim.execute('carrier_charge_oracle',f'tran {step:.16g} .03 .02 {step:.16g}\nwrite control.raw time v(ff) v(rr)',
                        ['control.raw'],extra=extra,environment_only=True)['control.raw']
        rows.append(coherent_amplitudes(raw['time'],raw.voltage('ff','rr'),[99000,100000,101000]))
    expected=.2*(70e-12*100e-12)/(170e-12)**2*(.02/60)
    for row in rows:
        assert row['99000']==pytest.approx(expected,rel=.02)
        assert row['101000']==pytest.approx(expected,rel=.02)
    assert rows[0]['99000']==pytest.approx(rows[1]['99000'],rel=.005)
