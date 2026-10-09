from __future__ import annotations

from itertools import product
import numpy as np

from .core import ROOT, SimulationError, read_yaml
from .metrics import at_frequency, db, device_noise_totals, harmonic_spectrum, integrate_asd, population_summary


def result(status, metrics=None, reason=None, coverage=None):
    return {'status': status, 'metrics': metrics or {}, 'reason': reason, 'coverage': coverage}


def thresholds():
    return read_yaml(ROOT / 'spec/microphone_spec.yaml')['requirements']


def scenario_ranges():
    c=read_yaml(ROOT/'spec/capsule_model.yaml')['parameters']
    d=read_yaml(ROOT/'spec/design_constraints.yaml'); p=d['power']; e=d['environment']
    return {'VS':p['supply_v']['range'],'FT':p['feed_absolute_tolerance_fraction']['range'],'FM':p['feed_pair_mismatch_fraction']['range'],
            'CF':c['front_capacitance_f']['range'],'CR':c['rear_capacitance_f']['range'],'LEAK':c['leakage_resistance_ohm']['range'],
            'PAR':c['parasitic_to_case_f']['range'],'SREF':c['sensitivity_at_reference_v_per_pa']['range'],
            'LEN':e['cable_length_m']['range'],'RW':e['cable_resistance_ohm_per_m_per_conductor']['range'],
            'CD':e['cable_direct_capacitance_f_per_m']['range'],'CS':e['cable_each_leg_to_shield_f_per_m']['range'],
            'ZIN':e['preamp_differential_load_ohm']['range'],'ZM':e['preamp_leg_mismatch_fraction']['range'],'TEMP':e['temperature_c']['range']}


def current(raw):
    return float(-raw['i(v.xenv.vphantom)'][0].real)


def response(raw):
    f = raw['frequency'].real
    gain = raw.voltage('pp', 'pn')
    ref = abs(at_frequency(f, gain, 1000))
    if ref < 1e-9:
        raise SimulationError('Missing useful pressure-to-output transfer')
    mask = (f >= 20) & (f <= 20000)
    # Include exact band edges; logarithmic sweep need not land on 20 Hz or 20 kHz.
    frequencies = np.r_[20, f[mask], 20000]
    band = np.array([at_frequency(f, gain, x) for x in frequencies])
    relative = 20*np.log10(np.maximum(np.abs(band)/ref, 1e-300))
    return {'sensitivity_v_per_pa_at_1khz': float(ref), 'response_deviation_db': float(np.max(np.abs(relative))),
            'lf_db': db(at_frequency(f, gain, 20)/ref), 'hf_db': db(at_frequency(f, gain, 20000)/ref),
            'phase_1khz_deg': float(np.angle(at_frequency(f, gain, 1000), deg=True)),
            'frequency_hz': f.tolist(), 'gain_v_per_pa': abs(gain).tolist(),
            'phase_deg': np.rad2deg(np.unwrap(np.angle(gain))).tolist()}


def operating_point(sim, ctx):
    raw = ctx['nominal']['op.raw']
    p = sim.params
    i = current(raw)
    vp = float(raw.voltage('p', 'mic_g')[0])
    vn = float(raw.voltage('n', 'mic_g')[0])
    rail = float(raw.voltage('rail', 'mic_g')[0])
    pol = float(raw.voltage('b', 'f')[0])
    xp = float(raw['v(xenv.xp)'][0])
    xn = float(raw['v(xenv.xn)'][0])
    ip = (p['VS']-xp)/(6800*(1+p['FT'])*(1+p['FM']/2))
    inn = (p['VS']-xn)/(6800*(1+p['FT'])*(1-p['FM']/2))
    mismatch = abs(ip-inn)/max(abs((ip+inn)/2), 1e-20)
    ok = 0 < i <= thresholds()['current_max_a']['value'] and 0 < rail < p['VS'] and pol > 0
    ctx['polarization_dc_v'] = pol
    m = {'current_a': i, 'current_per_leg_a': [ip, inn], 'conductor_current_mismatch_fraction': mismatch,
         'mic_terminal_v': [vp, vn], 'internal_rail_v': rail, 'polarization_dc_v': pol,
         'supplied_power_w': p['VS']*i, 'terminal_power_w': vp*ip+vn*inn,
         'device_power_qualification': 'pending part ratings/SOA; ideal fixture energy not accounted',
         'safe_capsule_bias': 'unknown; simulated voltage is not approved for hardware'}
    if sim.meta.get('power_devices'):
        from .architectures import dc_accounting
        m['dc_energy_accounting']=dc_accounting(sim,raw,m['terminal_power_w'])
        m['device_power_qualification']='Terminal currents/powers recorded; thermal/SOA and vendor power-block fidelity remain unqualified'
        if m['dc_energy_accounting']['relative_residual'] > 1e-4:
            ok=False
    return result('pass' if ok else 'fail', m, coverage='DC feasibility screen; device safe operating area remains a separate evidence gate')


def frequency_response(sim, ctx):
    m = response(ctx['nominal']['ac.raw'])
    return result('pass' if m['response_deviation_db'] <= thresholds()['electronics_response_db']['value'] else 'fail', m, coverage='1 Hz to 10 MHz, nominal environment; electrical model only')


def noise(sim, ctx):
    raw = sim.noise()
    f = raw['frequency'].real
    ac = ctx['nominal']['ac.raw']
    gain = np.array([abs(at_frequency(ac['frequency'], ac.voltage('pp','pn'), x)) for x in f])
    if np.any(gain < 1e-12):
        raise SimulationError('Cannot refer noise through zero capsule transfer')
    # ngspice noise vectors contain both per-element totals and sub-contributions.
    # Include each element total once; never add thermal/flicker children again.
    totals = device_noise_totals(raw)
    groups = {}
    matched = set()
    for group, prefixes in sim.meta.get('noise_groups', {}).items():
        keys = [k for k in totals if any(k.startswith(prefix) for prefix in prefixes)]
        if matched.intersection(keys):
            raise ValueError('Overlapping noise groups would double count noise')
        matched.update(keys)
        density = np.sqrt(sum((totals[k]**2 for k in keys), np.zeros_like(f)))
        groups[group] = {'output_v_rms': integrate_asd(f, density), 'pa_rms': integrate_asd(f, density/gain), 'vectors': keys}
    # Classification is explicit: DUT = electronics, capsule leakage = electrical surrogate,
    # environment = feed/cable/preamp load Johnson noise, excluded from microphone electronics.
    internal = np.sqrt(sum((v**2 for k,v in totals.items() if '.xdut.' in k), np.zeros_like(f)))
    external = np.sqrt(sum((v**2 for k,v in totals.items() if '.xenv.' in k), np.zeros_like(f)))
    sum_density = np.sqrt(sum((v**2 for v in totals.values()), np.zeros_like(f)))
    total = raw['onoise_spectrum'].real
    closure = float(np.max(np.abs(sum_density-total)/np.maximum(total,1e-30)))
    if closure > 1e-5:
        raise SimulationError(f'Noise contribution power does not close: relative error {closure}')
    if not any('.xdut.' in k for k in totals):
        raise SimulationError('No DUT noise sources were extracted; cannot claim zero electronics noise')
    pa = integrate_asd(f, internal/gain)
    paw = integrate_asd(f, internal/gain, True)
    s = sim.params['SREF'] * ctx['polarization_dc_v']/sim.params['VREF']
    ein = pa*s
    dba = db(paw/20e-6)
    m = {'band_hz': [float(f[0]),float(f[-1])], 'electronics_noise_pa_rms': pa,
         'electronics_noise_a_pa_rms': paw, 'electronics_noise_dba_conditional': dba,
         'electronics_ein_v_rms_conditional': ein, 'electronics_output_v_rms': integrate_asd(f, internal),
         'environment_output_v_rms': integrate_asd(f, external), 'full_fixture_output_v_rms': integrate_asd(f,total),
         'noise_power_closure_relative_error': closure, 'groups': groups,
         'unclassified_vectors': sorted(set(totals)-matched), 'frequency_hz': f.tolist(),
         'electronics_output_asd_v_per_sqrt_hz': internal.tolist(), 'full_fixture_asd_v_per_sqrt_hz': total.tolist(),
         'mechanical_capsule_noise_included': False, 'semiconductor_noise_validated': False}
    ok = ein <= thresholds()['electronics_ein_unweighted_v_rms']['value'] and dba <= thresholds()['electronics_noise_dba']['value']
    return result('pass' if ok else 'fail', m, coverage='Resistive fixture noise; conditional capsule sensitivity. Semiconductor and capsule mechanical noise unresolved.')


def distortion(sim, ctx):
    rows = []
    for f, level in product([100,1000,10000], [1.0, 20e-6*10**(135/20)]):
        wave = sim.transient(f, level*np.sqrt(2), settling=0.5, overrides={'LIN':1, 'POLDC':ctx['polarization_dc_v']})
        m = harmonic_spectrum(wave['time'], wave.voltage('pp','pn'), f)
        # Compare final two coherent windows to detect incomplete settling.
        cut = wave['time'].real[-1]-16/f
        earlier = wave['time'].real <= cut
        prior = harmonic_spectrum(wave['time'].real[earlier], wave.voltage('pp','pn').real[earlier], f)
        change = abs(prior['harmonics_v_rms'][0]/m['harmonics_v_rms'][0]-1)
        m.update(pressure_pa_rms=level, pressure_spl_db=db(level/20e-6), settling_amplitude_fraction=float(change), capsule_mode='linearized_at_actual_DC_bias')
        if change > 1e-3:
            raise SimulationError('Unsettled distortion waveform; extend simulation instead of accepting THD')
        limit = thresholds()['thd_at_1pa_percent' if level==1 else 'thd_at_135db_percent']['value']
        m['status'] = 'pass' if m['thd_percent'] <= limit else 'fail'
        rows.append(m)
    return result('pass' if all(x['status']=='pass' for x in rows) else 'fail', {'cases': rows, 'thd_percent': max(x['thd_percent'] for x in rows)}, coverage='Electronics under linearized imposed capsule motion; nominal only. Device/environment distortion corners remain pending.')


def headroom(sim, ctx):
    rows = ctx['checks']['distortion']['metrics'].get('cases', [])
    rows = [r for r in rows if r['frequency_hz']==1000]
    if not rows:
        return result('incomplete', reason='No valid distortion bracket')
    limit = thresholds()['thd_at_135db_percent']['value']
    passes = [r for r in rows if r['thd_percent'] <= limit]
    failures = [r for r in rows if r['thd_percent'] > limit]
    lower = max((r['pressure_pa_rms'] for r in passes), default=0)
    upper = min((r['pressure_pa_rms'] for r in failures if r['pressure_pa_rms']>lower), default=None)
    if upper is not None:
        for _ in range(8):
            level = np.sqrt(lower*upper) if lower else upper/2
            wave = sim.transient(1000, level*np.sqrt(2), settling=0.5, overrides={'LIN':1,'POLDC':ctx['polarization_dc_v']})
            h = harmonic_spectrum(wave['time'],wave.voltage('pp','pn'),1000)
            if h['thd_percent'] <= limit:
                lower=level
            else:
                upper=level
    return result('pass' if lower >= 20e-6*10**(135/20) else 'fail',
                  {'headroom_lower_bound_pa_rms': float(lower), 'first_failure_upper_bound_pa_rms': upper,
                   'right_censored': upper is None, 'headroom_pa_rms': None if upper is None else float(lower),
                   'threshold_percent': limit, 'frequency_hz':1000, 'system_max_spl_verified':False},
                  coverage='Bracketed electronics distortion boundary if a failure exists; otherwise lower bound only. Mechanical overload and device power pending.')


def port_matrix(sim, ports, label, environment_only=False):
    columns=[]
    f=None
    for j, port in enumerate(ports):
        raw = sim.execute(label, 'ac dec 8 20 20k\nwrite port.raw all', ['port.raw'], {'PRESSURE_AC':0},
                          extra=f'Iprobe mic_g {port} DC 0 AC 1', environment_only=environment_only)['port.raw']
        f=raw['frequency'].real
        columns.append(np.column_stack([raw.voltage(p,'mic_g') for p in ports]))
    return f, np.stack(columns, axis=-1)


def output_impedance(sim, ctx):
    f,zloaded=port_matrix(sim,['p','n'],'output_loaded')
    fe,zenv=port_matrix(sim,['p','n'],'output_environment',True)
    if not np.array_equal(f,fe):
        raise SimulationError('Cannot deembed different frequency grids')
    # Full 2-port deembedding handles mismatch; scalar subtraction would be wrong.
    ydut=np.linalg.inv(zloaded)-np.linalg.inv(zenv)
    zdut=np.linalg.inv(ydut)
    differential=np.einsum('i,nij,j->n',np.array([1,-1]),zdut,np.array([1,-1]))
    mismatch=np.abs(zdut[:,0,0]-zdut[:,1,1])/np.maximum((np.abs(zdut[:,0,0])+np.abs(zdut[:,1,1]))/2,1e-20)
    m={'frequency_hz':f.tolist(),'differential_ohm':np.abs(differential).tolist(),
       'differential_phase_deg':np.angle(differential,deg=True).tolist(),'output_impedance_ohm':float(np.max(np.abs(differential))),
       'leg_diagonal_ohm':np.abs(np.diagonal(zdut,axis1=1,axis2=2)).tolist(),
       'impedance_mismatch_fraction':float(np.max(mismatch)),
       'method':'Full 2-port Y subtraction of feed/cable/preamp, preserving DUT DC operating point',
       'raw_dut_z_real':zdut.real.tolist(),'raw_dut_z_imag':zdut.imag.tolist()}
    ctx['output']=m
    return result('pass' if m['output_impedance_ohm']<=thresholds()['differential_output_impedance_ohm']['value'] else 'fail', m)


def balance(sim, ctx):
    if 'output' not in ctx:
        return result('incomplete',reason='Output impedance deembedding failed')
    raw=sim.op_ac('common_mode',{'PRESSURE_AC':0,'CMAC':1})['ac.raw']
    f=raw['frequency'].real
    diff=raw.voltage('pp','pn')
    m={'impedance_mismatch_fraction':ctx['output']['impedance_mismatch_fraction'],
       'common_mode_to_differential_v_per_v_at_1khz':float(abs(at_frequency(f,diff,1000))),
       'common_mode_drive':'Preamp input midpoint relative to supply earth; fixture susceptibility, not microphone intrinsic CMRR'}
    return result('pass' if m['impedance_mismatch_fraction']<=thresholds()['impedance_balance_fraction']['value'] else 'fail',m)


def screen(sim, label, overrides):
    try:
        raw=sim.op_ac(label,overrides)
        m=response(raw['ac.raw'])
        i=current(raw['op.raw'])
        pol=float(raw['op.raw'].voltage('b','f')[0])
        ok=0<i<=thresholds()['current_max_a']['value'] and pol>0 and m['response_deviation_db']<=thresholds()['electronics_response_db']['value']
        return {'parameters':overrides,'status':'pass' if ok else 'fail','current_a':i,'polarization_dc_v':pol,
                'response_deviation_db':m['response_deviation_db'],'sensitivity_v_per_pa':m['sensitivity_v_per_pa_at_1khz']}
    except (SimulationError,ValueError,np.linalg.LinAlgError) as exc:
        return {'parameters':overrides,'status':'error','reason':str(exc)}


def phantom_supply(sim,ctx):
    ranges=scenario_ranges()
    rows=[screen(sim,'p48_corner',dict(VS=v,FT=t,FM=m)) for v,t,m in product(ranges['VS'],ranges['FT'],ranges['FM'])]
    return result('pass' if all(x['status']=='pass' for x in rows) else 'fail',{'cases':rows},coverage='8 DC/AC supply/feed extremes. Noise/distortion/abuse at corners pending.')


def temperature(sim,ctx):
    lo,hi=scenario_ranges()['TEMP']
    rows=[screen(sim,'temperature',{'TEMP':t}) for t in [lo,sim.params['TEMP'],hi]]
    return result('pass' if all(x['status']=='pass' for x in rows) else 'fail',{'cases':rows,'capsule_temperature_law_known':False},coverage='3 electrical temperatures; no validated mechanical or leakage temperature law')


def semiconductor_corners(sim,ctx):
    corners=sim.meta.get('device_corners',[])
    if not corners:
        return result('incomplete',reason='No manufacturer-bounded semiconductor corners; ideal fixtures cannot demonstrate no-selection yield')
    rows=[screen(sim,'device_corner',r['parameters']) for r in corners]
    qualified=all(r.get('provenance') in {'manufacturer_bound','measured_bound'} for r in corners)
    return result('pass' if qualified and all(x['status']=='pass' for x in rows) else 'fail' if any(x['status']!='pass' for x in rows) else 'incomplete',{'cases':rows},coverage='DC/AC only; full noise/distortion/stability corners pending')


def monte_carlo(sim,ctx):
    rng=np.random.default_rng(ctx['seed'])
    rows=[]
    for _ in range(ctx['samples']):
        # Scenario uncertainty is not a production population. All distributions are explicit here.
        overrides={k:float(np.exp(rng.uniform(np.log(lo),np.log(hi)))) if k=='LEAK' else float(rng.uniform(lo,hi)) for k,(lo,hi) in scenario_ranges().items()}
        for k,definition in sim.meta.get('population',{}).items():
            lo,hi=definition['range']
            if definition['distribution']=='uniform':
                overrides[k]=float(rng.uniform(lo,hi))
            elif definition['distribution']=='log_uniform':
                overrides[k]=float(np.exp(rng.uniform(np.log(lo),np.log(hi))))
            else:
                raise ValueError('Unsupported or undocumented population distribution')
        rows.append(screen(sim,'monte_carlo',overrides))
    summary=population_summary(rows,'response_deviation_db')
    summary.update(seed=ctx['seed'],distributions='Independent uniform scenario ranges; leakage log-uniform; not manufacturer distributions',cases=rows,
                   all_requirements_pass_fraction=None,screened_requirements=['current','positive_polarization','frequency_response'])
    return result('incomplete',summary,reason='Initial Monte Carlo runs DC/AC screens only; all-requirement manufacturing yield is not established')


def loading(sim,ctx):
    f,z=port_matrix(sim,['f','b','rear'],'input_admittance')
    y=np.linalg.inv(z)
    p=sim.params
    s=2j*np.pi*f
    a=s*p['CF']+1/p['LEAK']; b=s*p['CR']+1/p['LEAK']; par=s*p['PAR']; cross=s*p['CROSS']
    ycap=np.zeros_like(y)
    ycap[:,0,0]=a+par+cross; ycap[:,1,1]=a+b; ycap[:,2,2]=b+par+cross
    ycap[:,0,1]=ycap[:,1,0]=-a; ycap[:,1,2]=ycap[:,2,1]=-b; ycap[:,0,2]=ycap[:,2,0]=-cross
    ydut=y-ycap
    cin=ydut[:,0,0].imag/(2*np.pi*f)
    ac=ctx['nominal']['ac.raw']
    actual=abs(at_frequency(ac['frequency'],ac.voltage('f','mic_g'),1000))
    unloaded=p['SREF']*ctx['polarization_dc_v']/p['VREF']
    loss=-db(actual/unloaded)
    ranges=scenario_ranges()
    rows=[screen(sim,'capsule_corner',dict(CF=c,CR=cr,LEAK=l,PAR=cp)) for c,cr,l,cp in product(ranges['CF'],ranges['CR'],ranges['LEAK'],ranges['PAR'])]
    m={'frequency_hz':f.tolist(),'clamped_electrode_input_capacitance_f':cin.tolist(),
       'clamped_electrode_input_conductance_s':ydut[:,0,0].real.tolist(),
       'loading_loss_db':float(loss) if sim.meta['niche']['sensing']=='voltage' else None,
       'front_voltage_transfer_ratio_at_1khz':float(actual/unloaded), 'capsule_corner_cases':rows,
       'definition':'3-port Y subtraction of the capsule; input C/G with other electrodes AC-clamped. Dynamic floating/bootstrap behavior is retained in raw Y matrix.',
       'dut_y_real':ydut.real.tolist(),'dut_y_imag':ydut.imag.tolist()}
    return result('pass' if all(r['status']=='pass' for r in rows) else 'fail',m,coverage='Electrical loading and 16 assumed capsule corners; not an acoustic polar or mechanical model')


def startup(sim,ctx):
    raw=sim.execute('startup','tran 1m 5 0 1m\nwrite startup.raw all',['startup.raw'],{'START':1,'PRESSURE_AC':0})['startup.raw']
    t=raw['time'].real; rail=raw.voltage('rail','mic_g').real
    target=float(ctx['nominal']['op.raw'].voltage('rail','mic_g')[0])
    bad=np.flatnonzero(abs(rail-target)>.01*max(abs(target),1e-12))
    settled=float(t[min(int(bad[-1])+1,len(t)-1)]) if len(bad) else float(t[0])
    peak=float(np.max(abs(raw.voltage('pp','pn'))))
    ok=abs(rail[-1]-target)<=.01*abs(target) and settled<thresholds()['startup_settling_s']['value']
    return result('pass' if ok else 'fail',{'settling_to_1percent_s':settled,'rail_target_v':target,'rail_final_v':float(rail[-1]),'differential_output_peak_v':peak},coverage='Symmetric cold turn-on PWL. Hot-plug, asymmetric pin connection, disconnect, RF/ESD pending.')


def stability(sim,ctx):
    raw=ctx['nominal']['ac.raw']; f=raw['frequency'].real
    gain=abs(raw.voltage('pp','pn')); ref=abs(at_frequency(f,raw.voltage('pp','pn'),1000))
    peaking=db(np.max(gain[f>=20000])/ref)
    ranges=scenario_ranges(); env=read_yaml(ROOT/'spec/design_constraints.yaml')['environment']
    rows=[screen(sim,'cable_load_corner',dict(LEN=l,ZIN=z,ZM=m)) for l,z,m in product(ranges['LEN'],[env['preamp_differential_load_ohm']['stress_min'],ranges['ZIN'][1]],ranges['ZM'])]
    m={'hf_peaking_db':peaking,'analyzed_max_hz':float(f[-1]),'cable_load_cases':rows,'loop_phase_margin_deg':None,
       'oscillation_ruled_out':False,'reason':'Closed-loop AC peaking cannot prove loop stability; declared injection ports/Nyquist or return-ratio tests required.'}
    if peaking>thresholds()['hf_peaking_db']['value'] or any(x['status']!='pass' for x in rows):
        return result('fail',m,coverage='HF and cable/load screening')
    return result('incomplete',m,reason='Loop stability and multi-loop/servo interaction analysis not implemented yet; cannot qualify from peaking alone')


CHECKS={name:globals()[name] for name in ['operating_point','frequency_response','noise','distortion','headroom','output_impedance','balance','phantom_supply','temperature','semiconductor_corners','monte_carlo','loading','startup','stability']}


def evaluate(sim,seed=34047,samples=16,checks=None):
    selected=checks or list(CHECKS)
    ctx={'seed':seed,'samples':samples,'checks':{}}
    try:
        ctx['nominal']=sim.execute('operating_point','op\nwrite op.raw all',['op.raw'])
    except Exception as exc:
        return {n:result('error',reason=str(exc)) for n in selected}
    # Establish DC/current/energy before any transfer or noise analysis, including
    # selected subsets that need actual polarization for their interpretation.
    try:
        dc=operating_point(sim,ctx)
    except Exception as exc:
        return {n:result('error',reason=f'{type(exc).__name__}: {exc}') for n in selected}
    if 'operating_point' in selected: ctx['checks']['operating_point']=dc
    if selected == ['operating_point']: return ctx['checks']
    if sim.meta.get('analysis_domain') == 'periodic_mechanism_control':
        from .architectures import carrier_control
        try:
            control=carrier_control(sim)
            ctx['checks']['carrier_mechanism']=result('incomplete',control,reason='Deterministic control; periodic noise/physical oscillator/mixer remain unsupported')
        except Exception as exc:
            ctx['checks']['carrier_mechanism']=result('error',reason=f'{type(exc).__name__}: {exc}')
        for name in selected:
            if name!='operating_point':
                ctx['checks'][name]=result('incomplete',reason='Periodic architecture: ordinary DC-linearized audio/noise screens do not qualify demodulated behavior')
        return ctx['checks']
    try:
        ctx['nominal'].update(sim.op_ac())
    except Exception as exc:
        for n in selected:
            if n!='operating_point': ctx['checks'][n]=result('error',reason=str(exc))
        return ctx['checks']
    for name in selected:
        if name=='operating_point': continue
        try:
            ctx['checks'][name]=CHECKS[name](sim,ctx)
        except Exception as exc:
            ctx['checks'][name]=result('error',reason=f'{type(exc).__name__}: {exc}')
    return ctx['checks']
