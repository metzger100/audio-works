"""Register a reviewed structural child; never overwrite a parent or its failures."""
import argparse, re, sys
from pathlib import Path
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from meridian_lab.core import ROOT, read_yaml, verify_spec_lock
from meridian_lab.archive import graph_features

def register(parent, id_, circuit_path, metadata_path, hypothesis, structural_changes):
    verify_spec_lock()
    if not re.fullmatch(r'candidate_[0-9]{4,}',id_):
        raise ValueError('Use a new candidate_NNNN identity')
    folder=ROOT/'candidates'/id_
    if folder.exists():
        raise ValueError('Never overwrite an existing architectural experiment')
    circuit=Path(circuit_path).read_text(); metadata=read_yaml(metadata_path)
    if metadata['family'] not in {f['id'] for f in read_yaml(ROOT/'search/families.yaml')['families']}:
        raise ValueError('Unknown persistent architectural family')
    if not re.search(r'(?im)^\.subckt\s+DUT\s+f\s+b\s+rear\s+p\s+n\s+g\s+rail\b',circuit):
        raise ValueError('Missing standard DUT port contract')
    if re.search(r'(?im)^\s*\.(control|end|options|temp|param|op|ac|tran|noise)\b',circuit):
        raise ValueError('Circuit contains unauthorized analysis/spec overrides')
    old=graph_features(ROOT/'candidates'/parent/'circuit.cir'); new=graph_features(circuit_path)
    if old['graph_signature']==new['graph_signature'] and metadata['niche']==read_yaml(ROOT/'candidates'/parent/'topology.yaml')['niche']:
        raise ValueError('No recorded architectural change; use numerical optimization for values')
    metadata.update(id=id_,kind='research_candidate',parents=[parent],hypothesis=hypothesis,structural_changes=structural_changes,
                    eligible=False,qualification_evidence=[],state='engineering_ready')
    folder.mkdir()
    (folder/'circuit.cir').write_text(circuit)
    (folder/'topology.yaml').write_text(yaml.safe_dump(metadata,sort_keys=False))
    (folder/'hypothesis.md').write_text('# Structural hypothesis\n\n'+hypothesis+'\n\nChange: '+structural_changes+'\n')
    (folder/'notes.md').write_text('Unsimulated structural child. SPICE and the full suite decide viability.\n')
    return folder

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('parent'); p.add_argument('id'); p.add_argument('--circuit',required=True,type=Path); p.add_argument('--metadata',required=True,type=Path); p.add_argument('--hypothesis',required=True); p.add_argument('--changes',required=True); a=p.parse_args()
    print(register(a.parent,a.id,a.circuit,a.metadata,a.hypothesis,a.changes))
