# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison 001 from immutable records and original local waveforms.

No simulator, candidate, specification, archive or original result is modified.
Run from lab: .venv/bin/python research/compare_architectures.py
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from meridian_lab.core import parse_raw
from meridian_lab.metrics import at_frequency, device_noise_totals, integrate_asd

OUT = ROOT / 'results/reports/architecture_comparison_001'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def table(path, rows, fields=None):
    fields = fields or list(rows[0])
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def noise_group(vector):
    """Classify one device root, never its already-included noise children."""
    if '.xenv.' in vector:
        return 'environment (excluded)'
    if '.xcap.' in vector:
        return 'capsule Johnson surrogate (excluded)'
    if '.xdut.' not in vector:
        raise ValueError('Unidentified noise scope: ' + vector)
    ref = vector.split('.xdut.', 1)[1].split('.')[0]
    if ref.startswith(('xqout', 'xqinvert', 'rout', 'rinv', 'rcout')):
        return 'output drive and coupling'
    if ref.startswith(('rpolar', 'rback')):
        return 'polarization network'
    if ref.startswith(('xqreg', 'rharvest', 'rreg', 'rmid')):
        return 'power and midpoint'
    if ref.startswith(('xqservo', 'rservo')):
        return 'servo'
    if ref.startswith(('xjinput', 'xqinput', 'xqreference', 'xuinput')):
        return 'input semiconductor'
    # Explicit remaining input/reference/reset/degeneration resistors.
    if ref.startswith(('rbias', 'rgate', 'rrear', 'rsource', 'rsignal', 'rref',
                       'remitter', 'rtail', 'rcollector', 'rfeedback', 'rcfeedback')):
        return 'input bias, reset and degeneration'
    raise ValueError('Unclassified DUT noise root: ' + vector)


def verify_partition(frequency, totals, total):
    groups = defaultdict(list)
    for name in totals:
        groups[noise_group(name)].append(name)
    asd = {g: np.sqrt(sum((totals[k] ** 2 for k in names), np.zeros_like(frequency)))
           for g, names in groups.items()}
    reconstructed = np.sqrt(sum((v ** 2 for v in asd.values()), np.zeros_like(frequency)))
    closure = float(np.max(np.abs(reconstructed - total) / np.maximum(total, 1e-30)))
    if closure > 1e-5:
        raise ValueError(f'Contribution power does not close: {closure}')
    return groups, asd, closure


def cohort_key(record):
    return (record['spec_sha256'], record['suite_sha256'], record['backend'],
            json.dumps(record['source_manifest'], sort_keys=True))


def require_common(records):
    if len({cohort_key(r) for r in records}) != 1:
        raise ValueError('Different frozen comparison cohorts')


def pareto(rows, axes):
    """Scoped all-minimize projection: missing axes cannot dominate."""
    complete = [r for r in rows if all(type(r.get(a)) in (float, int) and np.isfinite(r[a]) for a in axes)]
    return [r['candidate'] for r in complete if not any(
        all(other[a] <= r[a] for a in axes) and any(other[a] < r[a] for a in axes)
        for other in complete if other is not r)]


def parse_elements(circuit, params):
    rows = []
    for line in circuit.splitlines():
        if not line.strip() or line.lstrip().startswith(('*', '.')):
            continue
        tokens = line.split()
        ref = tokens[0]
        kind = ref[0].upper()
        if kind == 'X':
            nodes, value = tokens[1:-1], tokens[-1]
        elif kind in {'R', 'C', 'V', 'B'}:
            nodes, value = tokens[1:3], ' '.join(tokens[3:])
        elif kind == 'E':
            nodes = tokens[1:3] if "VOL=" in line else tokens[1:5]
            value = ' '.join(tokens[3:]) if "VOL=" in line else ' '.join(tokens[5:])
        else:
            raise ValueError('Unsupported element in faithful diagram: ' + line)
        if re.fullmatch(r'\{\w+\}', value):
            value = str(params[value[1:-1]])
        rows.append({'reference': ref, 'kind': kind, 'nodes': nodes, 'value_or_model': value,
                     'source_line': line})
    return rows


def diagram(candidate, elements):
    """Full bipartite connectivity diagram; only zero-V observers collapse.

    All physical and behavioral elements remain explicit. The companion CSV
    retains the uncollapsed node order and original source line.
    """
    alias = {}

    def node(n):
        while n in alias:
            n = alias[n]
        return n

    for e in elements:
        if e['kind'] == 'V' and e['value_or_model'] == '0':
            alias[node(e['nodes'][1])] = node(e['nodes'][0])
    lines = ['graph DUT {', 'graph [overlap=false, splines=true, bgcolor="white",',
             f'label="{candidate}: netlist connectivity; zero-V observers collapsed; research only", labelloc=t];',
             'node [fontname="DejaVu Sans", fontsize=10]; edge [fontname="DejaVu Sans", fontsize=8];']
    names = sorted({node(n) for e in elements for n in e['nodes']})
    for n in names:
        lines.append(f'{json.dumps("n_" + n)} [label={json.dumps(n)}, shape=ellipse, color="#6a8295"];')
    for e in elements:
        if e['kind'] == 'V' and e['value_or_model'] == '0':
            continue
        name = 'e_' + e['reference']
        value = e['value_or_model']
        if len(value) > 65:
            value = value[:62] + '...'
        label = e['reference'] + '\n' + value
        color = '#a14265' if e['kind'] in {'B', 'E'} else '#246957' if e['kind'] == 'X' else '#555555'
        lines.append(f'{json.dumps(name)} [shape=box,label={json.dumps(label)},color="{color}"];')
        for i, n in enumerate(e['nodes'], 1):
            lines.append(f'{json.dumps("n_" + node(n))} -- {json.dumps(name)} [label="{i}"];')
    lines.append('}')
    path = OUT / f'{candidate}_connectivity.dot'
    path.write_text('\n'.join(lines) + '\n')
    subprocess.run(['dot', '-Kneato', '-Tsvg', str(path), '-o', str(path.with_suffix('.svg'))], check=True)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    cfg_path = ROOT / 'research/architecture_comparison_001.yaml'
    cfg = yaml.safe_load(cfg_path.read_text())
    inputs = {}
    checked = {}

    def evidence(path):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        inputs[str(path.relative_to(ROOT))] = sha(path)
        return path

    def load(path):
        return json.loads(evidence(path).read_text())

    def declared(path, expected):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        key = str(path.relative_to(ROOT))
        if key in checked and checked[key] != expected:
            raise ValueError('Conflicting declared hashes: ' + key)
        checked[key] = expected
        if not path.is_file() or sha(path) != expected:
            raise ValueError('Missing or changed original evidence: ' + key)

    def audit_jobs(value):
        if isinstance(value, dict):
            if 'folder' in value and ('netlist_sha256' in value or 'files' in value):
                folder = Path(value['folder'])
                if value.get('netlist_sha256'):
                    declared(folder / 'job.cir', value['netlist_sha256'])
                for name, h in value.get('files', {}).items():
                    declared(folder / name, h)
            for child in value.values():
                audit_jobs(child)
        elif isinstance(value, list):
            for child in value:
                audit_jobs(child)

    batch = Path(cfg['batch'])
    index = load(batch / 'evaluation.json')
    experiment_ids = list(index['baseline_experiments'].values())
    experiment_ids += [e['experiment'] for e in index['continuous'].values()]
    experiment_ids += [e['experiment'] for e in index['children'].values()]
    records = {id_: load(Path('results/runs') / id_ / 'results.json') for id_ in experiment_ids}
    require_common(list(records.values()))
    assert index['source_unchanged']
    for id_, r in records.items():
        folder = ROOT / 'results/runs' / id_
        for name, h in r['source_manifest'].items():
            declared(folder / 'source' / name, h)
        for name, h in r['implementation_manifest'].items():
            declared(folder / name, h)
        audit_jobs(r['jobs'])
        assert not r['eligible']
    # Inspect all six optimizers, preserving their separate earlier source cohort.
    search = load(batch / 'search.json')['experiments']
    optimizers = {}
    for family, id_ in search.items():
        directory = ROOT / 'results/runs' / id_
        r = load(directory / 'optimization.json')
        trials = load(directory / 'trials.json')
        for name, h in r['source_manifest'].items():
            declared(directory / 'source' / name, h)
        for name, h in r.get('implementation_manifest', {}).items():
            declared(directory / 'candidate' / name, h)
        audit_jobs(trials)
        optimizers[family] = {k: r.get(k) for k in ['experiment_id', 'candidate_id', 'evaluations',
                    'budget_declared_before_run', 'scenario_attempts', 'analysis_errors', 'termination',
                    'best', 'diagnostic_best_infeasible', 'rng_seed', 'suite_sha256', 'spec_sha256']}
    validation = {}
    for candidate, entry in index['children'].items():
        v = load(entry['validation'])
        audit_jobs(v)
        assert v['source_unchanged']
        assert v['source_manifest'] == next(iter(records.values()))['source_manifest']
        validation[candidate] = v
    # Use archived sourcing rather than attributing a new observation to an old run.
    first = ROOT / 'results/runs' / experiment_ids[0]
    part_register = yaml.safe_load(evidence(first / 'source/research/procurement/architecture_parts_2026-10-09.yaml').read_text())
    robust_register = yaml.safe_load(evidence(first / 'source/research/procurement/robust_parts_2026-10-09.yaml').read_text())
    refresh = yaml.safe_load(evidence(ROOT / 'research/comparison_procurement_observations_2026-10-09.yaml').read_text())
    flags = yaml.safe_load(evidence(ROOT / 'research/patents/first_architecture_batch_2026-10-09.yaml').read_text())
    robust_flags = yaml.safe_load(evidence(ROOT / 'research/patents/robust_optimization_2026-10-09.yaml').read_text())
    comparison_flags = yaml.safe_load(evidence(ROOT / 'research/patents/architecture_comparison_001_2026-10-09.yaml').read_text())
    patent_index = {r['candidate_id']: r for r in flags['records']}
    patent_index.update({r['candidate']: r for r in robust_flags['candidates']})

    nominal_rows, statuses, boms, details, contributions, spectra, harmonics = [], [], [], [], [], [], []
    representative_records = {}
    for candidate, choice in cfg['representatives'].items():
        r = next(r for r in records.values() if r['candidate_id'] == candidate)
        representative_records[candidate] = r
        folder = ROOT / 'results/runs' / r['experiment_id']
        bom = yaml.safe_load(evidence(folder / 'bom.yaml').read_text())
        circuit = evidence(folder / 'circuit.cir').read_text()
        elements = parse_elements(circuit, r['simulation_configuration'])
        table(OUT / f'{candidate}_connectivity.csv', elements)
        diagram(candidate, elements)
        physical = bom['physical_parts']
        active = sum(p['quantity'] for p in physical if p['unit'] == 'device')
        count = sum(p['quantity'] for p in physical)
        # Reject BOM components absent from the authoritative netlist.
        refs = {e['reference'].lower() for e in elements}
        assert all(p['reference'].lower() in refs or ('x' + p['reference'].lower()) in refs for p in physical)
        for part in physical:
            source = dict(part_register['parts'][part['part_id']])
            supplemental = robust_register['part'] if part['part_id'] == 'EEU-FR1J470' else None
            boms.append({'candidate': candidate, **part, 'procurement_evidence': source,
                         'supplemental_capacitor_evidence': supplemental})
        m = lambda check: r['checks'][check]['metrics']
        op, ac, noise, port = [m(c) for c in ['operating_point', 'frequency_response', 'noise', 'output_impedance']]
        row = {'candidate': candidate, 'name': choice['name'], 'family': r['topology']['family'],
               'experiment': r['experiment_id'], 'record': str((folder / 'results.json').relative_to(ROOT)),
               'current_a': op.get('current_a'), 'rail_v': op.get('internal_rail_v'),
               'simulated_polarization_v': op.get('polarization_dc_v'),
               'sensitivity_v_per_pa': ac.get('sensitivity_v_per_pa_at_1khz'),
               'response_deviation_db': ac.get('response_deviation_db'),
               'noise_pa_rms': noise.get('electronics_noise_pa_rms'),
               'noise_a_pa_rms': noise.get('electronics_noise_a_pa_rms'),
               'electronics_dba_conditional': noise.get('electronics_noise_dba_conditional'),
               'ein_v_rms_conditional': noise.get('electronics_ein_v_rms_conditional'),
               'output_noise_v_rms': noise.get('electronics_output_v_rms'),
               'z_diff_max_ohm': port.get('output_impedance_ohm'),
               'impedance_mismatch_fraction': port.get('impedance_mismatch_fraction'),
               'loading_loss_db': m('loading').get('loading_loss_db'),
               'startup_settling_s': m('startup').get('settling_to_1percent_s'),
               'startup_status': r['checks']['startup']['status'],
               'achieved_rail_settling_s': m('startup').get('settling_to_1percent_s') if r['checks']['startup']['status'] == 'pass' else None,
               'hf_peaking_db': m('stability').get('hf_peaking_db'),
               'active_packages': active, 'passive_parts': count-active, 'installed_count': count,
               'count_and_power_complete': candidate != 'candidate_0013',
               'priced_items_net_eur_scenario': bom['electronics_cost']['priced_items_net_eur_scenario'],
               'confirmed_delivered_eur': None, 'eligible': False,
               'physical_qualified': False, 'patent_screening': 'incomplete_phase8'}
        nominal_rows.append(row)
        for name, check in r['checks'].items():
            statuses.append({'candidate': candidate, 'check': name, 'status': check['status'],
                             'reason': check.get('reason'), 'coverage': check.get('coverage')})
        for metric in ['h2_percent', 'h3_percent', 'h4_to_h10_percent', 'thd_percent', 'clipping_v', 'headroom_pa_rms']:
            harmonics.append({'candidate': candidate, 'metric': metric, 'value': None,
                              'status': r['checks']['distortion']['status'],
                              'reason': r['checks']['distortion'].get('reason')})
        patent = patent_index[candidate]
        assert patent.get('candidate_version_or_hash', patent.get('circuit_sha256')) == sha(folder / 'circuit.cir')
        # Correct a metadata-only carrier flag using actual elements; retain original.
        corrections = []
        if candidate == 'candidate_0013':
            corrections.append('Original flag describes real outputs; exact descendant netlist has ideal Eoutp/Eoutn. Physical driver, oscillator and mixer classes remain unknown.')
        detail = {'candidate': candidate, 'choice': choice, 'identity': {
                    'spec_sha256': r['spec_sha256'], 'suite_sha256': r['suite_sha256'], 'backend': r['backend'],
                    'implementation_manifest': r['implementation_manifest'], 'source_manifest': r['source_manifest'],
                    'models': r['jobs'][0]['semiconductor_models'], 'versions': r['versions'],
                    'rng_seed': r['rng_seed'], 'parent_candidates': r['parent_candidates'],
                    'parent_experiments': r['parent_experiments']},
                  'checks': r['checks'], 'bom': bom, 'patent_original_feature_record': patent,
                  'patent_comparison_review': comparison_flags,
                  'patent_metadata_corrections': corrections,
                  'claims_and_official_status_evidence': [], 'prototype_manufacture_build_publication': 'hold',
                  'validation_summary': {k: validation[candidate][k] for k in ['corner_summary', 'random_summary', 'coverage']} if candidate in validation else None}
        details.append(detail)
        if not noise:
            continue
        raw_job = next(j for j in r['jobs'] if j['folder'].endswith('_noise'))
        raw = parse_raw(evidence(Path(raw_job['folder']) / 'noise.raw'))
        ac_job = next(j for j in r['jobs'] if j['folder'].endswith('_op_ac'))
        acraw = parse_raw(evidence(Path(ac_job['folder']) / 'ac.raw'))
        f = raw['frequency'].real
        gain = np.array([abs(at_frequency(acraw['frequency'], acraw.voltage('pp', 'pn'), x)) for x in f])
        roots = device_noise_totals(raw)
        groups, densities, closure = verify_partition(f, roots, raw['onoise_spectrum'].real)
        electronics = np.sqrt(sum((v**2 for k, v in densities.items() if not k.endswith('(excluded)')), np.zeros_like(f)))
        np.testing.assert_allclose(electronics, noise['electronics_output_asd_v_per_sqrt_hz'], rtol=1e-10)
        np.testing.assert_allclose(integrate_asd(f, electronics / gain), row['noise_pa_rms'], rtol=1e-10)
        for group, density in densities.items():
            contributions.append({'candidate': candidate, 'group': group,
                    'output_v_rms': integrate_asd(f, density), 'pressure_pa_rms_conditional': integrate_asd(f, density/gain),
                    'pressure_a_pa_rms_conditional': integrate_asd(f, density/gain, True),
                    'vectors': groups[group], 'power_closure_relative': closure})
        for i, frequency in enumerate(f):
            spectra.append({'candidate': candidate, 'frequency_hz': float(frequency),
                    'electronics_output_asd_v_sqrt_hz': float(electronics[i]),
                    'electronics_pressure_asd_pa_sqrt_hz': float(electronics[i]/gain[i]),
                    **{g: float(d[i]) for g, d in densities.items()}})

    # Matching endpoints, excluding implementation-specific combined/TCR cases.
    va, vb = [validation[c]['corners'] for c in ['candidate_0019', 'candidate_0023']]
    paired = []
    for a, b in zip(va, vb):
        sa, sb = a['scenario'], b['scenario']
        assert sa['id'] == sb['id']
        if sa != sb:
            continue
        values = [a.get('response_deviation_db'), b.get('response_deviation_db')]
        winner = None if any(x is None for x in values) else 'tie' if values[0] == values[1] else ['candidate_0019', 'candidate_0023'][int(values[1] < values[0])]
        paired.append({'scenario': sa['id'], 'parameters': sa.get('parameters', {}),
                       'conventional_response_db': values[0], 'servo_response_db': values[1],
                       'conventional_status': a['status'], 'servo_status': b['status'],
                       'smaller_response_deviation': winner, 'production_ranking': None})
    table(OUT / 'paired_endpoints.csv', paired)
    sensitivity = []
    for row in nominal_rows:
        if row['electronics_dba_conditional'] is None:
            continue
        for sref in [0.005, 0.020, 0.040]:
            sensitivity.append({'candidate': row['candidate'], 'sref_v_per_pa_at_60v': sref,
                    'derived_electronics_dba_conditional': row['electronics_dba_conditional'] + 20*np.log10(0.020/sref),
                    'derived_noise_pa_rms': row['noise_pa_rms']*0.020/sref,
                    'assumption': 'Linear pressure-transfer scaling; unchanged DC/stationary noise. No physical noise qualification.'})
    table(OUT / 'sensitivity_rescaling.csv', sensitivity)

    projection_rows = []
    for r in records.values():
        if r['topology']['family'] not in {'conventional_jfet', 'unconventional_jfet', 'no_fet'}:
            continue
        # Continuous proposals share a candidate identity; explicitly distinguish.
        label = r['candidate_id']
        if r['experiment_id'] in {e['experiment'] for e in index['continuous'].values()}:
            label += ':continuous'
        bom = yaml.safe_load(evidence(ROOT / 'results/runs' / r['experiment_id'] / 'bom.yaml').read_text())
        projection_rows.append({'candidate': label, 'experiment': r['experiment_id'], 'family': r['topology']['family'],
               'response_deviation_db': r['checks']['frequency_response']['metrics'].get('response_deviation_db'),
               'current_a': r['checks']['operating_point']['metrics'].get('current_a'),
               'installed_count': sum(p['quantity'] for p in bom['physical_parts']),
               'implementation': 'continuous proposal' if label.endswith(':continuous') else 'actual research BOM'})
    # Production front is a separate artifact and remains strictly empty.
    actual_rows = [r for r in projection_rows if r['implementation'] == 'actual research BOM']
    fronts = {'scope': 'Model-conditional nominal DC/AC projection only; no architecture qualification',
              'axes_all_minimize': ['response_deviation_db', 'current_a', 'installed_count'],
              'matching_spec_suite_source_backend': True,
              'actual_bom_projection': pareto(actual_rows, ['response_deviation_db', 'current_a', 'installed_count']),
              'continuous_proposals_separate_projection': pareto([r for r in projection_rows if r['implementation'] != 'actual research BOM'], ['response_deviation_db', 'current_a']),
              'excluded_axes': ['unvalidated noise', 'unsupported nonlinear', 'manufacturing yield', 'unknown delivered cost', 'carrier power'],
              'production_front': [], 'physical_qualified_front': [], 'rows': projection_rows}
    dump(OUT / 'research_pareto.json', fronts)
    dump(OUT / 'production_front.json', {'front': [], 'physical_qualified_front': [],
            'scope': 'Requires complete existing qualification, physical evidence and separate sourcing/patent gates',
            'gates_relaxed': False})
    table(OUT / 'nominal_metrics.csv', nominal_rows)
    table(OUT / 'qualification_coverage.csv', statuses)
    table(OUT / 'bom_lines.csv', boms)
    table(OUT / 'noise_contributions.csv', contributions)
    table(OUT / 'noise_spectra.csv', spectra, sorted({k for r in spectra for k in r}))
    table(OUT / 'harmonics_headroom.csv', harmonics)
    dump(OUT / 'architecture_comparison_001.json', {'schema_version': 1, 'date': cfg['date'],
         'scope': cfg['scope'], 'representatives': details, 'nominal_metrics': nominal_rows,
         'optimizers': optimizers, 'paired_endpoints': paired, 'noise_contributions': contributions,
         'current_procurement_refresh': refresh, 'sensitivity_scaling': sensitivity,
         'research_pareto': fronts, 'physical_measurements': [], 'all_requirement_yield': None,
         'claims_screened': [], 'production_selection': None})

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout='constrained')
    for row in nominal_rows:
        r = representative_records[row['candidate']]
        ac, noise = r['checks']['frequency_response']['metrics'], r['checks']['noise']['metrics']
        if not ac:
            continue
        label = row['candidate'].replace('candidate_', '') + ' ' + row['name']
        f, gain = np.array(ac['frequency_hz']), np.array(ac['gain_v_per_pa'])
        axes[0].semilogx(f, 20*np.log10(gain/abs(at_frequency(f,gain,1000))), label=label)
        nrows = [s for s in spectra if s['candidate'] == row['candidate']]
        axes[1].loglog([s['frequency_hz'] for s in nrows], [s['electronics_pressure_asd_pa_sqrt_hz'] for s in nrows], label=label)
    axes[0].set(xlim=(20,20000), ylim=(-10,24), xlabel='Frequency (Hz)', ylabel='Response relative to 1 kHz (dB)')
    axes[0].axhline(1,color='gray',ls='--'); axes[0].axhline(-1,color='gray',ls='--')
    axes[1].set(xlabel='Frequency (Hz)',ylabel='Conditional electronics pressure ASD (Pa/√Hz)')
    for ax in axes:
        ax.grid(alpha=.2); ax.legend(fontsize=7)
    fig.suptitle('Recorded models only; semiconductor noise unvalidated; capsule mechanics excluded')
    fig.savefig(OUT / 'response_noise.png', dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10,4.8), layout='constrained')
    groups = sorted({r['group'] for r in contributions if not r['group'].endswith('(excluded)')})
    x = np.arange(3); bottom = np.zeros(3)
    candidates = ['candidate_0019','candidate_0023','candidate_0012']
    for group in groups:
        values = []
        for candidate in candidates:
            rows = [r for r in contributions if r['candidate'] == candidate and r['group'] == group]
            total = sum(r['output_v_rms']**2 for r in contributions if r['candidate'] == candidate and not r['group'].endswith('(excluded)'))
            values.append(100*sum(r['output_v_rms']**2 for r in rows)/total)
        ax.bar(x,values,bottom=bottom,label=group); bottom += values
    ax.set(xticks=x,xticklabels=[c.replace('candidate_','') for c in candidates],ylabel='Unweighted output noise power (%)',ylim=(0,100))
    ax.legend(bbox_to_anchor=(1.01,1),loc='upper left',fontsize=8)
    ax.set_title('Raw root contributions; model-conditional, 20 Hz–20 kHz')
    fig.savefig(OUT / 'noise_contributions.png',dpi=170); plt.close(fig)

    region = [r for r in paired if r['scenario'].startswith(('CF_', 'CR_', 'PAR_', 'LEAK_', 'CROSS_', 'SREF_', 'LEN_', 'ZIN_'))]
    fig, ax = plt.subplots(figsize=(11,5.5),layout='constrained')
    x = np.arange(len(region)); width=.4
    ax.bar(x-width/2,[r['conventional_response_db'] for r in region],width,label='0019 fixed-bias JFET')
    ax.bar(x+width/2,[r['servo_response_db'] for r in region],width,label='0023 servo JFET')
    ax.set(yscale='log',xticks=x,xticklabels=[r['scenario'] for r in region],ylabel='Response deviation (dB, logarithmic axis)')
    ax.tick_params(axis='x',rotation=65); ax.axhline(1,color='gray',ls='--',label='Frozen limit')
    ax.legend(fontsize=8); ax.set_title('Shared external endpoints; smaller deviation changes with assumptions')
    fig.savefig(OUT / 'uncertainty_regions.png',dpi=170); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9,5.3),layout='constrained')
    family_labels = {'conventional_jfet':'Fixed-bias JFET', 'unconventional_jfet':'Servo JFET', 'no_fet':'BJT charge'}
    for family in ['conventional_jfet','unconventional_jfet','no_fet']:
        points = [r for r in actual_rows if r['family'] == family]
        ax.scatter([r['current_a']*1000 for r in points],[r['response_deviation_db'] for r in points],label=family_labels[family])
        previous_label_y = 0
        for r in sorted(points, key=lambda r:r['response_deviation_db']):
            label_y = max(r['response_deviation_db'], previous_label_y*1.16)
            ax.annotate(r['candidate'].replace('candidate_','') + f" ({r['installed_count']} parts)",
                        (r['current_a']*1000,r['response_deviation_db']),
                        xytext=(r['current_a']*1000+.035,label_y),textcoords='data',fontsize=7,
                        arrowprops={'arrowstyle':'-', 'color':'gray','lw':.5})
            previous_label_y = label_y
    ax.set(yscale='log',xlim=(4.0,5.45),xlabel='Nominal modeled P48 current (mA)',ylabel='Response deviation (dB)')
    ax.legend(fontsize=8); ax.grid(alpha=.2)
    ax.set_title('Research projection: actual BOMs, matching cohort; qualified front empty')
    fig.savefig(OUT / 'research_pareto.png',dpi=170); plt.close(fig)

    def num(value, scale=1):
        return 'unknown' if value is None else f'{value*scale:.5g}'

    md = ['# Generated comparison tables', '',
          'Derived from immutable same-cohort records. Values are model-conditional; unknowns remain unknown.', '',
          '| Candidate | Current mA | Rail / polarization V | Sensitivity mV/Pa | Response dB | EIN µV / dBA | Zdiff Ω / mismatch % | Active / passive |',
          '| --- | ---: | --- | ---: | ---: | --- | --- | --- |']
    for r in nominal_rows:
        md.append(f"| {r['candidate']} | {num(r['current_a'],1000)} | {num(r['rail_v'])} / {num(r['simulated_polarization_v'])} | {num(r['sensitivity_v_per_pa'],1000)} | {num(r['response_deviation_db'])} | {num(r['ein_v_rms_conditional'],1e6)} / {num(r['electronics_dba_conditional'])} | {num(r['z_diff_max_ohm'])} / {num(r['impedance_mismatch_fraction'],100)} | {r['active_packages']} / {r['passive_parts']} |")
    md += ['', '## Complete check statuses', '', '| Candidate | ' + ' | '.join(next(iter(representative_records.values()))['checks']) + ' |',
           '| --- | ' + ' | '.join(['---']*len(next(iter(representative_records.values()))['checks'])) + ' |']
    names = list(next(iter(representative_records.values()))['checks'])
    for c,r in representative_records.items():
        md.append('| ' + c + ' | ' + ' | '.join(r['checks'][k]['status'] for k in names) + ' |')
    md += ['', 'Carrier additionally has an errored carrier_mechanism check; ordinary columns are unsupported periodic analyses.', '',
           '## Exact BOM and sourcing observations', '',
           'All prices are incomplete catalogue scenarios. Every delivered total is unknown. Each source link retains exact variant, indexed age, MOQ/pack/lead and private-route limits. Nominal values and tolerances below come from the frozen BOM; original errors remain.', '']
    for d in details:
        c = d['candidate']; bom = d['bom']
        md += [f'### {c}', '',
               f"[Frozen netlist](../../runs/{representative_records[c]['experiment_id']}/circuit.cir) · [Frozen BOM](../../runs/{representative_records[c]['experiment_id']}/bom.yaml) · [Connectivity diagram]({c}_connectivity.svg) · [Every node/element]({c}_connectivity.csv)", '',
               '| Exact MPN | Installed qty | Nominal / tolerance | Package | MOQ / retail pack / excess | Indexed stock / age | Net unit EUR scenario |',
               '| --- | ---: | --- | --- | --- | --- | ---: |']
        for q in bom['quantity_summary']:
            source = part_register['parts'][q['exact_mpn']]
            p = next(p for p in bom['physical_parts'] if p['part_id'] == q['exact_mpn'])
            md.append(f"| [{q['exact_mpn']}]({source['url']}) | {q['installed_quantity']} | {p['value']} {p['unit']} / {num(p['tolerance_fraction'],100)}% | {p['package']} | {num(q.get('moq'))} / {num(q.get('retail_pack_size'))} / {num(q.get('unavoidable_pack_excess_scenario'))} | {num(source.get('stock_observed'))} / {source['reported_crawl_age']} | {num(q.get('unit_price_net_eur_observed'))} |")
        md += ['', f"Priced net subtotal EUR {bom['electronics_cost']['priced_items_net_eur_scenario']:.4f}; confirmed delivered total unknown. Unpriced: {json.dumps(bom['electronics_cost']['unpriced_items'])}.",
               'Full supplier URLs, ratings/technology, lifecycle, exact lead-time fields, intended purchasing quantities and unknown fees are in bom_lines.csv and the machine-readable comparison. Documented dimensions conflict for EEU-FR1J470: frozen catalogue says 12.7mm body, newer primary record says 11.2mm; physical outline/lead allowance needs resolution. Factory packs are not private retail MOQs.', '']
    (OUT / 'tables.md').write_text('\n'.join(md)+'\n')
    evidence(cfg_path)
    for path in [Path(__file__), ROOT/'src/meridian_lab/core.py', ROOT/'src/meridian_lab/metrics.py']:
        evidence(path)
    evidence(ROOT/'tests/test_comparison.py')
    outputs = {p.name: sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'provenance.json' and p.suffix != '.log'}
    dump(OUT/'provenance.json', {'schema_version':1, 'date':cfg['date'], 'status':'pass',
           'reporting_versions': {'python':sys.version, 'numpy':np.__version__, 'matplotlib':matplotlib.__version__,
              'graphviz':subprocess.run(['dot','-V'],capture_output=True,text=True,check=True).stderr.strip()},
           'input_sha256': inputs, 'verified_declared_files': checked,
           'output_sha256': outputs, 'cohort_spec_sha256': next(iter(records.values()))['spec_sha256'],
           'cohort_suite_sha256': next(iter(records.values()))['suite_sha256'],
           'full_suite_records':len(records), 'optimization_records':len(optimizers),
           'original_records_modified':False, 'new_spice_evaluations':0, 'independent_backup_complete':False})
    print(json.dumps({'status':'pass','full_suite_records':len(records), 'optimization_records':len(optimizers),
                      'verified_files':len(checked),'outputs':len(outputs), 'production_front':[]}))


if __name__ == '__main__':
    run()
