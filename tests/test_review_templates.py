import csv,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/name).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

class IndependentReviewTemplateGate(unittest.TestCase):
    def test_route_form_remains_unsigned(self):
        r=read("review/route_adjudication_TEMPLATE_BLANK.csv")
        ledger=read("data/environmental_pathway_evidence_11_routes_UNAPPROVED.csv")
        self.assertEqual(len(r),11)
        self.assertEqual({x["route_id"] for x in r},{x["route_id"] for x in ledger})
        for x in r:
            self.assertIsNone(x.get(None))
            self.assertEqual(x["status"],"PENDING_NOT_APPROVED")
            self.assertEqual(x["independent_route_decision_ACCEPT_EXCLUDE_HOLD"],"")
            self.assertEqual(x["signed_review_record_location_private"],"")
            self.assertEqual(x["data_steward_authorization"],"")
    def test_observation_form_remains_unsigned(self):
        r=read("review/observation_adjudication_TEMPLATE_BLANK.csv")
        source=read("data/candidates_UNAPPROVED.csv")
        mount=read("data/mount2025_route_comparisons_UNAPPROVED.csv")
        xiong=read("data/xiong2023_table2_UNAPPROVED.csv")
        self.assertEqual(len(r),19)
        self.assertEqual(len({x["comparison_id"] for x in r}),19)
        valid={x["comparison_id"] for x in source}|{x["comparison_id"] for x in mount}|{x["candidate_id"] for x in xiong}
        self.assertEqual({x["comparison_id"] for x in r}-valid,set())
        routes={x["route_id"] for x in read("data/environmental_pathway_evidence_11_routes_UNAPPROVED.csv")}
        for x in r:
            self.assertIsNone(x.get(None))
            self.assertEqual(x["status"],"PENDING_NOT_APPROVED")
            self.assertIn(x["route_id"],routes)
            self.assertEqual(x["independent_assay_decision_ACCEPT_EXCLUDE_HOLD"],"")
            self.assertEqual(x["data_steward_authorization"],"")
            self.assertEqual(x["signed_review_record_location_private"],"")
    def test_source_and_route_uniqueness(self):
        allobs=read("review/observation_adjudication_TEMPLATE_BLANK.csv")
        self.assertEqual({r["source_study"] for r in allobs},
                          {"MOUNT2025","KADLEC2024","ZHANG2011","XIONG2023"})
        s1=[r["comparison_id"] for r in allobs if r["source_study"]=="MOUNT2025"]
        self.assertEqual(len(s1),12)
        # Original six priority rows contain 3 Mount entries; the 12-source-comparison
        # Mount file must not add those 3 again as different training observations.
        self.assertEqual(len([r for r in s1 if r["comparison_id"].startswith("MOUNT25_01")]),2)
if __name__=="__main__":unittest.main()
