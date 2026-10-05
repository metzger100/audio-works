#!/usr/bin/env python3
"""Render comparisons from immutable isolated records, never regenerate simulations."""
from pathlib import Path
import sys,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from meridian_lab.core import digest,read_yaml,write_json

def main():
    folder=ROOT/'results/device_models/20261005T185102Z_95a6dda5'
    record=json.loads((folder/'results.json').read_text())
    assert record['source_unchanged'] is True
    used={}
    def csv(model,label,name):
        job=next(j for j in record['jobs'] if j['model_id']==model and j['label']==label)
        assert job['status']=='ok'
        p=folder/model/label/(name+'.csv');assert digest(p)==job['csv_hashes'][p.name]
        used[str(p.relative_to(ROOT))]=digest(p)
        header=p.read_text().splitlines()[0].split(',');data=np.loadtxt(p,delimiter=',',skiprows=1)
        return {n:data[:,i] for i,n in enumerate(header)}
    ref=folder/'source/models/semiconductor/references.yaml'
    assert digest(ref)==record['source_manifest']['models/semiconductor/references.yaml']
    refs=read_yaml(ref)
    plt.rcParams.update({'font.size':9,'axes.titlesize':11,'axes.labelsize':10})
    fig,axes=plt.subplots(2,2,figsize=(12,8.6),layout='constrained')
    colors=['#176a9c','#c77c23','#8e4e9b'];ids=['jfe150_generic','jfe150_weak','jfe150_strong']
    labels=['nominal','vendor weak (not bounded)','vendor strong (not bounded)']
    for model,label,color in zip(ids,labels,colors):
        a=csv(model,'transfer_25','transfer.raw');axes[0,0].plot(a['v(g)'], -a['i(vd)']*1e3,label=label,color=color)
        a=csv(model,'small_noise_0.002','noise.raw');axes[0,1].loglog(a['frequency'],a['inoise_spectrum']*1e9,label=label,color=color)
    for p in refs['jfe150']['curve_observations']['transfer_figure_6_1']['points']:
        low,high=p['current_interval_a'];axes[0,0].errorbar(p['vgs_v'],(low+high)*500,yerr=(high-low)*500,color='#202020',fmt='o',capsize=4)
    # Conflicting output reference at the same bias is retained, not averaged.
    p=refs['jfe150']['curve_observations']['output_figure_6_3']['points'][0]
    low,high=p['current_interval_a'];axes[0,0].errorbar(-.7,(low+high)*500,yerr=(high-low)*500,color='#b43636',fmt='s',capsize=4,label='Fig 6-3 conflicting reference')
    axes[0,0].set(xlabel='VGS (V)',ylabel='Drain current (mA)',title='JFE150 transfer: VDS=5 V, 25°C',xlim=(-1.6,.05),ylim=(0,42))
    axes[0,0].legend(fontsize=8)
    axes[0,1].scatter([10,1000],[1.6,.9],marker='o',color='#202020',label='2 mA typical table points',zorder=4)
    axes[0,1].set(xlabel='Frequency (Hz)',ylabel='Input voltage noise (nV/√Hz)',title='JFE150 noise: 2 mA, VDS=5 V',xlim=(1,1e5),ylim=(.6,8))
    axes[0,1].legend(fontsize=8)
    a=csv('opa197_pspice','small_25','noise.raw');axes[1,0].loglog(a['frequency'],a['inoise_spectrum']*1e9,color='#176a9c',label='OPA197 macro')
    axes[1,0].scatter([100,1000],[10.5,5.5],color='#202020',label='Typical table points',zorder=4)
    axes[1,0].set(xlabel='Frequency (Hz)',ylabel='Input voltage noise (nV/√Hz)',title='OPA197: ±18 V, mid-common-mode, 25°C',xlim=(1,1e5),ylim=(4,100))
    axes[1,0].legend(fontsize=8)
    ax=axes[1,1];ax.add_patch(Rectangle((24,55),22,25,facecolor='#e5efdf',edgecolor='#42633b',linestyle='--',label='Separate guaranteed limits; no joint distribution'))
    for model,label,color in zip(ids,labels,colors):
        m=record['results'][model]['measurements']['idss_gfs_25'];ax.scatter(m['idss_a']*1e3,m['gfs_s']*1e3,color=color,label=label)
    ax.set(xlabel='Idss (mA)',ylabel='GFS (mS)',title='JFE150 guaranteed DC screen: VDS=10 V',xlim=(15,49),ylim=(30,85))
    ax.legend(fontsize=7.5,loc='upper left')
    for ax in axes.flat:ax.grid(alpha=.22)
    fig.suptitle('Manufacturer models: scoped agreement and unresolved disagreement\nTypical noise is not a production maximum; no device or microphone qualification',fontsize=13)
    output=ROOT/'research/device_model_comparison.png';fig.savefig(output,dpi=170);plt.close(fig)
    def flatten(v,prefix=''):
        out={}
        for k,x in v.items():
            if isinstance(x,dict):out.update(flatten(x,prefix+k+'.'))
            elif isinstance(x,(int,float)) and not isinstance(x,bool):out[prefix+k]=x
        return out
    a=flatten(record['results']['jfe150_generic']['measurements']);b=flatten(record['results']['jfe150_pspice']['measurements'])
    common=a.keys()&b.keys();disagreement=max(abs(a[k]-b[k])/max(abs(a[k]),1e-30) for k in common)
    write_json(ROOT/'research/device_model_plot_provenance.json',dict(record=str((folder/'results.json').relative_to(ROOT)),record_sha256=digest(folder/'results.json'),renderer_sha256=digest(Path(__file__)),reference_sha256=digest(ref),csv_hashes=used,output_sha256=digest(output),generic_pspice_common_scalar_count=len(common),maximum_relative_scalar_disagreement=disagreement,note='Shared electrical parameters, not independent models; no smoothing/fitting/noise extrapolation'))
    print(str(output))
if __name__=='__main__':main()
