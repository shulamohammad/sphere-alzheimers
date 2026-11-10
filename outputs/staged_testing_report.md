# Staged biomarker testing: exploratory results

348 synthetic records; 10 paired repetitions of five-fold evaluation. Fixed logistic models; training-only routing margins and decision thresholds. Target sensitivity is 80% on inner scores, not guaranteed on held-out records.

| Policy | Mean measurements | Acquire extra tests | AUROC | Sensitivity | Specificity | Balanced accuracy |
|---|---:|---:|---:|---:|---:|---:|
| always_one | 1.00 | 0.0% | 0.772 | 79.0% | 59.4% | 0.692 |
| always_three | 3.00 | 100.0% | 0.757 | 79.2% | 56.0% | 0.676 |
| staged_25 | 1.50 | 25.1% | 0.763 | 78.9% | 56.4% | 0.676 |
| random_25 | 1.50 | 25.1% | 0.769 | 79.6% | 58.3% | 0.689 |
| staged_50 | 2.01 | 50.7% | 0.762 | 78.8% | 56.4% | 0.676 |
| random_50 | 2.01 | 50.7% | 0.764 | 78.8% | 58.9% | 0.688 |
| staged_75 | 2.50 | 75.1% | 0.761 | 78.6% | 56.4% | 0.675 |
| random_75 | 2.50 | 75.1% | 0.762 | 78.8% | 56.6% | 0.677 |

Staged suffixes are nominal training acquisition percentages. Random comparators match the staged policy’s achieved test count in every fold; they use fixed random seeds, not test labels. Measurement count is a proxy, not dollars or visits. AUROC and Brier use uncalibrated mixed model scores, so interpret cautiously.

## Paired balanced-accuracy differences versus budget-matched random acquisition

Ranges below reflect split variability, not confidence intervals or independent replications.
- 25% nominal: mean -0.0131; range -0.0378 to +0.0032.
- 50% nominal: mean -0.0122; range -0.0259 to +0.0046.
- 75% nominal: mean -0.0020; range -0.0173 to +0.0147.

## Limits

This simulates acquisition by hiding already-observed measurements. It does not evaluate real missing-data collection, actual expenses, clinical outcomes or patient-level generalization. Exact assay units and numeric sentinel conventions remain unresolved. Signed values were retained. The same jointly synthesized release is reused across experiments; repeats are dependent and no independent final test set exists. No best-policy claim is warranted.

Internal report. Source: Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Follow the accepted agreement before external disclosure.
