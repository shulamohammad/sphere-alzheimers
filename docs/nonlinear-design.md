# Nonlinear comparison

Specified 2026-11-09 before execution, informed by previous exploratory results.

Compare fixed standardized logistic regression C=1 with histogram gradient boosting: 100 iterations, learning rate 0.05, at most 4 leaves, minimum 20 samples per leaf, L2 regularization 1, early stopping disabled. No tuning. Compare each model on PTAU217 alone and on all three biomarkers. The one-feature nonlinear comparator separates nonlinear effects of PTAU217 from incremental value of GFAP/NFL.

Use the same 348 synthetic rows and ten stratified five-fold repetitions. Report paired per-repeat AUROC, average precision, Brier and log loss. Record ranges, not inferential confidence intervals. No threshold selection or policy fitting. These tests reuse the same release; a winning method would not constitute independent confirmation. Preserve signed data and all existing limitations about units, sentinel codes, synthesis dependence and clinical generalization.
