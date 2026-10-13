#!/usr/bin/env python3
"""Dataset audit, release gate, and conditional parent-product model development."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from transhazard.core import load_csv, write_json, audit_candidates, validate_approved_rows, model_readiness, fit_development

p=argparse.ArgumentParser(description="TransHazard scientific release guardrails")
p.add_argument("--mode",choices=["audit","train"],default="audit")
p.add_argument("--input",default="data/candidates_UNAPPROVED.csv")
p.add_argument("--release-metadata",default="data/approval_metadata_EXAMPLE_NOT_AUTHORIZED.json")
p.add_argument("--output-dir",default="outputs")
a=p.parse_args()
out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
rows=load_csv(a.input)
if a.mode=="audit":
    report=audit_candidates(rows)
    write_json(out/"candidate_audit.json",report)
    print(json.dumps(report,indent=2))
    sys.exit(1 if report["arithmetic_or_integrity_errors"] else 0)
meta=json.loads(Path(a.release_metadata).read_text(encoding="utf-8"))
errors=validate_approved_rows(rows,meta)
report={"task":"approved_Dataset_v2_and_parent_product_model",
        "n_rows":len(rows),"release_validation_errors":errors,
        "model_status":"NOT_TRAINED","scientific_release_status":"NO_GO",
        "authentication_limitation":"Code cannot authenticate human signatures, reviewer independence or source evidence."}
if not errors:
    report["assay_feasibility"]=model_readiness(rows)
    if any(c["status"]=="ELIGIBLE_FOR_DEVELOPMENT" for c in report["assay_feasibility"]):
        report["models"]=fit_development(rows,out)
        if any(x.get("selected_model") for x in report["models"]):
            report["model_status"]="DEVELOPMENT_MODELS_ONLY"
    report["scientific_release_status"]="REQUIRES_HUMAN_AUTHENTICATION_AND_EXTERNAL_VALIDATION"
write_json(out/"model_gate.json",report)
print(json.dumps(report,indent=2))
sys.exit(2 if report["model_status"]=="NOT_TRAINED" else 0)
