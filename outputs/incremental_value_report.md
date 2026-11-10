# Incremental biomarker value

Exploratory follow-up, 2026-11-09. Same 348 synthetic records; ten paired five-fold repetitions. Fixed standardized logistic regression (C=1), trained separately for each prespecified panel. Standardization is training-only. No threshold tuning is needed for these probability metrics.

| Panel | Mean AUROC | Average precision | Brier | Log loss | AUROC change vs p-tau217 |
|---|---:|---:|---:|---:|---:|
| PTAU217 | 0.772 | 0.536 | 0.133 | 0.433 | +0.000 |
| GFAP | 0.673 | 0.406 | 0.152 | 0.478 | -0.099 |
| NFL | 0.621 | 0.298 | 0.162 | 0.506 | -0.151 |
| PTAU217+GFAP | 0.765 | 0.523 | 0.134 | 0.437 | -0.007 |
| PTAU217+NFL | 0.762 | 0.528 | 0.134 | 0.438 | -0.010 |
| all_three | 0.757 | 0.518 | 0.135 | 0.440 | -0.014 |

Lower Brier/log loss is better. Differences are paired by split, not independent replicates. No confidence intervals or p-values are claimed.

## Feature correlations

| Population | n | p-tau217 / GFAP | p-tau217 / NfL | GFAP / NfL |
|---|---:|---:|---:|---:|
| pooled | 348 | 0.616 | 0.325 | 0.518 |
| healthy_control | 275 | 0.556 | 0.280 | 0.480 |
| probable_AD | 73 | 0.600 | 0.323 | 0.551 |

Pearson correlations are descriptive; Spearman values are retained in the JSON. Pooled correlations can partly reflect class differences. Neither high nor low correlation establishes incremental predictive value.

## Scope of conclusion

These ablations test whether added features improve this fixed linear classifier on this release. Failure to improve does not show that a biomarker lacks biological information, nonlinear predictive value or clinical usefulness. We have repeatedly inspected the same dataset, so this is discovery work, not independent confirmation. No optimal panel or clinical recommendation follows.

Signed synthetic values are retained. Exact units and finite missing-code conventions remain unresolved. No additional acquisition rule should be justified solely by these post-hoc results.

Internal report. Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Follow accepted publication-review terms before external sharing.
