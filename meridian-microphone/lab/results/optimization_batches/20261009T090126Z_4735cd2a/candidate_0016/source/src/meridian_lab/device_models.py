# SPDX-License-Identifier: GPL-3.0-or-later
"""Exact model resolution. Declarations confer provenance, never qualification."""
from pathlib import Path
import re
from .core import digest, read_yaml

def index(model_root):
    registry = read_yaml(Path(model_root) / 'semiconductor/registry.yaml')
    models = {}
    for device in registry['devices']:
        for model in device.get('models', []):
            if model['id'] in models:
                raise ValueError('Duplicate semiconductor model ID')
            models[model['id']] = dict(model, device_id=device['id'],
                                      manufacturer=device['manufacturer'])
    return models

def resolve(model_root, ids):
    available = index(model_root)
    output = []
    for id_ in ids:
        if id_ not in available:
            raise ValueError(f'Unknown registered semiconductor model {id_}')
        model = available[id_]
        if model.get('acquisition_status') != 'valid_spice':
            raise ValueError(f'Model {id_} has no valid acquired SPICE file')
        relative = Path(model['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Model path must remain within the model library')
        path = Path(model_root) / relative
        if not path.is_file() or digest(path) != model['sha256']:
            raise ValueError(f'Missing or changed vendor model {id_}; reacquire/audit, never silently update')
        text = path.read_text(errors='strict')
        if '<html' in text.lower() or not re.search(r'^\s*\.(model|subckt)\b',text,re.I|re.M):
            raise ValueError('Non-SPICE model content')
        if re.search(r'^\s*\.(include|inc|lib)\b',text,re.I|re.M):
            raise ValueError(f'Model {id_} has an external dependency; self-contained audited files required')
        # Preserve the vendor ancestor of an authored correction, including in failed
        # candidate jobs. A missing/cyclic ancestry must not look like vendor approval.
        lineage=[]; seen={id_}; parent=model.get('parent_model_id')
        while parent:
            if parent in seen or parent not in available:
                raise ValueError(f'Missing or cyclic model parent for {id_}')
            ancestor=available[parent];seen.add(parent)
            lineage.append({k:ancestor.get(k) for k in ('id','version','sha256','source_url','retrieved_date')})
            parent=ancestor.get('parent_model_id')
        output.append({**model, 'resolved_path':str(path),'model_lineage':lineage})
    return output

def candidate_models(model_root, meta, circuit):
    ids = meta.get('semiconductor_models', [])
    # External includes would escape the frozen manifest and exact-version contract.
    if re.search(r'^\s*\.(include|inc|lib)\b', circuit,re.I|re.M):
        raise ValueError('Candidate includes must use registered semiconductor_models declarations')
    models = resolve(model_root, ids)
    definitions = {}
    for model in models:
        text = Path(model['resolved_path']).read_text()
        scope = []
        for line in text.splitlines():
            if re.match(r'^\s*\.ends\b', line, re.I):
                if scope:
                    scope.pop()
                continue
            match = re.match(r'^\s*\.(model|subckt)\s+(\S+)', line, re.I)
            if not match:
                continue
            kind, name = match.groups()
            key = (kind.lower(), tuple(scope), name.lower())
            if key in definitions:
                raise ValueError(f'Duplicate SPICE definition {name} in {definitions[key]} and {model["id"]}; use one defining file')
            definitions[key] = model['id']
            if kind.lower() == 'subckt':
                scope.append(name.lower())
    return models, '\n'.join(f'.include "{m["resolved_path"]}"' for m in models)
