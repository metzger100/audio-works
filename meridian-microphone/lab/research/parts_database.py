#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Search the compatible parts evidence matrix without promoting unknown states."""
from pathlib import Path
import argparse,json,hashlib,math
import yaml
DEFAULT=Path(__file__).with_name('parts_database_expansion_002.yaml')

def records(database):
    for kind,key in [('semiconductor','parts'),('passive','passives'),('lead','research_leads')]:
        for row in database.get(key,[]):
            yield {'record_kind':kind,**row}

def search(database,query='',role=None,state=None):
    query=query.casefold();found=[]
    for row in records(database):
        if role and role not in row.get('roles',[]):continue
        if state and row.get('states',{}).get(state) is not True:continue
        if query and query not in json.dumps(row,ensure_ascii=False).casefold():continue
        found.append(row)
    return found

def counts(database):
    parts=database.get('parts',[])
    models=[m for p in parts for m in p.get('models',[]) if m.get('acquisition')=='valid_spice']
    return dict(exact_semiconductor_devices=len(parts),valid_spice_files=len(models),
                unique_valid_spice_hashes=len({m['sha256'] for m in models}),
                semiconductor_devices_with_model=sum(any(m.get('acquisition')=='valid_spice' for m in p.get('models',[])) for p in parts),
                exact_passive_entries=len(database.get('passives',[])),
                documentary_leads=len(database.get('research_leads',[])),physical_owned_stock=None)

def audit(database):
    errors=[];seen=set()
    roles={r['id'] for r in database.get('role_gap_matrix',[])}
    for row in records(database):
        key=(row['record_kind'],row.get('device_id',row.get('exact_mpn',row.get('mpn'))))
        if key[1] is None:errors.append('Missing exact record identity')
        if key in seen:errors.append(f'Duplicate identity {key}')
        seen.add(key)
        states=row.get('states',{})
        for state in ['investigated','acquired','characterized','candidate_combination_qualified']:
            if state in states and not isinstance(states[state],bool):errors.append(f'{key}: {state} must be independent boolean')
        if states.get('characterized') and not states.get('acquired'):errors.append(f'{key}: characterized without acquired evidence')
        if states.get('candidate_combination_qualified'):
            if not row.get('candidate_qualification_record'):errors.append(f'{key}: missing candidate qualification record')
            if row.get('sourcing',{}).get('implementation_qualified') is not True:errors.append(f'{key}: sourcing gate unresolved')
            if row.get('patent_screen',{}).get('candidate_gate')!='resolved':errors.append(f'{key}: patent gate unresolved')
        for role in row.get('roles',[]):
            if role not in roles:errors.append(f'{key}: unknown role {role}')
        for m in row.get('models',[]):
            if m.get('acquisition')=='valid_spice' and (not m.get('path') or len(m.get('sha256',''))!=64):errors.append(f'{key}: missing model path/hash')
        for behavior in states.get('behavior_validated',[]):
            if isinstance(behavior,dict) and behavior.get('status')=='pass' and not behavior.get('condition'):
                # Numerical refinement is distinct from physical evidence.
                if behavior.get('evidence') not in ['numerical_refinement','numerical_oracle']:errors.append(f'{key}: passing behavior lacks conditions')
    if database.get('measurement_state')!='No capsule or owned-stock measurements evidenced':errors.append('Measurement absence changed without an evidenced record')
    return errors

def audit_registry(database,registry):
    """Detect drift between the searchable view and compatible canonical registry."""
    errors=[];view={p['device_id']:p for p in database['parts']}
    canonical={d['id']:d for d in registry['devices']}
    if set(view)!=set(canonical):errors.append('Matrix/canonical device identities differ')
    for did in set(view)&set(canonical):
        if view[did]['exact_mpn']!=canonical[did]['exact_variant']:errors.append(f'{did}: exact identity differs')
        expected={m['id']:m['sha256'] for m in canonical[did].get('models',[])}
        actual={m['id']:m['sha256'] for m in view[did].get('models',[])}
        if expected!=actual:errors.append(f'{did}: model identity/hash differs')
        if view[did]['states']!=canonical[did]['evidence_states']:errors.append(f'{did}: independent evidence states differ')
    if database.get('counts') and database['counts']!=counts(database):errors.append('Stored counts differ from records')
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query',nargs='?',default='')
    parser.add_argument('--database',type=Path,default=DEFAULT)
    parser.add_argument('--role')
    parser.add_argument('--state',choices=['investigated','acquired','characterized'])
    parser.add_argument('--audit',action='store_true')
    parser.add_argument('--counts',action='store_true')
    parser.add_argument('--registry',type=Path,default=DEFAULT.parent.parent/'models/semiconductor/registry.yaml')
    args=parser.parse_args();database=yaml.safe_load(args.database.read_text())
    if args.audit:
        errors=audit(database)+audit_registry(database,yaml.safe_load(args.registry.read_text()))
        print(json.dumps(dict(status='fail' if errors else 'pass',errors=errors,counts=counts(database)),indent=2));return bool(errors)
    print(json.dumps(counts(database) if args.counts else search(database,args.query,args.role,args.state),indent=2,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
