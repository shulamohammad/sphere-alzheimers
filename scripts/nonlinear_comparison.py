"""Fixed-complexity nonlinear versus linear exploratory benchmark."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold,cross_val_predict
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss
from robustness import model

ROOT=Path(__file__).resolve().parents[1]
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
        for family in ['logistic','boosting']:
            for panel,cols in [('one',['PTAU217']),('three',['PTAU217','GFAP','NFL'])]:
                X=df[cols].to_numpy(float); assert np.isfinite(X).all()
                estimator=model() if family=='logistic' else HistGradientBoostingClassifier(max_iter=100,learning_rate=.05,max_leaf_nodes=4,min_samples_leaf=20,l2_regularization=1,early_stopping=False,random_state=seed)
                p=cross_val_predict(estimator,X,y,cv=splits,method='predict_proba')[:,1]
                assert np.isfinite(p).all() and np.all((p>=0)&(p<=1))
                rows.append(dict(seed=seed,model=f'{family}_{panel}',auroc=float(roc_auc_score(y,p)),average_precision=float(average_precision_score(y,p)),brier=float(brier_score_loss(y,p)),log_loss=float(log_loss(y,p))))
    metrics=['auroc','average_precision','brier','log_loss']
    names=['logistic_one','logistic_three','boosting_one','boosting_three']
    summary={n:{m:float(np.mean([r[m] for r in rows if r['model']==n])) for m in metrics} for n in names}
    comparisons={}
    for a,b in [('boosting_one','logistic_one'),('boosting_three','logistic_one'),('boosting_three','boosting_one')]:
        comparisons[f'{a} minus {b}']={}
        for m in metrics:
            ds=[next(r[m] for r in rows if r['seed']==s and r['model']==a)-next(r[m] for r in rows if r['seed']==s and r['model']==b) for s in range(20261201,20261211)]
            comparisons[f'{a} minus {b}'][m]={'mean':float(np.mean(ds)),'min':min(ds),'max':max(ds)}
    out=ROOT/'outputs'
    (out/'nonlinear_metrics.json').write_text(json.dumps(dict(summary=summary,comparisons=comparisons,runs=rows),indent=2)+'\n')
    lines=['# Fixed nonlinear model comparison','',
        'Exploratory synthetic-data benchmark. Same 348 records, ten paired five-fold repetitions. No hyperparameter selection. Boosting uses 100 iterations, learning rate 0.05, maximum 4 leaves, minimum 20 samples per leaf, L2=1, no early stopping. Logistic regression uses training-only scaling and C=1.','',
        '| Model | AUROC | Average precision | Brier | Log loss |','|---|---:|---:|---:|---:|']
    for n,s in summary.items(): lines.append(f"| {n} | {s['auroc']:.3f} | {s['average_precision']:.3f} | {s['brier']:.3f} | {s['log_loss']:.3f} |")
    lines+=['','Lower Brier and log loss are better. One-feature boosting tests nonlinear PTAU217 patterns; its comparison with three-feature boosting tests added-feature value within this model family.','', '## Paired AUROC differences','']
    for n,s in comparisons.items():
        v=s['auroc']; lines.append(f"- {n}: mean {v['mean']:+.4f}, range {v['min']:+.4f} to {v['max']:+.4f}.")
    lines+=['','Ranges describe repeated split variability, not confidence intervals. Repeats are dependent and the dataset has been examined repeatedly. No independent confirmation, optimal model, clinical efficacy or lack of biological usefulness is established. Fixed boosting is one nonlinear baseline, not a comprehensive nonlinear search.','',
        'Signed synthetic values remain unchanged; assay units and finite missing codes remain unresolved. Joint synthesis may create cross-record dependencies. No real-data test cohort is available.','',
        "Internal report. Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Follow accepted publication-review requirements before external sharing."]
    (out/'nonlinear_report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
