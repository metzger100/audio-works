# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce comparison002; verify original bytes before deriving supported axes."""
from pathlib import Path
from types import SimpleNamespace
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"src"),str(Path(__file__).parent)]
from meridian_lab.core import read_yaml,digest,environment_versions
from meridian_lab.bounded import write_data
import comparison_common as common
import comparison_metrics as metrics
from comparison_002_tables import csv,finite_summary,tables,plot

OUT=ROOT/"results/reports/architecture_comparison_002"


def main():
    inputs={};checked={}
    def evidence(path):
        p=Path(path)
        if not p.is_absolute():p=ROOT/p
        inputs[str(p.relative_to(ROOT))]=digest(p)
        return p
    def load(path):
        return read_yaml(evidence(path))
    def verify(path,sha):
        p=evidence(path)
        if digest(p)!=sha:raise ValueError("Missing/changed original: "+str(p))
        checked[str(p.relative_to(ROOT))]=sha
    def jobs(value):
        if isinstance(value,dict):
            if "folder" in value and "netlist_sha256" in value:
                verify(Path(value["folder"])/"job.cir",value["netlist_sha256"])
                for n,h in value.get("files",{}).items():verify(Path(value["folder"])/n,h)
            for v in value.values():jobs(v)
        elif isinstance(value,list):
            for v in value:jobs(v)
    cohort=load(OUT/"cohort.json");batch=Path(cohort["batch"])
    if not cohort["complete"]:raise ValueError("Finite cohort is incomplete")
    verify(batch/"results.json",cohort["results_sha256"])
    result=load(batch/"results.json");manifest=load(batch/"manifest.json")
    assert result["source_unchanged"]
    for n,h in manifest["sources"].items():verify(batch/"source"/n,h)
    for c,m in manifest["implementations"].items():
        for n,h in m.items():verify(batch/"implementations"/c/n,h)
    plan=load(batch/"plan.json")["plan"]
    records={c:load(Path("results/runs")/e/"results.json") for c,e in result["full_suite"].items()}
    common.require_common(list(records.values()))
    for c,r in records.items():
        folder=Path("results/runs")/r["experiment_id"]
        for n,h in r["source_manifest"].items():verify(folder/"source"/n,h)
        for n,h in r["implementation_manifest"].items():verify(folder/n,h)
        assert not r["eligible"]
        assert digest(ROOT/folder/"circuit.cir")==plan["representatives"][c]["netlist_sha256"]
        assert digest(ROOT/folder/"bom.yaml")==plan["representatives"][c]["bom_sha256"]
        jobs(r["jobs"])
    jobs(result["rows"])
    data=SimpleNamespace(evidence=evidence,contributions=[],spectra=[])
    nominal=[];coverage=[];boms=[];unknown=[];costs=[]
    common.OUT=OUT;metrics.OUT=OUT
    for c,r in records.items():
        folder=ROOT/"results/runs"/r["experiment_id"]
        bom=load(folder/"bom.yaml")
        choice={"name":plan["representatives"][c]["role"]}
        row=metrics.nominal_metrics(c,choice,r,bom,folder);nominal.append(row)
        metrics.noise_metrics(data,c,r,row)
        elements=common.parse_elements(evidence(folder/"circuit.cir").read_text(),r["simulation_configuration"])
        csv(OUT,c.replace("_","-")+"-connectivity.csv",elements)
        common.diagram(c,elements)
        for p in bom["physical_parts"]:boms.append(dict(candidate=c,**p))
        for n,x in r["checks"].items():coverage.append(dict(candidate=c,check=n,status=x["status"],reason=x.get("reason"),coverage=x.get("coverage")))
        for n in ["H2","H3","H4-H10","THD","electronics_clipping","headroom","maximum_acoustic_SPL"]:
            unknown.append(dict(candidate=c,metric=n,value=None,reason="Full DUT settled nonlinear prerequisites unsupported; no hardware/acoustic inference",evidence_check=r["checks"]["distortion"]["status"]))
        costs.append(dict(candidate=c,intended_microphones=1,electronics_partial_net_eur=bom["electronics_cost"]["priced_items_net_eur_scenario"],
            partial_date="2026-10-09; retained historical catalogue scenario",electronics_delivered_eur=None,
            fixed_capsule="one K47FRB",capsule_delivered_eur=None,other_implementation_eur=None,
            shipping_eur=None,tax_import_fees_eur=None,pack_excess=None,
            reason="No complete dated private Germany basket; no cost dominance"))
    refinement=[]
    for c in plan["matched_realized"]:
        a=next(r for r in result["rows"] if r["candidate"]==c and r["scenario"]=="baseline")
        b=next(r for r in result["rows"] if r["candidate"]==c and r["scenario"]=="nominal_refinement")
        refinement.append(dict(candidate=c,response64_to128_db_delta=b.get("response_deviation_db",0)-a.get("response_deviation_db",0) if "response_deviation_db" in a and "response_deviation_db" in b else None,
            noise128_to256_relative=b["noise_pa_rms"]/a["noise_pa_rms"]-1 if a.get("noise_pa_rms") and b.get("noise_pa_rms") else None,
            numerical_only=True,physical_model_error_bound=None))
    versions=load(batch/"source/research/patents/candidate-versions-001.json")
    bindings={item["candidate_id"]:item for item in versions["candidates"]}
    for c in records:
        assert bindings[c]["circuit_sha256"] == plan["representatives"][c]["netlist_sha256"]
    sources=load(batch/"source/research/architectures/comparison-sources-002-followup.json")
    for s in sources["sources"]:
        if s.get("path"):verify(batch/"source"/s["path"],s["sha256"])
    refresh=[dict(publication=p,territory="DE",observed_date="2026-10-17",status=s,
             change_from_16October="same observed label; other rights not inferred",source_id=i,
             claims_and_family_scope="screening001 exact-version maps; incomplete",gates="hold")
             for p,s,i in [("EP2675188B1","Anhängig/in Kraft","dpma_charge"),
                ("EP1585365B1","Nicht anhängig/erloschen","dpma_expired"),
                ("EP2974369B1","Nicht anhängig/erloschen;1October2020 nonpayment","dpma_reset")]]
    realization=[]
    old=load(batch/"source/results/optimization_batches/20261009T090126Z_4735cd2a/evaluation.json")
    for c,r in records.items():
        family=r["topology"]["family"]
        if family not in old["continuous"]:continue
        parent=load(Path("results/runs")/old["continuous"][family]["experiment"]/"results.json")
        actual=r["simulation_configuration"];continuous=parent["simulation_configuration"]
        for k,v in actual.items():
            if k in continuous and v!=continuous[k]:realization.append(dict(candidate=c,parameter=k,actual=v,continuous=continuous[k],delta=v-continuous[k],parent_experiment=parent["experiment_id"],scope="Identity/value delta only; historical performance not pooled"))
    output=dict(date="2026-10-17",scope=plan["scope"],batch=str(batch),records=records,
        nominal_metrics=nominal,coverage=coverage,bom=boms,matched_rows=result["rows"],
        noise_contributions=data.contributions,spectra=data.spectra,refinement=refinement,
        harmonics_headroom=unknown,finite_summaries=finite_summary(result["rows"]),costs=costs,
        source_refresh=sources,patent_refresh=refresh,realization_deltas=realization,
        families=load(batch/"source/search/families.yaml"),concepts=load(batch/"source/search/concepts.yaml"),
        patent_versions=versions,claim_mapping=load(batch/"source/research/patents/claim-mappings-001.json"),
        patent_territories=load(batch/"source/research/patents/territory-status-001.json"),
        patent_holds=load(batch/"source/research/patents/holds-screening-001.json"),
        physical_measurements=[],production_selection=None,all_requirement_yield=None)
    tables(OUT,output);plot(OUT,nominal,result["rows"],data.spectra,records)
    write_data(OUT/"comparison.json",output)
    for p in Path(__file__).parent.glob("*002*.py"):evidence(p)
    write_data(OUT/"provenance.json",dict(date="2026-10-17",verified_files=len(checked),
        input_sha256=inputs,verified_declared_files=checked,reporting_versions=environment_versions(),
        output_sha256={str(p.relative_to(OUT)):digest(p) for p in sorted(OUT.rglob("*")) if p.is_file() and p.name!="provenance.json" and p.suffix not in {".log"}},
        common_spec_sha256=next(iter(records.values()))["spec_sha256"],common_suite_sha256=next(iter(records.values()))["suite_sha256"],
        source_unchanged=True,originals_modified=False,physical_measurements=[],production_front=[]))
    print(json.dumps(dict(records=len(records),matched_cells=len(result["rows"]),verified_files=len(checked),output=str(OUT))))


if __name__=="__main__":
    main()
