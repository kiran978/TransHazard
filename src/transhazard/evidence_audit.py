"""Auditable expansion of Mount (2025) evidence without treating records as labels.

All paths refer to release candidate evidence; training remains prohibited.
"""
import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path


def load(path):
    with open(path,encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def norm_endpoint(ep):
    s=ep.strip().lower().replace(" ","_")
    if s in {"ec50_biomass","biomass_ec50"}:return "EC50_BIOMASS"
    if s in {"biomass_growth_ec50","growth_ec50"}:return "EC50_GROWTH"
    return s.upper()


def key(r):
    return (r["source_study"].strip().upper(),r["parent_CAS"].strip(),
            r["product_CAS"].strip(),r["species"].strip().lower(),
            norm_endpoint(r["endpoint"]),int(float(r["duration_hours"])),
            f'{float(r["parent_conc"]):.8g}',f'{float(r["product_conc"]):.8g}')


def route_key(r):
    return (r["parent_CAS"].strip(),r["product_CAS"].strip())


def analyze(priority,expanded,endpoints):
    errors=[]
    endpoint_index={}
    for r in endpoints:
        k=(r["assay_id"],norm_endpoint(r["endpoint"]))
        if k in endpoint_index:errors.append(f"Endpoint key repeated: {k}")
        endpoint_index[k]=r
        if r["review_status"]!="HOLD_UNAPPROVED":
            errors.append(f"Endpoint improperly approved: {k}")
        for col in ("estimate_ug_L","source_95LCL_ug_L","source_95UCL_ug_L"):
            if not math.isfinite(float(r[col])) or float(r[col])<=0:
                errors.append(f"Bad endpoint {k}: {col}")
        if not (float(r["source_95LCL_ug_L"])<=float(r["estimate_ug_L"])<=float(r["source_95UCL_ug_L"])):
            errors.append(f"Endpoint point estimate outside interval: {k}")
    for i,r in enumerate(expanded,2):
        tag=r["comparison_id"]
        if r["eligible_for_training"]!="NO" or r["independent_review_status"]!="NOT_RETURNED":
            errors.append(f"{tag}: premature approval")
        if int(float(r["duration_hours"]))!=168:
            errors.append(f"{tag}: non-7d context incorrectly included")
        p=endpoint_index.get((r["parent_assay_id"],norm_endpoint(r["endpoint"])))
        t=endpoint_index.get((r["product_assay_id"],norm_endpoint(r["endpoint"])))
        if not p or not t:
            errors.append(f"{tag}: endpoint evidence missing")
            continue
        for side,ref in (("parent",p),("product",t)):
            if r[f"{side}_CAS"]!=ref["CAS"]:errors.append(f"{tag}: CAS mismatches {side} source endpoint")
            if int(float(r["duration_hours"]))!=int(float(ref["duration_hours"])):
                errors.append(f"{tag}: duration mismatches {side} assay")
            if not math.isclose(float(r[f"{side}_conc"]),float(ref["estimate_ug_L"]),rel_tol=1e-10):
                errors.append(f"{tag}: source estimate mismatch {side}")
            if int(r[f"{side}_supplement_page"])!=int(ref["source_supplement_page"]):
                errors.append(f"{tag}: page reference mismatch {side}")
            for colA,colB in ((f"{side}_LCL_95","source_95LCL_ug_L"),(f"{side}_UCL_95","source_95UCL_ug_L")):
                if not math.isclose(float(r[colA]),float(ref[colB]),rel_tol=1e-10):
                    errors.append(f"{tag}: uncertainty limit mismatch {side}")
        ratio=(float(r["product_conc"])/float(r["product_MW"]))/(float(r["parent_conc"])/float(r["parent_MW"]))
        if not math.isclose(ratio,float(r["provisional_molar_ratio"]),rel_tol=1e-9):
            errors.append(f"{tag}: invalid molar ratio")
        if not math.isclose(math.log10(ratio),float(r["delta_log10"]),abs_tol=1e-9):
            errors.append(f"{tag}: invalid logarithmic delta")
        lo=(float(r["product_LCL_95"])/float(r["product_MW"]))/(float(r["parent_UCL_95"])/float(r["parent_MW"]))
        hi=(float(r["product_UCL_95"])/float(r["product_MW"]))/(float(r["parent_LCL_95"])/float(r["parent_MW"]))
        if not math.isclose(lo,float(r["interval_envelope_lower_NOT_95CI"]),rel_tol=1e-9):
            errors.append(f"{tag}: invalid descriptive envelope lower")
        if not math.isclose(hi,float(r["interval_envelope_upper_NOT_95CI"]),rel_tol=1e-9):
            errors.append(f"{tag}: invalid descriptive envelope upper")
        if "NOT_JOINT_95CI" not in r["uncertainty_interpretation"]:
            errors.append(f"{tag}: uncertainty falsely labeled as paired 95 CI")
        if "TRANSFORMATION_REVIEW_PENDING" not in r["review_flags"]:
            errors.append(f"{tag}: reaction-pathway review flag missing")
        if "72-55-9" in (r["parent_CAS"],r["product_CAS"]) and "DDE_FIT_NONUNIQUE_REVIEW" not in r["review_flags"]:
            errors.append(f"{tag}: missing DDE fit caveat")
        if norm_endpoint(r["endpoint"])=="EC50_BIOMASS" and r["product_CAS"]=="1022-22-6":
            if "METHANOL_BIOMASS_CONTROL_P_0.004" not in r["review_flags"]:
                errors.append(f"{tag}: missing DDMU solvent-control caveat")
    priority_keys=[key(r) for r in priority]
    expanded_keys=[key(r) for r in expanded]
    overlap=set(priority_keys).intersection(expanded_keys)
    if len(priority_keys)!=len(set(priority_keys)):
        errors.append("Priority input unexpectedly contains duplicate source/assay observations")
    if len(expanded_keys)!=len(set(expanded_keys)):
        errors.append("Mount expansion repeats an identical assay observation")
    unique={key(r):r for r in priority}
    new=[]
    for r in expanded:
        k=key(r)
        if k in unique:
            q=unique[k]
            if not math.isclose(float(q["provisional_molar_ratio"]),float(r["provisional_molar_ratio"]),rel_tol=1e-8):
                errors.append(f"{r['comparison_id']}: inconsistent duplicate with priority file")
        else:
            unique[k]=r
            new.append(r)
    allrows=list(unique.values())
    if any(r.get("eligible_for_training")!="NO" for r in allrows):
        errors.append("Merged data contain a training-eligible record")
    if any(r.get("independent_review_status")!="NOT_RETURNED" for r in allrows):
        errors.append("Merged data contain a reviewer decision not actually returned")
    groups=Counter((r["source_study"],r["chemical_network"]) for r in allrows)
    return {"validation_status":"PASS" if not errors else "FAIL",
      "errors":errors,
      "original_priority_rows":len(priority),
      "mount_source_endpoints":len(endpoints),
      "mount_provisional_comparison_rows":len(expanded),
      "overlaps_deduplicated":len(overlap),
      "new_nonduplicate_assay_rows":len(new),
      "unique_combined_assay_observations":len(allrows),
      "distinct_chemical_transformation_routes":len({route_key(r) for r in allrows}),
      "distinct_source_publications":len({r["source_study"] for r in allrows}),
      "distinct_chemical_networks":len({r["chemical_network"] for r in allrows}),
      "independent_reviewer_approved":0,
      "training_status":"NO_GO",
      "source_study_network_rows":[{"study":s,"network":n,"n_observations":v} for (s,n),v in sorted(groups.items())],
      "warning":"Publication assay observations and route-linked endpoints are NOT independent predictive validation samples. Supplementary PDF is user-supplied; data remain unapproved."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--priority",default="data/candidates_UNAPPROVED.csv")
    p.add_argument("--expanded",default="data/mount2025_route_comparisons_UNAPPROVED.csv")
    p.add_argument("--source-endpoints",default="data/mount2025_source_endpoints_UNAPPROVED.csv")
    p.add_argument("--report",default="outputs/expanded_evidence_audit.json")
    a=p.parse_args()
    result=analyze(load(a.priority),load(a.expanded),load(a.source_endpoints))
    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.report).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["validation_status"]=="PASS" else 1)
if __name__=="__main__":main()
