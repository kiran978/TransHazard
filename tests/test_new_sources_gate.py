import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from transhazard.new_sources_gate import audit,load,SOURCE,REVIEW

class PrimarySourceRecoveryGateTests(unittest.TestCase):
    def setUp(self):
        self.source=load(SOURCE)
        self.reviews=load(REVIEW)
    def test_knowledge_and_provenance(self):
        r=audit(self.source,self.reviews)
        self.assertEqual(r["qa_status"],"PASS",r["issues"])
        self.assertEqual(r["new_transformation_hypotheses"],3)
        self.assertEqual(r["distinct_new_toxicity_publications"],2)
        self.assertEqual(r["retrieved_full_supplements"],0)
        self.assertEqual(r["exact_source_extracted_new_pair_ratios"],0)
        self.assertEqual(r["human_independent_accepted"],0)
        self.assertEqual(r["dataset_v2_release"],"NO_GO")
    def test_error_if_censored_efsa_value_becomes_point_value(self):
        bad=[dict(r) for r in self.source]
        for row in bad:
            if row["route_id"]=="NEW_YUAN2023_SFX_X11519540":
                row["censored_crosscheck_LC50_text"]="350000"
        self.assertEqual(audit(bad,self.reviews)["qa_status"],"FAIL")
    def test_error_if_fabricated_li_point(self):
        bad=[dict(r) for r in self.source]
        bad[0]["point_estimate_parent"]="250.5"
        self.assertEqual(audit(bad,self.reviews)["qa_status"],"FAIL")
    def test_error_if_review_faked(self):
        bad=[dict(r) for r in self.reviews]
        bad[0]["external_scientist_decision_ACCEPT_HOLD_EXCLUDE"]="ACCEPT"
        self.assertEqual(audit(self.source,bad)["qa_status"],"FAIL")
if __name__=="__main__":unittest.main()
