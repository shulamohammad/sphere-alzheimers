# Experiment 2: split stability and threshold selection

Specified before running this experiment. Existing baseline results informed this follow-up; this is not a preregistered confirmatory study.

Keep the original 348-row synthetic cohort, features and fixed logistic regression. Compare PTAU217 alone and the three-biomarker panel over 10 predefined stratified five-fold splits (seeds 20261201–20261210). Report paired per-repeat AUROC differences and their range; these are split-sensitivity summaries, not independent samples or confidence intervals.

Within each outer training set, obtain four-fold inner out-of-fold scores. Choose the largest threshold with inner sensitivity at least 0.80, then evaluate that threshold on the untouched outer test fold. The 0.80 target is a methodological example, not a clinical requirement or guarantee. Compare with threshold 0.5. Do not choose thresholds from outer test labels.

Retain signed biomarker values; no clipping, assumed physical units or log transformation. Units and numeric missing codes remain unresolved. The SPHERE preprint says non-Gaussian continuous columns can be smoothed toward Gaussian distributions; that makes synthetic negative values plausible but does not confirm the provenance of these particular negatives.

Reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC13596149/ (Discussion and Methods). Independent real-data validation remains necessary for clinical claims. The jointly synthesized release does not supply an independent real-patient test set.
