"""Scientific release gate and leakage-resistant TransHazard regression.

This library cannot authenticate real-world reviewer identity or prove source validity.
It deliberately refuses unapproved, underpowered, or mixed-assay training sets.
"""
from __future__ import annotations
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

MANDATORY_QA = ('transformation_verified_Y_N', 'assay_equivalent_Y_N',
                'exposure_quality_acceptable_Y_N', 'estimator_credible_Y_N',
                'provenance_checked_Y_N')
SCIENTIFIC_GATE_FIELDS = ('independent_reviewer_full_name','reviewer_affiliation',
                          'reasoned_decision','signed_review_record_location',
                          'review_date_YYYY_MM_DD')
MIN_ROUTES=30
MIN_LEAKAGE_GROUPS=20
MIN_STUDIES=5
MIN_HOLDOUT_GROUPS=5


def load_csv(path):
    with open(path,encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def write_json(path,obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')


def ratio_from_row(r):
    """Product/parent 50% effect concentration, converted to molar units."""
    p=float(r['parent_conc']); t=float(r['product_conc'])
    mw_p=float(r['parent_MW']); mw_t=float(r['product_MW'])
    if not all(math.isfinite(v) and v>0 for v in (p,t,mw_p,mw_t)):
        raise ValueError('All effect concentrations and MWs must be finite and positive')
    return (t/mw_t)/(p/mw_p)


def audit_candidates(rows):
    issues=[]; distinct=set()
    for i,r in enumerate(rows,2):
        cid=r.get('comparison_id',f'row_{i}')
        if cid in distinct:issues.append(f'{cid}: duplicate comparison ID')
        distinct.add(cid)
        try:
            ratio=ratio_from_row(r)
            expected=float(r.get('provisional_molar_ratio') or r.get('molar_product_parent_ratio'))
            if not math.isclose(ratio,expected,rel_tol=0.001,abs_tol=1e-7):
                issues.append(f'{cid}: recalculated molar ratio {ratio:.8g} != recorded {expected:.8g}')
        except (ValueError,KeyError,TypeError) as e:issues.append(f'{cid}: {e}')
        if str(r.get('eligible_for_training','')).upper()!='NO':
            issues.append(f'{cid}: candidate unexpectedly flagged training eligible')
    return {'n_candidates':len(rows),'n_routes':len({r['route_id'] for r in rows}),
            'n_studies':len({r['source_study'] for r in rows}),
            'n_networks':len({r['chemical_network'] for r in rows}),
            'n_approved':0,'arithmetic_or_integrity_errors':issues,
            'scientific_release':'NO_GO',
            'reason':'Candidates are explicitly unapproved; no independent review returned.'}


def has_human_review(r):
    if str(r.get('decision_ACCEPT_EXCLUDE_HOLD','')).strip().upper()!='ACCEPT':return False
    if any(str(r.get(k,'')).strip().upper()!='Y' for k in MANDATORY_QA):return False
    if any(not str(r.get(k,'')).strip() for k in SCIENTIFIC_GATE_FIELDS):return False
    return True


def validate_approved_rows(rows,release_metadata):
    errors=[]
    if not rows: errors.append('No observations supplied.')
    if release_metadata.get('release_status')!='APPROVED_BY_HUMAN_RESEARCH_TEAM':
        errors.append('Missing independently authorized, frozen release metadata.')
    for k in ('release_id','data_steward','reviewer_authentication_reference','release_date'):
        if not release_metadata.get(k):errors.append(f'Release authorization missing {k}.')
    seen=set()
    for idx,r in enumerate(rows,2):
        id_=str(r.get('comparison_id','')).strip()
        if not id_ or id_ in seen: errors.append(f'Row {idx}: blank or repeated comparison_id.')
        seen.add(id_)
        if not has_human_review(r):errors.append(f'Row {idx}/{id_}: missing completed scientific ACCEPT review or evidence gates.')
        if r.get('eligible_for_training','').strip().upper()!='YES':
            errors.append(f'Row {idx}/{id_}: training eligibility not explicitly YES in approved dataset.')
        if r.get('approved_Dataset_v2_label','').strip().upper()!='YES':
            errors.append(f'Row {idx}/{id_}: not marked YES by the authenticated Dataset v2 release steward.')
        for side in ('parent','product'):
            if r.get(f'{side}_concentration_censor','').strip().upper()!='NONE':
                errors.append(f'Row {idx}/{id_}: missing exact, uncensored {side} effect concentration.')
        if not r.get('transformation_primary_evidence_reference','').strip():
            errors.append(f'Row {idx}/{id_}: missing primary transformation-route evidence reference.')
        if r.get('source_study','').strip()=='' or r.get('route_id','').strip()=='':
            errors.append(f'Row {idx}/{id_}: study or route missing.')
        if not all(r.get(k,'').strip() for k in ('parent_CAS','product_CAS','parent_smiles','product_smiles',
                                                 'species','endpoint','duration_hours','concentration_unit')):
            errors.append(f'Row {idx}/{id_}: chemical or assay identifiers missing.')
        try:
            ratio=ratio_from_row(r)
            y=math.log10(ratio)
            if r.get('delta_log10') and not math.isclose(y,float(r['delta_log10']),abs_tol=0.002):
                errors.append(f'Row {idx}/{id_}: delta_log10 inconsistent with molar concentration.')
        except Exception as e:errors.append(f'Row {idx}/{id_}: invalid numeric effect information: {e}')
        # No chemical identity guesswork; molecular structures must be preverified.
        try:
            from rdkit import Chem
            for side in ('parent','product'):
                mol=Chem.MolFromSmiles(r.get(f'{side}_smiles',''))
                if not mol:
                    errors.append(f'Row {idx}/{id_}: invalid {side}_smiles.')
                else:
                    from rdkit.Chem import Descriptors
                    asserted=float(r[f'{side}_MW'])
                    if abs(Descriptors.MolWt(mol)-asserted)/asserted>0.03:
                        errors.append(f'Row {idx}/{id_}: {side} chemical structure MW mismatches asserted MW (>3%).')
        except ImportError:
            errors.append('RDKit missing; molecule validation cannot be performed.')
            break
    return errors


class UnionFind:
    def __init__(self):self.p={}
    def find(self,a):
        if a not in self.p:self.p[a]=a
        if self.p[a]!=a:self.p[a]=self.find(self.p[a])
        return self.p[a]
    def union(self,a,b):
        ra=self.find(a);rb=self.find(b)
        if ra!=rb:self.p[rb]=ra


def leakage_components(rows):
    """Couple assays sharing EITHER a study, chemical, route, or declared network.

    A connected component is indivisible. Publication-wide edges are intentionally
    conservative, including disjoint chemical sets in the same paper.
    """
    uf=UnionFind()
    for i,r in enumerate(rows):
        rid=f'row:{i}'
        for k,prefix in (('route_id','route'),('source_study','study'),
                         ('chemical_network','network'),('parent_CAS','cas'),('product_CAS','cas')):
            v=str(r.get(k,'')).strip()
            if v:uf.union(rid,f'{prefix}:{v}')
        # CAS aliases/synonyms can still resolve to the same canonical chemical.
        for side in ('parent','product'):
            smi=r.get(f'{side}_smiles','').strip()
            if smi:
                try:
                    from rdkit import Chem
                    m=Chem.MolFromSmiles(smi)
                    if m: uf.union(rid, 'smiles:'+Chem.MolToSmiles(m,isomericSmiles=True))
                except ImportError:
                    raise RuntimeError('RDKit required to certify canonical-structure leakage grouping')
    keys=[uf.find(f'row:{i}') for i in range(len(rows))]
    normalize={v:f'G{n+1:03d}' for n,v in enumerate(sorted(set(keys)))}
    return [normalize[v] for v in keys]


def context_key(row):
    return (row['species'].strip(),row['endpoint'].strip().upper(),
            str(int(float(row['duration_hours']))))


def model_readiness(rows,required_routes=MIN_ROUTES,required_groups=MIN_LEAKAGE_GROUPS,
                    required_studies=MIN_STUDIES):
    """Assay-homogeneous cohorts only. These are configurable CONSERVATIVE policy cutoffs."""
    contexts=defaultdict(list)
    for r in rows:contexts[context_key(r)].append(r)
    results=[]
    for key,arr in sorted(contexts.items()):
        groups=leakage_components(arr)
        counts={'n_rows':len(arr),'n_routes':len({r['route_id'] for r in arr}),
                'n_studies':len({r['source_study'] for r in arr}),
                'n_leakage_groups':len(set(groups)),
                'n_networks':len({r.get('chemical_network') for r in arr})}
        reasons=[]
        if counts['n_routes']<required_routes:reasons.append('Insufficient distinct routes')
        if counts['n_studies']<required_studies:reasons.append('Insufficient independent studies')
        if counts['n_leakage_groups']<required_groups:reasons.append('Insufficient study/chemical-disjoint groups')
        if counts['n_leakage_groups']<MIN_HOLDOUT_GROUPS+3:reasons.append('Not enough disjoint groups for development plus holdout')
        results.append({'context':dict(zip(('species','endpoint','duration_hours'),key)),
                        **counts,'status':'ELIGIBLE_FOR_DEVELOPMENT' if not reasons else 'UNDERPOWERED',
                        'reasons':reasons})
    return results


def rdkit_features(rows,n_bits=128):
    from rdkit import Chem,DataStructs
    from rdkit.Chem import Descriptors,rdMolDescriptors,Crippen,rdFingerprintGenerator
    import numpy as np
    factory=rdFingerprintGenerator.GetMorganGenerator(radius=2,fpSize=n_bits)
    def vec(smiles):
        mol=Chem.MolFromSmiles(smiles)
        if mol is None:raise ValueError('Invalid verified SMILES')
        fp=factory.GetFingerprint(mol)
        bits=np.zeros(n_bits,dtype=np.float64)
        DataStructs.ConvertToNumpyArray(fp,bits)
        props=np.array([Descriptors.MolWt(mol),Crippen.MolLogP(mol),
            rdMolDescriptors.CalcTPSA(mol),rdMolDescriptors.CalcNumHBA(mol),
            rdMolDescriptors.CalcNumHBD(mol),rdMolDescriptors.CalcNumRotatableBonds(mol),
            rdMolDescriptors.CalcNumAromaticRings(mol),mol.GetNumHeavyAtoms()],dtype=np.float64)
        return np.concatenate((props,bits))
    X=[]
    for r in rows:
        a=vec(r['parent_smiles']);b=vec(r['product_smiles'])
        X.append(np.concatenate((a,b,b-a)))
    return np.stack(X)


def fit_development(rows,output_dir,random_state=20261013):
    """Fitted MODELS ARE DEVELOPMENT-ONLY; held-out split is internal and not external validation."""
    from sklearn.model_selection import GroupShuffleSplit,GroupKFold
    from sklearn.dummy import DummyRegressor
    from sklearn.linear_model import Ridge
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
    import numpy as np,joblib
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    reports=[]
    for ck in sorted({context_key(r) for r in rows}):
        arr=[r for r in rows if context_key(r)==ck]
        ready=model_readiness(arr)[0]
        if ready['status']!='ELIGIBLE_FOR_DEVELOPMENT':
            reports.append(ready);continue
        groups=np.array(leakage_components(arr));X=rdkit_features(arr)
        y=np.array([math.log10(ratio_from_row(r)) for r in arr])
        unique=len(set(groups))
        test_fraction=max(.2,MIN_HOLDOUT_GROUPS/unique)
        split=GroupShuffleSplit(n_splits=1,test_size=test_fraction,random_state=random_state)
        ti,vi=next(split.split(X,y,groups))
        train_groups=len(set(groups[ti]));test_groups=len(set(groups[vi]))
        if train_groups<5 or test_groups<MIN_HOLDOUT_GROUPS:
            reports.append({**ready,'status':'UNDERPOWERED_AFTER_SPLIT'});continue
        gkf=GroupKFold(n_splits=min(5,train_groups))
        candidates={
            'baseline_mean':DummyRegressor(strategy='mean'),
            'ridge':make_pipeline(StandardScaler(),Ridge(alpha=10.0)),
            'random_forest':RandomForestRegressor(n_estimators=200,max_depth=5,
                         min_samples_leaf=2,random_state=random_state,n_jobs=1)}
        cv_scores={}
        for name,m in candidates.items():
            maes=[]
            for a,b in gkf.split(X[ti],y[ti],groups[ti]):
                m.fit(X[ti][a],y[ti][a]);pred=m.predict(X[ti][b])
                maes.append(float(mean_absolute_error(y[ti][b],pred)))
            cv_scores[name]=float(np.mean(maes))
        best=min(cv_scores,key=cv_scores.get)
        m=candidates[best];m.fit(X[ti],y[ti]);yp=m.predict(X[vi])
        data={'status':'INTERNAL_DEVELOPMENT_HOLDOUT_ONLY_NOT_EXTERNAL_VALIDATION',
              'context':ready['context'],'n_train':int(len(ti)),'n_test':int(len(vi)),
              'n_train_groups':train_groups,'n_test_groups':test_groups,'selected_model':best,
              'group_cv_mae_by_model':cv_scores,'holdout_mae':float(mean_absolute_error(y[vi],yp)),
              'holdout_rmse':float(math.sqrt(mean_squared_error(y[vi],yp))),
              'holdout_r2':float(r2_score(y[vi],yp)) if len(vi)>1 else None,
              'scientific_scope':'Same-species, same-endpoint, same-duration only; not external validation.'}
        prefix='_'.join(k.lower().replace(' ','_') for k in ck)
        joblib.dump(m,out/f'{prefix}_development_only.joblib')
        reports.append(data)
    return reports
