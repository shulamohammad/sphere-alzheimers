"""Build the final internal report and figures from verified metrics."""
import base64
import html
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'
def read(n): return json.loads((OUT/n).read_text())

def main():
    assert read('verification.json')['status']=='passed'
    nl=read('nonlinear_metrics.json'); staged=read('staged_testing_metrics.json')
    checks=read('final_checks.json'); errors=read('error_analysis_metrics.json')
    figures=OUT/'figures'; figures.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    names=['logistic_one','logistic_three','boosting_one','boosting_three']
    labels=['Logistic · p-tau217','Logistic · three markers','Boosting · p-tau217','Boosting · three markers']
    vals=[nl['summary'][n]['auroc'] for n in names]
    lo=[min(r['auroc'] for r in nl['runs'] if r['model']==n) for n in names]
    hi=[max(r['auroc'] for r in nl['runs'] if r['model']==n) for n in names]
    axs[0].barh(labels,vals,color=['#166c80','#8dabb0','#8dabb0','#8dabb0'])
    axs[0].errorbar(vals,range(4),xerr=[np.array(vals)-lo,np.array(hi)-vals],fmt='none',color='#16313a',capsize=3)
    axs[0].set(xlim=(0,1),xlabel='AUROC (higher is better)',title='A. Model comparison'); axs[0].invert_yaxis()
    for i,v in enumerate(vals): axs[0].text(v+.025,i,f'{v:.3f}',va='center')
    for prefix,color,label in [('staged','#c47724','Uncertainty routing'),('random','#67818b','Random routing')]:
        ss=[staged['summary'][f'{prefix}_{q}'] for q in (25,50,75)]
        axs[1].plot([s['mean_measurements'] for s in ss],[s['balanced_accuracy'] for s in ss],'o-',color=color,label=label)
    for name,marker,label in [('always_one','s','Always one'),('always_three','D','Always three')]:
        s=staged['summary'][name]; axs[1].scatter(s['mean_measurements'],s['balanced_accuracy'],marker=marker,s=65,label=label)
    axs[1].set(xlabel='Mean biomarker measurements per record',ylabel='Balanced accuracy',ylim=(.64,.72),title='B. Simulated measurement tradeoff')
    axs[1].legend(fontsize=8)
    fig.suptitle('Exploratory SPHERE benchmark · 348 synthetic records',fontsize=14)
    fig.savefig(figures/'results.png',dpi=180); fig.savefig(figures/'results.svg'); plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.5,5),layout='constrained')
    ax.plot([0,1],[0,1],'--',color='gray',label='Perfect calibration reference')
    bins=[b for b in checks['calibration_bins'] if b['n']]
    ax.plot([b['mean_probability'] for b in bins],[b['observed_fraction'] for b in bins],'o-',color='#166c80',label='p-tau217 logistic model')
    for b in bins: ax.annotate(f"n={b['n']}",(b['mean_probability'],b['observed_fraction']),xytext=(5,6),textcoords='offset points',fontsize=8)
    ax.set(xlim=(0,1),ylim=(0,1),xlabel='Mean predicted probability',ylabel='Observed positive fraction',title='Calibration · one prespecified five-fold split')
    ax.legend(fontsize=8); fig.savefig(figures/'calibration.png',dpi=180); plt.close(fig)
    blocks=[]
    def h(title): blocks.append(f'<h2>{html.escape(title)}</h2>')
    def p(text): blocks.append(f'<p>{text}</p>')
    def table(headers,rows):
        blocks.append('<div class="table"><table><thead><tr>'+''.join(f'<th>{html.escape(str(x))}</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>')
    h('Research question and outcome')
    p('Does acquiring GFAP and NfL selectively improve classification of probable Alzheimer’s disease versus healthy controls beyond p-tau217 alone, while using fewer measurements than a full panel?')
    p('<strong>In this exploratory synthetic-data benchmark, the staged policy did not improve the observed error–measurement tradeoff.</strong> The p-tau217-only logistic model had the highest mean AUROC among the fixed models tested. Extra biomarkers improved the boosting model relative to one-feature boosting, but that model remained below the logistic reference. This is a bounded negative result, not proof of biomarker redundancy or clinical superiority.')
    h('Data and endpoint')
    p('The official SPHERE archive supplied 644 demographics records and 618 targeted-biomarker records. All biomarker IDs matched demographics and were unique. The analysis retained 73 records labeled exactly “Probable Alzheimers Disease” and 275 labeled “Healthy Control.” MCI, possible/mixed AD, other diagnoses and unknown labels were excluded. This case–control contrast is not a screening population or a forecast of future Alzheimer’s disease.')
    p('Predictors were PTAU217, GFAP and NFL. IDs, diagnosis indicators and cognitive scores were excluded. Exported values were finite but included negatives. Values were preserved unchanged; exact assay units, preprocessing and finite missing-code conventions remain unresolved. Thus all numerical results are conditional on treating exported values as usable synthetic features.')
    h('Methods and evaluation')
    p('We used fixed logistic regression with C=1 and training-fold standardization, plus a fixed modest histogram-boosting comparator (100 iterations, learning rate 0.05, at most four leaves, minimum leaf size 20, L2=1). There was no hyperparameter search. Ten stratified five-fold repetitions used seeds 20261201–20261210. Methods shared test folds; repeated observations are dependent.')
    p('Within each outer training set, four-fold predictions selected the largest decision threshold attaining at least 80% training sensitivity. Outer test labels did not choose thresholds. Staged policies requested two additional measurements when first-stage scores were near the training-derived decision boundary; margins used the 25th, 50th or 75th training distance percentile. Random comparators matched achieved test acquisition counts in each fold. Hybrid scores received a training-selected final threshold. This simulated acquisition of already-measured features; measurement counts are not dollars, visits or actual savings.')
    p('The study progressed through exploratory follow-ups after inspecting earlier results. The release has therefore been reused for discovery. There is no untouched final cohort, independent real-data test or preregistered confirmatory analysis. Split ranges in figures are not confidence intervals.')
    h('Model comparisons')
    table(['Model','AUROC','Average precision','Brier','Log loss'],[[label]+[f"{nl['summary'][name][m]:.3f}" for m in ['auroc','average_precision','brier','log_loss']] for name,label in zip(names,labels)])
    p('AUROC and average precision are better when higher; Brier and log loss are better when lower. Positive prevalence is 73/348 (21.0%). The simple model also had the best mean probability-error scores among these fixed choices. This does not establish optimality among all possible algorithms.')
    def embed(path,alt): blocks.append(f'<img alt="{alt}" src="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}">')
    embed(figures/'results.png','Model comparison and measurement tradeoff')
    p('Panel A shows mean AUROC and min–max variation over ten repeated splits. Panel B compares mean balanced accuracy, the average of sensitivity and specificity, against measurement count. Its vertical axis is restricted to show small differences.')
    h('Staged-testing results')
    table(['Policy','Measurements','Sensitivity','Specificity','Balanced accuracy'],[[n,f"{staged['summary'][n]['mean_measurements']:.2f}",f"{staged['summary'][n]['sensitivity']:.1%}",f"{staged['summary'][n]['specificity']:.1%}",f"{staged['summary'][n]['balanced_accuracy']:.3f}"] for n in ['always_one','staged_25','random_25','staged_50','random_50','staged_75','random_75','always_three']])
    p('Additional acquisition did not improve the aggregate tradeoff relative to always using p-tau217 in these experiments. Uncertainty-based routing trailed its budget-matched random comparator on mean balanced accuracy at all three budgets. We did not select a deployment policy from these results.')
    h('Why the extra measurements failed to help here')
    table(['Group','Records','Errors corrected','Errors introduced'],[[r['group'],r['n_records'],f"{r['corrected']:.1f}",f"{r['introduced']:.1f}"] for r in errors['by_class']])
    p('Averaged across repetitions, moving from one to three biomarkers corrected 7.0 errors but introduced 16.4. The excess was concentrated in healthy-control false positives. Among records near the first-stage boundary, corrections occurred in 7.8% of record-evaluations and new errors in 17.4%. These comparisons include both feature changes and changed decision thresholds. They do not isolate causal effects of biomarkers. Uncertainty identifies unstable decisions, not necessarily cases where another measurement is informative.')
    h('Calibration, subgroup descriptions and sanity checks')
    embed(figures/'calibration.png','Calibration bins with denominators')
    p('Calibration uses one prespecified split (seed 20261201), five fixed probability bins, and uncalibrated out-of-fold scores. Sparse high-probability bins should not be overinterpreted. A separate age/sex-only reference had AUROC '+f"{checks['demographics_only']['auroc']:.3f}"+'. Twenty-five label-shuffle controls averaged AUROC '+f"{checks['negative_control']['mean_auc']:.3f}"+'; this is an engineering sanity check, not an inferential test for dependent synthetic records.')
    table(['Group','n','Positive / negative','AUROC','Sensitivity','Specificity'],[[r['group'],r['n'],f"{r['positive']} / {r['negative']}",f"{r['auroc']:.3f}",f"{r['sensitivity']:.1%}",f"{r['specificity']:.1%}"] for r in checks['subgroups'] if 'auroc' in r])
    p('These subgroup summaries reuse one split and have small positive counts. They describe variation worth investigating; they do not establish fairness or inequity in a real population. Age groups overlap the sex groups. Protected attributes were not used in the primary models. No subgroup-specific thresholds or eligibility decisions were implemented.')
    h('Limitations that constrain the conclusion')
    p('SPHERE is a jointly synthesized release; ordinary row-level cross-validation is weaker evidence than evaluation on independent original records. Clinical units and numeric sentinel definitions were not confirmed. The narrow probable-AD-versus-control endpoint excludes diagnostically difficult groups and can exaggerate relevance to real screening. Repeated examination creates selection optimism. Models and routing heuristics cover a limited design space; mixed scores are not independently calibrated. No real costs, patient outcomes, clinical utility or causal effects were measured. Data access and publication-review obligations continue to apply.')
    h('Independent validation plan—not completed')
    p('ADNI documents a UPENN plasma table containing p-tau217, GFAP and NfL. Access is through an application and approved-researcher archive. We have not applied, accepted an agreement or analyzed ADNI data. Matching biomarker names does not establish compatible assays or scales. Before transfer, confirm assay units, transformations, diagnostic mapping, visit alignment, participant independence and cohort overlap. Freeze features and model choices before evaluating a genuinely separate test cohort. Any recalibration requires a separate calibration partition; report recalibrated and unrecalibrated results distinctly. If harmonization is not defensible, replicate the analysis design within ADNI rather than claiming direct model transport.')
    h('What this project contributes')
    p('The completed contribution is an auditable exploratory benchmark: paired feature ablations, a nonlinear comparator, training-only staged-acquisition rules, matched-budget random controls and error-transition analysis. It demonstrates a failure mode in this setting: uncertain cases need not benefit from additional measurements. A methodological breakthrough, publication-level novelty and clinical validation have not been established. For an application, accurately describe this as an independent reproducible research project and explain the decisions you can defend.')
    h('Reproduction and delivery')
    p('Run <code>python scripts/run_all.py</code> in the project’s installed environment. The runner executes the audit, all experiments, final checks, reconciliation and this report. Dependencies are pinned in requirements.txt. Input hashes and environment details are retained in outputs. The distributable internal archive excludes raw datasets, credentials, environments and individual-record predictions. Do not publish the archive or results without checking the accepted Stanford agreement.')
    h('Sources and acknowledgment')
    p('<a href="https://adrc-sphere.stanford.edu/">Stanford SPHERE portal</a>; <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC13596149/">SPHERE methods preprint</a>; <a href="https://adni.loni.usc.edu/quick-start-guide-asset/bioflood.html">ADNI biofluid documentation</a>; <a href="https://adni.loni.usc.edu/data-samples/">ADNI access overview</a>. Sources reviewed November 9, 2026. Stanford Alzheimer’s Disease Research Center, NIH/NIA grant P30 AG066515.')
    style='body{font:17px/1.6 system-ui,sans-serif;color:#20343c;max-width:1060px;margin:48px auto;padding:0 24px;background:#fff}h1{font-size:38px;line-height:1.15}h2{margin-top:42px;color:#135a6b;font-size:25px}p{max-width:920px}.meta{color:#607078}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px 12px;border-bottom:1px solid #dce4e6;text-align:left}th{background:#edf4f5}img{width:100%;height:auto;margin:20px 0}.table{overflow:auto}code{background:#edf4f5;padding:3px 5px}a{color:#12677c}@media print{body{margin:0;font-size:11pt}h2{break-after:avoid}table,img{break-inside:avoid}}'
    doc='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SPHERE research report</title><style>'+style+'</style><body><p class="meta">COMPLETED EXPLORATORY STUDY · NOVEMBER 9, 2026 · INTERNAL REVIEW</p><h1>Do uncertain predictions benefit from more biomarkers?</h1><p class="meta">A reproducible staged-testing study on SPHERE synthetic Alzheimer’s data</p>'+''.join(blocks)+'</body></html>'
    (OUT/'FINAL_REPORT.html').write_text(doc)
    print('Saved self-contained FINAL_REPORT.html and research figures.')

if __name__=='__main__': main()
