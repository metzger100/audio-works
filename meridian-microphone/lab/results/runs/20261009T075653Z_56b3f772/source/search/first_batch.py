# SPDX-License-Identifier: GPL-3.0-or-later
"""One-time registration of six reviewed mechanisms; refuses existing identities.

The generator is provenance, not an optimizer or performance declaration.
Run from the lab with .venv/bin/python search/first_batch.py.
"""
from pathlib import Path
import sys
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from meridian_lab.core import ROOT
from mutate import register


class Attempt:
    def __init__(self, number, family, title, concept, sensing, feedback, questions, sources):
        self.id = f'candidate_{number:04d}'
        self.title = title
        self.lines = ['* SPDX-License-Identifier: CERN-OHL-S-2.0', '* Internal research; no build recommendation.', '.subckt DUT f b rear p n g rail']
        self.bom = []
        self.meta = dict(family=family, concept_parent=concept, ideal_devices=False,
                        semiconductor_models=['bc846b_emitter_r1'], parameters={}, population={},
                        device_models=[], qualification_evidence=[], noise_groups={},
                        dc_probes=[], loop_probes=[], power_devices=[], power_resistors=[],
                        questions=questions, sources=sources,
                        input_device_class='JFET' if number < 3 else 'BJT' if number == 5 else 'CMOS',
                        fet_audio_path=number != 5, fet_power_circuitry=False,
                        internal_device_classes='CMOS per OPA197 datasheet; macro internals are behavioral, not transistor evidence' if number != 5 else 'NPN only',
                        procurement_state='research_BOM_live_orderability_and_delivered_quote_unverified',
                        patent_state='unscreened_no_clearance', prototype_gate='hold',
                        manufacture_gate='hold', build_publication_gate='hold',
                        niche=dict(input_device='JFET' if number < 3 else 'BJT' if number == 5 else 'CMOS',
                                   sensing=sensing, reference='floating_bridge' if number == 6 else 'single_ended',
                                   feedback=feedback, bias='source_servo' if number == 2 else 'fixed_parts',
                                   active_device_count=0, servo=number == 2,
                                   output='differential_real_devices', common_mode='divider', bootstrap=number == 3))
        self.power()

    def parameter(self, name, value, tolerance, provenance):
        key = name.upper() + '_VALUE'
        self.meta['parameters'][key] = dict(default=value, range=[value*(1-tolerance), value*(1+tolerance)],
                                             scale='log', provenance=provenance)
        self.meta['population'][key] = dict(range=[value*(1-tolerance), value*(1+tolerance)],
                                            distribution='uniform', provenance=provenance,
                                            interpretation='independent tolerance stress, not a measured production distribution')
        return key

    def resistor(self, name, a, b, value, high=False, parasitic=False):
        part = 'HVA12JA1G00' if high else {47:'RC0603FR-0747RL', 1000:'RC0603FR-071KL',
                2200:'RC0603FR-072K2L', 3300:'RC0603FR-073K3L', 10000:'RC0603FR-0710KL',
                100000:'RC0603FR-07100KL', 1000000:'RC0603FR-071ML'}[value] if not parasitic else None
        tol = .05 if high else .01
        if parasitic:
            key=self.parameter(name, value, .9, 'assumed board leakage; broader capsule range remains unchanged')
        else:
            key=self.parameter(name, value, tol, f'BOM {part}; catalogue tolerance; excess noise/voltage coefficient unqualified')
            self.bom.append(dict(reference=name, part_id=part, quantity=1, value=value, unit='ohm', tolerance_fraction=tol))
        self.lines.append(f'{name} {a} {b} {{{key}}}')
        self.meta['power_resistors'].append(dict(reference=name, nodes=[a,b], parameter=key))
        if high:
            self.capacitor('C'+name[1:]+'stray',a,b,2e-13,assumed=True)

    def capacitor(self, name, a, b, value, assumed=False):
        part={47e-6:'EEU-FR1J470', 1e-6:'R82EC4100DQ70J', 1e-7:'R82EC3100DQ70J',
              1e-10:'C0603C101J1GACTU'}.get(value)
        tol=.20 if value==47e-6 else .05
        key=self.parameter(name,value,.9 if assumed else tol,
                           'assumed geometry/parasitic; not a purchasable part or measured bound' if assumed else f'BOM {part}; capacitance tolerance; dielectric/leakage/ESR coverage partial')
        self.lines.append(f'{name} {a} {b} {{{key}}}')
        if not assumed:
            if part is None: raise ValueError('Unsourced nominal capacitor')
            self.bom.append(dict(reference=name,part_id=part,quantity=1,value=value,unit='F',tolerance_fraction=tol))
            # Explicit conservative ESR and insulation controls, separately labelled assumptions.
            # Bulk storage and film loss need measured frequency/temperature-dependent models.

    def device(self, name, model, nodes, part, model_id):
        currents=[]; internals=[]
        for i,node in enumerate(nodes):
            sense=f'V{name}_{i}'; inside=f'{name}_t{i}'
            self.lines.append(f'{sense} {node} {inside} 0')
            currents.append(f'i(v.xdut.{sense.lower()})'); internals.append(inside)
        self.lines.append(f'X{name} '+ ' '.join(internals)+' '+model)
        self.meta['power_devices'].append(dict(instance=name,model_id=model_id,nodes=nodes,currents=currents))
        if model_id not in self.meta['semiconductor_models']: self.meta['semiconductor_models'].append(model_id)
        self.bom.append(dict(reference=name,part_id=part,quantity=1,value=model,unit='device',tolerance_fraction=None))
        self.meta['niche']['active_device_count']+=1

    def power(self):
        self.resistor('Rharvestp','p','raw',2200)
        self.resistor('Rharvestn','n','raw',2200)
        self.capacitor('Craw','raw','g',47e-6)
        self.resistor('Rregtop','raw','regbase',100000)
        self.resistor('Rregbottom','regbase','g',100000)
        self.capacitor('Cregbase','regbase','g',1e-6)
        self.device('Qreg','BC846B',['raw','regbase','rail'],'BC846B,215','bc846b_emitter_r1')
        self.capacitor('Crail','rail','g',47e-6)
        self.resistor('Rmidtop','rail','mid',10000)
        self.resistor('Rmidbottom','mid','g',10000)
        self.capacitor('Cmid','mid','g',47e-6)
        # 10 MOhm realized as ten standard 1 MOhm parts, not an ideal unavailable value.
        previous='raw'
        for i in range(10):
            node='pol' if i==9 else f'pol_{i}'
            self.resistor(f'Rpolar{i}',previous,node,1000000);previous=node
        self.capacitor('Cpol','pol','g',1e-7)
        self.resistor('Rback','pol','b',1000000)

    def opamp(self,name,positive,negative,output):
        self.device(name,'OPAx197',[positive,negative,'rail','g',output],'OPA197IDBVR','opa197_pspice')

    def output(self,signal,buffer=True):
        if buffer: self.opamp('Uoutp',signal,'outp','outp')
        elif signal != 'outp':
            self.lines.append(f'Voutlink {signal} outp 0')
        self.resistor('Rinvertin','outp','inv',10000)
        self.resistor('Rinvertfb','outn','inv',10000)
        self.opamp('Uoutn','mid','inv','outn')
        self.coupling()

    def coupling(self):
        # Positive electrolytic terminal belongs to the higher P48 pin; power-off reversal unqualified.
        self.resistor('Routp','outp','cp',47)
        self.resistor('Routn','outn','cn',47)
        self.capacitor('Coutp','p','cp',47e-6)
        self.capacitor('Coutn','n','cn',47e-6)

    def finish(self):
        self.lines.append('.ends DUT')
        folder=ROOT/'search/proposals'/self.id; folder.mkdir(exist_ok=False)
        circuit=folder/'circuit.cir'; circuit.write_text('\n'.join(self.lines)+'\n')
        metadata=folder/'topology.yaml'; metadata.write_text(yaml.safe_dump(self.meta,sort_keys=False))
        hypothesis=self.meta['questions']['hypothesis']
        dest=register('fixture_0001',self.id,circuit,metadata,hypothesis,
                      f'Independent {self.title} mechanism child of interface fixture; not a copied production microphone.')
        bom=dict(schema_version=1,candidate=self.id,intended_equipment='one possible finished microphone; alternatives are not a shopping list',
                 capsule=dict(mpn='K47FRB',quantity=1,safe_polarization='unknown',included_in_electronics_cost=False),
                 procurement_register='../../research/procurement/architecture_parts_2026-10-09.yaml',
                 physical_parts=self.bom,simulation_only='Zero-volt current observers and explicit geometry/leakage controls are not purchases',
                 substitutes_qualified=[],build_ready=False)
        if self.meta['ideal_devices']:
            bom['missing_implementation_parts']=['carrier oscillator/anti-phase excitation and its power/noise','synchronous analog demodulator and its power/noise']
        (dest/'bom.yaml').write_text(yaml.safe_dump(bom,sort_keys=False))
        (dest/'notes.md').write_text(f'# {self.title}\n\nInventor: see the nine questions and falsifiable hypothesis in [metadata](topology.yaml).\n\nEngineer: fixed ordinary nominal parts, NPN divider-fed rail, filtered polarization and real output terminals. No selection or trimming. [BOM](bom.yaml) is an intended-quantity research BOM; live availability, delivered costs, parasitic/leakage/excess-noise and full production device behavior remain unqualified. Board parasitics are assumptions, not purchased components. All qualification and patent gates remain held.\n\nRun `./run evaluate {self.id}`. Sources are frozen per experiment. No optimization or substitute credit is claimed.\n')
        return dest


def questions(quantity,loading,bias,gain,output,noise,distortion,fatal,test,hypothesis):
    return dict(sensed_quantity=quantity,loading=loading,dc_bias=bias,gain_or_impedance_transformation=gain,
                balanced_output=output,expected_noise=noise,expected_distortion=distortion,
                likely_fatal_flaw=fatal,quickest_falsification=test,hypothesis=hypothesis)


def main():
    shared_output='Real output devices and two 47 ohm/47 uF legs; harvest/cable/load coupling measured, symmetry not presumed'
    a=Attempt(1,'conventional_jfet','Conventional degenerated JFET reference','concept_0001','voltage','source_degeneration',questions(
        'front open-circuit voltage','JFE input C, 1 GOhm gate bias; source follower reduces Cgs loading',
        'gate at rail/4; 3.3 kohm source degeneration; fixed parts across device spread',
        'source follower then AC coupling into real CMOS differential driver',shared_output,
        'JFE voltage/current/flicker plus gate/polarization resistors and both output opamps',
        'source-follower curvature, drain modulation and output clipping','production corner bias/noise/model coverage',
        'DC current/VGS/VDS across weak/strong proposals, then loading/noise',
        'A fixed degenerated JFE150 follower may retain usable bias without selecting a specimen; a failed nominal attempt cannot reject JFETs.'),['S14','S15'])
    for i in range(3): a.resistor(f'Rgatetop{i}','rail' if i==0 else f'gate_div{i-1}', 'gatebias' if i==2 else f'gate_div{i}',10000)
    a.resistor('Rgatebottom','gatebias','g',10000);a.capacitor('Cgatebias','gatebias','g',47e-6)
    a.resistor('Rbias','f','gatebias',1e9,high=True);a.resistor('Rrear','rear','g',1000)
    a.device('Jinput','JFE150',['rail','f','source','rail','g'],'JFE150DBVR','jfe150_pspice')
    a.resistor('Rsource','source','g',3300);a.capacitor('Caudio','source','signal',1e-6)
    a.resistor('Rsignal','signal','mid',1000000);a.output('signal');a.finish()

    a=Attempt(2,'unconventional_jfet','JFET slow source-current servo','concept_0015','voltage','slow_source_current_servo',questions(
        'front voltage above the slow servo bandwidth','1 GOhm gate servo injection; finite input C',
        'filtered source compared with rail/10; servo sets source current through 1 kohm',
        'audio source follower; DC loop has separate authority and bandwidth',shared_output,
        'servo voltage noise through gate resistor, JFE flicker/current noise and output noise',
        'servo/audio interaction, rail-dependent reference and clipping','insufficient servo authority or loop instability',
        'source-current DC, leakage extremes, startup and audio/servo return ratio',
        'A slow feedback current controller may reduce specimen-dependent bias without selection while preserving voltage sensing above its bandwidth.'),['S06','S14','S15'])
    previous='rail'
    for i in range(9):
        node='setpoint' if i==8 else f'set_div{i}'
        a.resistor(f'Rsettop{i}',previous,node,10000);previous=node
    a.resistor('Rsetbottom','setpoint','g',10000);a.capacitor('Cset','setpoint','g',47e-6)
    a.resistor('Rsense','source','slow',1000000);a.capacitor('Csense','slow','g',1e-6)
    a.opamp('Uservo','setpoint','slow','servo')
    a.resistor('Rbias','f','servo',1e9,high=True);a.resistor('Rrear','rear','g',1000)
    a.device('Jinput','JFE150',['rail','f','source','rail','g'],'JFE150DBVR','jfe150_pspice')
    a.resistor('Rsource','source','g',1000);a.capacitor('Caudio','source','signal',1e-6)
    a.resistor('Rsignal','signal','mid',1000000);a.output('signal');a.finish()

    a=Attempt(3,'bootstrap','CMOS voltage input with driven guard','concept_0005','voltage','unity_voltage_guard',questions(
        'front voltage','finite CMOS Cin; guard follows front; bias return bootstrapped in audio',
        'midrail through 1 GOhm; guard DC anchored by 1 Mohm',
        'OPA197 follower plus finite-bandwidth guard buffer',shared_output,
        'input CMOS en/in/1f, guard coupling and both output channels',
        'common-mode crossover and positive-feedback tracking error','guard noise or instability exceeds loading benefit',
        'compare guarded/untracked admittance and noise with assumed 0.5-10 pF geometry',
        'A real follower guard may reduce external capacitive/leakage loading; it cannot erase the opamp intrinsic input capacitance.'),['S06','S16'])
    a.resistor('Rbias','f','boot',1e9,high=True);a.resistor('Rbootdc','boot','mid',1000000)
    a.opamp('Uinput','f','outp','outp');a.opamp('Uguard','outp','guard','guard')
    a.capacitor('Cboot','guard','boot',1e-6);a.capacitor('Cguard','f','guard',5e-12,assumed=True)
    a.resistor('Rguardleak','f','guard',1e12,parasitic=True);a.resistor('Rrear','rear','g',1000)
    a.output('outp',buffer=False);a.finish()

    a=Attempt(4,'charge','CMOS charge feedback with resistive reset','concept_0010','charge','capacitive_feedback',questions(
        'front displacement charge','virtual midrail at front; 100 pF feedback capacitor sets conversion',
        '1 GOhm feedback bleed supplies input bias and capsule leakage; DC authority explicitly finite',
        'Q/Cfb then real inverted output',shared_output,
        'feedback thermal/excess noise, CMOS en times noise gain and in, output driver noise',
        'finite loop gain, DC leakage saturation and rail clipping','leakage times 1 GOhm exhausts swing',
        'DC at LEAK=1G then charge transfer/noise across C/leakage corners',
        'Capacitive feedback may flatten electrical charge conversion while a finite resistive reset prevents indefinite drift only within measured DC authority.'),['S05','S07','S16'])
    a.opamp('Uinput','mid','f','outp');a.resistor('Rfeedback','outp','f',1e9,high=True)
    a.capacitor('Cfeedback','outp','f',1e-10);a.resistor('Rrear','rear','g',1000)
    a.output('outp',buffer=False);a.finish()

    a=Attempt(5,'no_fet','BJT-only discrete charge-feedback input','concept_0007','charge','bipolar_capacitive_feedback',questions(
        'front displacement charge at a bipolar summing input','finite differential-pair loop; base shot noise remains',
        'fixed midrail pair and degenerated tail; 1 Mohm DC feedback supplies base current',
        'discrete differential error amplifier, 100 nF feedback and emitter followers',shared_output,
        'base-current shot noise, feedback resistor and collector/output noise; missing KF explicitly unknown',
        'differential pair curvature, finite loop gain, unequal follower bias','low reset resistance requires very large Cfb and loses sensitivity/SNR',
        'base current/feedback authority, pressure-referred shot noise and finite-loop response',
        'An entirely BJT audio/power path can perform charge feedback without a FET, but base-current noise and DC authority may dominate the LF budget.'),['S05','S07','S17'])
    a.resistor('Rreftop','rail','ref',10000);a.resistor('Rrefbottom','ref','g',10000);a.capacitor('Cref','ref','g',47e-6)
    a.device('Qinput','BC846B',['outa','f','e1'],'BC846B,215','bc846b_emitter_r1')
    a.device('Qreference','BC846B',['outb','ref','e2'],'BC846B,215','bc846b_emitter_r1')
    a.resistor('Remitter1','e1','tail',1000);a.resistor('Remitter2','e2','tail',1000)
    a.resistor('Rtail','tail','g',10000);a.resistor('Rcollector1','rail','outa',10000);a.resistor('Rcollector2','rail','outb',10000)
    a.resistor('Rfeedback','outa','f',1000000);a.capacitor('Cfeedback','outa','f',1e-7)
    a.device('Qoutp','BC846B',['rail','outa','outp'],'BC846B,215','bc846b_emitter_r1')
    a.device('Qoutn','BC846B',['rail','outb','outn'],'BC846B,215','bc846b_emitter_r1')
    a.resistor('Routloadp','outp','g',10000);a.resistor('Routloadn','outn','g',10000)
    a.resistor('Rrear','rear','g',1000);a.coupling();a.finish()

    a=Attempt(6,'floating','Floating carrier bridge mechanism control','concept_0019','carrier_capacitance','synchronous_demodulation_control',questions(
        'front/rear capacitance modulation of an anti-phase analog carrier','floating capacitor bridge; 100 pF fixed references; both input buffer loads explicit',
        'filtered DC backplate and midrail electrode returns; no physical safe RF/DC rating inferred',
        'bridge sidebands then synchronous product and two-pole RC low-pass',shared_output,
        'periodic device noise, oscillator AM/PM and mixer folding; ordinary DC noise is invalid',
        'bridge imbalance, product/filters, force/back-action absent from capsule model',
        'unimplemented oscillator/mixer power/noise and unvalidated periodic protocol',
        'carrier on/off pressure sidebands, demodulation phase, step refinement and analytic charge-control oracle',
        'A floating bridge should create pressure-dependent carrier sidebands; an ideal oscillator/multiplier can isolate this mechanism without qualifying a hardware architecture.'),['S09','S16'])
    a.meta.update(ideal_devices=True,analysis_domain='periodic_mechanism_control',carrier_protocol='deterministic_r1_noise_unimplemented')
    for key,value in [('CARRIER_HZ',100000),('CARRIER_PEAK',.2)]:
        a.meta['parameters'][key]=dict(default=value,range=[value/2,value*2],scale='linear',provenance='explicit unsourced oscillator control, not device rating')
    a.lines += ["Bcarrier excite pol V={CARRIER_PEAK*sin(2*PI*CARRIER_HZ*time)}", "Banti anti pol V={-CARRIER_PEAK*sin(2*PI*CARRIER_HZ*time)}"]
    a.capacitor('Cexcite','excite','b',1e-7)
    a.capacitor('Cbridgef','f','anti',1e-10);a.capacitor('Cbridger','rear','anti',1e-10)
    a.resistor('Rbias','f','mid',1e9,high=True);a.resistor('Rrearbias','rear','mid',1e9,high=True)
    a.opamp('Ufront','f','frontbuf','frontbuf');a.opamp('Urear','rear','rearbuf','rearbuf')
    a.lines.append("Bdemod demod mid V={(v(frontbuf,rearbuf))*2*sin(2*PI*CARRIER_HZ*time)}")
    a.resistor('Rfilter1','demod','lp1',1000);a.capacitor('Cfilter1','lp1','mid',1e-7)
    a.resistor('Rfilter2','lp1','audio',1000);a.capacitor('Cfilter2','audio','mid',1e-7)
    a.output('audio');a.finish()


if __name__=='__main__': main()
