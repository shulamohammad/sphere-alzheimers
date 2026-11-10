"""Paired split sensitivity and nested threshold selection, synthetic data only."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, roc_curve, confusion_matrix

ROOT=Path(__file__).resolve().parents[1]
def model():
    return make_pipeline(StandardScaler(), LogisticRegression(C=1.,max_iter=2000))

def threshold(y,p):
    _,tpr,t=roc_curve(y,p,drop_intermediate=False)
    return float(max(t[(tpr>=.8)&np.isfinite(t)]))

def rates(y,pred):
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {'sensitivity':float(tp/(tp+fn)), 'specificity':float(tn/(tn+fp))}

def main():
    d=pd.read_csv(ROOT/'data/raw/demographics_diagnosis.csv')
    b=pd.read_csv(ROOT/'data/raw/biomarkers.csv')
    assert d.adrc_id.is_unique and b.adrc_id.is_unique
    df=d.merge(b,on='adrc_id',validate='one_to_one')
    df=df[df.diagnosis_consensus.isin(['Probable Alzheimers Disease','Healthy Control'])].sort_values('adrc_id').reset_index(drop=True)
    y=(df.diagnosis_consensus=='Probable Alzheimers Disease').astype(int).to_numpy()
    assert len(y)==348 and y.sum()==73
    rows=[]
    for seed in range(20261201,20261211):
        splits=list(StratifiedKFold(5,shuffle=True,random_state=seed).split(df,y))
        for name,cols in [('PTAU217',['PTAU217']),('three_biomarkers',['PTAU217','GFAP','NFL'])]:
            X=df[cols].to_numpy(dtype=float)
            assert np.isfinite(X).all()
            p=np.full(len(y),np.nan); pred=np.zeros(len(y),dtype=int); seen=np.zeros(len(y),dtype=int); ts=[]
            for fold,(train,test) in enumerate(splits):
                assert not set(train)&set(test)
                inner=StratifiedKFold(4,shuffle=True,random_state=seed+fold+100)
                ip=cross_val_predict(model(),X[train],y[train],cv=inner,method='predict_proba')[:,1]
                t=threshold(y[train],ip); ts.append(t)
                assert (ip[y[train]==1]>=t).mean()>=.8
                fitted=model().fit(X[train],y[train])
                p[test]=fitted.predict_proba(X[test])[:,1]
                pred[test]=(p[test]>=t).astype(int); seen[test]+=1
            assert np.all(seen==1) and np.isfinite(p).all()
            rows.append(dict(seed=seed,model=name,auroc=float(roc_auc_score(y,p)),
                average_precision=float(average_precision_score(y,p)),brier=float(brier_score_loss(y,p)),
                fixed=rates(y,p>=.5),nested=rates(y,pred),thresholds=ts))
    delta=[rows[i+1]['auroc']-rows[i]['auroc'] for i in range(0,len(rows),2)]
    summary={}
    for name in ['PTAU217','three_biomarkers']:
        r=[x for x in rows if x['model']==name]
        summary[name]={'mean_auroc':float(np.mean([x['auroc'] for x in r])),
            'auroc_range':[min(x['auroc'] for x in r),max(x['auroc'] for x in r)],
            'mean_fixed_sensitivity':float(np.mean([x['fixed']['sensitivity'] for x in r])),
            'mean_nested_sensitivity':float(np.mean([x['nested']['sensitivity'] for x in r])),
            'mean_nested_specificity':float(np.mean([x['nested']['specificity'] for x in r]))}
    result={'summary':summary,'paired_auroc_difference_three_minus_one':delta,'runs':rows,
        'limitations':'Exploratory synthetic-only results; dependent repeats, no clinical CI; units and missing-code conventions unresolved.'}
    (ROOT/'outputs/robustness_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Split stability and nested thresholds','',result['limitations'],'',
        '10 paired repetitions of five-fold evaluation. Threshold selected using four-fold scores inside each training fold, targeting sensitivity >= 0.80. Outer test labels never select the threshold. Repetitions reuse the same records.','',
        '| Model | Mean AUROC | AUROC range | Sensitivity at 0.5 | Nested sensitivity | Nested specificity |',
        '|---|---:|---:|---:|---:|---:|']
    for n,s in summary.items():
        lines.append(f"| {n} | {s['mean_auroc']:.3f} | {s['auroc_range'][0]:.3f}–{s['auroc_range'][1]:.3f} | {s['mean_fixed_sensitivity']:.3f} | {s['mean_nested_sensitivity']:.3f} | {s['mean_nested_specificity']:.3f} |")
    lines+=['',f'Paired AUROC difference (three minus one): mean {np.mean(delta):.4f}; range {min(delta):.4f} to {max(delta):.4f}. This range is not a confidence interval.', '',
        'Higher sensitivity trades off against false positives. The 0.80 training target is not guaranteed on held-out data. No clinical threshold, cost saving, fairness or patient-outcome conclusion follows.', '',
        'Internal report. Stanford Alzheimer\'s Disease Research Center, NIH/NIA grant P30 AG066515. Comply with accepted publication-review terms before external disclosure.']
    (ROOT/'outputs/robustness_report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'summary':summary,'mean_paired_difference':float(np.mean(delta))},indent=2))

if __name__=='__main__': main()
