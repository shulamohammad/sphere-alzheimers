# Initial SPHERE data audit

Date: 2026-11-08. Source: official archive from https://adrc-sphere.stanford.edu/ after the user completed access.

## Verified from downloaded files

- Demographics: 644 records, 30 columns including participant ID.
- Targeted biomarkers: 618 records, 4 columns including participant ID; PTAU217, GFAP, NFL.
- IDs are nonempty and unique within both tables. All 618 biomarker IDs match demographics. There are 26 demographics records without a biomarker row.
- Raw diagnoses are more detailed than the explorer's grouped labels. Matched records include 73 probable AD, 275 healthy controls, and 121 MCI. Other records include other diagnoses, possible/mixed AD and unknown labels.
- Diagnosis indicator columns are present. All diagnosis-derived columns and IDs must be excluded as predictors.

## Proposed first comparison

Probable AD versus healthy controls among matched participants: 348 records (73 versus 275), before feature-level missingness checks. Keep MCI for a separately defined analysis. This is cross-sectional classification of synthetic diagnostic groups, not prediction of future disease.

## Outstanding checks

Verify biomarker units, transformations, missing codes and demographic encodings against the dictionary. Review the generation method for synthetic-record dependence and temporal validity. No clinical generalization or methodological novelty has been established. No model has been trained.

## Reproduction and storage

Run `python3 scripts/audit_data.py` from the project directory. It checks keys and shape and writes source checksums and aggregate diagnostics to outputs/initial_audit.json. Raw rows are not printed. The original archive remains in Downloads; only two initial tables were extracted into data/raw. Raw data and record-level outputs are excluded from version control. Aggregate metrics, reports, and figures are retained in the private repository. This is an internal working report; external disclosure must follow the accepted agreement.
