"""Calibration, descriptive subgroup checks and pipeline controls.

These are exploratory checks on an already inspected synthetic release.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_auc_score, brier_score_loss, average_precision_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from robustness import model, threshold, rates

ROOT=Path(__file__).resolve().parents[1]
SEED=20261201

def main():
    d=pd.read_csv(ROOT/'data/raw/demographics_diagnosis.csv')
    b=pd.read_csv(ROOT/'data/raw/biomarkers.csv')
    assert d.adrc_id.is_unique and b.adrc_id.is_unique
    df=d.merge(b,on='adrc_id',validate='one_to_one')
    df=df[df.diagnosis_consensus.isin(['Probable Alzheimers Disease','Healthy Control'])].sort_values('adrc_id').reset_index(drop=True)
    y=(df.diagnosis_consensus=='Probable Alzheimers Disease').astype(int).to_numpy()
    X=df[['PTAU217']].to_numpy(float)
    assert len(y)==348 and sum(y)==73 and np.isfinite(X).all()
    splits=list(StratifiedKFold(5,shuffle=True,random_state=SEED).split(X,y))
    p=np.full(len(y),np.nan); decisions=np.zeros(len(y),int); fold_ids=np.zeros(len(y),int)
    for fold,(tr,te) in enumerate(splits):
        assert not set(tr)&set(te)
        inner=StratifiedKFold(4,shuffle=True,random_state=SEED+fold+100)
        ip=cross_val_predict(model(),X[tr],y[tr],cv=inner,method='predict_proba')[:,1]
        t=threshold(y[tr],ip)
        fitted=model().fit(X[tr],y[tr])
        # A concrete leakage check: fitted scaling must equal training statistics.
        assert np.allclose(fitted.named_steps['standardscaler'].mean_,X[tr].mean(axis=0))
        p[te]=fitted.predict_proba(X[te])[:,1]
        decisions[te]=p[te]>=t; fold_ids[te]=fold
    assert np.isfinite(p).all()
    # Five fixed probability bins, never chosen to improve apparent calibration.
    bins=[]
    for lo,hi in zip(np.arange(0,1,.2),np.arange(.2,1.01,.2)):
        mask=(p>=lo)&((p<hi) if hi<.999 else (p<=1))
        bins.append({'lower':float(lo),'upper':float(hi),'n':int(mask.sum()),
            'mean_probability':float(p[mask].mean()) if mask.any() else None,
            'observed_fraction':float(y[mask].mean()) if mask.any() else None})
    assert sum(x['n'] for x in bins)==len(y)
    groups=[]
    age=pd.to_numeric(df.age_at_visit,errors='raise').to_numpy()
    for name,mask in [('female',df.sex.to_numpy()=='female'),('male',df.sex.to_numpy()=='male'),('age_under_75',age<75),('age_75_plus',age>=75)]:
        n=int(mask.sum()); positives=int(y[mask].sum()); negatives=n-positives
        if min(positives,negatives)<10:
            groups.append({'group':name,'n':n,'positive':positives,'negative':negatives,'metrics_suppressed':'fewer than 10 records in a class'})
        else:
            groups.append(dict(group=name,n=n,positive=positives,negative=negatives,
                auroc=float(roc_auc_score(y[mask],p[mask])),brier=float(brier_score_loss(y[mask],p[mask])),**rates(y[mask],decisions[mask])))
    # Negative control: shuffle labels and rebuild stratification for each shuffle.
    rng=np.random.default_rng(20261109); null=[]
    for i in range(25):
        shuffled=rng.permutation(y)
        cv=StratifiedKFold(5,shuffle=True,random_state=SEED+i)
        pp=cross_val_predict(model(),X,shuffled,cv=cv,method='predict_proba')[:,1]
        null.append(float(roc_auc_score(shuffled,pp)))
    # Demographic reference: primary endpoint unchanged, age/sex only, no indicators of diagnosis.
    demo_X=np.column_stack([age,(df.sex.to_numpy()=='male').astype(float)])
    demo_p=cross_val_predict(model(),demo_X,y,cv=splits,method='predict_proba')[:,1]
    # Purely local diagnostics: predictions stay in gitignored outputs.
    pd.DataFrame({'synthetic_id':df.adrc_id,'fold':fold_ids,'label':y,'probability':p,'decision':decisions}).to_csv(ROOT/'outputs/local_oof_predictions.csv',index=False)
    result={
        'seed':SEED,'n':len(y),'positive':int(y.sum()),'calibration_bins':bins,'subgroups':groups,
        'observed_auroc':float(roc_auc_score(y,p)),
        'negative_control':{'n_permutations':25,'mean_auc':float(np.mean(null)),'range':[min(null),max(null)],'all_aucs':null,'interpretation':'Engineering sanity check, not a valid population-level permutation test for dependent synthetic records.'},
        'demographics_only':{'auroc':float(roc_auc_score(y,demo_p)),'brier':float(brier_score_loss(y,demo_p))},
        'sklearn_version':sklearn.__version__,
        'source_hashes':{name:hashlib.sha256((ROOT/'data/raw'/name).read_bytes()).hexdigest() for name in ['demographics_diagnosis.csv','biomarkers.csv']},
        'limits':'Uncalibrated model; calibration/subgroups use one prespecified split, no inferential intervals. No fairness or clinical claims. Negative values retained; finite sentinels unresolved.'}
    (ROOT/'outputs/final_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['observed_auroc','negative_control','demographics_only','subgroups']},indent=2))

if __name__=='__main__': main()
