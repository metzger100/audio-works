# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit architecture accounting and deterministic carrier controls.

No periodic-noise or hardware-qualification claim is supplied by this module.
"""
import numpy as np
from .core import SimulationError


def node_voltage(raw, node):
    name = {'g':'mic_g','f':'f','b':'b','rear':'rear','p':'p','n':'n','rail':'rail'}.get(node,'xdut.'+node.lower())
    return float(raw.voltage(name,'mic_g')[0].real)


def dc_accounting(sim, raw, terminal_power):
    devices=[]
    for device in sim.meta.get('power_devices',[]):
        voltages=[node_voltage(raw,n) for n in device['nodes']]
        currents=[float(raw[c][0].real) for c in device['currents']]
        devices.append(dict(instance=device['instance'],model_id=device['model_id'],
                            terminal_voltages_v=voltages,terminal_currents_a=currents,
                            absorbed_power_w=float(np.dot(voltages,currents)),
                            terminal_kcl_residual_a=float(sum(currents))))
    resistors=[]
    for resistor in sim.meta.get('power_resistors',[]):
        a,b=[node_voltage(raw,n) for n in resistor['nodes']]
        resistors.append(dict(reference=resistor['reference'],absorbed_power_w=(a-b)**2/sim.params[resistor['parameter']]))
    capsule_power=sum(float(raw.voltage('b',x)[0].real)**2/sim.params['LEAK'] for x in ['f','rear'])
    absorbed=sum(d['absorbed_power_w'] for d in devices)+sum(r['absorbed_power_w'] for r in resistors)+capsule_power
    return dict(devices=devices,resistors=resistors,capsule_leakage_power_w=capsule_power,
                summed_absorbed_power_w=absorbed,terminal_power_w=terminal_power,
                residual_w=terminal_power-absorbed,
                relative_residual=abs(terminal_power-absorbed)/max(abs(terminal_power),1e-20),
                scope='DC terminal energy only; vendor macro internals, thermal/SOA and periodic controls unqualified')


def coherent_amplitudes(t, y, frequencies):
    """Simultaneously fit carrier/sidebands; avoids rectangular FFT leakage.

    Fit only a settled coherent window chosen by the caller. Returns peak amplitude.
    """
    t=np.asarray(t).real; y=np.asarray(y).real
    if len(t)<16 or not np.isfinite(y).all() or not np.all(np.diff(t)>0):
        raise SimulationError('Invalid periodic waveform')
    if len(set(frequencies)) != len(frequencies) or any(f<=0 for f in frequencies):
        raise ValueError('Distinct positive frequencies required')
    columns=[np.ones_like(t),t-t.mean()]
    for f in frequencies:
        columns += [np.sin(2*np.pi*f*t),np.cos(2*np.pi*f*t)]
    matrix=np.column_stack(columns)
    coefficients,_,rank,_=np.linalg.lstsq(matrix,y,rcond=None)
    if rank != len(columns): raise SimulationError('Singular carrier fit')
    return {str(f):float(np.hypot(*coefficients[2+2*i:4+2*i])) for i,f in enumerate(frequencies)}


def periodic_frequencies(carrier, audio):
    """Include direct audio and mixer images on nonuniform simulator time grids."""
    return [audio,2*audio]+[n*carrier+k*audio for n in [1,2] for k in [-2,-1,0,1,2]]


def carrier_control(sim):
    """Runnable pressure/carrier on-off controls, with explicit unsupported noise.

    The frozen test uses 100 kHz carrier, 1 kHz pressure, two timestep densities.
    It retains baseline imbalance, phase/filter loss and real buffer/output loading.
    """
    carrier=sim.params['CARRIER_HZ']; audio=1000.; rows=[]
    fit_frequencies=periodic_frequencies(carrier,audio)
    vectors='time v(mic_g) v(f) v(b) v(rear) v(pp) v(pn) v(xdut.frontbuf) v(xdut.rearbuf) v(xdut.demod) v(xdut.audio) i(v.xenv.vphantom)'
    for pressure,amplitude,density in [(0.,sim.params['CARRIER_PEAK'],32),(1.,0.,32),
                                        (1.,sim.params['CARRIER_PEAK'],32),(1.,sim.params['CARRIER_PEAK'],64)]:
        step=1/(carrier*density)
        wave=sim.execute('carrier_control',f'tran {step:.16g} .03 .02 {step:.16g}\nwrite carrier.raw {vectors}',
                         ['carrier.raw'],dict(FREQ=audio,PRESSURE_PEAK=pressure,CARRIER_PEAK=amplitude,LIN=0))['carrier.raw']
        t=wave['time'].real
        rf=wave.voltage('xdut.frontbuf','xdut.rearbuf')
        rows.append(dict(pressure_peak_pa=pressure,carrier_peak_v=amplitude,samples_per_carrier=density,
                         bridge_peak_v=coherent_amplitudes(t,rf,fit_frequencies),
                         output_peak_v=coherent_amplitudes(t,wave.voltage('pp','pn'),fit_frequencies),
                         demod_peak_v=coherent_amplitudes(t,wave.voltage('xdut.demod','mic_g'),fit_frequencies),
                         mean_phantom_current_a=float(-np.mean(wave['i(v.xenv.vphantom)'].real)),
                         period_noise_validated=False))
    coarse,fine=rows[-2:]
    v0=coarse['output_peak_v'][str(audio)];v1=fine['output_peak_v'][str(audio)]
    refinement=abs(v0-v1)/max(v1,1e-30)
    return dict(cases=rows,output_timestep_relative_change=refinement,
                mechanism_observation='deterministic sidebands/demodulation only; unsupported periodic noise does not reject the family',
                periodic_noise='incomplete: stationary device spectra, cyclostationary folding, oscillator AM/PM, stochastic injection and PSD confidence not validated',
                hardware_energy='incomplete: ideal excitation/multiplier and any ideal buffers deliver unbudgeted power; currents of present physical model blocks are recorded, but do not constitute complete architecture evidence',
                full_audio_band='not validated; present low-pass is a 1 kHz mechanism control')
