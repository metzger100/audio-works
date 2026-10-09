#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Finite gap-closing controls; no generic model fitting or microphone selection."""
from pathlib import Path
from datetime import datetime, timezone
import sys,uuid,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'models/semiconductor'),str(ROOT/'research')]
from meridian_lab.core import source_manifest,read_yaml,verify_spec_lock,write_json,environment_versions
from meridian_lab.device_models import index,resolve
from meridian_lab.metrics import at_frequency
from characterize import Experiment,interpolate,compare
from parts_controls_001 import capacitance

EXTRA=['research/parts_controls_002.py','research/parts_controls_001.py','research/parts_control_plan_003.yaml','tools/ngspice-run']
def manifest():
    result=source_manifest()
    for rel in EXTRA: result[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    return result

def bipolar(exp,m,ref):
    rows=[];values={};s=ref['polarity'];primitive=m.get('primitive','X')
    def circuit(v=.6,rs=1e-6,vc=5):
        return f'Vc c 0 {s*vc}\nVin in 0 DC {s*v} AC 1\nRb in b {rs}\n{primitive}q c b 0 {m["subcircuit"]}\nHout out 0 Vc 1'
    for t in [-10,25,50]:
        out=exp.execute(m,f'transfer_{t}',circuit(),f'dc Vin {s*.3} {s*1} {s*.0005}\nwrite dc.raw v(in) i(vc) i(vin)',['dc.raw'],t)
        if not out:continue
        d=out['dc.raw'];current=-s*d['i(vc)'];grid=[]
        for target in [.0001,.001,.002,.01]:
            vb=interpolate(d,current,target,'v(in)')
            ib=abs(interpolate(d,current,target,'i(vin)'))
            grid.append(dict(ic_a=target,vbe_v=abs(vb),ib_a=ib,hfe=target/ib))
            if t==25 and target in ref['hfe_min']:
                rows.append(compare(f'hfe_{target}',target/ib,lo=ref['hfe_min'][target],hi=ref.get('hfe_max_at_10ma') if target==.01 else None,condition=ref['source']+' VCE5V25C; pulse-reference isothermal screen'))
        values[f'grid_{t}']=grid
    if not values:return rows,values
    c=f'Vc c 0 DC {s*10} AC 1\nVb b 0 0\nRe e 0 1e15\n{primitive}q c b e {m["subcircuit"]}'
    out=exp.execute(m,'collector_cap',c,'ac lin 1 1Meg 1Meg\nwrite ac.raw i(vc)',['ac.raw'])
    if out:rows.append(compare('ccb',capacitance(-out['ac.raw']['i(vc)'][0],1e6),hi=ref['ccb_max_f'],condition='VCB10V1MHz emitter1Pohm; finite fixture'))
    for t in [25,100]:
        out=exp.execute(m,f'icbo_{t}',c.replace(f'DC {s*10}',f'DC {s*120}'),'op\nwrite op.raw i(vc)',['op.raw'],t)
        if out:
            value=abs(float(out['op.raw']['i(vc)'][0]));values[f'icbo_{t}_a']=value
            limit=ref.get(f'icbo_max_{t}c_a')
            if limit is not None:rows.append(compare(f'icbo_{t}',value,hi=limit,condition='VCB120V emitter1Pohm'))
    if ref.get('nf_rs_ohm'):
        rs=ref['nf_rs_ohm']
        out=exp.execute(m,'nf_bias',circuit(rs=rs),f'dc Vin {s*.3} {s*1} {s*.0005}\nwrite dc.raw v(in) i(vc)',['dc.raw'])
        if out:
            bias=abs(interpolate(out['dc.raw'],-s*out['dc.raw']['i(vc)'],.0002,'v(in)'));noise=[]
            for n in [64,128]:
                out=exp.execute(m,f'noise_{n}',circuit(bias,rs),f'op\nwrite op.raw i(vc)\nnoise v(out) Vin dec {n} 10 100k 1\nsetplot noise1\nwrite noise.raw all',['op.raw','noise.raw'],refine=n==128)
                if out:
                    en=float(at_frequency(out['noise.raw']['frequency'],out['noise.raw']['inoise_spectrum'],1000));noise.append(en)
                    nf=float(10*np.log10(en**2/(4*1.380649e-23*298.15*rs)))
                    values['nf_actual_ic_a']=abs(float(out['op.raw']['i(vc)'][0]));values['nf_density_1khz_db']=nf
            if noise:rows.append(compare('nf_density_screen',nf,hi=ref['nf_max_db'],evidence='conditional_frequency_screen',condition='IC200uA VCE5V Rs10ohm f1k25C; unspecified measurement filter; no broadband claim'))
            if len(noise)==2:rows.append(compare('noise_refinement',abs(noise[1]/noise[0]-1),hi=.01,evidence='numerical_refinement'))
    for t,rail in [(-10,44),(25,48),(50,52)]:
        c=f'Vc c 0 {s*rail}\nVref ref 0 {s*1.7}\nRb ref b 100k\nRe e 0 1k\n{primitive}q c b e {m["subcircuit"]}'
        out=exp.execute(m,f'coupled_support_{rail}_{t}',c,'op\nwrite op.raw v(e) v(b) i(vc) i(vref)',['op.raw'],t)
        if out:
            d=out['op.raw'];ic=abs(float(d['i(vc)'][0]));vce=abs(s*rail-float(d['v(e)'][0]))
            values[f'coupled_support_{rail}_{t}']=dict(ic_a=ic,vce_v=vce,dissipation_w=ic*vce,base_drop_v=abs(float(d['i(vref)'][0]))*100000)
    values['scope']='Isothermal controls; no electrothermal feedback/SOA/breakdown/flicker or production guarantee. Passive nominal fixture is not a qualified BOM.'
    return rows,values

def dual(exp,m,ref):
    rows=[];values={}
    def circuit(vg=0,vd=10):return f'Vd d 0 {vd}\nVg g 0 DC {vg} AC 1\nJq d g 0 {m["subcircuit"]}\nHout out 0 Vd 1'
    bias=None
    for t in [-10,25,50]:
        out=exp.execute(m,f'transfer_{t}',circuit(),'dc Vg -2 0 .001\nwrite dc.raw v(g) i(vd)',['dc.raw'],t)
        if out:
            d=out['dc.raw'];values[f'idss_{t}_a']=-float(d['i(vd)'][-1])
            if t==25:
                rows.append(compare('idss_25c',values[f'idss_{t}_a'],*ref['idss_a'],condition=ref['source']+' VDS10 VGS0'))
                bias=interpolate(d,-d['i(vd)'],.002,'v(g)')
    ns=[]
    if bias is not None:
        for n in [64,128]:
            out=exp.execute(m,f'noise_{n}',circuit(bias),f'op\nwrite op.raw i(vd)\nnoise v(out) Vg dec {n} 1 100k 1\nsetplot noise1\nwrite noise.raw all',['op.raw','noise.raw'],refine=n==128)
            if out:
                d=out['noise.raw'];ns.append([float(at_frequency(d['frequency'],d['inoise_spectrum'],f)) for f in [10,1000]])
                values['noise_2ma_v_sqrt_hz']=dict(zip([10,1000],ns[-1]))
        if ns:
            for i,f in enumerate([10,1000]):rows.append(compare(f'en_{f}',ns[-1][i],typ=ref['en_2ma'][f],condition=ref['source']+' IC2mA VDS10 25C NBW1Hz; note3 typical disclaimer'))
        if len(ns)==2:
            for i,f in enumerate([10,1000]):rows.append(compare(f'noise_refinement_{f}',abs(ns[1][i]/ns[0][i]-1),hi=.01,evidence='numerical_refinement'))
    out=exp.execute(m,'ciss',circuit(),'ac lin 1 1Meg 1Meg\nwrite ac.raw i(vg)',['ac.raw'])
    if out:rows.append(compare('ciss',capacitance(-out['ac.raw']['i(vg)'][0],1e6),typ=ref['ciss_typ_f'],condition='VDS10 VGS0 1MHz25C'))
    out=exp.execute(m,'gate_leak',circuit(-25,0),'op\nwrite op.raw i(vg)',['op.raw'])
    if out:rows.append(compare('gate_leak',abs(float(out['op.raw']['i(vg)'][0])),hi=ref['leak_max_a'],condition='VGS-25 VDS0 25C'))
    values['scope']='One nominal half; ordinary matching limits documentary only, no substrate/dual covariance/mismatch validation.'
    return rows,values

def amplifier(exp,m):
    rows=[];values={}
    for translation in ([0,20] if m['device_id']=='opa928' else [0]):
        extra='guard1 guard2 ' if m['device_id']=='opa928' else ''
        lo=translation;hi=lo+16;cm=lo+8
        c=f'Vp p 0 {hi}\nVn n 0 {lo}\nVin in 0 DC {cm} AC 1\nXq in out p n out {extra}{m["subcircuit"]}\nVm mid 0 {cm}\nRl out mid 10k\n.nodeset v(out)={cm}\n.options gmin=1e-16'
        out=exp.execute(m,f'nodeset_translate_{translation}',c,'op\nwrite op.raw v(out) i(vin) i(vp)\nac dec 64 10 10Meg\nwrite ac.raw v(out)\nnoise v(out) Vin dec 128 10 100k 1\nsetplot noise1\nwrite noise.raw all',['op.raw','ac.raw','noise.raw'])
        if out:
            d=out['op.raw'];values[str(translation)]=dict(output_error_v=float(d['v(out)'][0])-cm,iq_a=-float(d['i(vp)'][0]),ib_a=float(d['i(vin)'][0]),en_1khz=float(at_frequency(out['noise.raw']['frequency'],out['noise.raw']['inoise_spectrum'],1000)))
    if m['device_id']=='opa928' and len(values)==2:
        rows.append(compare('translation_output_error',abs(values['0']['output_error_v']-values['20']['output_error_v']),hi=1e-5,evidence='numerical_oracle',condition='Same16V grounded/translated+20V follower; no guard load or charge validation'))
    values['scope']='Nodeset is only an initial guess. No model edits or relaxed thresholds. Numerical translation is not independent noise/overload/leakage validation.'
    return rows,values

def main():
    verify_spec_lock();plan=read_yaml(ROOT/'research/parts_control_plan_003.yaml');before=manifest()
    folder=ROOT/'results/device_models'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_parts2_'+uuid.uuid4().hex[:8]);folder.mkdir(parents=True,exist_ok=False)
    for rel in before:
        target=folder/'source'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/rel).read_bytes())
    available=index(folder/'source/models');exp=Experiment(folder,available);results={}
    for mid in plan['models']:
        m=available[mid]
        try:
            resolve(exp.root,[mid])
            if m['device_id']=='lsk389a':rows,values=dual(exp,m,exp.refs['parts_expansion_002']['lsk389a'])
            elif m['device_id'] in ['opa1656','opa928','lmp7721']:rows,values=amplifier(exp,m)
            else:
                ref=exp.refs['parts_expansion_002']['diotec_2n5551' if m['device_id']=='diotec_mmbt5551' else m['device_id']]
                rows,values=bipolar(exp,m,ref)
                if m['device_id']=='diotec_mmbt5551':
                    for row in rows:row.update(status='reference_only',condition=row['condition']+'; TO92 reference is not exact SOT23 validation')
            jobs=[j for j in exp.jobs if j['model_id']==mid];errors=sum(j['status']=='error' for j in jobs)
            results[mid]=dict(comparisons=rows,measurements=values,failed_jobs=errors,status='error' if errors else 'disagreement' if any(r['status']=='fail' for r in rows) else 'scoped_record')
        except (RuntimeError,ValueError,OSError) as exc:results[mid]=dict(status='error',reason=str(exc))
        if len(exp.jobs)>plan['maximum_jobs']:raise RuntimeError('Finite declared job budget exceeded')
        write_json(folder/'checkpoint.json',dict(results=results,jobs=exp.jobs,complete=False));print(mid,results[mid]['status'],flush=True)
    unchanged=manifest()==before
    write_json(folder/'results.json',dict(schema_version=1,experiment_id=folder.name,timestamp_utc=datetime.now(timezone.utc).isoformat(),plan=plan,source_manifest=before,source_unchanged=unchanged,versions=environment_versions(),results=results,jobs=exp.jobs,eligible_for_production=False,candidate_evaluations=0,parent_experiments=plan['parent_experiments'],status='recorded_unqualified' if unchanged else 'source_integrity_error'))
    print(json.dumps(dict(record=str(folder/'results.json'),jobs=len(exp.jobs),errors=sum(j['status']=='error' for j in exp.jobs),source_unchanged=unchanged)))
    return 2 if not unchanged or any(r['status'] in ['error','disagreement'] for r in results.values()) else 0
if __name__=='__main__':raise SystemExit(main())
