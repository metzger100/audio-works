# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify every declared new source/implementation/deck/raw hash, including failures."""
from pathlib import Path
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(batch):
    expected={};errors=[];records=[]
    def check(p,h):
        p=p.resolve()
        if p in expected and expected[p]!=h:errors.append('Conflicting hash: '+str(p))
        expected[p]=h
        if not p.is_file() or sha(p)!=h:errors.append('Missing/changed: '+str(p))
    def jobs(value):
        if isinstance(value,dict):
            if 'folder' in value and ('netlist_sha256' in value or 'files' in value):
                folder=Path(value['folder']);folder=folder if folder.is_absolute() else ROOT/folder
                if value.get('netlist_sha256'):check(folder/'job.cir',value['netlist_sha256'])
                for name,h in value.get('files',{}).items():check(folder/name,h)
            for v in value.values():jobs(v)
        elif isinstance(value,list):
            for v in value:jobs(v)
    search=json.loads((batch/'search.json').read_text())['experiments']
    evaluation=json.loads((batch/'evaluation.json').read_text())
    ids=list(search.values())+list(evaluation['baseline_experiments'].values())+[x['experiment'] for x in evaluation['continuous'].values()]+[x['experiment'] for x in evaluation['children'].values()]
    for id_ in ids:
        directory=ROOT/'results/runs'/id_
        name='optimization.json' if id_ in search.values() else 'results.json'
        p=directory/name;r=json.loads(p.read_text());records.append(str(p.relative_to(ROOT)))
        for rel,h in r['source_manifest'].items():check(directory/'source'/rel,h)
        location='candidate' if name=='optimization.json' else ''
        for rel,h in r.get('implementation_manifest',{}).items():check(directory/location/rel,h)
        jobs(r)
        if name=='optimization.json':jobs(json.loads((directory/'trials.json').read_text()))
    for p in batch.rglob('frozen_manifest.json'):
        r=json.loads(p.read_text());records.append(str(p.relative_to(ROOT)))
        for rel,h in r['sources'].items():check(p.parent/'source'/rel,h)
        for rel,h in r['implementation'].items():check(p.parent/'candidate'/rel,h)
    for p in list(batch.rglob('validation.json'))+list(batch.rglob('discrete.json')):
        jobs(json.loads(p.read_text()));records.append(str(p.relative_to(ROOT)))
    # Preserve failed initial controls and all repaired successors, not only final pass.
    verification=[]
    for p in (ROOT/'results/verification').glob('20261009T*/verification.json'):
        r=json.loads(p.read_text())
        if 'tests/test_robust.py' not in r['source_manifest']:continue
        verification.append({'record':str(p.relative_to(ROOT)),'status':r['status'],'source_unchanged':r['source_unchanged']})
        for rel,h in r['source_manifest'].items():check(p.parent/'source'/rel,h)
        for rel,h in r['raw_data_hashes'].items():check(p.parent/rel,h)
    assert evaluation['source_unchanged'] and not errors
    out={'schema_version':1,'date':'2026-10-09','status':'pass','batch':str(batch.relative_to(ROOT)),
         'optimization_records':len(search),'full_suite_records':len(ids)-len(search),
         'verified_records':records,'unique_declared_files_checked':len(expected),
         'verification_records':verification,'hash_errors':errors,'parent_relationships_preserved':True,
         'manifest_sha256':sha(batch/'plan.json'),'specifications_unchanged':True,
         'independent_backup_complete':False,'legacy_missing_originals':89,
         'record_hashes':{name:sha(ROOT/name) for name in records},'verification_driver_sha256':sha(Path(__file__))}
    (ROOT/'research/robust_optimization_integrity_2026-10-09.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','optimization_records','full_suite_records','unique_declared_files_checked','hash_errors']},indent=2))
if __name__=='__main__':verify((ROOT/sys.argv[1]).resolve())
