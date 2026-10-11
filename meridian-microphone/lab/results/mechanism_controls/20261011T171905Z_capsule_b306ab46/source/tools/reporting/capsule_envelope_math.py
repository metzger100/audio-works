# SPDX-License-Identifier: GPL-3.0-or-later
"""Independent low-frequency controls; hypotheses, never capsule ratings."""
from pathlib import Path
import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad

EPS = 8.8541878128e-12  # F/m; numerical approximation, no metrology assertion
KB = 1.380649e-23  # J/K, exact SI
TEMP = 298.15


def write_csv(path, rows):
    with Path(path).open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def calculate(out):
    """Compare quadrature/finite differences with closed forms before any SPICE."""
    radius = .0135  # SC10 documented RK47 film radius, not K47FRB active radius
    fraction = .55  # assumed perforation/electrode fraction, not measured
    area = np.pi * radius**2
    gap0 = EPS * fraction * area / 70e-12
    tension = radius**2 / (8 * gap0 * (.02 / 60))
    geometry = []
    for cap in [45e-12, 70e-12, 100e-12]:
        gap = EPS * fraction * area / cap
        compliance = radius**2 / (8 * tension)
        numeric_area = quad(lambda r: 2*np.pi*r, 0, radius)[0]
        numeric_displacement = quad(
            lambda r: 2*np.pi*r*(radius**2-r**2)/(4*tension), 0, radius
        )[0] / numeric_area
        h = gap * 1e-5
        derivative = (EPS*fraction*area/(gap-h)-EPS*fraction*area/(gap+h))/(2*h)
        assert np.isclose(derivative, cap/gap, rtol=1e-8)
        assert np.isclose(numeric_displacement, compliance, rtol=1e-10)
        geometry.append(dict(capacitance_F=cap, analog_radius_m=radius,
                             assumed_electrode_fraction=fraction, inferred_gap_m=gap,
                             implied_tension_N_per_m=tension, mean_compliance_m_per_Pa=compliance,
                             Sref_V_per_Pa=60*compliance/gap,
                             charge_per_Pa_at_40V_C_per_Pa=cap*40*compliance/gap))
    write_csv(out/'geometry.csv', geometry)
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    freq = np.geomspace(20, 20000, 400)
    for resistance in [1e9, 1e12, 1e14]:
        cap = 70e-12
        tau = resistance*cap
        exact = 2*KB*TEMP/(np.pi*cap)*(np.arctan(2*np.pi*20000*tau)-np.arctan(2*np.pi*20*tau))
        numeric = quad(lambda u: 4*KB*TEMP*resistance/(1+(2*np.pi*np.exp(u)*tau)**2)*np.exp(u),
                       np.log(20), np.log(20000), epsabs=1e-24, epsrel=1e-10)[0]
        assert np.isclose(numeric, exact, rtol=1e-8)
        # Independent full-band integration in normalized angular frequency.
        integral = quad(lambda u: 1/(1+u*u), 0, np.inf)[0]
        assert np.isclose(2*KB*TEMP/(np.pi*cap)*integral, KB*TEMP/cap)
        rows.append(dict(leakage_ohm=resistance, capacitance_F=cap,
                         leak_current_at_40V_A=40/resistance, isolated_tau_s=tau,
                         thermal_voltage_20_20k_V_rms=np.sqrt(exact),
                         reset_kTC_V_rms=np.sqrt(KB*TEMP/cap)))
        asd = np.sqrt(4*KB*TEMP*resistance/(1+(2*np.pi*freq*tau)**2))
        axes[0].loglog(freq, asd*1e9, label=f'R={resistance:g} ohm')
    for delta in [1e-4, 1e-3]:
        # A frequency-local dissipative shunt hypothesis; no constant-R equivalent.
        g = 2*np.pi*freq*70e-12*delta
        voltage = np.sqrt(4*KB*TEMP*g)/(2*np.pi*freq*70e-12)
        axes[1].loglog(freq, voltage*1e9, label=f'assumed tan(delta)={delta:g}')
    write_csv(out/'charge-reset-loss.csv', rows)
    for axis in axes:
        axis.set_xlabel('Frequency (Hz)'); axis.set_ylabel('Node ASD (nV/sqrt(Hz))')
        axis.grid(True, which='both', alpha=.25); axis.legend(fontsize=8)
    axes[0].set_title('Isolated leakage RC thermal noise')
    axes[1].set_title('Supplementary passive-loss hypotheses')
    fig.suptitle('70 pF / 298.15 K; analytic node models, no acoustic noise rating')
    fig.tight_layout(); fig.savefig(out/'loss-noise.png', dpi=160); plt.close(fig)
    # Reduced capacitance matrix with grounded common backplate/case.
    matrices=[]
    for cf, cr in [(45e-12,100e-12),(100e-12,45e-12),(70e-12,70e-12)]:
        for cross in [0,5e-12]:
            matrix=np.array([[cf+10e-12+cross,-cross],[-cross,cr+10e-12+cross]])
            values=np.linalg.eigvalsh(matrix)
            assert min(values)>0
            matrices.append(dict(CF_F=cf,CR_F=cr,PAR_F=10e-12,CROSS_F=cross,
                                 eigen_min_F=min(values),eigen_max_F=max(values),
                                 bridge_static_imbalance_fraction=(cf-cr)/(cf+cr)))
    write_csv(out/'capacitance-matrix.csv', matrices)
    # Local voltage-source piston softening diagnostic, not collapse voltage.
    soft=[]
    for lam in [0,.1,.3]:
        soft.append(dict(assumed_lambda=lam,sensitivity_multiplier=1/(1-lam)))
    write_csv(out/'softening.csv',soft)
    controls={'units_checked':True,'capacitance_finite_difference_rtol':1e-8,
              'membrane_area_quadrature_rtol':1e-10,'RC_band_quadrature_rtol':1e-8,
              'kTC_full_band_identity':True,'capacitance_matrix_positive':True,
              'K47FRB_geometry_established':False,'absolute_noise_overload_bias_established':False}
    (out/'math-controls.json').write_text(json.dumps(controls,indent=2)+'\n')


def plots(out, rows):
    usable=[r for r in rows if r['candidate']!='candidate_0012' and 'response_deviation_db' in r]
    ids=list(dict.fromkeys(r['scenario'] for r in usable))
    fig, axes=plt.subplots(2,1,figsize=(11,7),sharex=True)
    for c in ['candidate_0017','candidate_0019','candidate_0023']:
        data={r['scenario']:r for r in usable if r['candidate']==c}
        axes[0].plot(range(len(ids)),[data.get(s,{}).get('response_deviation_db',np.nan) for s in ids],'.-',label=c)
        axes[1].semilogy(range(len(ids)),[data.get(s,{}).get('noise_pa_rms_conditional',np.nan)*1e3 for s in ids],'.-',label=c)
    axes[0].axhline(1,color='black',ls='--',lw=.8)
    axes[0].set_ylabel('Response deviation (dB)')
    axes[1].set_ylabel('Conditional electronics noise (mPa rms)')
    axes[1].set_xticks(range(len(ids)),ids,rotation=60,ha='right',fontsize=7)
    for ax in axes:ax.grid(alpha=.3);ax.legend(fontsize=8)
    fig.suptitle('Finite electrical scenarios; no production or acoustic qualification')
    fig.tight_layout();fig.savefig(out/'scenario-sensitivity.png',dpi=160);plt.close(fig)
