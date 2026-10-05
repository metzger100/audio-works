from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from dataclasses import dataclass

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC_FILES = [ROOT / 'spec' / n for n in ('microphone_spec.yaml', 'capsule_model.yaml', 'design_constraints.yaml', 'scoring.yaml')]


def read_yaml(path):
    return yaml.safe_load(Path(path).read_text())


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def display_path(path):
    path = Path(path)
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_manifest():
    files = []
    for folder in ['spec', 'models', 'src', 'tests', 'optimization', 'search']:
        files.extend(p for p in (ROOT / folder).rglob('*') if p.suffix in {'.yaml', '.cir', '.py'})
    files.extend([ROOT / 'requirements.txt', ROOT / 'tools/ngspice-run'])
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(files) if p.is_file()}


def spec_digest():
    return hashlib.sha256(''.join(digest(p) for p in SPEC_FILES).encode()).hexdigest()


def verify_spec_lock():
    expected = read_yaml(ROOT / 'spec/lock.yaml')['sha256']
    if spec_digest() != expected:
        raise ValueError('Specification changed. Create a documented specification amendment; do not silently relax tests.')


class SimulationError(RuntimeError):
    pass


@dataclass
class Raw:
    vectors: dict[str, np.ndarray]
    plot: str

    def __getitem__(self, key):
        try:
            return self.vectors[key.lower()]
        except KeyError as exc:
            raise SimulationError(f'Missing required vector {key}; never treated as a pass') from exc

    def voltage(self, positive, negative='0'):
        a = self[f'v({positive})'] if positive != '0' else 0
        b = self[f'v({negative})'] if negative != '0' else 0
        return a - b


def parse_raw(path):
    lines = Path(path).read_text().splitlines()
    headers = {}
    try:
        iv = lines.index('Variables:')
        it = lines.index('Values:')
        for line in lines[:iv]:
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k] = v.strip()
        names = [line.split()[1].lower() for line in lines[iv + 1:it]]
        nvar, npoint = int(headers['No. Variables']), int(headers['No. Points'])
        if len(names) != nvar or npoint < 1:
            raise ValueError('Invalid raw dimensions')
        is_complex = 'complex' in headers['Flags']
        values = []
        indexes = []
        for line in lines[it + 1:]:
            if not line.strip():
                continue
            fields = line.split()
            if len(values) % nvar == 0:
                if len(fields) != 2:
                    raise ValueError('Missing raw point index')
                indexes.append(int(fields[0]))
                token = fields[1]
            else:
                if len(fields) != 1:
                    raise ValueError('Invalid raw vector entry')
                token = fields[0]
            if is_complex:
                real, imag = token.split(',')
                values.append(complex(float(real), float(imag)))
            else:
                values.append(float(token))
        if indexes != list(range(npoint)) or len(values) != nvar * npoint:
            raise ValueError('Truncated/nonsequential raw data')
        data = np.array(values).reshape(npoint, nvar)
        if not np.isfinite(data).all():
            raise ValueError('Nonfinite raw data')
        if names[0] in {'time', 'frequency'} and npoint > 1:
            if not np.all(np.diff(data[:, 0].real) > 0):
                raise ValueError('Nonmonotonic scale')
        return Raw(dict(zip(names, data.T)), headers['Plotname'])
    except (ValueError, KeyError, IndexError) as exc:
        raise SimulationError(f'Invalid simulator output {path}: {exc}') from exc


def defaults():
    c = read_yaml(ROOT / 'spec/capsule_model.yaml')['parameters']
    d = read_yaml(ROOT / 'spec/design_constraints.yaml')
    e = d['environment']
    return {
        'CF': c['front_capacitance_f']['nominal'], 'CR': c['rear_capacitance_f']['nominal'],
        'SREF': c['sensitivity_at_reference_v_per_pa']['nominal'],
        'VREF': c['reference_polarization_v']['nominal'], 'LEAK': c['leakage_resistance_ohm']['nominal'],
        'PAR': c['parasitic_to_case_f']['nominal'], 'CROSS': c['front_rear_stray_f']['nominal'],
        'LIN': 0, 'POLDC': 60, 'VS': d['power']['supply_v']['nominal'], 'FT': 0, 'FM': 0,
        'LEN': e['cable_length_m']['nominal'], 'RW': e['cable_resistance_ohm_per_m_per_conductor']['nominal'],
        'RS': e['shield_resistance_ohm_per_m']['nominal'], 'CD': e['cable_direct_capacitance_f_per_m']['nominal'],
        'CS': e['cable_each_leg_to_shield_f_per_m']['nominal'], 'ZIN': e['preamp_differential_load_ohm']['nominal'],
        'ZM': 0, 'CC': e['preamp_coupling_f_per_leg']['nominal'], 'CP': e['preamp_input_capacitance_f_per_leg']['nominal'],
        'TEMP': e['temperature_c']['nominal'], 'START': 0, 'CMAC': 0,
        'PRESSURE_AC': 1, 'PRESSURE_PEAK': 0, 'FREQ': 1000,
    }


class Simulator:
    def __init__(self, candidate, directory, overrides=None):
        self.candidate = ROOT / 'candidates' / candidate
        self.meta = read_yaml(self.candidate / 'topology.yaml')
        if self.meta['id'] != candidate:
            raise ValueError('Candidate ID mismatch')
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.params = defaults()
        self.params.update({k: v['default'] for k, v in self.meta.get('parameters', {}).items()})
        for k, v in (overrides or {}).items():
            if k not in self.params or not np.isfinite(v):
                raise ValueError(f'Unknown or nonfinite parameter {k}')
            self.params[k] = float(v)
        self.count = 0
        self.jobs = []
        self.model_root = ROOT / 'models'

    def execute(self, label, commands, files, overrides=None, extra='', environment_only=False, capsule_only=False):
        verify_spec_lock()
        p = dict(self.params)
        for k, v in (overrides or {}).items():
            if k not in p or not np.isfinite(v):
                raise ValueError(f'Unknown or nonfinite parameter {k}')
            p[k] = float(v)
        circuit = (self.candidate / 'circuit.cir').read_text()
        if re.search(r'^\s*\.(control|end|options|temp|param|ac|tran|noise|op)\b', circuit, re.I | re.M):
            raise ValueError('Candidate must contain a DUT subcircuit, not simulation/specification overrides')
        self.count += 1
        folder = self.directory / f'{self.count:04d}_{label}'
        folder.mkdir(exist_ok=False)
        defs = '\n'.join(f'.param {k}={v:.16g}' for k, v in p.items() if k != 'TEMP')
        body = f'''Meridian research {label}
{defs}
.temp {p['TEMP']}
.options reltol=1e-6 method=gear maxord=2 abstol=1e-15 vntol=1e-9 gmin=1e-15
.include "{self.model_root / 'capsule/flat_k47.cir'}"
.include "{self.model_root / 'environment/p48.cir'}"
VP pressure 0 DC 0 AC {{PRESSURE_AC}} SIN(0 {{PRESSURE_PEAK}} {{FREQ}})
VPR pressure_r 0 DC 0 AC 0
'''
        if not capsule_only:
            body += 'Xenv p n mic_g pp pn cm P48 VS={VS} FT={FT} FM={FM} LEN={LEN} RW={RW} RS={RS} CD={CD} CS={CS} ZIN={ZIN} ZM={ZM} CC={CC} CP={CP} START={START} CMAC={CMAC}\n'
        if not environment_only:
            body += 'Xcap f b rear pressure pressure_r mic_g FLAT_K47 CF={CF} CR={CR} SREF={SREF} VREF={VREF} LEAK={LEAK} PAR={PAR} CROSS={CROSS} LIN={LIN} POLDC={POLDC}\n'
            if capsule_only:
                body += 'Vg mic_g 0 0\nVbias b mic_g {POLDC}\nRtest f mic_g {BIAS_R}\nCtest f mic_g {INPUT_C}\nRrear rear mic_g 1k\n'
            else:
                body += circuit + '\nXdut f b rear p n mic_g rail DUT\n'
        body += extra + '\n.control\nset filetype=ascii\nset numdgt=16\n' + commands + '\nquit\n.endc\n.end\n'
        (folder / 'job.cir').write_text(body)
        write_json(folder / 'parameters.json', p)
        env = os.environ.copy()
        env['LC_ALL'] = 'C'
        executable = os.environ.get('MERIDIAN_NGSPICE', str(ROOT / 'tools/ngspice-run'))
        try:
            run = subprocess.run([executable, '-n', '-b', 'job.cir'], cwd=folder, env=env, capture_output=True, text=True, timeout=60)
        except (subprocess.TimeoutExpired, OSError) as exc:
            (folder / 'simulator.log').write_text(str(exc))
            self.jobs.append({'folder': display_path(folder), 'status': 'error', 'reason': str(exc)})
            raise SimulationError(str(exc)) from exc
        log = run.stdout + '\n' + run.stderr
        (folder / 'simulator.log').write_text(log)
        bad = re.search(r'(?im)^\s*(error\b|fatal\b|warning\b|.*timestep too small|.*singular matrix|.*convergence failed|.*analysis.*aborted)', log)
        if run.returncode or bad:
            reason = f'ngspice exit {run.returncode}: {bad.group(0) if bad else log[-500:]}'
            self.jobs.append({'folder': display_path(folder), 'status': 'error', 'reason': reason})
            raise SimulationError(reason)
        try:
            output = {name: parse_raw(folder / name) for name in files}
        except (OSError, SimulationError) as exc:
            self.jobs.append({'folder': display_path(folder), 'status': 'error', 'reason': str(exc)})
            raise SimulationError(f'{folder}: missing/invalid analysis output: {exc}') from exc
        self.jobs.append({'folder': display_path(folder), 'status': 'ok', 'netlist_sha256': digest(folder / 'job.cir'), 'files': {n: digest(folder / n) for n in files}})
        return output

    def op_ac(self, label='op_ac', overrides=None):
        return self.execute(label, 'op\nwrite op.raw all\nac dec 32 1 10Meg\nwrite ac.raw all', ['op.raw', 'ac.raw'], overrides)

    def noise(self, overrides=None):
        return self.execute('noise', 'noise v(pp,pn) VP dec 64 20 20k 1\nsetplot noise1\nwrite noise.raw all', ['noise.raw'], overrides)['noise.raw']

    def transient(self, frequency, pressure_peak, samples=256, cycles=40, settling=1.0, overrides=None):
        duration = settling + cycles / frequency
        step = 1 / frequency / samples
        return self.execute('distortion', f'tran {step:.16g} {duration:.16g} {settling:.16g} {step:.16g}\nwrite tran.raw all', ['tran.raw'], {'FREQ': frequency, 'PRESSURE_PEAK': pressure_peak, **(overrides or {})})['tran.raw']


def environment_versions():
    import scipy, pandas, matplotlib
    executable = os.environ.get('MERIDIAN_NGSPICE', str(ROOT / 'tools/ngspice-run'))
    return {'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__, 'pandas': pandas.__version__, 'matplotlib': matplotlib.__version__, 'yaml': yaml.__version__, 'ngspice': subprocess.run([executable, '--version'], capture_output=True, text=True).stdout.strip()}
