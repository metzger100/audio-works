# SPDX-License-Identifier: GPL-3.0-or-later
"""Register sourced-passive children without modifying evaluated parents."""
from first_batch_children import clone, finish, remove


def c0g_realization(a):
    for part in a.bom:
        if part['part_id']!='C0603C101J1GACTU': continue
        part['part_id']='CC0603JRNPO0BN101'
        name=part['reference']
        # Manufacturer: 100pF +/-5%, IR >=10Gohm, DF<=0.1%.
        # The DF-derived series R is a 1MHz worst-DF control, NOT a loss spectrum.
        for i,line in enumerate(a.lines):
            fields=line.split()
            if fields and fields[0]==name:
                left,right=fields[1:3]; internal=name.lower()+'_loss'
                fields[1]=internal;a.lines[i]=' '.join(fields)
                a.resistor('R'+name+'loss',left,internal,1.5915494309,parasitic=True)
                a.resistor('R'+name+'insulation',left,right,1e10,parasitic=True)
                key=name.upper()+'_VALUE'
                a.meta['parameters'][key]['provenance']='BOM CC0603JRNPO0BN101; 100pF 5%, 100V C0G; worst-DF/IR controls separate'
                a.meta['population'][key]['provenance']=a.meta['parameters'][key]['provenance']
                # Broad sensitivity controls retain unmeasured frequency dependence.
                for suffix,value,range_ in [('loss',1.5915494309,[0.15915494309,15.915494309]),('insulation',1e10,[1e10,1e14])]:
                    p=('R'+name+suffix).upper()+'_VALUE'
                    a.meta['parameters'][p].update(range=range_,provenance='Yageo primary DF/IR anchor; decade loss stress / IR lower-bound-to-1e14 scenario, not a production distribution')
                    a.meta['population'][p].update(range=range_,provenance=a.meta['parameters'][p]['provenance'])
                break


def main():
    a=clone('candidate_0005',12,'BJT-only charge input with obtainable 10k parts')
    remove(a,['Rfeedback'])
    a.resistor('Rfeedbacka','outa','f',1e6)
    a.resistor('Rfeedbackb','outa','f',1e6)
    a.meta['questions']['dc_bias']='Two parallel ordinary 1Mohm feedback resistors (500kohm nominal) increase DC base-current authority; fixed discrete pair/tail, no trimming'
    finish(a,'Specify obtainable AC-series 10k parts and test a 500kohm DC feedback branch realized as two parallel 1Mohm resistors. Lower reset resistance trades base-current authority against charge gain/noise; no selection or excess-noise equivalence. Preserve BJT-only mechanism and rerun complete supported suite.')
    for parent,number in [('candidate_0009',13),('candidate_0011',14)]:
        a=clone(parent,number,'100pF C0G realization with leakage/loss controls')
        c0g_realization(a)
        finish(a,'Replace backordered KEMET 100pF by documented Yageo CC0603JRNPO0BN101; include explicit insulation and loss sensitivity controls. These do not validate a complete temperature/frequency loss model or the ideal carrier hardware. Rerun all supported checks.')


if __name__=='__main__':main()
