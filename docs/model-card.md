# Model and study card

Status: completed exploratory synthetic-data research package; no clinical deployment.

Task: cross-sectional classification of exactly labeled probable Alzheimer’s disease versus healthy controls. The 348-row joined subset contains 73 positive and 275 negative synthetic records. It excludes MCI and possible/mixed diagnoses.

Reference model: standardized logistic regression C=1 using PTAU217. Other panels and a fixed histogram-gradient-boosting comparator are evaluated. No final deployment model is exported: there is no approved clinical use or independent validation.

Intended use: learning, methods prototyping and internal research discussion. Not intended for diagnosis, screening, prognosis, treatment selection, insurance pricing, eligibility, denial or patient prioritization.

Evidence: repeated internal cross-validation, paired ablation, nested threshold selection, matched-measurement acquisition controls, calibration and descriptive subgroup checks. Repetitions reuse the same jointly synthesized release. All successive experiments are exploratory; no untouched confirmatory cohort remains.

Known gaps: uncertain assay units and finite missing codes, synthetic values outside physical ranges, possible synthetic-record dependence, no external cohort, no outcome/cost study, no sufficient fairness evidence. Age/sex subgroup summaries are small and descriptive. Equal measurement counts do not imply equal financial or clinical burden.

Outcome: additional tests did not improve the aggregate staged-policy tradeoff in this setting. This does not show biological redundancy or imply clinical recommendations. The project’s value is the reproducible negative finding and careful evaluation, not an established novel method.

Data governance: raw data and record-level predictions remain local and excluded from the deliverable archive. Follow the actual Stanford agreement before sharing results or publishing. No outgoing messages, external publication or data-access applications were performed.
