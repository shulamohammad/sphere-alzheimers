# Staged testing experiment

Specified before execution; exploratory follow-up to the existing baseline.

Use the same 348 complete synthetic records and ten fixed five-fold splits as experiment 2. Preserve exported values and use measurement count rather than monetary cost. A p-tau217-only model costs one measurement; acquiring GFAP and NFL adds two. The all-three model is available only for acquired cases in the simulated policy.

Within each outer training set, obtain four-fold out-of-fold probabilities from fixed standardized logistic models. Select a first-stage decision threshold targeting 80% training sensitivity. Define uncertainty as proximity of the first-stage probability to this decision threshold (a heuristic, not a calibrated confidence guarantee). Set routing margins at the 25th, 50th and 75th percentiles of training uncertainty distances. Apply these fixed margins to outer test probabilities. The achieved test budget may differ from the nominal training fraction.

Combine the three-feature score for routed cases with the one-feature score for other cases. Fit the hybrid decision threshold using training out-of-fold scores, targeting 80% sensitivity. Routing and final thresholds never use outer labels. Refit the two base models on the full outer training fold for test scoring. Training out-of-fold predictions are reused to design the policy; only outer evaluation is held out.

Comparators: always one, always three, and random acquisition at each staged policy's exact achieved outer-test measurement count. Random training acquisition uses the same number selected by the training uncertainty margin. Random routing uses fixed seeds and no labels. Report aggregate sensitivity, specificity, balanced accuracy, AUROC, Brier, acquisition fraction and mean measurements. Same outer test folds for all comparisons.

Budget 0 and full acquisition are checked against always-one and always-three endpoints. Random routing must match acquisition counts. No policy will be selected for deployment or described as optimal from these outer results. Split ranges are descriptive, not confidence intervals; repeated folds reuse records. No real monetary savings, patient outcomes or clinical validity can be inferred. Units/missing-code assumptions and synthetic dependence remain unresolved.
