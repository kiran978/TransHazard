import json, math, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from transhazard.core import load_csv,ratio_from_row,audit_candidates,validate_approved_rows,leakage_components,model_readiness
ROOT=Path(__file__).resolve().parents[1]
ROWS=load_csv(ROOT/"data/candidates_UNAPPROVED.csv")
class ScientificGateTests(unittest.TestCase):
    def test_counts_and_arithmetic(self):
        r=audit_candidates(ROWS)
        self.assertEqual((r["n_candidates"],r["n_routes"],r["n_approved"]),(6,4,0))
        self.assertEqual(r["arithmetic_or_integrity_errors"],[])
    def test_all_unapproved(self):
        meta=json.loads((ROOT/"data/approval_metadata_EXAMPLE_NOT_AUTHORIZED.json").read_text())
        self.assertTrue(validate_approved_rows(ROWS,meta))
    def test_molar_ratios(self):
        for r in ROWS:self.assertAlmostEqual(ratio_from_row(r),float(r["provisional_molar_ratio"]),places=5)
    def test_bad_concentrations(self):
        r=dict(ROWS[0]);r["parent_conc"]="0"
        with self.assertRaises(ValueError):ratio_from_row(r)
    def test_shared_studies_do_not_split(self):
        g=leakage_components(ROWS)
        self.assertEqual(g[0],g[1])
        self.assertEqual(g[0],g[2])
        self.assertEqual(g[3],g[4])
        self.assertNotEqual(g[0],g[3])
    def test_assay_separation_and_no_go(self):
        contexts=model_readiness(ROWS)
        self.assertEqual(len(contexts),5)
        self.assertTrue(all(c["status"]=="UNDERPOWERED" for c in contexts))
    def test_direction(self):
        self.assertGreater(math.log10(ratio_from_row(ROWS[0])),0)
        self.assertLess(math.log10(ratio_from_row(ROWS[4])),0)
if __name__=="__main__":unittest.main()
