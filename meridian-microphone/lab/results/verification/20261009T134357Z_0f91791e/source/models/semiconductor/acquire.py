#!/usr/bin/env python3
"""Acquire public evidence into an unredistributed local cache; no login/terms acceptance."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import zipfile
import io
from datetime import datetime, timezone
import yaml

BASE = Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def audit_local_derivatives(entries, root):
    """Check both locally authored bytes and the immutable source they derive from."""
    observations=[]
    for entry in entries:
        row={'id':entry['id'],'action':'local_derivative_audit','operation':entry['operation']}
        try:
            for path_key, hash_key in [('path','sha256'),('ancestor_path','ancestor_sha256')]:
                relative=Path(entry[path_key])
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('Derivative evidence path escapes laboratory')
                path=(root/relative).resolve()
                if not path.is_relative_to(root.resolve()):
                    raise ValueError('Derivative evidence symlink escapes laboratory')
                if not path.is_file() or sha(path.read_bytes())!=entry[hash_key]:
                    raise ValueError('Missing or changed '+path_key)
            row.update(status='ok',sha256=entry['sha256'],ancestor_sha256=entry['ancestor_sha256'])
        except (ValueError,OSError) as exc:
            row.update(status='error',diagnostic=str(exc))
        observations.append(row)
    return observations

def acquire(manifest, selected=None):
    if selected and not set(selected)<=set(e['id'] for e in manifest['downloads']+manifest.get('local_derivatives',[])):
        raise ValueError('Unknown acquisition ID; no downloads performed')
    observations = []
    for entry in manifest['downloads']:
        if selected and entry['id'] not in selected:
            continue
        destination = BASE / entry['target']
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            data = destination.read_bytes()
            action = 'existing_cache'
        else:
            # A public download, never an order, form submission or licence acceptance.
            result = subprocess.run(['curl', '-A', 'Mozilla/5.0', '-L', '--fail',
                                     '--max-time', '45', entry['url']], capture_output=True)
            if result.returncode:
                observations.append({'id':entry['id'], 'status':'error',
                                     'diagnostic':result.stderr.decode(errors='replace')})
                continue
            data = result.stdout
            action = 'download'
        expected = entry.get('sha256')
        if expected and sha(data) != expected:
            # Changed vendor bytes remain evidence, never a silent library update.
            failed=BASE/'vendor/acquisition/responses'/f'{entry["id"]}_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")}_{sha(data)}.bin'
            failed.parent.mkdir(parents=True,exist_ok=True);failed.write_bytes(data)
            observations.append({'id':entry['id'], 'status':'hash_mismatch',
                                 'url':entry['url'],'observed_sha256':sha(data),'preserved_response':str(failed.relative_to(BASE))})
            continue
        if not destination.exists():
            destination.write_bytes(data)
        # Keep bad response bytes as failure evidence, but never qualify HTML as SPICE.
        if entry['target'].endswith('.lib') and (b'<html' in data[:500].lower() or b'.subckt' not in data.lower() and b'.model' not in data.lower()):
            observations.append({'id':entry['id'], 'status':'invalid_model_content',
                                 'url':entry['url'], 'target':entry['target'],
                                 'sha256':sha(data), 'diagnostic':'No SPICE definition; possible web challenge'})
            continue
        if entry['target'].endswith('.pdf') and not data.startswith(b'%PDF'):
            observations.append({'id':entry['id'], 'status':'invalid_pdf_content',
                                 'sha256':sha(data)})
            continue
        files = {}
        for member, target in entry.get('members', {}).items():
            content = zipfile.ZipFile(io.BytesIO(data)).read(member)
            output = BASE / target
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists() and output.read_bytes() != content:
                raise ValueError(f'Refusing to replace changed evidence: {output}')
            output.write_bytes(content)
            files[target] = sha(content)
        observations.append({'id':entry['id'], 'status':'ok', 'action':action,
                             'url':entry['url'], 'target':entry['target'],
                             'sha256':sha(data), 'files':files})
    derivatives=[e for e in manifest.get('local_derivatives',[]) if not selected or e['id'] in selected]
    observations.extend(audit_local_derivatives(derivatives,BASE.parents[1]))
    folder = BASE / 'vendor' / 'acquisition'
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    output = folder / (now.strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    output.write_text(json.dumps({'timestamp_utc':now.isoformat(),
                                 'observations':observations}, indent=2) + '\n')
    print(json.dumps({'record':str(output), 'observations':observations}, indent=2))
    return 0 if all(r['status']=='ok' for r in observations) else 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', nargs='+')
    args = parser.parse_args()
    raise SystemExit(acquire(yaml.safe_load((BASE/'acquisition.yaml').read_text()),args.only))
