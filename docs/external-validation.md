# Independent validation: identified, not performed

ADNI provides a UPENN plasma biomarker table including p-tau217, GFAP and NfL. The official table was renamed UPENN_PLASMA_FUJIREBIO_QUANTERIX. Source: https://adni.loni.usc.edu/quick-start-guide-asset/bioflood.html and https://adni.loni.usc.edu/updated-upenn-plasma-biomarkers-ab42-ab40-ptau217-nfl-gfap-measured-by-fujirebio-quanterix-adni1go234-data-now-available/

Access is for approved researchers through LONI IDA: https://adni.loni.usc.edu/data-samples/ . Checked 2026-11-09. No application, agreement acceptance, contact or external analysis has been performed.

Before validation: obtain authorized access; verify compatible assays, units, transformations, detection-limit conventions, participant independence and diagnostic labels. Align visits using documented date windows; do not mix future measurements with baseline labels. Determine whether source cohorts overlap. Freeze feature set, parameters and endpoints before testing.

If direct transfer from synthetic data is meaningful, freeze the SPHERE-fitted model and its scaling, then evaluate on the independent cohort without tuning. Any recalibration must use a distinct calibration partition. Otherwise describe work as a replication with a new training/test split, not external validation of the original fitted model. Do not infer assay equivalence from shared feature names.
