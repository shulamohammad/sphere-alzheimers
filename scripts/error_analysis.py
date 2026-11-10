"""Post-hoc error audit; no acquisition policy is trained from these outcomes."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from robustness import model, threshold

ROOT=Path(__file__).resolve().parents[1]

def main():
    d=pd.read_csv(ROOT/'data/raw/demographics_diagnosis.csv')
    b=pd.read_csv(ROOT/'data/raw/biomarkers.csv')
    assert d.adrc_id.is_unique and b.adrc_id.is_unique
    df=d.merge(b,on='adrc_id',validate='one_to_one')
    df=df[df.diagnosis_consensus.isin(['Probable Alzheimers Disease','Healthy Control'])].sort_values('adrc_id').reset_index(drop=True)
    y=(df.diagnosis_consensus=='Probable Alzheimers Disease').astype(int).to_numpy()
    X=df[['PTAU217','GFAP','NFL']].to_numpy(float)
    assert len(y)==348 and y.sum()==73 and np.isfinite(X).all()
    records=[]; repeat_summaries=[]; coefficients=[]
    helpful=np.zeros(len(y),int); harmful=np.zeros(len(y),int)
    for seed in range(20261201,20261211):
        p=np.full((2,len(y)),np.nan); pred=np.zeros((2,len(y)),int)
        uncertain=np.zeros(len(y),bool); seen=np.zeros(len(y),int)
        for fold,(tr,te) in enumerate(StratifiedKFold(5,shuffle=True,random_state=seed).split(X,y)):
            assert not set(tr)&set(te)
            inner=list(StratifiedKFold(4,shuffle=True,random_state=seed+fold+100).split(X[tr],y[tr]))
            for m,cols in enumerate(([0],[0,1,2])):
                ip=cross_val_predict(model(),X[tr][:,cols],y[tr],cv=inner,method='predict_proba')[:,1]
                t=threshold(y[tr],ip)
                fitted=model().fit(X[tr][:,cols],y[tr])
                p[m,te]=fitted.predict_proba(X[te][:,cols])[:,1]
                pred[m,te]=(p[m,te]>=t).astype(int)
                if m==0:
                    margin=np.quantile(abs(ip-t),.25)
                    uncertain[te]=abs(p[m,te]-t)<=margin
                else:
                    coefficients.append(fitted.named_steps['logisticregression'].coef_[0].tolist())
            seen[te]+=1
        assert np.all(seen==1) and np.isfinite(p).all()
        correct=pred==y[None,:]
        h=~correct[0]&correct[1]; bad=correct[0]&~correct[1]
        helpful+=h; harmful+=bad
        group=np.select([h,bad,correct[0]&correct[1]],['corrected','introduced','both_correct'],default='both_wrong')
        entry={'seed':seed,'corrected':int(h.sum()),'introduced':int(bad.sum()),
            'errors_one':int((~correct[0]).sum()),'errors_three':int((~correct[1]).sum())}
        assert entry['errors_three']-entry['errors_one']==entry['introduced']-entry['corrected']
        repeat_summaries.append(entry)
        for i in range(len(y)):
            records.append({'repeat':seed,'class':int(y[i]),'transition':str(group[i]),
                'uncertain':bool(uncertain[i]),'brier_delta':float((p[1,i]-y[i])**2-(p[0,i]-y[i])**2)})
    frame=pd.DataFrame(records)
    tab=[]
    for cls,label in [(1,'Probable AD'),(0,'Healthy control')]:
        sub=frame[frame['class']==cls]
        tab.append(dict(group=label,n_records=int((y==cls).sum()),
            **{k:float((sub.transition==k).sum()/10) for k in ['corrected','introduced','both_correct','both_wrong']}))
    bins=[]
    for flag,label in [(True,'Near threshold (training 25% margin)'),(False,'Outside margin')]:
        sub=frame[frame.uncertain==flag]
        bins.append(dict(group=label,record_evaluations=len(sub),
            correction_rate=float((sub.transition=='corrected').mean()),
            introduction_rate=float((sub.transition=='introduced').mean()),
            mean_brier_change=float(sub.brier_delta.mean())))
    coef=np.array(coefficients)
    result=dict(status='Post-hoc exploratory synthetic-data error analysis',repeats=repeat_summaries,
        by_class=tab,by_uncertainty=bins,
        stability={'ever_corrected':int((helpful>0).sum()),'ever_harmed':int((harmful>0).sum()),
            'corrected_at_least_8_of_10':int((helpful>=8).sum()),'harmed_at_least_8_of_10':int((harmful>=8).sum()),
            'both_directions_across_splits':int(((helpful>0)&(harmful>0)).sum())},
        standardized_coefficient_summary={name:{'median':float(np.median(coef[:,j])),
            'min':float(coef[:,j].min()),'max':float(coef[:,j].max()),'positive_folds':int((coef[:,j]>0).sum())}
            for j,name in enumerate(['PTAU217','GFAP','NFL'])})
    (ROOT/'outputs/error_analysis_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    mean=lambda k:np.mean([r[k] for r in repeat_summaries])
    lines=['# Error analysis: adding GFAP and NFL','',
        'Post-hoc audit of the same 348 synthetic records and ten paired five-fold repetitions. All predictions are outer-held-out; thresholds are selected within training folds. No new routing policy is fitted from these error labels.','',
        f"Per repetition: {mean('corrected'):.1f} mistakes corrected; {mean('introduced'):.1f} new mistakes introduced. Total errors: {mean('errors_one'):.1f} with one biomarker versus {mean('errors_three'):.1f} with three.",'',
        '| Group | Unique records | Corrected errors | Introduced errors | Both correct | Both wrong |',
        '|---|---:|---:|---:|---:|---:|']
    for r in tab:
        lines.append(f"| {r['group']} | {r['n_records']} | {r['corrected']:.1f} | {r['introduced']:.1f} | {r['both_correct']:.1f} | {r['both_wrong']:.1f} |")
    lines+=['','Counts are averages over repetitions, not new patients.','',
        '## Is uncertainty a useful acquisition signal?','',
        '| Region | Record-evaluations | Error correction rate | New-error rate | Brier change (three minus one) |',
        '|---|---:|---:|---:|---:|']
    for r in bins:
        lines.append(f"| {r['group']} | {r['record_evaluations']} | {r['correction_rate']:.1%} | {r['introduction_rate']:.1%} | {r['mean_brier_change']:+.4f} |")
    lines+=['','Record-evaluations reuse the same records. These are descriptive pooled rates, not independent observations. Positive Brier change is worse. This compares the two standalone classifiers at their own training-selected thresholds; it is not an exact attribution of errors in the hybrid policy.','',
        '## Stability across splits','']
    lines += [f'- {k}: {v}' for k,v in result['stability'].items()]
    lines+=['','## Interpretation and next decision','',
        'Uncertainty identifies closeness to a boundary, not whether an extra measurement contains useful information. Classifier transitions include both feature effects and changed training-selected thresholds, so they are not causal biomarker effects. Training coefficients are descriptive and must not be interpreted as causal or clinical effects.','',
        'Keep the one-biomarker model as the reference. A future benefit-aware acquisition policy must learn benefit labels entirely within training data, with an additional nested evaluation layer. These post-hoc errors cannot be used to design and then claim independent validation on the same outer test records. Before that complexity, inspect feature redundancy and assess whether another modality supplies genuinely complementary information.','',
        'All results remain synthetic-only with unresolved biomarker units and missing-code conventions. Repeated experiments reuse the release, and no independent real test cohort is available. This is not a fairness audit, clinical recommendation, or evidence that the biomarkers lack clinical value.','',
        "Internal report. Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Observe accepted publication-review terms before external sharing."]
    (ROOT/'outputs/error_analysis_report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'by_class':tab,'by_uncertainty':bins,'stability':result['stability'],'mean_corrected':mean('corrected'),'mean_introduced':mean('introduced')},indent=2))

if __name__=='__main__': main()
