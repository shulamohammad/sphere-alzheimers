# Questions for the data provider

Not sent. These questions concern interpretation of the released synthetic data, not reconstruction of original records.

1. For biomarkers.csv, what are the assay units and preprocessing steps for PTAU217, GFAP, and NFL? Are these signed values intended to be analyzed as exported?
2. Are any finite numeric values used as missing-data or below-detection-limit codes? How should below-detection-limit measurements be handled in this release?
3. Does adrc_id consistently identify the same synthetic row across demographics and biomarkers, and which visit or aggregation defines the released measurements and consensus diagnosis?
4. Are there recommended evaluation protocols for classification using the decoded diagnosis labels? How should users interpret cross-validation within a jointly synthesized release compared with an independent held-out real-data evaluation?
5. Is a public biomarker dictionary available elsewhere? The portal Blood Biomarkers dictionary filter returned no entries during our check.

Until clarified: preserve exported signed values, do not apply clinical cutoffs, do not claim validated patient prediction, and keep the analysis explicitly exploratory. No outgoing message is authorized or sent.
