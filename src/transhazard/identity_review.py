"""Chemical reference-identity and environmental-pathway QA.

Reference structure verification is NOT authentication of the chemicals used in an assay.
No human reviewer decision is imputed by this script.
"""
import argparse
import csv
import json
import math
from pathlib import Path
from collections import defaultdict
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

ROOT=Path(__file__).resolve().parents[2]
REFERENCE=ROOT/"data/chemical_identity_reference_NOT_ASSAY_APPROVED.csv"
PATHWAYS=ROOT/"data/environmental_pathway_evidence_11_routes_UNAPPROVED.csv"
XIONG=ROOT/"data/xiong2023_table2_UNAPPROVED.csv"

def read(path):
    with open(path,encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def get_reference_structures(rows):
    structures={}
    warnings=[]
    for row in rows:
        cas=row["CAS"]
        if cas in structures: warnings.append(f"Duplicate CAS: {cas}");continue
        mol=Chem.MolFromSmiles(row["proposed_structure_smiles"])
        if mol is None: warnings.append(f"Invalid structure for {cas}");continue
        if row["approved_for_modeling"]!="NO" or row["source_standard_stereochemistry_verified"]!="NO":
            warnings.append(f"Premature approval assertion: {cas}")
        structures[cas]={"name":row["compound_label"],
                         "smiles":Chem.MolToSmiles(mol,isomericSmiles=True),
                         "inchi_key":Chem.MolToInchiKey(mol),
                         "formula":rdMolDescriptors.CalcMolFormula(mol),
                         "MW":Descriptors.MolWt(mol),
                         "ref":row["structure_reference"]}
    return structures,warnings

def run_registry_audit(structure_rows,pathways,xiong):
    compounds,issues=get_reference_structures(structure_rows)
    known_cas=set(compounds)
    route_types={}
    for r in pathways:
        key=r["route_id"]
        if key in route_types: issues.append("Duplicate route ID "+key)
        route_types[key]=r["environmental_pathway_evidence_class"]
        if r["independent_approved"]!="NO":
            issues.append("Premature environmental route approval "+key)
        if r["route_screening_status"].strip()=="":
            issues.append("Missing route-screening decision "+key)
        if not r["transformation_evidence_source"].startswith("https://"):
            issues.append("Missing transformation literature URL "+key)
        for side in ("parent","product"):
            cas=r[f"{side}_CAS"]
            if cas and cas not in known_cas:
                issues.append(f"Missing {side} reference structure for {key}:{cas}")
        if key=="XIONG2023_01" and r["product_CAS"]:
            issues.append("O/N regioisomer of methylated acetaminophen inferred without source confirmation.")
    xiong_molar=[]
    by_id={r["route_id"]:r for r in pathways}
    for r in xiong:
        rid=r["candidate_id"]
        pathway=by_id.get(rid)
        if not pathway:
            issues.append(f"No pathway row for {rid}");continue
        if r["eligible_for_training"]!="NO" or r["independent_review_status"]!="NOT_RETURNED":
            issues.append(f"Xiong record incorrectly training eligible {rid}")
        parent_cas=pathway["parent_CAS"]
        product_cas=pathway["product_CAS"]
        if parent_cas and product_cas and parent_cas in compounds and product_cas in compounds:
            pa,pr=compounds[parent_cas],compounds[product_cas]
            rp=float(r["parent_LC50_mg_L"])
            rt=float(r["product_LC50_mg_L"])
            ratio=(rt/pr["MW"])/(rp/pa["MW"])
            if not math.isclose(rt/rp,float(r["product_parent_mass_LC50_ratio"]),rel_tol=1e-8):
                issues.append(f"Mass ratio check failed for {rid}")
            xiong_molar.append({
                "candidate_id":rid,"parent":r["parent"],"product":r["product"],
                "parent_reference_CAS":parent_cas,"product_reference_CAS":product_cas,
                "parent_reference_MW":f"{pa['MW']:.6f}",
                "product_reference_MW":f"{pr['MW']:.6f}",
                "molar_product_parent_LC50_ratio_PROVISIONAL":f"{ratio:.9f}",
                "delta_log10_PROVISIONAL":f"{math.log10(ratio):.9f}",
                "conditional_identity_note":"Valid only if source test standard matches the proposed neutral-isomer structures and MW basis; do not train",
                "environmental_evidence":pathway["environmental_pathway_evidence_class"],
                "reviewer_approval":"NO",
                "training_eligibility":"NO"
            })
        else:
            # A blocked identity cannot silently supply a molar toxicity-change effect.
            if rid!="XIONG2023_01":issues.append(f"Unexpected unresolved identity for {rid}")
    if len(xiong_molar)!=3:issues.append("Expected exactly three provisional Xiong molar ratios")
    result={"status":"PASS" if not issues else "FAIL",
        "n_reference_chemical_identifiers":len(compounds),
        "n_pathway_hypotheses":len(pathways),
        "n_xiong_molar_point_estimates_conditional":len(xiong_molar),
        "n_approved_assay_identities":0,
        "n_independent_scientific_approvals":0,
        "dataset_v2_status":"NO_GO",
        "reviewer_required":True,
        "reference_identity_scope":"Named CAS/structure registry only; does not verify source study assay standards, exposure species, or their exact chemical form",
        "route_evidence_classes":{key:sum(r["environmental_pathway_evidence_class"]==key for r in pathways)
            for key in sorted({r["environmental_pathway_evidence_class"] for r in pathways})},
        "blocking_issues":issues}
    return result,xiong_molar

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--report",default="outputs/identity_pathway_gate.json")
    ap.add_argument("--molar",default="outputs/xiong2023_molar_PROVISIONAL_NOT_APPROVED.csv")
    args=ap.parse_args()
    result,xiong_molar=run_registry_audit(read(REFERENCE),read(PATHWAYS),read(XIONG))
    p=Path(args.report);p.parent.mkdir(exist_ok=True,parents=True)
    p.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    m=Path(args.molar);m.parent.mkdir(exist_ok=True,parents=True)
    if xiong_molar:
        with m.open("w",newline="",encoding="utf-8") as f:
            dw=csv.DictWriter(f,fieldnames=list(xiong_molar[0].keys()))
            dw.writeheader();dw.writerows(xiong_molar)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)
if __name__=="__main__":main()
