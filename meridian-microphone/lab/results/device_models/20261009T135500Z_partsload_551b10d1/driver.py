from pathlib import Path
import sys,uuid,json
from datetime import datetime,timezone
root=Path('/home/leobareth/Dokumente/Hardware/audio-works/meridian-microphone/lab');sys.path[:0]=[str(root/'src'),str(root/'models/semiconductor')]
from meridian_lab.core import source_manifest,verify_spec_lock,write_json,read_yaml,environment_versions
from meridian_lab.device_models import index
from characterize import Experiment
plan=read_yaml(root/'research/parts_model_load_plan_001.yaml');verify_spec_lock();manifest=source_manifest()
folder=root/'results/device_models'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_partsload_'+uuid.uuid4().hex[:8]);folder.mkdir(exist_ok=False)
for rel in manifest:
 p=folder/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((root/rel).read_bytes())
exp=Experiment(folder,index(folder/'source/models'));results={}
for id_ in plan['models']:
 m=exp.models[id_];sub=m['subcircuit']
 if id_.startswith('lsk'):c=f'Vd d 0 5\nVg g 0 -.2\nJq d g 0 {sub}'
 elif id_.startswith('diotec'):c=f'Vc c 0 5\nVb b 0 .6\nXq c b 0 {sub}'
 else:
  supply,cm=(16,8) if id_.startswith('opa') else (5,1)
  c=f'Vp p 0 {supply}\nVn n 0 0\nVin in 0 {cm}\nXq in out p n out {sub}\nVm mid 0 {cm}\nRl out mid 10k\n.options gmin=1e-16'
 out=exp.execute(m,'load_only',c,'op\nwrite op.raw all',['op.raw']);results[id_]={'status':'loaded_scoped' if out else 'error','behavior_characterized':False,'performance_assigned':False}
write_json(folder/'results.json',{'schema_version':1,'experiment_id':folder.name,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'source_manifest':manifest,'source_unchanged':source_manifest()==manifest,'plan':plan,'results':results,'jobs':exp.jobs,'versions':environment_versions(),'eligible_for_production':False,'candidate_evaluations':0})
print(folder)
