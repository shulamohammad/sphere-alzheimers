"""Simulated staged acquisition on complete synthetic records only."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, brier_score_loss
from robustness import model, threshold, rates

ROOT=Path(__file__).resolve().parents[1]
def route(distance, margin):
    return distance <= margin

def evaluate():
    demo=pd.read_csv(ROOT/'data/raw/demographics_diagnosis.csv')
    bio=pd.read_csv(ROOT/'data/raw/biomarkers.csv')
    assert demo.adrc_id.is_unique and bio.adrc_id.is_unique
    df=demo.merge(bio,on='adrc_id',validate='one_to_one')
    df=df[df.diagnosis_consensus.isin(['Probable Alzheimers Disease','Healthy Control'])].sort_values('adrc_id').reset_index(drop=True)
    y=(df.diagnosis_consensus=='Probable Alzheimers Disease').astype(int).to_numpy()
    X=df[['PTAU217','GFAP','NFL']].to_numpy(float)
    assert len(y)==348 and y.sum()==73 and np.isfinite(X).all()
    rows=[]; audit=[]
    names=['always_one','always_three']+[f'{mode}_{q}' for q in (25,50,75) for mode in ('staged','random')]
    for seed in range(20261201,20261211):
        buffers={n:{'p':np.full(len(y),np.nan),'pred':np.zeros(len(y),int),'acq':np.zeros(len(y),bool)} for n in names}
        seen=np.zeros(len(y),int)
        for fold,(tr,te) in enumerate(StratifiedKFold(5,shuffle=True,random_state=seed).split(X,y)):
            assert not set(tr)&set(te)
            inner=list(StratifiedKFold(4,shuffle=True,random_state=seed+fold+100).split(X[tr],y[tr]))
            train_scores=[]; test_scores=[]
            for cols in ([0],[0,1,2]):
                a=X[tr][:,cols]; b=X[te][:,cols]
                train_scores.append(cross_val_predict(model(),a,y[tr],cv=inner,method='predict_proba')[:,1])
                test_scores.append(model().fit(a,y[tr]).predict_proba(b)[:,1])
            a,c=train_scores; b,d=test_scores
            t1=threshold(y[tr],a)
            def store(name, itr, ite):
                ps=np.where(itr,c,a); pt=np.where(ite,d,b)
                t=threshold(y[tr],ps)
                buffers[name]['p'][te]=pt
                buffers[name]['pred'][te]=(pt>=t).astype(int)
                buffers[name]['acq'][te]=ite
                audit.append(dict(seed=seed,fold=fold,policy=name,threshold=t,acquired=int(ite.sum()),n_test=len(te)))
                return pt,t
            p0,t0=store('always_one',np.zeros(len(tr),bool),np.zeros(len(te),bool))
            p1,tall=store('always_three',np.ones(len(tr),bool),np.ones(len(te),bool))
            assert np.array_equal(p0,b) and np.array_equal(p1,d)
            assert t0==t1 and tall==threshold(y[tr],c)
            for q in (25,50,75):
                margin=float(np.quantile(abs(a-t1),q/100))
                itr=route(abs(a-t1),margin); ite=route(abs(b-t1),margin)
                store(f'staged_{q}',itr,ite)
                rng=np.random.default_rng(seed+fold*1000+q)
                rtr=np.zeros(len(tr),bool); rte=np.zeros(len(te),bool)
                rtr[rng.permutation(len(tr))[:itr.sum()]]=True
                rte[rng.permutation(len(te))[:ite.sum()]]=True
                assert rtr.sum()==itr.sum() and rte.sum()==ite.sum()
                store(f'random_{q}',rtr,rte)
            seen[te]+=1
        assert np.all(seen==1)
        for name,z in buffers.items():
            assert np.isfinite(z['p']).all()
            rr=rates(y,z['pred'])
            rows.append(dict(seed=seed,policy=name,**rr,balanced_accuracy=(rr['sensitivity']+rr['specificity'])/2,
                auroc=float(roc_auc_score(y,z['p'])),brier=float(brier_score_loss(y,z['p'])),
                acquisition_fraction=float(z['acq'].mean()),mean_measurements=float(1+2*z['acq'].mean())))
    metrics=['auroc','brier','sensitivity','specificity','balanced_accuracy','acquisition_fraction','mean_measurements']
    summary={n:{m:float(np.mean([r[m] for r in rows if r['policy']==n])) for m in metrics} for n in names}
    out=ROOT/'outputs'
    (out/'staged_testing_metrics.json').write_text(json.dumps(dict(summary=summary,runs=rows,fold_audit=audit),indent=2)+'\n')
    lines=['# Staged biomarker testing: exploratory results','',
        '348 synthetic records; 10 paired repetitions of five-fold evaluation. Fixed logistic models; training-only routing margins and decision thresholds. Target sensitivity is 80% on inner scores, not guaranteed on held-out records.','',
        '| Policy | Mean measurements | Acquire extra tests | AUROC | Sensitivity | Specificity | Balanced accuracy |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for n,s in summary.items():
        lines.append(f"| {n} | {s['mean_measurements']:.2f} | {s['acquisition_fraction']:.1%} | {s['auroc']:.3f} | {s['sensitivity']:.1%} | {s['specificity']:.1%} | {s['balanced_accuracy']:.3f} |")
    lines+=['','Staged suffixes are nominal training acquisition percentages. Random comparators match the staged policy’s achieved test count in every fold; they use fixed random seeds, not test labels. Measurement count is a proxy, not dollars or visits. AUROC and Brier use uncalibrated mixed model scores, so interpret cautiously.','',
        '## Paired balanced-accuracy differences versus budget-matched random acquisition','',
        'Ranges below reflect split variability, not confidence intervals or independent replications.']
    for q in (25,50,75):
        ds=[next(r['balanced_accuracy'] for r in rows if r['seed']==s and r['policy']==f'staged_{q}')-next(r['balanced_accuracy'] for r in rows if r['seed']==s and r['policy']==f'random_{q}') for s in range(20261201,20261211)]
        lines.append(f'- {q}% nominal: mean {np.mean(ds):+.4f}; range {min(ds):+.4f} to {max(ds):+.4f}.')
    lines+=['','## Limits','',
        'This simulates acquisition by hiding already-observed measurements. It does not evaluate real missing-data collection, actual expenses, clinical outcomes or patient-level generalization. Exact assay units and numeric sentinel conventions remain unresolved. Signed values were retained. The same jointly synthesized release is reused across experiments; repeats are dependent and no independent final test set exists. No best-policy claim is warranted.','',
        'Internal report. Source: Stanford Alzheimer\'s Disease Research Center, NIH/NIA grant P30 AG066515. Follow the accepted agreement before external disclosure.']
    (out/'staged_testing_report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': evaluate()
