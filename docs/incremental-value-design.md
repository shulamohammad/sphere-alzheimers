# Feature ablation design

2026-11-09, specified before execution. Post-hoc follow-up to earlier studies, not confirmatory preregistration.

Six panels: each biomarker alone; PTAU217+GFAP; PTAU217+NFL; all three. Keep fixed logistic regression C=1 and identical ten five-fold seeds from prior studies. Compare AUROC, average precision, Brier and log loss. Report paired differences, without significance claims from dependent repetitions. This removes threshold-selection differences from the primary comparison.

Describe Pearson and Spearman correlations both pooled and within diagnostic groups. Do not infer conditional independence from correlations or causal biomarker effects from ablations. No new acquisition rule will be trained using outer-test labels. Negative values remain unchanged, and unresolved units/sentinel semantics remain documented assumptions.
