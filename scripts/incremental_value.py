"""Exploratory feature ablation; differences do not prove conditional independence."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss
from robustness import model

ROOT=Path(__file__).resolve().parents[1]
def main():
    demo=pd.read_csv(ROOT/'data/raw/demographics_diagnosis.csv')
    bio=pd.read_csv(ROOT/'data/raw/biomarkers.csv')
    assert demo.adrc_id.is_unique and bio.adrc_id.is_unique
    df=demo.merge(bio,on='adrc_id',validate='one_to_one')
    df=df[df.diagnosis_consensus.isin(['Probable Alzheimers Disease','Healthy Control'])].sort_values('adrc_id').reset_index(drop=True)
    y=(df.diagnosis_consensus=='Probable Alzheimers Disease').astype(int).to_numpy()
    names=['PTAU217','GFAP','NFL']
    assert len(y)==348 and y.sum()==73 and np.isfinite(df[names].to_numpy()).all()
    panels={n:[n] for n in names}
    panels.update({'PTAU217+GFAP':['PTAU217','GFAP'],'PTAU217+NFL':['PTAU217','NFL'],'all_three':names})
    rows=[]
    for seed in range(20261201,20261211):
        splits=list(StratifiedKFold(5,shuffle=True,random_state=seed).split(df,y))
        for name,cols in panels.items():
            p=cross_val_predict(model(),df[cols].to_numpy(),y,cv=splits,method='predict_proba')[:,1]
            rows.append(dict(seed=seed,panel=name,auroc=float(roc_auc_score(y,p)),
                average_precision=float(average_precision_score(y,p)),brier=float(brier_score_loss(y,p)),log_loss=float(log_loss(y,p))))
    summary={}
    for name in panels:
        rr=[r for r in rows if r['panel']==name]
        diffs={metric:[r[metric]-next(b[metric] for b in rows if b['seed']==r['seed'] and b['panel']=='PTAU217') for r in rr] for metric in ['auroc','brier','log_loss']}
        summary[name]={metric:float(np.mean([r[metric] for r in rr])) for metric in ['auroc','average_precision','brier','log_loss']}
        summary[name]['paired_delta_vs_ptau']={m:{'mean':float(np.mean(v)),'min':min(v),'max':max(v)} for m,v in diffs.items()}
    correlations={}
    for label,sub in [('pooled',df),('healthy_control',df[y==0]),('probable_AD',df[y==1])]:
        correlations[label]={'n':len(sub),'pearson':sub[names].corr().to_dict(),'spearman':sub[names].corr(method='spearman').to_dict()}
    result={'summary':summary,'runs':rows,'correlations':correlations,'limits':'Same synthetic release and dependent repeated splits; fixed linear model only; no significance test or conditional-independence claim.'}
    (ROOT/'outputs/incremental_value_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Incremental biomarker value','',
        'Exploratory follow-up, 2026-11-09. Same 348 synthetic records; ten paired five-fold repetitions. Fixed standardized logistic regression (C=1), trained separately for each prespecified panel. Standardization is training-only. No threshold tuning is needed for these probability metrics.','',
        '| Panel | Mean AUROC | Average precision | Brier | Log loss | AUROC change vs p-tau217 |',
        '|---|---:|---:|---:|---:|---:|']
    for n,s in summary.items():
        lines.append(f"| {n} | {s['auroc']:.3f} | {s['average_precision']:.3f} | {s['brier']:.3f} | {s['log_loss']:.3f} | {s['paired_delta_vs_ptau']['auroc']['mean']:+.3f} |")
    lines+=['','Lower Brier/log loss is better. Differences are paired by split, not independent replicates. No confidence intervals or p-values are claimed.','',
        '## Feature correlations','', '| Population | n | p-tau217 / GFAP | p-tau217 / NfL | GFAP / NfL |','|---|---:|---:|---:|---:|']
    for label,c in correlations.items():
        r=c['pearson']
        lines.append(f"| {label} | {c['n']} | {r['PTAU217']['GFAP']:.3f} | {r['PTAU217']['NFL']:.3f} | {r['GFAP']['NFL']:.3f} |")
    lines+=['','Pearson correlations are descriptive; Spearman values are retained in the JSON. Pooled correlations can partly reflect class differences. Neither high nor low correlation establishes incremental predictive value.','',
        '## Scope of conclusion','',
        'These ablations test whether added features improve this fixed linear classifier on this release. Failure to improve does not show that a biomarker lacks biological information, nonlinear predictive value or clinical usefulness. We have repeatedly inspected the same dataset, so this is discovery work, not independent confirmation. No optimal panel or clinical recommendation follows.','',
        'Signed synthetic values are retained. Exact units and finite missing-code conventions remain unresolved. No additional acquisition rule should be justified solely by these post-hoc results.','',
        "Internal report. Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Follow accepted publication-review terms before external sharing."]
    (ROOT/'outputs/incremental_value_report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({n:{k:v for k,v in s.items() if k!='paired_delta_vs_ptau'} for n,s in summary.items()},indent=2))

if __name__=='__main__': main()
