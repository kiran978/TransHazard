"""Source-recovery release gate for Li 2026 and Yuan 2023.

Provenance: publisher article/abstract, SI index (not downloaded), EFSA 2015
revised assessment. No exact LC50 point estimates extracted from either SI.
"""
import csv
import json
import argparse
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/"data/new_sources_Li2026_Yuan2023_HOLD_UNAPPROVED.csv"
REVIEW=REPO/"review/new_source_independent_expert_FORM_BLANK.csv"

def load(path):
    with open(path,encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def audit(rows,review_rows):
    issues=[]
    if len(rows)!=3:issues.append("Expected exactly three source-review route hypotheses.")
    if len(review_rows)!=3:issues.append("Expected exactly three blank expert-review forms.")
    ids=[r["route_id"] for r in rows]
    if len(set(ids))!=len(ids):issues.append("Duplicate route hypothesis.")
    if set(ids)!={x["route_id"] for x in review_rows}:issues.append("Expert form routes do not match.")
    for r in rows:
        rid=r["route_id"]
        if r["eligible_for_model"]!="NO":issues.append(f"{rid}: unverified model eligibility assertion.")
        if not r["internal_eligibility_recommendation"].startswith("HOLD_"):
            issues.append(f"{rid}: must remain on HOLD pending original supplemental measurements.")
        if r["independent_reviewer_decision"]!="NOT_RETURNED":
            issues.append(f"{rid}: claimed independent signoff without reviewed evidence.")
        if r["point_estimate_parent"] or r["point_estimate_product"]:
            issues.append(f"{rid}: exact primary LC50 fabricated or prematurely imported.")
        if r["chemical_standards_verified"]!="NO":
            issues.append(f"{rid}: chemistry standard not independently verified.")
        if not r["toxicity_source_url"].startswith("https://"):
            issues.append(f"{rid}: missing publication URL.")
        if not r["source_primary_supplement_url"].startswith("https://"):
            issues.append(f"{rid}: missing supplemental source URL.")
        if "PDF" not in r["supplement_retrieval_status"]:
            issues.append(f"{rid}: supplemental retrieval state must be explicit.")
    by_id={r["route_id"]:r for r in rows}
    for cas,value in (
        ("NEW_YUAN2023_SFX_X11719474",">205000"),
        ("NEW_YUAN2023_SFX_X11519540",">350000")
    ):
        row=by_id.get(cas)
        if row is None or row["censored_crosscheck_LC50_text"].strip()!=value:
            issues.append(f"{cas}: EFSA right-censoring information corrupted.")
        if row and row["crosscheck_units"]!="ug/L":
            issues.append(f"{cas}: EFSA crosscheck units modified.")
    li=by_id.get("NEW_LI2026_HHCB_LACTONE")
    if li and (li["parent_LC50_reported_text"]!="150.8-350.2"
        or li["product_LC50_reported_text"]!="138.4-464.9"):
        issues.append("Li 2026 abstract-reported ranges were overwritten with unsourced values.")
    for r in review_rows:
        rid=r["route_id"]
        for k in ("external_scientist_decision_ACCEPT_HOLD_EXCLUDE",
                  "external_scientist_reason","reviewer_provenance_token",
                  "private_signed_record_reference","scientific_review_date",
                  "steward_released_Y_N"):
            if r.get(k,""):issues.append(f"{rid}: supposedly blank reviewer field {k} is filled.")
        if r.get("record_status")!="PENDING":
            issues.append(f"{rid}: reviewer form prematurely marked complete.")
    return {
        "qa_status":"PASS" if not issues else "FAIL",
        "new_transformation_hypotheses":len(rows),
        "distinct_new_toxicity_publications":len({r["toxicity_publication"] for r in rows}),
        "retrieved_full_supplements":0,
        "exact_source_extracted_new_pair_ratios":0,
        "eligible_for_human_review":len(rows),
        "human_independent_accepted":0,
        "training_eligible_from_this_batch":0,
        "dataset_v2_release":"NO_GO",
        "recorded_efsa_cross_study_bounds_ug_L":{"X11719474":">205000","X11519540":">350000"},
        "issues":issues,
        "limitation":"Sources indexed, original supplement PDFs not actually retrieved; publications and regulatory thresholds cannot authenticate independent adjudication."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--report",default="outputs/new_source_recovery_gate.json")
    args=p.parse_args()
    r=audit(load(SOURCE),load(REVIEW))
    dest=Path(args.report);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2))
    raise SystemExit(0 if r["qa_status"]=="PASS" else 1)
