# Fixed nonlinear model comparison

Exploratory synthetic-data benchmark. Same 348 records, ten paired five-fold repetitions. No hyperparameter selection. Boosting uses 100 iterations, learning rate 0.05, maximum 4 leaves, minimum 20 samples per leaf, L2=1, no early stopping. Logistic regression uses training-only scaling and C=1.

| Model | AUROC | Average precision | Brier | Log loss |
|---|---:|---:|---:|---:|
| logistic_one | 0.772 | 0.536 | 0.133 | 0.433 |
| logistic_three | 0.757 | 0.518 | 0.135 | 0.440 |
| boosting_one | 0.722 | 0.453 | 0.142 | 0.459 |
| boosting_three | 0.738 | 0.461 | 0.143 | 0.457 |

Lower Brier and log loss are better. One-feature boosting tests nonlinear PTAU217 patterns; its comparison with three-feature boosting tests added-feature value within this model family.

## Paired AUROC differences

- boosting_one minus logistic_one: mean -0.0502, range -0.0689 to -0.0310.
- boosting_three minus logistic_one: mean -0.0338, range -0.0641 to -0.0122.
- boosting_three minus boosting_one: mean +0.0164, range -0.0106 to +0.0417.

Ranges describe repeated split variability, not confidence intervals. Repeats are dependent and the dataset has been examined repeatedly. No independent confirmation, optimal model, clinical efficacy or lack of biological usefulness is established. Fixed boosting is one nonlinear baseline, not a comprehensive nonlinear search.

Signed synthetic values remain unchanged; assay units and finite missing codes remain unresolved. Joint synthesis may create cross-record dependencies. No real-data test cohort is available.

Internal report. Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Follow accepted publication-review requirements before external sharing.
