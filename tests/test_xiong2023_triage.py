import csv,math,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"data/xiong2023_table2_UNAPPROVED.csv"
class Xiong2023EvidenceTriage(unittest.TestCase):
    def test_source_table2_is_not_training_data(self):
        with P.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),4)
        self.assertEqual({r["source_study"] for r in rows},{"XIONG2023"})
        self.assertEqual({(r["species"],r["endpoint"],r["duration_hours"]) for r in rows},
                         {("Daphnia magna","LC50","48")})
        self.assertTrue(all(r["independent_review_status"]=="NOT_RETURNED" and
                            r["eligible_for_training"]=="NO" for r in rows))
        self.assertTrue(all(r["aqueous_exposure_concentration_basis"]=="Measured aqueous concentrations in assay" for r in rows))
        self.assertTrue(all("molar ratio pending" in r["source_relevant_caveat"] for r in rows))
        self.assertTrue(all("environment" in r["source_relevant_caveat"].lower() or "route" in r["source_relevant_caveat"].lower() for r in rows))
        original={"acetaminophen":(21.2,2.4,32.1,5.7),
                  "diazepam":(3.0,.3,4.4,1.1),
                  "methylparaben":(34.4,4.3,225.6,17.3),
                  "naproxen":(32.1,4.9,67.9,6.0)}
        for r in rows:
            v=original[r["parent"]]
            self.assertEqual(tuple(float(r[k]) for k in ("parent_LC50_mg_L","parent_reported_SD_mg_L",
                          "product_LC50_mg_L","product_reported_SD_mg_L")),v)
            self.assertTrue(math.isclose(float(r["product_parent_mass_LC50_ratio"]),v[2]/v[0],rel_tol=1e-8))
    def test_organism_metabolism_is_not_environmental_pathway_signoff(self):
        with P.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
        for r in rows:
            self.assertTrue("environment" in (r["experimental_route_evidence_scope"]+
                          r["source_relevant_caveat"]).lower())
        ac=next(r for r in rows if r["parent"]=="acetaminophen")
        self.assertIn("not detected",ac["experimental_route_evidence_scope"].lower())
if __name__=="__main__": unittest.main()
