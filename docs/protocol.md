# Draft evaluation protocol

Status: prospective plan, not a preregistration or completed analysis.

## Audit before modeling

- Record each file's official source, acquisition date, release/version, SHA-256, dimensions and dictionary.
- Verify the participant identifier, repeat visits, timestamp semantics, duplicate records, and join cardinality. Reject joins that multiply rows unexpectedly.
- Decode diagnosis categories explicitly. Do not silently merge Parkinson's disease, Lewy-body disease, MCI, and AD into one label.
- Verify whether longitudinal relationships survive synthesis. Forecasting is out of scope until this is established.
- Identify missing-value sentinels from the dictionary rather than treating every numeric code as a measurement.
- Record available counts and intersections per modality. Compare cohorts before comparing feature sets.
- Distinguish targeted blood biomarkers from broad proteomic panels; their costs are not interchangeable.

## Leakage and synthetic-data limitations

Exclude identifiers, diagnosis encodings, and variables directly used to construct the endpoint from primary predictors. In particular, inspect CDR and cognitive scores against diagnostic criteria. Any cognitive-score-inclusive model must be clearly separated and justified.

Fit imputation, scaling, feature selection, calibration and tuning within training partitions. Keep all visits for a synthetic participant together if identifiers support this. Review the SPHERE generation paper: a globally synthesized release may induce cross-record dependence that ordinary row splitting does not remove. Internal held-out synthetic performance cannot establish independent real-patient performance.

## Evaluation design

Freeze cohort, target, eligible features, metrics and split procedure before model selection. Choose fold counts based on the smallest class and unique participant count; do not insist on a nominal five-fold design when counts are inadequate. Use nested stratified/grouped validation where feasible, with identical outer splits across methods. Reserve an untouched final evaluation set only if sample size supports it.

Baselines: prevalence/majority predictor; regularized logistic regression; a constrained boosted-tree model. Compare simple methods before adding neural architectures.

Report class counts, AUROC, AUPRC with prevalence reference, sensitivity/specificity at training-selected thresholds, Brier score and calibration plots. Estimate uncertainty at participant level when justified; state that intervals remain conditional on the synthetic release. Do not tune thresholds on evaluation folds.

## Measurement and cost experiments

Compare available low-dimensional measurements with richer panels on matched eligible cohorts. Separately evaluate the practical available-case population so complete-case selection is visible. Distinguish native missingness from simulated removal of measurements. Include a missingness-only diagnostic baseline to detect collection-pattern shortcuts.

Begin with measurement counts and explicitly hypothetical relative cost tiers. Add dollar figures only with defensible sources and sensitivity ranges. Report performance-cost tradeoffs, not actual savings. Later compare fixed measurement bundles with uncertainty-guided acquisition under the same budgets.

## Fairness and outcomes

Evaluate age and other available, documented groups only when sample sizes permit useful estimates. Report denominators and uncertainty; do not claim fairness from nonsignificant differences. Synthetic group patterns may differ from those in real populations. No outcome, clinical utility, causal effect or insurance eligibility claims follow from this study alone.

## Completion criteria for milestone one

Access terms recorded; source files inventoried; target and feature set frozen; leakage risks documented; simple baselines run reproducibly; cohort counts and uncertainty reported; limitations written before advancing to more complex models.
