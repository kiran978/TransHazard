"""SYNTHETIC ONLY: software execution test, not TransHazard validation."""
import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from transhazard.core import fit_development,model_readiness,leakage_components,rdkit_features
class SyntheticSmokeTest(unittest.TestCase):
    def test_features_and_grouped_development(self):
        rows=[]
        for i in range(45):
            n=i+1
            rows.append({"comparison_id":f"SYNTHETIC_{i}",
                         "route_id":f"FAKE_ROUTE_{i}","source_study":f"FAKE_STUDY_{i}",
                         "chemical_network":f"FAKE_NET_{i}",
                         "parent_CAS":f"FAKE_{i}_P","product_CAS":f"FAKE_{i}_T",
                         "parent_smiles":"C"*n,"product_smiles":"C"*n+"O",
                         "species":"FAKE_SPECIES","endpoint":"LC50","duration_hours":"48",
                         "parent_conc":str(1+.08*i),"product_conc":str(.65+.09*i),
                         "parent_MW":"1","product_MW":"1"})
        self.assertEqual(len(set(leakage_components(rows))),45)
        self.assertEqual(rdkit_features(rows[:3]).shape[0],3)
        self.assertEqual(model_readiness(rows)[0]["status"],"ELIGIBLE_FOR_DEVELOPMENT")
        with tempfile.TemporaryDirectory() as path:
            result=fit_development(rows,path)
            self.assertEqual(len(result),1)
            self.assertIn("selected_model",result[0])
            self.assertEqual(result[0]["status"],"INTERNAL_DEVELOPMENT_HOLDOUT_ONLY_NOT_EXTERNAL_VALIDATION")
            self.assertEqual(len(list(Path(path).glob("*.joblib"))),1)
if __name__=="__main__":unittest.main()
