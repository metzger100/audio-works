"""Independent analytic oracles. Simulator completion alone is insufficient."""
import numpy as np
import pytest

from meridian_lab.core import Simulator
from meridian_lab.metrics import at_frequency, a_weighting, harmonic_spectrum, integrate_asd
from meridian_lab.qualification import output_impedance, loading


def test_capsule_ac_matches_charge_conservation(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    data=sim.execute('capsule_oracle','op\nwrite op.raw all\nac dec 16 20 20k\nwrite ac.raw all', ['op.raw','ac.raw'],capsule_only=True)
    p=sim.params; f=1000; w=2*np.pi*f
    # DC leakage reduces the effective polarization; finite input resistance and stray C reduce transfer.
    pol=p['POLDC']*p['LEAK']/(p['LEAK']+p['BIAS_R'])
    ctotal=p['CF']+p['PAR']+p['CROSS']+p['INPUT_C']
    expected=1j*w*p['CF']*p['SREF']/p['VREF']*pol/(1/p['BIAS_R']+1/p['LEAK']+1j*w*ctotal)
    actual=at_frequency(data['ac.raw']['frequency'],data['ac.raw'].voltage('f','mic_g'),f)
    assert abs(actual)>0.01  # specifically rejects the silent zero-AC derivative model
    assert actual==pytest.approx(expected,rel=3e-4)


def test_p48_loaded_rail_matches_feed_and_cable_drop(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    data=sim.op_ac(); p=sim.params
    series=(6800+p['LEN']*p['RW']+p['HARVEST_R'])/2+p['LEN']*p['RS']
    expected=p['VS']*p['POWER_R']/(p['POWER_R']+series)
    rail=float(data['op.raw'].voltage('rail','mic_g')[0])
    assert rail==pytest.approx(expected,rel=1e-4)
    assert rail<p['VS']-5


def test_output_impedance_two_port_deembedding_matches_analytic_network(tmp_path):
    # Disable capsule-to-output controlled gain for this symmetric passive oracle.
    # With gain enabled, backplate supply coupling can create real impedance imbalance.
    sim=Simulator('fixture_0001',tmp_path,{'GAIN':0})
    out=output_impedance(sim,{})['metrics']
    f=10000; p=sim.params
    expected=2/(1/(p['OUTPUT_R']+1/(2j*np.pi*f*p['OUTPUT_C']))+1/p['HARVEST_R'])
    z=np.array(out['raw_dut_z_real'])+1j*np.array(out['raw_dut_z_imag'])
    v=np.array([1,-1]); zd=np.einsum('i,nij,j->n',v,z,v)
    assert at_frequency(out['frequency_hz'],zd,f)==pytest.approx(expected,rel=3e-4)
    assert out['impedance_mismatch_fraction']<1e-5


def test_three_port_loading_extracts_known_input_capacitance(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    nominal=sim.op_ac()
    pol=float(nominal['op.raw'].voltage('b','f')[0])
    out=loading(sim,{'nominal':nominal,'polarization_dc_v':pol})['metrics']
    cin=at_frequency(out['frequency_hz'],out['clamped_electrode_input_capacitance_f'],1000)
    assert cin==pytest.approx(sim.params['INPUT_C'],rel=0.005)
    conductance=at_frequency(out['frequency_hz'],out['clamped_electrode_input_conductance_s'],1000)
    assert conductance==pytest.approx(1/sim.params['BIAS_R'],rel=0.01)


def test_harmonics_on_adaptive_like_nonuniform_grid():
    rng=np.random.default_rng(123)
    t=np.r_[0,np.cumsum(rng.uniform(0.05,1.0,60000))]
    t=t/t[-1]*0.1
    y=0.3+np.sin(2*np.pi*1000*t)+0.01*np.sin(2*np.pi*2000*t)+0.02*np.cos(2*np.pi*3000*t)
    m=harmonic_spectrum(t,y,1000)
    assert m['h2_percent']==pytest.approx(1,rel=.002)
    assert m['h3_percent']==pytest.approx(2,rel=.002)
    assert m['thd_percent']==pytest.approx(np.sqrt(5),rel=.002)


def test_white_noise_integral_and_a_weighting_normalization():
    f=np.geomspace(20,20000,1000)
    assert integrate_asd(f,np.full_like(f,1e-9))==pytest.approx(1e-9*np.sqrt(19980))
    assert a_weighting(np.array([1000]))[0]==pytest.approx(1,rel=.002)


def test_capsule_ac_transient_agree_in_linearized_mode(tmp_path):
    sim=Simulator('fixture_0001',tmp_path)
    out=sim.execute('ac_transient_oracle','ac dec 16 20 20k\nwrite ac.raw all\ntran 4u .3 .2 4u\nwrite tran.raw all',
                    ['ac.raw','tran.raw'],{'LIN':1,'POLDC':40,'PRESSURE_PEAK':.01},capsule_only=True)
    gain=abs(at_frequency(out['ac.raw']['frequency'],out['ac.raw'].voltage('f','mic_g'),1000))
    h=harmonic_spectrum(out['tran.raw']['time'],out['tran.raw'].voltage('f','mic_g'),1000)
    assert h['harmonics_v_rms'][0]==pytest.approx(gain*.01/np.sqrt(2),rel=.002)
