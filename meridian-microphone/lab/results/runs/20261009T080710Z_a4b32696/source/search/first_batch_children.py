# SPDX-License-Identifier: GPL-3.0-or-later
"""Preserve failed parents; register discrete-driver and explicit carrier children."""
from copy import deepcopy
import re
import yaml
from first_batch import Attempt
from mutate import register
from meridian_lab.core import ROOT,read_yaml


def clone(parent,number,title):
    a=Attempt.__new__(Attempt);a.id=f'candidate_{number:04d}';a.title=title
    a.meta=deepcopy(read_yaml(ROOT/'candidates'/parent/'topology.yaml'))
    a.bom=deepcopy(read_yaml(ROOT/'candidates'/parent/'bom.yaml')['physical_parts'])
    a.lines=(ROOT/'candidates'/parent/'circuit.cir').read_text().splitlines()[:-1]
    a.meta['parents']=[parent];a.parent=parent
    # Preserve the unavailable original 10k dependency in the parent. Realized child
    # specifies active automotive AC series; shared value does not qualify excess noise.
    for part in a.bom:
        if part['part_id']=='RC0603FR-0710KL': part['part_id']='AC0603FR-0710KL'
    for definition in a.meta['parameters'].values():
        definition['provenance']=definition['provenance'].replace('RC0603FR-0710KL','AC0603FR-0710KL')
    return a


def remove(a,names):
    a.lines=[line for line in a.lines if not any(re.match(r'(?i)^(?:X|V)'+re.escape(name)+r'(?:_|\s)',line) for name in names)
             and not any(line.split()[0].lower()==name.lower() for name in names)]
    a.meta['power_devices']=[d for d in a.meta['power_devices'] if d['instance'] not in names]
    a.meta['power_resistors']=[r for r in a.meta['power_resistors'] if r['reference'] not in names]
    a.bom=[p for p in a.bom if p['reference'] not in names]
    for name in names:
        a.meta['parameters'].pop(name.upper()+'_VALUE',None);a.meta['population'].pop(name.upper()+'_VALUE',None)
    a.meta['niche']['active_device_count']=len(a.meta['power_devices'])


def bipolar_outputs(a,signal):
    remove(a,['Uoutp','Uoutn','Rinvertin','Rinvertfb'])
    a.device('Qoutp','BC846B',['rail',signal,'outp'],'BC846B,215','bc846b_emitter_r1')
    a.device('Qinvert','BC846B',['inverse',signal,'ie'],'BC846B,215','bc846b_emitter_r1')
    a.resistor('Rinvemitter','ie','g',10000);a.resistor('Rinvcollector','rail','inverse',10000)
    a.device('Qoutn','BC846B',['rail','inverse','outn'],'BC846B,215','bc846b_emitter_r1')
    a.resistor('Routloadp','outp','g',10000);a.resistor('Routloadn','outn','g',10000)
    # Every newly introduced 10k also uses the realized child part.
    for part in a.bom:
        if part['part_id']=='RC0603FR-0710KL':part['part_id']='AC0603FR-0710KL'
    a.meta['niche']['output']='discrete_NPN_differential_fixed_degeneration'
    a.meta['questions']['balanced_output']='NPN follower plus emitter-degenerated NPN inverse/follower; finite unequal impedances measured'


def finish(a,changes):
    a.meta['semiconductor_models']=list(dict.fromkeys(d['model_id'] for d in a.meta['power_devices']))
    a.lines.append('.ends DUT')
    folder=ROOT/'search/proposals'/a.id;folder.mkdir(exist_ok=False)
    (folder/'circuit.cir').write_text('\n'.join(a.lines)+'\n')
    (folder/'topology.yaml').write_text(yaml.safe_dump(a.meta,sort_keys=False))
    dest=register(a.parent,a.id,folder/'circuit.cir',folder/'topology.yaml',a.meta['questions']['hypothesis'],changes)
    bom=read_yaml(ROOT/'candidates'/a.parent/'bom.yaml');bom.update(candidate=a.id,parent_bom=a.parent,physical_parts=a.bom)
    if a.id=='candidate_0009':
        bom['missing_implementation_parts']=['physical carrier oscillator/anti-phase excitation','physical synchronous multiplier',
                    'input buffers and balanced audio drivers, their power/noise/clipping']
    (dest/'bom.yaml').write_text(yaml.safe_dump(bom,sort_keys=False))
    (dest/'notes.md').write_text(f'# {a.title}\n\nParent [{a.parent}](../{a.parent}/notes.md) and all failed records are retained.\n\nEngineer change: {changes}\n\n[Topology and nine questions](topology.yaml) · [Intended-quantity research BOM](bom.yaml). No selection, trimming, substitute-equivalence, production-noise or patent clearance is claimed. Explicit ideal blocks remain ineligible. Nominal passives/tolerance stress are implemented; unmeasured ESR/leakage/excess-noise/temperature laws remain qualification gaps.\n')


def main():
    a=clone('candidate_0001',7,'Conventional JFET with discrete NPN output')
    bipolar_outputs(a,'signal')
    a.meta.update(input_device_class='JFET',internal_device_classes='JFET input; NPN audio drivers and power',fet_audio_path=True)
    finish(a,'Retain gate-bias/source-degeneration voltage conversion; replace failed CMOS output macros with three real NPN stages; realize backordered 10k passives as separately specified AC series.')

    a=clone('candidate_0002',8,'JFET with discrete differential DC servo and NPN output')
    remove(a,['Uservo','Rsense','Csense','Rsetbottom','Cset']+[f'Rsettop{i}' for i in range(9)])
    previous='rail'
    for i in range(15):
        node='setpoint' if i==14 else f'set_div{i}'
        a.resistor(f'Rservoref{i}',previous,node,10000);previous=node
    a.resistor('Rservorefground','setpoint','g',10000);a.capacitor('Cservoref','setpoint','g',47e-6)
    previous='source'
    for i in range(3):
        node='slow' if i==2 else f'sense_div{i}'
        a.resistor(f'Rservosense{i}',previous,node,100000);previous=node
    a.resistor('Rservosenseground','slow','g',100000);a.capacitor('Cservoslow','slow','g',47e-6)
    a.device('Qservoerror','BC846B',['servo','slow','se'],'BC846B,215','bc846b_emitter_r1')
    a.device('Qservoref','BC846B',['rail','setpoint','se'],'BC846B,215','bc846b_emitter_r1')
    a.resistor('Rservotail','se','g',1000);a.resistor('Rservoout','rail','servo',100000)
    bipolar_outputs(a,'signal')
    a.meta.update(input_device_class='JFET',internal_device_classes='JFET input; NPN servo/audio drivers/power',fet_audio_path=True)
    a.meta['questions']['dc_bias']='NPN differential error compares source/4 with rail/16; resistor tail, capacitor slow path and explicit base-current error; source resistor sets current'
    finish(a,'Replace failed CMOS slow servo by a discrete NPN differential DC controller with level-divided sensing; preserve high-impedance JFET voltage/audio conversion; use discrete NPN outputs and AC-series 10k parts.')

    a=clone('candidate_0006',9,'Carrier bridge with explicit ideal buffers')
    remove(a,['Ufront','Urear','Uoutp','Uoutn','Rinvertin','Rinvertfb'])
    a.lines += ["Efront frontbuf g f g 1", "Erear rearbuf g rear g 1", "Eoutp outp g audio g 1", "Eoutn outn g VOL='2*v(mid,g)-v(audio,g)'"]
    a.meta.update(ideal_devices=True,input_device_class='ideal_voltage_control',fet_audio_path='unknown_for_unimplemented_hardware',
                  internal_device_classes='NPN power; ideal signal/excitation/demodulator controls, no physical input/output classes claimed')
    a.meta['niche']['input_device']='ideal_bridge_control';a.meta['niche']['output']='ideal_differential_control'
    finish(a,'Retain floating capacitive bridge and synchronous product; replace failed macro buffers/drivers with explicit ideal controls. No architecture noise, power, clipping or build-ready claim; physical implementations remain unresolved.')

    for parent,number,front in [('candidate_0003',10,'frontout'),('candidate_0004',11,'chargeout')]:
        a=clone(parent,number,'CMOS conversion with discrete NPN output')
        remove(a,['Uoutn','Rinvertin','Rinvertfb'])
        # Existing front opamp output now drives the NPN stage, keeping feedback on
        # its own output. The actual conversion principle is unchanged.
        a.lines=[re.sub(r'\boutp\b',front,line) if not re.match(r'(?i)^(Routp|Coutp)\b',line) else line for line in a.lines]
        for device in a.meta['power_devices']: device['nodes']=[front if n=='outp' else n for n in device['nodes']]
        for resistor in a.meta['power_resistors']:
            if resistor['reference']!='Routp':resistor['nodes']=[front if n=='outp' else n for n in resistor['nodes']]
        bipolar_outputs(a,front)
        a.meta.update(input_device_class='CMOS',internal_device_classes='CMOS input/guard (if present); NPN audio drivers and power',fet_audio_path=True)
        finish(a,'Preserve CMOS voltage/guard or charge feedback; replace output macro with discrete NPN stages to test loading/power interaction; actual AC-series 10k BOM is separately re-evaluated.')


if __name__=='__main__':main()
