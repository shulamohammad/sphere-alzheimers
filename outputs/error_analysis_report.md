# Error analysis: adding GFAP and NFL

Post-hoc audit of the same 348 synthetic records and ten paired five-fold repetitions. All predictions are outer-held-out; thresholds are selected within training folds. No new routing policy is fitted from these error labels.

Per repetition: 7.0 mistakes corrected; 16.4 new mistakes introduced. Total errors: 126.9 with one biomarker versus 136.3 with three.

| Group | Unique records | Corrected errors | Introduced errors | Both correct | Both wrong |
|---|---:|---:|---:|---:|---:|
| Probable AD | 73 | 1.5 | 1.4 | 56.3 | 13.8 |
| Healthy control | 275 | 5.5 | 15.0 | 148.4 | 106.1 |

Counts are averages over repetitions, not new patients.

## Is uncertainty a useful acquisition signal?

| Region | Record-evaluations | Error correction rate | New-error rate | Brier change (three minus one) |
|---|---:|---:|---:|---:|
| Near threshold (training 25% margin) | 874 | 7.8% | 17.4% | +0.0023 |
| Outside margin | 2606 | 0.1% | 0.5% | +0.0024 |

Record-evaluations reuse the same records. These are descriptive pooled rates, not independent observations. Positive Brier change is worse. This compares the two standalone classifiers at their own training-selected thresholds; it is not an exact attribution of errors in the hybrid policy.

## Stability across splits

- ever_corrected: 37
- ever_harmed: 69
- corrected_at_least_8_of_10: 0
- harmed_at_least_8_of_10: 1
- both_directions_across_splits: 22

## Interpretation and next decision

Uncertainty identifies closeness to a boundary, not whether an extra measurement contains useful information. Classifier transitions include both feature effects and changed training-selected thresholds, so they are not causal biomarker effects. Training coefficients are descriptive and must not be interpreted as causal or clinical effects.

Keep the one-biomarker model as the reference. A future benefit-aware acquisition policy must learn benefit labels entirely within training data, with an additional nested evaluation layer. These post-hoc errors cannot be used to design and then claim independent validation on the same outer test records. Before that complexity, inspect feature redundancy and assess whether another modality supplies genuinely complementary information.

All results remain synthetic-only with unresolved biomarker units and missing-code conventions. Repeated experiments reuse the release, and no independent real test cohort is available. This is not a fairness audit, clinical recommendation, or evidence that the biomarkers lack clinical value.

Internal report. Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Observe accepted publication-review terms before external sharing.
