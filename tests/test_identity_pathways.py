"""Unit tests for source-backed reference-identity QA (not scientific signoff)."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from transhazard.identity_review import read,get_reference_structures,run_registry_audit,REFERENCE,PATHWAYS,XIONG

class IdentityPathwayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chem=read(REFERENCE)
        cls.routes=read(PATHWAYS)
        cls.xiong=read(XIONG)
        cls.compounds,cls.issues=get_reference_structures(cls.chem)

    def test_reference_structures_sanitized(self):
        self.assertEqual(len(self.compounds),17,self.issues)
        self.assertEqual(self.issues,[])
        self.assertAlmostEqual(self.compounds["27619-97-2"]["MW"],428.17,places=1)
        self.assertAlmostEqual(self.compounds["307-24-4"]["MW"],314.05,places=1)
        self.assertEqual(self.compounds["50-29-3"]["formula"],"C14H9Cl5")
        self.assertEqual(self.compounds["72-54-8"]["formula"],"C14H10Cl4")
        self.assertEqual(self.compounds["72-55-9"]["formula"],"C14H8Cl4")
        self.assertEqual(self.compounds["1022-22-6"]["formula"],"C14H9Cl3")
        self.assertEqual(self.compounds["121-75-5"]["formula"],"C10H19O6PS2")
        self.assertEqual(self.compounds["1634-78-2"]["formula"],"C10H19O7PS")

    def test_isomers_not_silently_mixed(self):
        self.assertNotEqual(self.compounds["50-29-3"]["inchi_key"],
                            self.compounds["789-02-6"]["inchi_key"])
        self.assertNotEqual(self.compounds["72-54-8"]["inchi_key"],
                            self.compounds["53-19-0"]["inchi_key"])

    def test_pathway_gate(self):
        report,molar=run_registry_audit(self.chem,self.routes,self.xiong)
        self.assertEqual(report["status"],"PASS",report["blocking_issues"])
        self.assertEqual((report["n_pathway_hypotheses"],len(molar)),(11,3))
        self.assertEqual((report["n_approved_assay_identities"],
                          report["n_independent_scientific_approvals"]), (0,0))
        self.assertEqual(report["dataset_v2_status"],"NO_GO")
        self.assertEqual(set(x["candidate_id"] for x in molar),
                         {"XIONG2023_02","XIONG2023_03","XIONG2023_04"})

    def test_organism_only_not_environmental_proof(self):
        route={r["route_id"]:r for r in self.routes}
        self.assertTrue(route["XIONG2023_02"]["environmental_pathway_evidence_class"].startswith("IN_ORGANISM"))
        self.assertEqual(route["XIONG2023_01"]["product_CAS"],"")
        self.assertTrue(route["MOUNT25_OPDDT_TO_OPDDD"]["route_screening_status"].startswith("HOLD"))
        self.assertTrue(all(r["independent_approved"]=="NO" for r in self.routes))

    def test_rejects_unreviewed_approval(self):
        bad=[dict(x) for x in self.routes];bad[0]["independent_approved"]="YES"
        report,_=run_registry_audit(self.chem,bad,self.xiong)
        self.assertEqual(report["status"],"FAIL")
        self.assertTrue(any("Premature" in x for x in report["blocking_issues"]))

    def test_rejects_unsupported_methylacetaminophen_isomer(self):
        bad=[dict(x) for x in self.routes]
        for r in bad:
            if r["route_id"]=="XIONG2023_01":
                r["product_CAS"]="123-45-6"
        report,_=run_registry_audit(self.chem,bad,self.xiong)
        self.assertEqual(report["status"],"FAIL")
        self.assertTrue(any("regioisomer" in x for x in report["blocking_issues"]))

if __name__=="__main__":unittest.main()
