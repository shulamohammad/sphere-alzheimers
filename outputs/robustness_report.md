# Split stability and nested thresholds

Exploratory synthetic-only results; dependent repeats, no clinical CI; units and missing-code conventions unresolved.

10 paired repetitions of five-fold evaluation. Threshold selected using four-fold scores inside each training fold, targeting sensitivity >= 0.80. Outer test labels never select the threshold. Repetitions reuse the same records.

| Model | Mean AUROC | AUROC range | Sensitivity at 0.5 | Nested sensitivity | Nested specificity |
|---|---:|---:|---:|---:|---:|
| PTAU217 | 0.772 | 0.767–0.776 | 0.241 | 0.790 | 0.594 |
| three_biomarkers | 0.757 | 0.749–0.767 | 0.241 | 0.792 | 0.560 |

Paired AUROC difference (three minus one): mean -0.0143; range -0.0228 to -0.0051. This range is not a confidence interval.

Higher sensitivity trades off against false positives. The 0.80 training target is not guaranteed on held-out data. No clinical threshold, cost saving, fairness or patient-outcome conclusion follows.

Internal report. Stanford Alzheimer's Disease Research Center, NIH/NIA grant P30 AG066515. Comply with accepted publication-review terms before external disclosure.
