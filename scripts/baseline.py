"""Exploratory internal synthetic-data benchmark; no clinical validation."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
demo = pd.read_csv(ROOT/'data/raw/demographics_diagnosis.csv')
bio = pd.read_csv(ROOT/'data/raw/biomarkers.csv')
df = demo.merge(bio, on='adrc_id', validate='one_to_one')
df = df[df.diagnosis_consensus.isin(['Probable Alzheimers Disease','Healthy Control'])].sort_values('adrc_id').reset_index(drop=True)
y = (df.diagnosis_consensus == 'Probable Alzheimers Disease').astype(int).to_numpy()
features = ['PTAU217','GFAP','NFL']
X = df[features].apply(pd.to_numeric, errors='raise')
assert np.isfinite(X.to_numpy()).all()
assert df.adrc_id.is_unique and len(df) == 348 and y.sum() == 73
# Preserve signed synthetic values. Do not invent clinical cutoffs or log-transform them.
splits = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=20261108).split(X,y))
results = []
predictions = {}
for name, cols in [('prevalence',features),('PTAU217',['PTAU217']),('three_biomarkers',features)]:
    model = DummyClassifier(strategy='prior') if name=='prevalence' else make_pipeline(StandardScaler(), LogisticRegression(C=1.0,max_iter=2000))
    p = cross_val_predict(model, X[cols], y, cv=splits, method='predict_proba')[:,1]
    predictions[name] = p
    tn,fp,fn,tp = confusion_matrix(y,p>=0.5,labels=[0,1]).ravel()
    # Split variability is not an independent clinical confidence interval.
    fold_auc = [float(roc_auc_score(y[test],p[test])) for _,test in splits]
    results.append(dict(model=name,features=[] if name=='prevalence' else cols,
        auroc=float(roc_auc_score(y,p)), average_precision=float(average_precision_score(y,p)),
        brier=float(brier_score_loss(y,p)), sensitivity_at_0_5=float(tp/(tp+fn)),
        specificity_at_0_5=float(tn/(tn+fp)), fold_auroc=fold_auc))
out = ROOT/'outputs'; out.mkdir(exist_ok=True)
metadata = dict(status='EXPLORATORY: units/sentinel conventions unconfirmed; synthetic-only evaluation',
    n=len(y),positive=int(y.sum()),negative=int((1-y).sum()),seed=20261108,
    sklearn=sklearn.__version__,numpy=np.__version__,pandas=pd.__version__,
    files={n:hashlib.sha256((ROOT/'data/raw'/n).read_bytes()).hexdigest() for n in ['demographics_diagnosis.csv','biomarkers.csv']},
    results=results)
(out/'baseline_metrics.json').write_text(json.dumps(metadata,indent=2)+'\n')
lines=['# Exploratory baseline results','',metadata['status'],'',
    '348 synthetic records: 73 probable AD and 275 healthy controls. Five fixed stratified folds; preprocessing fitted within training folds. Fixed regularization; no tuning or model selection. All methods share folds. Threshold 0.5 is descriptive, not clinically optimized.','',
    '| Model | AUROC | Average precision | Brier score | Sensitivity at 0.5 | Specificity at 0.5 |',
    '|---|---:|---:|---:|---:|---:|']
for r in results:
    lines.append(f"| {r['model']} | {r['auroc']:.3f} | {r['average_precision']:.3f} | {r['brier']:.3f} | {r['sensitivity_at_0_5']:.3f} | {r['specificity_at_0_5']:.3f} |")
lines += ['', 'Average precision prevalence reference: '+f'{y.mean():.3f}. Lower Brier is better.', '',
    'The pooled prevalence-model AUROC can deviate from 0.5 because training prevalence varies by fold; within each fold its AUROC is 0.5.', '',
    'These results measure internal separability in a jointly synthesized release. Synthetic rows may be dependent. No independent real-data validation, fairness claim, causal claim, cost saving or patient-outcome claim is supported. Biomarker values include negatives; these were retained as exported, with no assumption that they are physical concentrations. Dictionary verification remains unresolved. This run is an engineering benchmark, not a validated scientific result.', '',
    'Stanford Alzheimer\'s Disease Research Center, NIH/NIA grant P30 AG066515. Source: https://adrc-sphere.stanford.edu/. Internal report; comply with accepted publication-review terms before sharing.']
(out/'baseline_report.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(results,indent=2))
