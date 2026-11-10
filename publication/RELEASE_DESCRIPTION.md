# Selective Biomarker Testing for Alzheimer’s Classification

An exploratory evaluation using SPHERE synthetic data.

## Release description

This research package evaluates whether selectively adding GFAP and NfL to p-tau217 improves diagnostic-group classification under measurement budgets. It includes reproducible analysis code, pinned dependencies, aggregate results, and a self-contained report.

The analysis uses 348 synthetic records representing probable Alzheimer’s disease and healthy-control groups. Across repeated cross-validation, p-tau217-only logistic regression achieved mean AUROC 0.772; the three-marker logistic model achieved 0.757. The tested uncertainty-based selective-testing strategies did not improve the observed error–measurement tradeoff over the one-marker reference.

These are exploratory findings from a synthetic dataset, not evidence that additional biomarkers lack clinical value. This study does not predict future disease or establish clinical utility, monetary savings, patient outcomes, or fairness. Assay semantics remain incompletely confirmed; independent real-data validation has not been performed. Repeated exploration on the same release limits confirmatory interpretation.

## Reproduction and data access

See README.md and outputs/FINAL_REPORT.html in the research package. Researchers must obtain their own authorized SPHERE data access. Raw data, record-level predictions, credentials, and local environments are excluded.

## Acknowledgment

Stanford Alzheimer’s Disease Research Center, NIH/NIA grant P30 AG066515.

## Publication status

Prepared for release; not published or peer reviewed. Public posting awaits documentation that the Stanford pre-disclosure review requirement has been satisfied. No repository URL, DOI, or acceptance is claimed.
