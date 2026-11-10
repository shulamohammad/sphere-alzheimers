"""Reconcile independent experiment outputs and key evaluation invariants."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name): return json.loads((ROOT/'outputs'/name).read_text())
def close(a,b): assert abs(a-b)<1e-10,(a,b)
def main():
    audit=read('initial_audit.json'); robust=read('robustness_metrics.json'); staged=read('staged_testing_metrics.json')
    errors=read('error_analysis_metrics.json'); ablation=read('incremental_value_metrics.json'); nonlinear=read('nonlinear_metrics.json'); checks=read('final_checks.json')
    assert audit['matched_participants']==618 and checks['n']==348 and checks['positive']==73
    for name,sha in checks['source_hashes'].items(): assert audit['files'][name]['sha256']==sha
    for old,stage,abl,nl in [('PTAU217','always_one','PTAU217','logistic_one'),('three_biomarkers','always_three','all_three','logistic_three')]:
        expected=robust['summary'][old]['mean_auroc']
        for v in [staged['summary'][stage]['auroc'],ablation['summary'][abl]['auroc'],nonlinear['summary'][nl]['auroc']]: close(v,expected)
    assert len(staged['fold_audit'])==400 and len(nonlinear['runs'])==40 and len(ablation['runs'])==60
    for seed in range(20261201,20261211):
        for fold in range(5):
            f={r['policy']:r for r in staged['fold_audit'] if r['seed']==seed and r['fold']==fold}
            for q in (25,50,75): assert f[f'staged_{q}']['acquired']==f[f'random_{q}']['acquired']
            assert f['always_one']['acquired']==0
            assert f['always_three']['acquired']==f['always_three']['n_test']
    for row in errors['by_class']:
        close(sum(row[k] for k in ['corrected','introduced','both_correct','both_wrong']),row['n_records'])
    for r in errors['repeats']:
        for old,k in [('PTAU217','errors_one'),('three_biomarkers','errors_three')]:
            z=next(x for x in robust['runs'] if x['seed']==r['seed'] and x['model']==old)
            close(73*(1-z['nested']['sensitivity'])+275*(1-z['nested']['specificity']),r[k])
    assert sum(x['n'] for x in checks['calibration_bins'])==348
    assert len(checks['negative_control']['all_aucs'])==25
    for groups in [('female','male'),('age_under_75','age_75_plus')]:
        assert sum(x['n'] for x in checks['subgroups'] if x['group'] in groups)==348
    status={'status':'passed','checks':['source hashes','cohort counts','cross-experiment baseline equality','staged/random measurement budgets','endpoint acquisition','error-transition reconciliation','calibration denominators','subgroup denominators','negative-control count']}
    (ROOT/'outputs/verification.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status))
if __name__=='__main__': main()
