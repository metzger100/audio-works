# SPDX-License-Identifier: GPL-3.0-or-later
"""Scoped finite statistics, source/claim/cost tables and static comparison plots."""
from collections import Counter
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meridian_lab.bounded import write_csv, write_data
from comparison_common import pareto


def csv(out, name, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    write_csv(out / name, rows, fields or ["state"])


def finite_summary(rows):
    """Every failed/error attempt stays in n; intervals apply only to IID holdouts."""
    summaries = []
    for c in sorted({r["candidate"] for r in rows}):
        for held in [False, True]:
            sample = [r for r in rows if r["candidate"] == c and r["holdout"] == held]
            n = len(sample)
            k = sum(r["status"] == "pass" for r in sample)
            values = [r["response_deviation_db"] for r in sample if r.get("response_deviation_db") is not None]
            interval = ([float(beta.ppf(.025,k,n-k+1)) if k else 0.,
                         float(beta.ppf(.975,k+1,n-k)) if k<n else 1.] if held and n else None)
            summaries.append(dict(candidate=c, holdout=held, attempts=n, screens_pass=k,
                error_count=sum(r["status"]=="error" for r in sample),
                failed_count=sum(r["status"]=="fail" for r in sample),
                statuses=dict(Counter(r["status"] for r in sample)),
                all_requirement_yield=None, artificial_screen_fraction=k/n if n else None,
                exact_95percent_interval=interval, finite_responses=len(values),
                worst_response_db=max(values) if values else None,
                empirical_p95_db=float(np.percentile(values,95)) if values else None,
                scope="DC/AC feasibility of finite artificial scenarios only; noise availability does not qualify it"))
    return summaries


def research_front(nominal):
    rows = [r for r in nominal if r["candidate"] in {"candidate_0017","candidate_0019","candidate_0023","candidate_0025"}]
    axes = ["response_deviation_db", "current_a", "installed_count"]
    return dict(scope="Nominal DC/AC/count only; identical JFE/BC model scope; no noise/yield/cost dominance",
                axes_all_minimize=axes, candidates=pareto(rows,axes), rows=rows,
                excluded=["different-device controls","unvalidated noise","missing nonlinear","unknown delivered costs","continuous proposals"],
                production_front=[], physical_qualified_front=[], gates_relaxed=False)


def plot(out, nominal, rows, spectra, records):
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout="constrained")
    for r in nominal:
        c=r["candidate"]
        ac=records[c]["checks"]["frequency_response"]["metrics"]
        if ac:
            f=np.asarray(ac["frequency_hz"]);g=np.asarray(ac["gain_v_per_pa"])
            axes[0].semilogx(f,20*np.log10(g/np.interp(1000,f,g)),label=c[-4:])
        s=[s for s in spectra if s["candidate"]==c]
        if s:
            axes[1].loglog([v["frequency_hz"] for v in s],
                [v["electronics_pressure_asd_pa_sqrt_hz"] for v in s],label=c[-4:])
    axes[0].set(xlim=(20,20000),xlabel="Frequency (Hz)",ylabel="Normalized response (dB)")
    axes[1].set(xlabel="Frequency (Hz)",ylabel="Conditional electronics ASD (Pa/√Hz)")
    fig.suptitle("Common cohort; stationary modeled sources; no acoustic/noise qualification")
    for ax in axes:
        ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.savefig(out/"response-noise.png",dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout="constrained")
    for c in ["candidate_0017","candidate_0019","candidate_0023","candidate_0025"]:
        points=[r for r in rows if r["candidate"]==c and r["scenario"] in
                ["leakage_low","leakage10G","leakage100G","leakage_high"]]
        points.sort(key=lambda r:r["declared"]["parameters"]["LEAK"])
        x=[r["declared"]["parameters"]["LEAK"] for r in points]
        axes[0].loglog(x,[r.get("noise_pa_rms",np.nan)*1e6 for r in points],"o-",label=c[-4:])
        axes[1].semilogx(x,[r.get("response_deviation_db",np.nan) for r in points],"o-",label=c[-4:])
    axes[0].set(ylabel="Conditional electronics noise (µPa RMS)")
    axes[1].set(ylabel="Response deviation (dB)")
    axes[1].axhline(1,color="gray",ls=":")
    for ax in axes:
        ax.set_xlabel("Leakage per diaphragm (Ω)");ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.suptitle("Retained adverse cases; no full-envelope winner")
    fig.savefig(out/"leakage-regions.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.8),layout="constrained")
    for r in research_front(nominal)["rows"]:
        ax.scatter(r["current_a"]*1000,r["response_deviation_db"])
        ax.annotate(r["candidate"][-4:]+f" ({r['installed_count']})",(r["current_a"]*1000,r["response_deviation_db"]),xytext=(4,5),textcoords="offset points",fontsize=8)
    ax.set(xlabel="Modeled P48 current (mA)",ylabel="Response deviation (dB)",title="JFET nominal DC/AC/count research projection; qualified front empty")
    ax.grid(alpha=.2);fig.savefig(out/"research-pareto.png",dpi=180);plt.close(fig)


def tables(out, data):
    nominal,rows=data["nominal_metrics"],data["matched_rows"]
    for name,entries in [("nominal-metrics",nominal),("coverage",data["coverage"]),
            ("matched-scenarios",[{k:v for k,v in r.items() if k not in {"dc","ac","jobs","contributions"}} for r in rows]),
            ("bom",data["bom"]),("noise-contributions",data["noise_contributions"]),
            ("noise-spectra",data["spectra"]),("uncertainty",data["finite_summaries"]),
            ("refinement",data["refinement"]),("harmonics-headroom",data["harmonics_headroom"]),
            ("source",data["source_refresh"]["sources"]),("cost",data["costs"]),
            ("patent-status-refresh",data["patent_refresh"]),("realization-deltas",data["realization_deltas"])]:
        csv(out,name+".csv",entries)
    write_data(out/"research-pareto.json",research_front(nominal))
    write_data(out/"production-front.json",dict(front=[],physical_qualified_front=[],gates_relaxed=False,
        required="Unchanged complete suite, validated device/noise/production/physical evidence; separate procurement/patent gates"))
    lines=["# Common-cohort tables — 17 October 2026","",
        "Conditional numerical research; all implementations unqualified. Full reasons/raw identities remain in the machine records.","",
        "|Candidate|mA|Rail V|Bias V|Response dB|Noise µPa / A µPa|Count|",
        "|---|---:|---:|---:|---:|---:|---:|"]
    def fmt(x,scale=1):
        return "unknown" if x is None else f"{x*scale:.6g}"
    for r in nominal:
        lines.append(f"|{r['candidate'][-4:]}|{fmt(r['current_a'],1000)}|{fmt(r['rail_v'])}|{fmt(r['simulated_polarization_v'])}|{fmt(r['response_deviation_db'])}|{fmt(r['noise_pa_rms'],1e6)} / {fmt(r['noise_a_pa_rms'],1e6)}|{r['installed_count']}|")
    lines += ["","Noise is conditional on unvalidated model spectra and assumed capsule transfer; capsule/environment Johnson surrogates are excluded. Carrier current/count are partial ideal-control accounting.","",
        "[All check states](coverage.csv) · [Exact BOM](bom.csv) · [Uncertainty and denominators](uncertainty.csv) · [Holdouts and adverse cases](matched-scenarios.csv) · [Realization deltas](realization-deltas.csv)","",
        "## Exact implementations", ""]
    for c,r in data["records"].items():
        eid=r["experiment_id"]
        lines += [f"- {c}: [frozen netlist](../../runs/{eid}/circuit.cir), [BOM](../../runs/{eid}/bom.yaml), [complete suite](../../runs/{eid}/results.json), [connectivity]({c.replace('_','-')}-connectivity.svg)"]
    lines += ["","## Finite holdout screen","","|Candidate|Pass / attempted|Errors|Exact95% interval|Worst finite dB|","|---|---:|---:|---|---:|"]
    for r in data["finite_summaries"]:
        if r["holdout"]:
            lines.append(f"|{r['candidate'][-4:]}|{r['screens_pass']} / {r['attempts']}|{r['error_count']}|{r['exact_95percent_interval']}|{fmt(r['worst_response_db'])}|")
    lines += ["","Intervals concern the declared artificial DC/AC sampler only; they are not production yield or all-requirement pass rates."]
    (out/"tables.md").write_text("\n".join(lines)+"\n")
