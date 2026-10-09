# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
import sys,yaml,json
from collections import Counter
sys.path.insert(0,str(Path('search').resolve()))
from first_batch_children import clone,finish
from meridian_lab.core import ROOT,read_yaml
from copy import deepcopy
a=clone('candidate_0007',15,'Conventional JFET reference with filtered backplate')
a.capacitor('Cbackfilter','b','g',1e-7)
a.meta['questions']['hypothesis']='If the unfiltered final 1Mohm backplate feed dominates the conventional reference noise, an actual 100nF backplate bypass should lower that contribution without selecting a JFET or changing voltage conversion.'
a.meta['questions']['quickest_falsification']='Full stationary-noise contribution comparison with parent; preserved DC and transfer, then all supported tests'
finish(a,'Retain JFE source degeneration, all bias/output devices and nominal values. Add one ordinary 100nF 100V PET capacitor after the final backplate resistor, testing its observed dominant Johnson-noise path. No trimming or device selection; rerun full suite.')
f=ROOT/'candidates'/a.id
(f/'realization.py').write_bytes(Path('/tmp/meridian_reference_child.py').read_bytes())
bom=read_yaml(f/'bom.yaml');reg=read_yaml(ROOT/'research/procurement/architecture_parts_2026-10-09.yaml')['parts']
for p in bom['physical_parts']:
 r=reg[p['part_id']];p.update(technology=r['technology'],package=r['package'],ratings=r['ratings'],source_record=f"{bom['procurement_register']}#parts/{p['part_id']}",source_date='2026-10-09',manufacturer_document=r['manufacturer_document'])
qty=Counter()
for p in bom['physical_parts']:qty[p['part_id']]+=p['quantity']
group=[];subtotal=0;unpriced=[]
for mpn,q in qty.items():
 r=reg[mpn];v=r['unit_price_net_eur_observed']
 if v is None:unpriced.append(dict(mpn=mpn,quantity=q))
 else:subtotal+=q*v
 group.append(dict(exact_mpn=mpn,installed_quantity=q,purchase_quantity_scenario=q if r['moq_observed']==1 else None,unavoidable_pack_excess_scenario=0 if r['moq_observed']==1 else None,moq=r['moq_observed'],retail_pack_size=r['retail_pack_size_observed'],factory_pack_not_ordered=r['factory_pack'],seller=r['seller'],unit_price_net_eur_observed=v,extended_net_eur_scenario=q*v if v is not None else None))
bom['quantity_summary']=group;bom['electronics_cost'].update(priced_items_net_eur_scenario=round(subtotal,6),unpriced_items=unpriced,priced_items_vat_inclusive_eur_scenario=round(subtotal*1.19,6))
(f/'bom.yaml').write_text(yaml.safe_dump(bom,sort_keys=False))
print(a.id)
