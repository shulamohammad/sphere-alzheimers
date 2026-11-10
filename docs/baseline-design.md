# Exploratory benchmark specification

Fixed before first training run, 2026-11-08.

Population: exact probable AD and healthy-control labels, joined one-to-one with biomarkers; 348 synthetic rows. Features: PTAU217 alone versus PTAU217/GFAP/NFL. No demographics, cognitive scores, ID or diagnosis indicators in predictors.

Fixed logistic regression C=1, standardized within training folds, and a training-prevalence control. Five stratified folds, random seed 20261108, identical across methods. No hyperparameter search. Report pooled out-of-fold AUROC, average precision, Brier score, and sensitivity/specificity at a fixed descriptive threshold of 0.5. Fold AUROC describes split variability, not confidence in patient performance.

Portal dictionary filter for Blood Biomarkers returned zero entries on 2026-11-08. All 618 rows have finite values in the three biomarker columns, but each column contains negative values. Keep signed values unchanged for this explicitly exploratory engineering run. Do not label values as physical concentrations or assume absence of numeric sentinels. Confirm semantics before a research-grade experiment.

The method preprint describes joint synthesis and evaluates some downstream tasks by training on synthetic data and testing on original held-out representations. Our release has no original held-out test set, so internal synthetic cross-validation is a weaker evaluation and cannot validate real-patient generalization.

Sources: https://adrc-sphere.stanford.edu/ (interactive dictionary); https://pmc.ncbi.nlm.nih.gov/articles/PMC13596149/ (method preprint).
