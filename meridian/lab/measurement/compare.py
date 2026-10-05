"""Import a physical interchange record and compare like-named scalar metrics.

No source record, model, threshold or qualification state is modified.
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from meridian_lab.core import ROOT, write_json, digest

def compare(measured, simulated):
    required={'schema_version','candidate_id','backend','spec_sha256','checks','provenance'}
    if not required.issubset(measured) or measured['schema_version']!=1 or measured['backend']!='physical_measurement':
        raise ValueError('Invalid physical measurement interchange header')
    if measured['candidate_id']!=simulated['candidate_id'] or measured['spec_sha256']!=simulated['spec_sha256']:
        raise ValueError('Candidate and specification identities must match')
    provenance={'timestamp','instrument_or_simulator','configuration','raw_data_hashes'}
    if not provenance.issubset(measured['provenance']):
        raise ValueError('Missing calibration/configuration/raw provenance')
    delta={}
    for name,check in measured['checks'].items():
        if check.get('status') not in {'pass','fail','error','incomplete'} or not isinstance(check.get('metrics'),dict):
            raise ValueError('Invalid physical check status/metrics')
        before=simulated['checks'].get(name,{}).get('metrics',{})
        delta[name]={k:v-before[k] for k,v in check['metrics'].items() if type(v) in {int,float} and type(before.get(k)) in {int,float}}
    return {'schema_version':1,'candidate_id':measured['candidate_id'],'scalar_deltas_measurement_minus_simulation':delta,
            'configuration_must_be_reviewed_for_equivalence':True,'automatic_model_or_qualification_change':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('measurement',type=Path); p.add_argument('simulation',type=Path); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    result=compare(json.loads(a.measurement.read_text()),json.loads(a.simulation.read_text()))
    result['source_sha256']={'measurement':digest(a.measurement),'simulation':digest(a.simulation)}
    write_json(a.output,result); print(a.output)
