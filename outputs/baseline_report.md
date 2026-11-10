# Exploratory baseline results

EXPLORATORY: units/sentinel conventions unconfirmed; synthetic-only evaluation

348 synthetic records: 73 probable AD and 275 healthy controls. Five fixed stratified folds; preprocessing fitted within training folds. Fixed regularization; no tuning or model selection. All methods share folds. Threshold 0.5 is descriptive, not clinically optimized.

| Model | AUROC | Average precision | Brier score | Sensitivity at 0.5 | Specificity at 0.5 |
|---|---:|---:|---:|---:|---:|
| prevalence | 0.492 | 0.207 | 0.166 | 0.000 | 1.000 |
| PTAU217 | 0.777 | 0.544 | 0.131 | 0.247 | 0.978 |
| three_biomarkers | 0.770 | 0.537 | 0.132 | 0.247 | 0.978 |

Average precision prevalence reference: 0.210. Lower Brier is better.

The pooled prevalence-model AUROC can deviate from 0.5 because training prevalence varies by fold; within each fold its AUROC is 0.5.

These results measure internal separability in a jointly synthesized release. Synthetic rows may be dependent. No independent real-data validation, fairness claim, causal claim, cost saving or patient-outcome claim is supported. Biomarker values include negatives; these were retained as exported, with no assumption that they are physical concentrations. Dictionary verification remains unresolved. This run is an engineering benchmark, not a validated scientific result.

Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Source: https://adrc-sphere.stanford.edu/. Internal report; comply with accepted publication-review terms before sharing.
