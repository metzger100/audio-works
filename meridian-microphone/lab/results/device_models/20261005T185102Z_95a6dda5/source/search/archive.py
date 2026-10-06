"""Rebuild the derived archive from immutable full experiment records."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from meridian_lab.core import ROOT, write_json
from meridian_lab.archive import update

if __name__=='__main__':
    # Run only while evaluators are idle. Original results are never modified.
    write_json(ROOT/'results/archive.json',{'schema_version':1,'experiments':[],'niches':{},'family_counts':{},'champions':{}})
    records=sorted((ROOT/'results/runs').glob('*/results.json'))
    for path in records:
        update(json.loads(path.read_text()))
    print(f'Rebuilt from {len(records)} preserved records.')
