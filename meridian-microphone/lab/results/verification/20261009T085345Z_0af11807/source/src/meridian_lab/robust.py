# SPDX-License-Identifier: GPL-3.0-or-later
"""Budgeted, single-axis optimization of explicitly scoped SPICE scenarios.

No probabilistic interpretation is assigned to guaranteed bounds. A scenario
optimum is neither an all-corner bound nor a qualified implementation.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
import uuid

import numpy as np
from scipy.optimize import differential_evolution
from scipy.stats import binom

from .core import ROOT, Simulator, digest, environment_versions, read_yaml, source_manifest, spec_digest, verify_spec_lock, write_json
from .cli import implementation_manifest
from . import qualification as q
from .metrics import population_summary


AXES = {
    'response': ('frequency_response', 'response_deviation_db', 'minimize', None),
    'current': ('operating_point', 'current_a', 'minimize', None),
    'noise': ('noise', 'electronics_noise_pa_rms', 'minimize', 'validated_noise_models'),
    'distortion': ('distortion', 'thd_percent', 'minimize', 'validated_nonlinear_models'),
    'headroom': ('headroom', 'headroom_pa_rms', 'maximize', 'validated_nonlinear_models'),
    'loading': ('loading', 'loading_loss_db', 'minimize', 'validated_loading_models'),
    'balance': ('balance', 'impedance_mismatch_fraction', 'minimize', 'validated_port_models'),
    'drive': ('output_impedance', 'output_impedance_ohm', 'minimize', 'validated_port_models'),
    'complexity': (None, 'component_count', 'minimize', 'realized_component_count'),
}


class BudgetExhausted(RuntimeError):
    pass


def audit(meta, axis):
    """Fail closed for missing behaviors and incompatible analysis protocols."""
    if axis not in AXES:
        raise ValueError('Unknown separate objective axis')
    if meta.get('analysis_domain') == 'periodic_mechanism_control':
        return {'allowed': False, 'reason': 'Periodic conversion needs a validated periodic objective protocol.'}
    required = AXES[axis][3]
    if required and required not in meta.get('qualification_evidence', []):
        return {'allowed': False, 'reason': 'Missing prerequisite: ' + required}
    return {'allowed': True, 'scope': 'restricted model-conditional DC/AC research; no production ranking',
            'noise_ranking_allowed': 'validated_noise_models' in meta.get('qualification_evidence', []),
            'manufacturing_evidence': False}


def aggregate(rows, metric, mode='worst', percentile=95, direction='minimize'):
    """Adverse finite specimens stay; any absent/error sample invalidates objective."""
    values = [float(r[metric]) for r in rows if isinstance(r.get(metric), (int, float))
              and np.isfinite(r[metric])]
    complete = len(values) == len(rows) and bool(rows) and all(r['status'] != 'error' for r in rows)
    worst = (max(values) if direction == 'minimize' else min(values)) if values else None
    if mode not in {'nominal', 'worst', 'scenario_percentile'}:
        raise ValueError('Use nominal, worst, or explicitly empirical scenario_percentile')
    value = None
    if complete:
        if mode == 'nominal':
            value = values[0]
        elif mode == 'worst':
            value = worst
        else:
            if not 50 <= percentile < 100:
                raise ValueError('Scenario percentile must be >=50 and <100')
            value = float(np.percentile(values, percentile if direction == 'minimize' else 100-percentile))
    return {'value': value, 'complete': complete, 'samples': len(rows),
            'finite_samples': len(values), 'missing_or_error_samples': len(rows)-sum(
                isinstance(r.get(metric), (int, float)) and np.isfinite(r[metric]) and r['status'] != 'error' for r in rows),
            'worst_observed': worst, 'p95_scenario': float(np.percentile(values, 95)) if values else None,
            'interpretation': 'finite tested scenarios only; no full-envelope bound or population percentile'}


def percentile_interval(values, percentile=95):
    """Distribution-free order-statistic CI under the declared IID scenario sampler.

    Null endpoints denote unbounded tails, not omitted adverse specimens.
    """
    values = sorted(float(v) for v in values if np.isfinite(v))
    n = len(values)
    if not n:
        return [None, None]
    low, high = binom.ppf([.025, .975], n, percentile/100).astype(int)
    return [values[low-1] if low > 0 else None, values[high] if high < n else None]


def uncertainty_ranges(meta, design=None):
    ranges = q.scenario_ranges()
    # The original general screen omitted cross capacitance; preserve it here.
    ranges['CROSS'] = read_yaml(ROOT/'spec/capsule_model.yaml')['parameters']['front_rear_stray_f']['range']
    for key, definition in meta.get('population', {}).items():
        ranges[key] = list(definition['range'])
    for group in (design or {}).values():
        for target in group['targets']:
            tolerance = group.get('tolerance_fraction')
            if tolerance is not None:
                center = meta['parameters'][target]['default']
                ranges[target] = [center*(1-tolerance), center*(1+tolerance)]
    return ranges


def random_scenarios(meta, seed, count, design=None):
    rng = np.random.default_rng(seed)
    ranges = uncertainty_ranges(meta, design)
    log_keys = {'LEAK'} | {k for k, d in meta.get('population', {}).items() if d.get('distribution') == 'log_uniform'}
    return [{'id': f'holdout_seed_{seed}_{i}', 'kind': 'IID artificial scenario design; not production',
             'parameters': {k: float(np.exp(rng.uniform(np.log(lo), np.log(hi)))) if k in log_keys
                            else float(rng.uniform(lo, hi)) for k, (lo, hi) in ranges.items()}}
            for i in range(count)]


def corner_scenarios(meta, design=None):
    ranges = uncertainty_ranges(meta, design)
    # One-at-a-time extremes plus combined opposite endpoints; no exhaustive claim.
    cases = [{'id': f'{k}_{side}', 'kind': 'bounded endpoint scenario', 'parameters': {k: ends[i]}}
             for k, ends in ranges.items() if k not in meta.get('population', {})
             for i, side in enumerate(['low', 'high'])]
    cases += [{'id': 'combined_'+side, 'kind': 'combined bounded stress',
               'parameters': {k: v[i] for k, v in ranges.items()}} for i, side in enumerate(['low', 'high'])]
    # Complete temperature-dependent files are used; semiconductor parameters are
    # never independently randomized. Vendor coupled JFE proposals remain stresses
    # with known limit failures, not certified process coverage.
    if any(m.startswith('jfe150') for m in meta.get('semiconductor_models', [])):
        for model in ['jfe150_weak', 'jfe150_strong']:
            cases.append({'id': model, 'kind': 'complete coupled vendor proposal; fails library bounds; not production corner',
                          'model_replacement': model, 'parameters': {}})
    return cases


def measure(candidate, directory, snapshot, overrides, scenarios, axis='response'):
    rows = []
    for i, scenario in enumerate(scenarios):
        started = time.monotonic()
        sim = Simulator(candidate, directory/f'scenario_{i:04d}', {**overrides, **scenario.get('parameters', {})})
        sim.candidate = snapshot/'candidate'
        sim.model_root = snapshot/'source/models'
        sim.meta = deepcopy(sim.meta)
        if scenario.get('model_replacement'):
            sim.meta['semiconductor_models'] = [scenario['model_replacement'] if m.startswith('jfe150') else m
                                                 for m in sim.meta['semiconductor_models']]
            # Separate immutable scenario implementation; never mutate the parent
            # snapshot or splice independent BETA/VTO parameters into a device.
            corner_candidate = sim.directory/'candidate'
            corner_candidate.mkdir()
            circuit = (sim.candidate/'circuit.cir').read_text()
            symbol = scenario['model_replacement'].upper()
            (corner_candidate/'circuit.cir').write_text(re.sub(r'(?im)\bJFE150\s*$', symbol, circuit))
            sim.candidate = corner_candidate
        row = {'scenario': scenario, 'status': 'error', 'jobs': sim.jobs}
        try:
            ctx = {'nominal': sim.execute('dc_feasibility', 'op\nwrite op.raw all', ['op.raw']), 'checks': {}}
            op = q.operating_point(sim, ctx)
            ctx['checks']['operating_point'] = op
            row.update(current_a=op['metrics']['current_a'], polarization_dc_v=op['metrics']['polarization_dc_v'])
            if op['status'] != 'pass':
                row.update(status='fail', stage='DC infeasible; expensive analyses skipped')
            else:
                ctx['nominal'].update(sim.op_ac('ac_feasibility'))
                fr = q.frequency_response(sim, ctx)
                ctx['checks']['frequency_response'] = fr
                row.update(response_deviation_db=fr['metrics']['response_deviation_db'],
                           sensitivity_v_per_pa=fr['metrics']['sensitivity_v_per_pa_at_1khz'],
                           status=fr['status'], stage='DC/AC screen')
                check, metric, _, _ = AXES[axis]
                if axis == 'complexity':
                    bom = read_yaml(snapshot/'candidate/bom.yaml')
                    row[metric] = sum(p['quantity'] for p in bom['physical_parts'])
                elif check not in {'operating_point', 'frequency_response'}:
                    # Prerequisite audited by caller; preserve dependencies/errors.
                    for name in {'noise':['noise'], 'distortion':['distortion'], 'headroom':['distortion','headroom'],
                                 'loading':['loading'], 'balance':['output_impedance','balance'], 'drive':['output_impedance']}[axis]:
                        ctx['checks'][name] = q.CHECKS[name](sim, ctx)
                    value = ctx['checks'][check]['metrics'].get(metric)
                    if value is None:
                        raise ValueError('Objective has absent or censored metric')
                    row[metric] = value
        except Exception as exc:
            row.update(status='error', reason=f'{type(exc).__name__}: {exc}')
        row['runtime_s'] = time.monotonic()-started
        rows.append(row)
    return rows


def freeze(directory, candidate):
    manifest = source_manifest()
    implementation = implementation_manifest(ROOT/'candidates'/candidate)
    for relative in manifest:
        p = directory/'source'/relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT/relative).read_bytes())
    (directory/'candidate').mkdir()
    for relative in implementation:
        (directory/'candidate'/relative).write_bytes((ROOT/'candidates'/candidate/relative).read_bytes())
    write_json(directory/'frozen_manifest.json', {'sources':manifest, 'implementation':implementation})
    return manifest, implementation


def optimize(candidate, definition, budget=12, seed=34047, axis='response', mode='worst', scenarios=None, percentile=95):
    verify_spec_lock()
    if budget < 6:
        raise ValueError('Budget must include nominal plus at least five initial points')
    meta = read_yaml(ROOT/'candidates'/candidate/'topology.yaml')
    prerequisite = audit(meta, axis)
    experiment = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_robust_'+uuid.uuid4().hex[:8]
    directory = ROOT/'results/runs'/experiment
    directory.mkdir(exist_ok=False)
    manifest, implementation = freeze(directory, candidate)
    parent_file = ROOT/'candidates'/candidate/'results.json'
    parent = json.loads(parent_file.read_text())['latest_experiment'] if parent_file.exists() else None
    scenarios = scenarios or [{'id':'nominal', 'parameters':{}, 'kind':'nominal'},
                              {'id':'training_supply_low', 'parameters':{'VS':44,'FT':.20}, 'kind':'supply bounded stress'},
                              {'id':'training_supply_high', 'parameters':{'VS':52,'FT':-.20}, 'kind':'supply bounded stress'}]
    if mode == 'nominal':
        scenarios = scenarios[:1]
    for group in definition.values():
        lo, hi = group['range']
        if not (0 < lo < hi) or not group.get('rationale'):
            raise ValueError('Positive physically justified bounds required')
        for target in group['targets']:
            if target not in meta['parameters']:
                raise ValueError('Undeclared topology parameter: '+target)
    base = {'schema_version':2, 'experiment_id':experiment, 'candidate_id':candidate,
            'parent_experiments':[parent] if parent else [], 'axis':axis, 'aggregation':mode,
            'percentile':percentile if mode=='scenario_percentile' else None, 'prerequisite_audit':prerequisite,
            'budget_declared_before_run':budget, 'seed':seed, 'design_parameters':definition,
            'hard_constraints':['DC energy closure/current/positive rail/positive polarization', 'response <= frozen 1dB for each tested scenario'],
            'training_scenarios':scenarios, 'source_manifest':manifest, 'implementation_manifest':implementation,
            'suite_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),
            'spec_sha256':spec_digest(), 'versions':environment_versions(),
            'eligible':False, 'global_optimality':False, 'manufacturing_yield':None,
            'patent_state':meta.get('patent_state','unscreened'), 'procurement_state':meta.get('procurement_state','unknown')}
    write_json(directory/'plan.json', base)
    started = time.monotonic()
    trials, cache = [], {}
    keys = list(definition)
    bounds = [tuple(np.log(definition[k]['range'])) for k in keys]
    metric = AXES[axis][1]
    direction = AXES[axis][2]

    def evaluate(x):
        key = tuple(float(v) for v in x)
        if key in cache:
            return cache[key]
        if len(trials) >= budget:
            raise BudgetExhausted()
        values = {k:float(np.clip(np.exp(v), *definition[k]['range'])) for k,v in zip(keys,x)}
        overrides = {t:values[k] for k in keys for t in definition[k]['targets']}
        folder = directory/f'trial_{len(trials):05d}'
        folder.mkdir()
        rows = measure(candidate, folder, directory, overrides, scenarios, axis)
        summary = aggregate(rows, metric, mode, percentile, direction)
        item = {'trial':len(trials), 'design_values':values, 'parameters':overrides, 'cases':rows,
                'objective':summary, 'screen_feasible':all(r['status']=='pass' for r in rows)}
        write_json(folder/'trial.json', item)
        trials.append(item)
        value = summary['value']
        # No weighted penalty: response itself guides search from the infeasible
        # region; acceptance constraints are applied separately to every scenario.
        score = float(value)*(1 if direction=='minimize' else -1) if value is not None else np.inf
        cache[key] = score
        return score

    termination = 'prerequisite_hold'
    answer = None
    if prerequisite['allowed']:
        nominal = [np.log(meta['parameters'][definition[k]['targets'][0]]['default']) for k in keys]
        evaluate(nominal)
        rng = np.random.default_rng(seed)
        # Deterministic endpoints and interior points seed a bounded DE run.
        init = np.array([[lo for lo,hi in bounds], [hi for lo,hi in bounds],
                         [(lo+hi)/2 for lo,hi in bounds],
                         *[[rng.uniform(lo,hi) for lo,hi in bounds] for _ in range(3)]])
        if all(r['status']=='error' for r in trials[0]['cases']):
            termination = 'nominal_integration_failure_hold; remaining budget unused'
        else:
            try:
                answer = differential_evolution(evaluate, bounds, init=init, maxiter=budget,
                                                rng=rng, polish=False, tol=1e-7, atol=0)
                termination = 'scipy_convergence' if answer.success else 'scipy_iteration_limit'
            except BudgetExhausted:
                termination = 'evaluation_budget_exhausted'
    feasible = [t for t in trials if t['screen_feasible'] and t['objective']['complete']]
    best = (min if direction=='minimize' else max)(feasible, key=lambda t:t['objective']['value']) if feasible else None
    finite = [t for t in trials if t['objective']['value'] is not None]
    diagnostic = (min if direction=='minimize' else max)(finite,key=lambda t:t['objective']['value']) if finite else None
    unchanged = source_manifest()==manifest and implementation_manifest(ROOT/'candidates'/candidate)==implementation
    record = {**base, 'status':'proposal_requires_full_suite' if best and unchanged else 'no_feasible_tested_proposal' if unchanged and prerequisite['allowed'] else 'prerequisite_hold' if unchanged else 'source_integrity_error',
              'termination':termination, 'scipy_success':bool(answer.success) if answer else False,
              'scipy_message':str(answer.message) if answer else None,
              'evaluations':len(trials), 'trial_failures':sum(not t['screen_feasible'] for t in trials),
              'scenario_attempts':sum(len(t['cases']) for t in trials),
              'analysis_errors':sum(r['status']=='error' for t in trials for r in t['cases']),
              'runtime_s':time.monotonic()-started, 'best':best, 'diagnostic_best_infeasible':diagnostic if best is None else None,
              'source_unchanged':unchanged, 'full_suite_experiment':None,
              'note':'No feasible tested point is not a proof that the full value region is infeasible.'}
    write_json(directory/'optimization.json', record)
    write_json(directory/'trials.json', trials)
    if best:
        write_json(directory/'proposed_parameters.json', best['parameters'])
    return record


def validate(candidate, overrides, directory, seed, samples=16, design=None):
    directory = Path(directory)
    directory.mkdir(exist_ok=False)
    manifest, implementation = freeze(directory, candidate)
    meta = read_yaml(directory/'candidate/topology.yaml')
    # Center tolerances on the continuous design instead of the original BOM.
    for key,value in overrides.items():
        if key in meta['parameters']:
            meta['parameters'][key]['default'] = value
    corners = corner_scenarios(meta, design)
    random = random_scenarios(meta, seed, samples, design)
    rows = measure(candidate, directory/'corners', directory, overrides, corners)
    random_rows = measure(candidate, directory/'independent_random', directory, overrides, random)
    summary = population_summary(random_rows, 'response_deviation_db')
    values = [r['response_deviation_db'] for r in random_rows if r['status'] in {'pass','fail'} and 'response_deviation_db' in r]
    summary.update(percentile_95_interval=percentile_interval(values),
                   confidence_scope='IID artificial scenario sampler only; no production/yield interpretation; missing analyses unresolved')
    record = {'candidate_id':candidate, 'parameters':overrides, 'seed':seed,
              'corner_summary':aggregate(rows,'response_deviation_db'), 'corners':rows,
              'random_summary':summary, 'random_cases':random_rows,
              'source_manifest':manifest, 'implementation_manifest':implementation, 'spec_sha256':spec_digest(),
              'source_unchanged':source_manifest()==manifest and implementation_manifest(ROOT/'candidates'/candidate)==implementation,
              'coverage':'DC/AC only; library vendor-corner disagreements preserved; not all-requirement robustness',
              'manufacturing_evidence':False, 'eligible':False}
    write_json(directory/'validation.json',record)
    return record
