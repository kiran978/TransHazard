import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from transhazard.evidence_audit import analyze,load
class Mount2025SourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.p=load(ROOT/"data/candidates_UNAPPROVED.csv")
        self.m=load(ROOT/"data/mount2025_route_comparisons_UNAPPROVED.csv")
        self.e=load(ROOT/"data/mount2025_source_endpoints_UNAPPROVED.csv")
    def test_count_and_provenance(self):
        r=analyze(self.p,self.m,self.e)
        self.assertEqual(r["validation_status"],"PASS",r["errors"])
        self.assertEqual((r["original_priority_rows"],r["mount_source_endpoints"],
                         r["mount_provisional_comparison_rows"]), (6,16,12))
        self.assertEqual((r["overlaps_deduplicated"],r["new_nonduplicate_assay_rows"]), (3,9))
        self.assertEqual((r["unique_combined_assay_observations"],r["distinct_chemical_transformation_routes"]), (15,7))
        self.assertEqual((r["distinct_source_publications"],r["distinct_chemical_networks"]), (3,3))
        self.assertEqual((r["independent_reviewer_approved"],r["training_status"]), (0,"NO_GO"))
    def test_rejects_bad_source_point(self):
        m=[r.copy() for r in self.m]
        m[0]["parent_conc"]="0.99"
        r=analyze(self.p,m,self.e)
        self.assertEqual(r["validation_status"],"FAIL")
        self.assertTrue(any("estimate mismatch" in e or "invalid molar ratio" in e for e in r["errors"]))
    def test_rejects_false_training_approval(self):
        m=[r.copy() for r in self.m]
        m[0]["eligible_for_training"]="YES"
        r=analyze(self.p,m,self.e)
        self.assertEqual(r["validation_status"],"FAIL")
    def test_rejects_uncertainty_misrepresentation(self):
        m=[r.copy() for r in self.m]
        m[0]["uncertainty_interpretation"]="FORMAL_95CI"
        r=analyze(self.p,m,self.e)
        self.assertEqual(r["validation_status"],"FAIL")
if __name__=="__main__":unittest.main()
