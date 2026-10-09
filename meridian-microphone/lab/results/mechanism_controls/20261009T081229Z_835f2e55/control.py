# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit isolated bridge/demodulator physics control; never qualifies P48 hardware."""
from datetime import datetime,timezone
import hashlib,json,math,uuid
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from meridian_lab.core import ROOT,Simulator,source_manifest,digest,write_json,spec_digest
from meridian_lab.architectures import coherent_amplitudes

def main():
    id_=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8]
    folder=ROOT/'results/mechanism_controls'/id_;folder.mkdir(parents=True,exist_ok=False)
    manifest=source_manifest()
    for p in manifest:
        dest=folder/'source'/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/p).read_bytes())
    (folder/'control.py').write_bytes(Path(__file__).read_bytes())
    sim=Simulator('fixture_0001',folder);sim.model_root=folder/'source/models'
    rows=[]
    for pressure,carrier,density in [(0,.2,32),(1,0,32),(1,.2,32),(1,.2,64)]:
        extra=f'''Vrf bb 0 DC 40 SIN(40 {carrier} 100k)
Vanti aa 0 DC 40 SIN(40 {-carrier} 100k)
Vpressure pf 0 SIN(0 {pressure} 1k)
Vrearpressure pr 0 0
Xisland ff bb rr pf pr 0 FLAT_K47 CF=70p CR=70p PAR=1f CROSS=1f LEAK=1e14
Ccomparef ff aa 100p
Ccomparer rr aa 100p
Rreturnf ff 0 1e12
Rreturnr rr 0 1e12
Bproduct dd 0 V=2*(v(ff)-v(rr))*sin(2*pi*100k*time)
Rlp dd recovered 1k
Clp recovered 0 100n'''
        step=1/(100000*density)
        raw=sim.execute('bridge_demod_oracle',f'tran {step:.16g} .03 .02 {step:.16g}\nwrite control.raw time v(ff) v(rr) v(dd) v(recovered)',
                         ['control.raw'],extra=extra,environment_only=True)['control.raw']
        rows.append(dict(pressure_peak_pa=pressure,carrier_peak_v=carrier,samples_per_carrier=density,
            sidebands_peak_v=coherent_amplitudes(raw['time'],raw.voltage('ff','rr'),[99000,100000,101000]),
            demod_peak_v=coherent_amplitudes(raw['time'],raw['v(recovered)'],[1000,2000])))
    expected_side=.2*70e-12*100e-12/(170e-12)**2*(.02/60)
    expected_output=2*expected_side/math.sqrt(1+(2*math.pi*1000*1000*100e-9)**2)
    coarse,fine=rows[-2:];refinement=abs(coarse['demod_peak_v']['1000']-fine['demod_peak_v']['1000'])/expected_output
    ok=all(r['demod_peak_v']['1000']<expected_output*.01 for r in rows[:2]) and all(abs(r['demod_peak_v']['1000']/expected_output-1)<.02 for r in rows[-2:]) and refinement<.005
    write_json(folder/'results.json',dict(schema_version=1,experiment_id=id_,source_manifest=manifest,source_unchanged=source_manifest()==manifest,
       spec_sha256=spec_digest(),rng_seed=34047,random_sampling=False,control_script_sha256=digest(folder/'control.py'),
       status='pass' if ok else 'fail',eligible=False,parent_candidates=['candidate_0006','candidate_0009','candidate_0013'],
       hypothesis='Charge conservation yields carrier sidebands and calculable ideal synchronous recovery in an isolated island.',
       cases=rows,expected_sideband_peak_v=expected_side,expected_demod_peak_v=expected_output,relative_timestep_change=refinement,jobs=sim.jobs,
       limits='Isolated zero-parasitic analytic control, explicit ideal excitation/product; no P48 energy, physical driver/mixer/oscillator, safe polarization or periodic-noise qualification. Original capsule application envelope unchanged. 40V is an imposed control, not a safe capsule rating.'))
    print(json.dumps({'folder':str(folder.relative_to(ROOT)),'control_status':'pass' if ok else 'fail','expected_demod_peak_v':expected_output,'relative_refinement':refinement}))
    return 0 if ok else 2

if __name__=='__main__':raise SystemExit(main())
