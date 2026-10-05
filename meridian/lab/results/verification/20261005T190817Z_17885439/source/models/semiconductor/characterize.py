#!/usr/bin/env python3
"""Isolated device characterization against primary evidence; errors survive in records."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import uuid
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from meridian_lab.core import digest, read_yaml, source_manifest, parse_raw, write_json, environment_versions, verify_spec_lock
from meridian_lab.device_models import resolve, index
from meridian_lab.metrics import at_frequency

class Experiment:
    def __init__(self, folder, models, refinement=False):
        self.folder=folder; self.models=models; self.jobs=[]; self.refinement=refinement
        self.root=folder/'source/models'
        self.refs=read_yaml(self.root/'semiconductor/references.yaml')
        self.partial={}

    def execute(self, model, label, circuit, commands, outputs, temp=25, refine=False):
        directory=self.folder/model['id']/label
        directory.mkdir(parents=True,exist_ok=False)
        m=resolve(self.root,[model['id']])[0]
        reltol=1e-7 if refine else 1e-6
        body=f'''Meridian isolated {model['id']} {label}
.include "{m['resolved_path']}"
.temp {temp}
.options reltol={reltol} abstol=1e-16 vntol=1e-10 gmin=1e-15 method=gear maxord=2
{circuit}
.control
set filetype=ascii
set numdgt=16
{commands}
quit
.endc
.end
'''
        (directory/'job.cir').write_text(body)
        job=dict(model_id=m['id'],label=label,temperature_c=temp,refinement=refine,
                 netlist_sha256=digest(directory/'job.cir'),model_sha256=m['sha256'],
                 model_version=m['version'],parent_model_id=m.get('parent_model_id'),
                 compatibility=m.get('ngspice_behavior'),directory=str(directory.relative_to(self.folder)))
        self.jobs.append(job)
        env=os.environ.copy(); env['LC_ALL']='C'
        if m.get('ngspice_behavior'): env['MERIDIAN_NGSPICE_BEHAVIOR']=m['ngspice_behavior']
        else: env.pop('MERIDIAN_NGSPICE_BEHAVIOR',None)
        try:
            process=subprocess.Popen([os.environ.get('MERIDIAN_NGSPICE',str(ROOT/'tools/ngspice-run')),'-n','-b','job.cir'],
                                     cwd=directory,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                     text=True,start_new_session=True)
            try:
                stdout,stderr=process.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL)
                stdout,stderr=process.communicate()
                (directory/'simulator.log').write_text(stdout+'\n'+stderr)
                raise ValueError('Simulator process-group timeout after15s; partial diagnostic output preserved')
            log=stdout+'\n'+stderr
            (directory/'simulator.log').write_text(log)
            bad=re.search(r'(?im)^\s*(error\b|fatal\b|warning\b|.*timestep too small|.*singular matrix|.*convergence failed|.*analysis.*aborted)',log)
            if process.returncode or bad: raise ValueError(f'exit {process.returncode}: {bad.group(0) if bad else log[-300:]}')
            raw={n:parse_raw(directory/n) for n in outputs}
            job.update(status='ok',raw_data_hashes={n:digest(directory/n) for n in outputs})
            # Compact portable numeric evidence; full ASCII raw vectors remain local.
            for name,data in raw.items():
                chosen=[k for k in data.vectors if '.' not in k and not k.startswith('v(x')]
                columns=[]; names=[]
                for k in chosen:
                    v=data[k]
                    columns.append(v.real); names.append(k+'_real' if np.iscomplexobj(v) else k)
                    if np.iscomplexobj(v): columns.append(v.imag); names.append(k+'_imag')
                target=directory/(name+'.csv')
                np.savetxt(target,np.array(columns).T,delimiter=',',header=','.join(names),comments='',fmt='%.12g')
                job.setdefault('csv_hashes',{})[target.name]=digest(target)
            write_json(directory/'job.json',job)
            return raw
        except (ValueError,OSError,subprocess.TimeoutExpired,RuntimeError) as exc:
            job.update(status='error',reason=str(exc))
            (directory/'failure.json').write_text(json.dumps(job,indent=2)+'\n')
            return None

def interpolate(raw, current, target, vector):
    x=np.asarray(current).real
    valid=(x>0)&np.isfinite(x)
    x=x[valid]; y=np.asarray(raw[vector]).real[valid]
    order=np.argsort(x); x=x[order]; y=y[order]
    if len(x)<2 or not x[0]<=target<=x[-1]: raise ValueError('Target current outside simulated transfer curve')
    return float(np.interp(target,x,y))

def compare(name,value,lo=None,hi=None,typ=None,relative=.20,evidence='guaranteed_limit',condition=''):
    if typ is not None: lo=typ*(1-relative); hi=typ*(1+relative); evidence='typical_accuracy_screen'
    ok=(lo is None or value>=lo) and (hi is None or value<=hi)
    return dict(name=name,value=float(value),status='pass' if ok else 'fail',lower=lo,upper=hi,
                typical=typ,relative_disagreement=None if typ is None else float((value-typ)/typ),
                evidence=evidence,condition=condition)

def fet_circuit(sub,gate,drain=5,high=25):
    return f'Vd d 0 {drain}\nVg g 0 DC {gate} AC 1\nVh h 0 {high}\nVl l 0 -5\nXq d g 0 h l {sub}\nHout out 0 Vd 1\nHgate ig 0 Vg 1'

def jfet(exp,m):
    rows=[]; measurements={}; sub=m['subcircuit']; biases={}
    exp.partial[m['id']]=dict(comparisons=rows,measurements=measurements)
    for t in [-40,-10,25,50,125]:
        out=exp.execute(m,f'transfer_{t}',fet_circuit(sub,-1),
                        'dc Vg -1.8 0 .002\nwrite transfer.raw v(g) i(vd) i(vg)', ['transfer.raw'],t)
        if not out: continue
        raw=out['transfer.raw']; cur=-raw['i(vd)']
        measurements[f'transfer_{t}']={'idss_at_5v_a':float(cur[-1])}
        if t==25:
            for id_ in [.0001,.002,.005]: biases[id_]=interpolate(raw,cur,id_,'v(g)')
            for p in exp.refs['jfe150']['curve_observations']['transfer_figure_6_1']['points']:
                value=float(np.interp(p['vgs_v'],raw['v(g)'],cur))
                rows.append(compare(f'typical_transfer_vgs_{p["vgs_v"]}',value,*p['current_interval_a'],evidence='typical_curve_reading_interval',condition='Fig6-1,VDS5V,25C'))
    for t in [-40,25,125]:
        out=exp.execute(m,f'idss_gfs_{t}',fet_circuit(sub,0,10),'op\nwrite op.raw v(g) i(vd)\nac lin 1 1000 1000\nwrite ac.raw i(vd)',['op.raw','ac.raw'],t)
        if out:
            idss=-float(out['op.raw']['i(vd)'][0]); gm=abs(out['ac.raw']['i(vd)'][0])
            measurements[f'idss_gfs_{t}']={'idss_a':idss,'gfs_s':float(gm)}
            rows.append(compare(f'idss_{t}',idss,.024 if t==25 else .022,.046 if t==25 else .057,condition='table6.5,VDS10V,VGS0'))
            if t==25: rows.append(compare('gfs_25',gm,.055,.080,condition='table6.5,VDS10V,VGS0'))
    for id_,vg in biases.items():
        out=exp.execute(m,f'small_noise_{id_}',fet_circuit(sub,vg),
                        'op\nwrite op.raw i(vd) i(vg)\nac dec 48 1 100Meg\nwrite ac.raw i(vd) i(vg)\nnoise v(out) Vg dec 48 .1 100k 1\nsetplot noise1\nwrite noise.raw all\nnoise v(ig) Vg dec 48 .1 100k 1\nsetplot noise3\nwrite gate_noise.raw all',
                        ['op.raw','ac.raw','noise.raw','gate_noise.raw'])
        if not out: continue
        op=out['op.raw']; ac=out['ac.raw']; noise=out['noise.raw']; inoise=out['gate_noise.raw']
        cap=float((-at_frequency(ac['frequency'],ac['i(vg)'],1000)/(2j*np.pi*1000)).real)
        gm=abs(at_frequency(ac['frequency'],ac['i(vd)'],1000))
        measurements[f'bias_{id_}']=dict(vgs_v=vg,id_a=-float(op['i(vd)'][0]),gm_s=float(gm),
                ciss_f=cap,gate_current_a=float(op['i(vg)'][0]),gate_current_noise_1k_a_sqrt_hz=float(at_frequency(inoise['frequency'],inoise['onoise_spectrum'],1000)),
                voltage_noise_10hz=float(at_frequency(noise['frequency'],noise['inoise_spectrum'],10)),
                voltage_noise_1khz=float(at_frequency(noise['frequency'],noise['inoise_spectrum'],1000)))
        for ref in exp.refs['jfe150']['noise_v_sqrt_hz']:
            if ref['id_a']==id_: rows.append(compare(f'en_{id_}_{ref["f_hz"]}',at_frequency(noise['frequency'],noise['inoise_spectrum'],ref['f_hz']),typ=ref['typical'],condition='table6.5,VDS5V,25C'))
        if id_==.002:
            rows.append(compare('ciss_2ma',cap,typ=24e-12,condition='table6.5,VDS5V; unspecified capacitance bias follows table default'))
            rows.append(compare('in_2ma_1k',measurements[f'bias_{id_}']['gate_current_noise_1k_a_sqrt_hz'],typ=1.8e-15,condition='table6.5; Hgate1ohm noiseless observer'))
    out=exp.execute(m,'vgs_limits_10v',fet_circuit(sub,-1,10),'dc Vg -1.8 0 .001\nwrite transfer.raw v(g) i(vd)',['transfer.raw'])
    if out:
        raw=out['transfer.raw']; cur=-raw['i(vd)']
        for i,limits in [(1e-7,[-1.5,-.9]),(.0001,[-1.3,-.7]),(.002,[-1.1,-.5])]:
            rows.append(compare(f'vgs_at_{i}',interpolate(raw,cur,i,'v(g)'),*limits,condition='table6.5,VDS10V,25C'))
    out=exp.execute(m,'output_curve_minus_0p7',fet_circuit(sub,-.7),'dc Vd .01 20 .05\nwrite output.raw v(d) i(vd) i(vg)',['output.raw'])
    if out:
        for p in exp.refs['jfe150']['curve_observations']['output_figure_6_3']['points']:
            value=np.interp(p['vds_v'],out['output.raw']['v(d)'],-out['output.raw']['i(vd)'])
            rows.append(compare(f'output_vds_{p["vds_v"]}',value,*p['current_interval_a'],evidence='typical_curve_reading_interval',condition='Fig6-3,VGS=-.7,25C'))
    out=exp.execute(m,'leakage',fet_circuit(sub,-.7,2,high=5),'op\nwrite op.raw i(vg)',['op.raw'])
    if out: rows.append(compare('gate_leakage',abs(out['op.raw']['i(vg)'][0]),hi=10e-12,condition='table6.5,VDS2V,VGS-.7V,VCH5V,VCL-5V'))
    # Datasheet capacitance gate bias is ambiguous (VDS0 cannot sustain the table's default2mA).
    # Preserve both off-bias and operating-bias results instead of selecting a favorable reading.
    for vd in [0,5]:
        out=exp.execute(m,f'off_bias_cap_{vd}',fet_circuit(sub,0,vd),
                        'ac lin 1 1Meg 1Meg\nwrite ac.raw i(vg) i(vd)',['ac.raw'])
        if out:
            measurements[f'off_bias_cap_{vd}']={'ciss_f':float((-out['ac.raw']['i(vg)'][0]/(2j*np.pi*1e6)).real),'vgs_v':0,'vds_v':vd,
                'condition_status':'explicit_exploratory_off_bias; manufacturer capacitance gate-bias clarification required'}
    if .002 in biases:
        out=exp.execute(m,'noise_ac_refined',fet_circuit(sub,biases[.002]),
            'ac dec 96 1 100Meg\nwrite ac.raw i(vd) i(vg)\nnoise v(out) Vg dec 96 .1 100k 1\nsetplot noise1\nwrite noise.raw all',
            ['ac.raw','noise.raw'],refine=True)
        if out and 'bias_0.002' in measurements:
            actual=float(at_frequency(out['noise.raw']['frequency'],out['noise.raw']['inoise_spectrum'],1000))
            rows.append(compare('noise_refinement',abs(actual/measurements['bias_0.002']['voltage_noise_1khz']-1),hi=.01,evidence='numerical_refinement'))
    if .002 in biases:
        circuit=f'Vs rail 0 12\nRd rail d 2k\nVg g 0 DC {biases[.002]} SIN({biases[.002]} .5 1000)\nVh h 0 12\nVl l 0 -5\nXq d g 0 h l {sub}'
        tran=[]
        for step in [2e-6,1e-6]:
            out=exp.execute(m,f'large_signal_{step}',circuit,f'tran {step} .02 .01 {step}\nwrite tran.raw v(d) v(g) i(vs)',['tran.raw'],refine=step==1e-6)
            if out: tran.append(out['tran.raw'])
        if len(tran)==2: rows.append(refinement(tran[0],tran[1],'time','v(d)','large_signal_refinement'))
    for row in rows:
        if m['id'] in {'jfe150_weak','jfe150_strong'} and row['evidence'].startswith('typical'):
            row['status']='reference_only';row['note']='Typical curves/noise are not guaranteed corner limits; disagreement remains quantified.'
        if row['name']=='ciss_2ma':
            row['status']='condition_unresolved';row['note']='Table capacitance gate bias unspecified; off/operating bias both retained. No confirmed device failure from this comparison.'
    return dict(comparisons=rows,measurements=measurements,scope='DC/caps/terminal noise/large-signal screen; no production noise/yield/SOA qualification')

def refinement(a,b,x,y,name):
    ya=a[y].real; yb=np.interp(a[x].real,b[x].real,b[y].real)
    value=float(np.max(abs(ya-yb))/max(float(np.ptp(ya)),1e-12))
    return compare(name,value,hi=.01,evidence='numerical_refinement',condition='range-normalized maximum difference on common grid')

def bjt_circuit(sub,pol,vb,rs=0,vc=5):
    s=1 if pol=='npn' else -1
    return f'Vc c 0 {s*vc}\nVb inp 0 DC {s*vb} AC 1\n'+(f'Rsource inp b {rs}\n' if rs else 'Vlink inp b 0\n')+f'Xq c b 0 {sub}\nHout out 0 Vc 1'

def bipolar(exp,m):
    pol='npn' if m['device_id']=='bc846b' else 'pnp'; s=1 if pol=='npn' else -1
    rows=[]; measurements={}; curves={}; bias=None; sub=m['subcircuit']
    exp.partial[m['id']]=dict(comparisons=rows,measurements=measurements)
    for t in [-55,-10,25,50,150]:
        out=exp.execute(m,f'transfer_{t}',bjt_circuit(sub,pol,.65),
              f'dc Vb {s*.3} {s*.9} {s*.001}\nwrite transfer.raw v(b) i(vc) i(vb)',['transfer.raw'],t)
        if not out: continue
        raw=out['transfer.raw']; cur=-s*raw['i(vc)']; curves[t]=raw
        vb=abs(interpolate(raw,cur,.002,'v(b)')); ib=abs(interpolate(raw,cur,.002,'i(vb)'))
        measurements[f'bias_{t}']={'vbe_v':vb,'base_current_a':ib,'hfe':.002/ib}
        if t==25:
            bias=vb; ref=exp.refs['bipolar'][m['device_id']]
            rows.append(compare('hfe',.002/ib,*ref['hfe_limits'],condition='table8,VCE5V,IC2mA,25C'))
            rows.append(compare('vbe',vb,*ref['vbe_limits_v'],condition='table8,VCE5V,IC2mA,25C'))
    if bias is None: return dict(comparisons=rows,measurements=measurements,scope='failed DC prevents further meaningful characterization')
    out=exp.execute(m,'output',bjt_circuit(sub,pol,bias),f'dc Vc {s*.01} {s*20} {s*.05}\nwrite output.raw v(c) i(vc) i(vb)',['output.raw'])
    fine=exp.execute(m,'transfer_refined',bjt_circuit(sub,pol,bias),f'dc Vb {s*.3} {s*.9} {s*.0005}\nwrite transfer.raw v(b) i(vc) i(vb)',['transfer.raw'],refine=True)
    if fine and 25 in curves:
        coarse=curves[25]; value=abs(abs(interpolate(fine['transfer.raw'],-s*fine['transfer.raw']['i(vc)'],.002,'v(b)'))-bias)/bias
        rows.append(compare('bias_refinement',value,hi=.01,evidence='numerical_refinement'))
    vb10=abs(interpolate(curves[25],-s*curves[25]['i(vc)'],.01,'v(b)'))
    out=exp.execute(m,'bandwidth',bjt_circuit(sub,pol,vb10),
            'op\nwrite op.raw i(vc) i(vb)\nac dec 64 100k 10G\nwrite ac.raw i(vc) i(vb)',['op.raw','ac.raw'])
    if out:
        raw=out['ac.raw']; h=abs(raw['i(vc)']/raw['i(vb)']); f=raw['frequency'].real
        ft=float(np.interp(1,h[::-1],f[::-1])) if h[0]>1 and h[-1]<1 else None
        h100=float(at_frequency(f,h,1e8)); measurements['bandwidth']={'unity_current_gain_hz':ft,'hfe_at100MHz':h100,'bias_ic_a':float(abs(out['op.raw']['i(vc)'][0]))}
        rows.append(compare('ft_100MHz_test',h100*1e8,lo=1e8,condition='manufacturer fT test at100MHz,VCE5V,IC10mA'))
    # Reverse collector-base admittance with ideal zero emitter current, matching datasheet.
    circuit=f'Vc c 0 DC {s*10} AC 1\nVb b 0 0\nRreturn e b 1T\nXq c b e {sub}'
    out=exp.execute(m,'collector_capacitance',circuit,'op\nwrite op.raw i(vc)\nac lin 1 1Meg 1Meg\nwrite ac.raw i(vc)',['op.raw','ac.raw'])
    if out:
        cap=float((-out['ac.raw']['i(vc)'][0]/(2j*np.pi*1e6)).real)
        measurements['cc_f']=cap; ref=exp.refs['bipolar'][m['device_id']]
        rows.append(compare('cc_typical',cap,typ=ref['cc_typical_f'],condition=exp.refs['bipolar']['cc_condition']))
        if ref['cc_max_f']: rows.append(compare('cc_guaranteed_max',cap,hi=ref['cc_max_f']))
        refined=exp.execute(m,'collector_cap_return_refinement',circuit.replace('1T','1G'),
                            'ac lin 1 1Meg 1Meg\nwrite ac.raw i(vc)',['ac.raw'],refine=True)
        if refined:
            other=float((-refined['ac.raw']['i(vc)'][0]/(2j*np.pi*1e6)).real)
            rows.append(compare('collector_cap_return_refinement',abs(other/cap-1),hi=.01,evidence='numerical_refinement',condition='1T versus1G explicit emitter return; approximate open emitter'))
    saturation=f'Ic 0 c {s*.01}\nIb 0 b {s*.0005}\nXq c b 0 {sub}'
    out=exp.execute(m,'saturation',saturation,'op\nwrite op.raw v(c) v(b)',['op.raw'])
    if out: rows.append(compare('vcesat',abs(out['op.raw']['v(c)'][0]),hi=exp.refs['bipolar'][m['device_id']]['vcesat_max_v'],condition=exp.refs['bipolar']['saturation_condition']))
    ib200=abs(interpolate(curves[25],-s*curves[25]['i(vc)'],.0002,'i(vb)'))
    vb200=abs(interpolate(curves[25],-s*curves[25]['i(vc)'],.0002,'v(b)'))+ib200*2000
    out=exp.execute(m,'noise_figure',bjt_circuit(sub,pol,vb200,2000),
        'op\nwrite op.raw i(vc) i(vb)\nnoise v(out) Vb dec 48 1 100k 1\nsetplot noise1\nwrite noise.raw all',['op.raw','noise.raw'])
    if out:
        noise=out['noise.raw']; en=float(at_frequency(noise['frequency'],noise['inoise_spectrum'],1000)); nf=10*np.log10(en**2/(4*1.380649e-23*298.15*2000))
        measurements['noise']={'nf_1khz_db':float(nf),'en_total_source_referred_1khz':en,'actual_ic_a':float(abs(out['op.raw']['i(vc)'][0])),'flicker_present':False}
        rows.append(compare('noise_figure_max',nf,hi=10,condition=exp.refs['bipolar']['noise_figure']))
        rows.append(compare('noise_figure_typical',nf,1.6,2.4,evidence='typical_accuracy_screen',condition='2 dB typical; +/-0.4dB research screen'))
    return dict(comparisons=rows,measurements=measurements,scope='nominal DC/AC/NF only; KF omitted; no qualified low-noise input/population/SOA')

def opa(exp,m):
    rows=[]; measurements={}
    exp.partial[m['id']]=dict(comparisons=rows,measurements=measurements)
    def circuit(v=0,rs=0,load=10000,gain=1):
        feedback='out' if gain==1 else 'fb'
        return f'Vp p 0 18\nVn n 0 -18\nVin src 0 DC {v} AC 1 SIN(0 {20/gain} 1000)\n'+(f'Rsource src inp {rs}\n' if rs else 'Vlink src inp 0\n')+f'Xu inp {feedback} p n out {m["subcircuit"]}\nRload out 0 {load}\n'+('Rf out fb 9k\nRg fb 0 1k' if gain==10 else '')
    for t in [-40,-10,25,50,125]:
        out=exp.execute(m,f'small_{t}',circuit(),'op\nwrite op.raw v(out) i(vp) i(vn) i(vin)\nac dec 64 1 100Meg\nwrite ac.raw v(out) i(vin)\nnoise v(out) Vin dec 64 1 100k 1\nsetplot noise1\nwrite noise.raw all',['op.raw','ac.raw','noise.raw'],t)
        if not out: continue
        op=out['op.raw']; ac=out['ac.raw']; noise=out['noise.raw']; f=ac['frequency'].real; gain=abs(ac['v(out)'])
        bandwidth=float(np.interp(1/np.sqrt(2),gain[::-1],f[::-1])); cap=float((-at_frequency(f,ac['i(vin)'],1000)/(2j*np.pi*1000)).real)
        measurements[f'bias_{t}']=dict(iq_a=-float(op['i(vp)'][0]),ib_a=float(op['i(vin)'][0]),offset_v=float(op['v(out)'][0]),
                                        follower_bandwidth_hz=bandwidth,ciss_f=cap,en_1k=float(at_frequency(noise['frequency'],noise['inoise_spectrum'],1000)))
        if t==25:
            rows.extend([compare('iq_max',-op['i(vp)'][0],hi=.0013,condition='table6.7,VS36V,VCM0,RL10k'),
                compare('ib_max',abs(op['i(vin)'][0]),hi=20e-12,condition='table6.7,25C,mid-supply'),
                compare('ciss',cap,typ=6.4e-12,condition='common-mode Cin; follower bootstraps differential Cin')])
            for hz,typ in exp.refs['opa197']['voltage_noise_v_sqrt_hz'].items():
                rows.append(compare(f'en_{hz}',at_frequency(noise['frequency'],noise['inoise_spectrum'],hz),typ=typ,condition='table6.7,VS36V,VCM0'))
    # Current noise: separate input-current observer with input clamped (1 ohm noiseless CCVS).
    c=circuit()+ '\nHinput inoise 0 Vin 1'
    out=exp.execute(m,'current_noise',c,'noise v(inoise) Vin dec 64 1 100k 1\nsetplot noise1\nwrite noise.raw all',['noise.raw'])
    if out:
        value=float(at_frequency(out['noise.raw']['frequency'],out['noise.raw']['onoise_spectrum'],1000))
        measurements['in_1k_a_sqrt_hz']=value; rows.append(compare('current_noise_1k',value,typ=1.5e-15,condition='input-current observer,clamped input,unity follower'))
    # DC feedback is closed through Lbias; AC loop is open through Cbreak.
    # A follower's peaking/closed-loop -3dB frequency is not GBW.
    openloop=f'Vp p 0 18\nVn n 0 -18\nVin inp 0 DC 0 AC 1\nXu inp inv p n out {m["subcircuit"]}\nLbias out inv 1G\nCbreak inv 0 1\nRload out 0 10k'
    out=exp.execute(m,'open_loop_bandwidth',openloop,'op\nwrite op.raw v(out)\nac dec 96 1 100Meg\nwrite ac.raw v(out) v(inv)',['op.raw','ac.raw'])
    if out:
        f=out['ac.raw']['frequency'].real;a=abs(out['ac.raw']['v(out)']); cross=np.where(a<1)[0]
        if len(cross) and cross[0]>0:
            i=cross[0]; gbw=float(np.exp(np.interp(0,np.log(a[i-1:i+1][::-1]),np.log(f[i-1:i+1][::-1]))))
            measurements['open_loop_unity_gain_hz']=gbw
            rows.append(compare('gbw',gbw,typ=1e7,condition='DC closed/AC open loop using1GH and1F fixture,RL10k'))
        else:
            rows.append(dict(name='gbw',status='unqualified',evidence='missing_unity_crossing',condition='AC sweep did not bracket unity open-loop gain'))
    for sign in [1,-1]:
        out=exp.execute(m,f'dc_clipping_branch_{sign}',circuit(load=2000,gain=10),
                        f'dc Vin 0 {sign*2} {sign*.005}\nwrite dc.raw v(out) i(vp) i(vn)',['dc.raw'])
        if out:
            v=out['dc.raw']['v(out)'];headroom=18-sign*v[-1]
            measurements[f'clipping_{sign}']=dict(headroom_v=float(headroom),output_v=float(v[-1]))
            rows.append(compare(f'output_headroom_{sign}',headroom,hi=.5,condition='RL2k plus10k feedback load,VS36V; branch from converged0V input,CM within range'))
    out=exp.execute(m,'loaded_supply_ramp',circuit(load=2000),'dc Vin 0 5 .025\nwrite dc.raw v(out) i(vp) i(vn)',['dc.raw'])
    if out:
        current=-out['dc.raw']['i(vp)'][-1]; measurements['loaded_supply_a']=float(current)
        rows.append(compare('output_supply_current',current,typ=.0035,condition='5V/2k +1mA Iq; circuit KCL consistency, not datasheet maximum'))
    fine=exp.execute(m,'noise_refined',circuit(),'noise v(out) Vin dec 128 1 100k 1\nsetplot noise1\nwrite noise.raw all',['noise.raw'],refine=True)
    if fine and 'bias_25' in measurements:
        value=float(at_frequency(fine['noise.raw']['frequency'],fine['noise.raw']['inoise_spectrum'],1000))
        rows.append(compare('noise_refinement',abs(value/measurements['bias_25']['en_1k']-1),hi=.01,evidence='numerical_refinement'))
    trans=[]
    for step in [1e-6,.5e-6]:
        out=exp.execute(m,f'clipping_tran_{step}',circuit(load=2000,gain=10),f'tran {step} .02 .01 {step}\nwrite tran.raw v(out) i(vp)',['tran.raw'],refine=step==.5e-6)
        if out: trans.append(out['tran.raw'])
    if len(trans)==2: rows.append(refinement(trans[0],trans[1],'time','v(out)','clipping_refinement'))
    return dict(comparisons=rows,measurements=measurements,scope='tested nominal CMOS macro DC/AC/noise/clipping and supply; no THD/process/thermal/crossover qualification')

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--models',nargs='+'); parser.add_argument('--parent-experiment',action='append',default=[]); args=parser.parse_args()
    for parent in args.parent_experiment:
        p=ROOT/'results/device_models'/parent
        if Path(parent).name!=parent or not any((p/n).is_file() for n in ['results.json','failure.json']):
            raise ValueError('Parent experiment must resolve to a preserved device-model record')
    verify_spec_lock(); manifest=source_manifest()
    folder=ROOT/'results/device_models'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True,exist_ok=False)
    for relative in manifest:
        p=folder/'source'/relative; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes((ROOT/relative).read_bytes())
    available=index(folder/'source/models'); ids=args.models or list(available)
    exp=Experiment(folder,available); results={}
    for id_ in ids:
        try:
            if id_ not in available: raise ValueError('Unknown model ID')
            m=available[id_]; resolve(exp.root,[id_])
            results[id_]=jfet(exp,m) if m['device_id']=='jfe150' else opa(exp,m) if m['device_id']=='opa197' else bipolar(exp,m)
            results[id_]['status']='disagreement' if any(r['status']=='fail' for r in results[id_]['comparisons']) else 'scoped_agreement'
        except (ValueError,RuntimeError,OSError) as exc:
            results[id_]={**exp.partial.get(id_,{}),'status':'error','reason':str(exc)}
        errors=[j for j in exp.jobs if j['model_id']==id_ and j['status']=='error']
        if errors: results[id_]['status']='error'; results[id_]['failed_jobs']=len(errors)
        write_json(folder/'checkpoint.json',{'results':results,'jobs':exp.jobs,'source_manifest':manifest,'complete':False})
        print(id_,results[id_]['status'],flush=True)
    unchanged=source_manifest()==manifest
    record=dict(schema_version=1,experiment_id=folder.name,timestamp_utc=datetime.now(timezone.utc).isoformat(),
                rng_seed=None,sampling='deterministic grids; no manufacturing probabilities',parent_experiments=args.parent_experiment,
                source_manifest=manifest,source_unchanged=unchanged,versions=environment_versions(),
                results=results,jobs=exp.jobs,eligible_for_production=False,
                status='recorded_unqualified' if unchanged else 'source_integrity_error',
                unresolved='Behavior-specific scope; failures preserved; no model receives a blanket low-noise/production qualification')
    write_json(folder/'results.json',record)
    print(json.dumps({'record':str(folder/'results.json'),'jobs':len(exp.jobs),'errors':sum(j['status']=='error' for j in exp.jobs),'source_unchanged':unchanged},indent=2))
    return 2 if not unchanged or any(r['status'] in {'error','disagreement'} for r in results.values()) else 0

if __name__=='__main__': raise SystemExit(main())
