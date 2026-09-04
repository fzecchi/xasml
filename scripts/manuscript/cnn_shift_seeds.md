# CNN energy-shift seed test

## Run configuration

| Item | Value |
|---|---|
| Run date | 2026-08-14 |
| Script | `scripts/manuscript/cnn_shift_seeds.py` |
| Backend | Keras 3.15.1 with PyTorch 2.13.0 |
| Data split seed | 42 |
| Training seeds | 42, 0, 1, 2, 3, 4, 5, 6, 7, 8, 81, 13 |
| Test set | 416 spectra |
| Energy shifts | −1.0, −0.5, 0.0, +0.5, +1.0 eV |

The train, validation, and test spectra are fixed across training seeds. The test metadata and order are identical across all five shift conditions. Each shift is applied on the full energy grid before trimming and area normalization. The model architecture, optimizer, class weights, and callbacks match `cnn_classifier.ipynb`.

## Baseline per-seed results

Each cell reports balanced accuracy / T:4 recall in percent.

| Seed | −1.0 eV | −0.5 eV | 0.0 eV | +0.5 eV | +1.0 eV |
|---:|---:|---:|---:|---:|---:|
| 42 | 76.0 / 54.1 | 89.8 / 82.0 | 94.1 / 91.0 | 92.6 / 89.3 | 86.5 / 77.0 |
| 0 | 71.5 / 46.7 | 86.8 / 77.0 | 94.0 / 91.0 | 91.2 / 86.1 | 85.4 / 74.6 |
| 1 | 81.5 / 66.4 | 90.8 / 85.2 | 92.6 / 91.0 | 90.2 / 85.2 | 86.5 / 77.0 |
| 2 | 93.5 / 91.0 | 94.6 / 92.6 | 93.6 / 91.0 | 90.9 / 85.2 | 86.4 / 76.2 |
| 3 | 74.6 / 51.6 | 89.5 / 82.0 | 94.1 / 91.0 | 92.5 / 89.3 | 84.0 / 72.1 |
| 4 | 50.0 / 0.0 | 50.0 / 0.0 | 50.0 / 0.0 | 50.0 / 0.0 | 50.0 / 0.0 |
| 5 | 72.3 / 48.4 | 88.3 / 80.3 | 93.9 / 91.8 | 89.8 / 84.4 | 83.8 / 71.3 |
| 6 | 73.3 / 50.0 | 87.9 / 79.5 | 94.0 / 91.8 | 91.8 / 87.7 | 82.6 / 68.9 |
| 7 | 68.5 / 41.0 | 87.1 / 78.7 | 93.4 / 92.6 | 91.1 / 87.7 | 85.3 / 74.6 |
| 8 | 65.9 / 34.4 | 82.4 / 68.9 | 93.7 / 91.8 | 90.7 / 86.9 | 85.2 / 75.4 |
| 81 | 71.6 / 47.5 | 89.4 / 83.6 | 93.7 / 91.8 | 91.6 / 87.7 | 87.5 / 79.5 |
| 13 | 81.8 / 66.4 | 90.1 / 83.6 | 93.4 / 90.2 | 89.3 / 82.0 | 82.5 / 68.0 |

## Baseline training failure

Seed 4 predicts only O:6 on the clean test set. An isolated rerun reproduces this collapse and stops after 57 epochs. It is a training failure rather than state leakage.

## Baseline summary across all 12 seeds

Values are mean ± population standard deviation. Combined statistics were calculated from the one-decimal per-seed values above. Accuracy and recall are percentages. Losses are percentage points relative to the clean result from the same seed.

| Shift | Balanced accuracy | T:4 recall | Balanced loss | T:4 loss |
|---:|---:|---:|---:|---:|
| −1.0 eV | 73.38 ± 9.93 | 49.79 ± 20.58 | 16.67 ± 8.73 | 33.96 ± 17.70 |
| −0.5 eV | 85.56 ± 11.07 | 74.45 ± 23.07 | 4.48 ± 3.16 | 9.30 ± 6.25 |
| 0.0 eV | 90.04 ± 12.08 | 83.75 ± 25.26 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| +0.5 eV | 87.64 ± 11.39 | 79.29 ± 23.99 | 2.40 ± 1.07 | 4.46 ± 2.28 |
| +1.0 eV | 82.14 ± 9.81 | 67.88 ± 20.73 | 7.90 ± 2.90 | 15.87 ± 5.76 |

## Baseline summary across 11 non-collapsed models

Values are mean ± population standard deviation. Losses are paired to the clean result from the same training seed and are reported in percentage points.

| Shift | Balanced accuracy | T:4 recall | Balanced loss | T:4 loss |
|---:|---:|---:|---:|---:|
| −1.0 eV | 75.50 ± 7.31 | 54.32 ± 14.70 | 18.18 ± 7.46 | 37.05 ± 15.08 |
| −0.5 eV | 88.79 ± 2.86 | 81.22 ± 5.54 | 4.89 ± 2.98 | 10.15 ± 5.83 |
| 0.0 eV | 93.68 ± 0.42 | 91.36 ± 0.63 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| +0.5 eV | 91.06 ± 0.99 | 86.50 ± 2.10 | 2.62 ± 0.82 | 4.86 ± 1.92 |
| +1.0 eV | 85.06 ± 1.58 | 74.05 ± 3.42 | 8.62 ± 1.73 | 17.31 ± 3.35 |

## Baseline interpretation

The −1.0 eV shift produces lower balanced accuracy and lower T:4 recall than the +1.0 eV shift in 10 of the 11 non-collapsed models. Seed 2 is the exception. The seed-42 T:4 recall at −1.0 eV is 54.1%, close to the non-collapsed mean of 54.3%, but the 14.7-point standard deviation shows substantial initialization dependence.

## Shift-augmented CNN

The augmented models use the corrected full-grid augmentation pipeline from `cnn_classifier_augmented.ipynb`. The augmented training set is fixed with random seed 42, and the augmented validation set is fixed with random seed 43. Only model initialization and batch order vary. The training and validation shapes are 3,235 × 701 and 693 × 701, respectively.

The results were generated with `scripts/manuscript/cnn_shift_augmented_seeds.py`. Eleven augmented seeds completed. Seed 13 was interrupted during training and is not included below.

### Corrected seed-42 checkpoint

These values replace the stale augmented seed-42 values in the manuscript.

| Shift | Balanced accuracy | O:6 recall | T:4 recall |
|---:|---:|---:|---:|
| −1.0 eV | 92.5 | 94.9 | 90.2 |
| −0.5 eV | 93.5 | 95.9 | 91.0 |
| 0.0 eV | 92.9 | 94.9 | 91.0 |
| +0.5 eV | 94.4 | 96.3 | 92.6 |
| +1.0 eV | 94.1 | 95.6 | 92.6 |

### Per-seed augmented results

Each shift cell reports balanced accuracy / T:4 recall in percent.

| Seed | Epochs | −1.0 eV | −0.5 eV | 0.0 eV | +0.5 eV | +1.0 eV |
|---:|---:|---:|---:|---:|---:|---:|
| 42 | 134 | 92.5 / 90.2 | 93.5 / 91.0 | 92.9 / 91.0 | 94.4 / 92.6 | 94.1 / 92.6 |
| 0 | 139 | 93.7 / 91.8 | 93.5 / 91.0 | 94.0 / 91.8 | 94.3 / 92.6 | 93.6 / 91.0 |
| 1 | 144 | 92.2 / 90.2 | 92.4 / 90.2 | 92.6 / 91.0 | 93.5 / 91.8 | 93.5 / 91.8 |
| 2 | 314 | 92.5 / 90.2 | 93.5 / 91.8 | 93.9 / 92.6 | 93.5 / 91.8 | 93.5 / 91.0 |
| 3 | 162 | 93.7 / 93.4 | 93.8 / 92.6 | 94.1 / 92.6 | 94.1 / 92.6 | 93.6 / 92.6 |
| 4 | 163 | 93.3 / 92.6 | 93.7 / 93.4 | 94.0 / 93.4 | 94.3 / 93.4 | 94.2 / 93.4 |
| 5 | 145 | 93.1 / 91.0 | 93.5 / 91.8 | 93.9 / 92.6 | 94.3 / 93.4 | 92.7 / 90.2 |
| 6 | 108 | 93.3 / 92.6 | 93.3 / 93.4 | 93.5 / 93.4 | 94.6 / 94.3 | 92.5 / 90.2 |
| 7 | 142 | 93.3 / 91.0 | 92.5 / 90.2 | 93.3 / 91.0 | 94.0 / 91.8 | 93.2 / 90.2 |
| 8 | 142 | 93.3 / 91.0 | 93.5 / 91.0 | 94.6 / 92.6 | 94.9 / 93.4 | 94.3 / 92.6 |
| 81 | 146 | 92.8 / 91.0 | 93.3 / 91.0 | 94.1 / 92.6 | 94.4 / 92.6 | 92.6 / 89.3 |

### Summary across 11 augmented models

Values are mean ± population standard deviation. Accuracy and recall are percentages. Losses are paired to the clean result from the same seed and are reported in percentage points.

| Shift | Balanced accuracy | T:4 recall | Balanced loss | T:4 loss |
|---:|---:|---:|---:|---:|
| −1.0 eV | 93.06 ± 0.48 | 91.36 ± 1.04 | 0.65 ± 0.46 | 0.87 ± 0.87 |
| −0.5 eV | 93.32 ± 0.43 | 91.58 ± 1.08 | 0.40 ± 0.42 | 0.65 ± 0.57 |
| 0.0 eV | 93.72 ± 0.56 | 92.24 ± 0.86 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| +0.5 eV | 94.21 ± 0.40 | 92.75 ± 0.77 | −0.49 ± 0.50 | −0.52 ± 0.62 |
| +1.0 eV | 93.44 ± 0.60 | 91.35 ± 1.26 | 0.28 ± 0.78 | 0.88 ± 1.52 |

For the ten completed seeds with a non-collapsed baseline model, augmentation improves balanced accuracy at −1.0 eV by 18.17 ± 7.69 percentage points. The mean clean-accuracy change is −0.02 ± 0.52 points. Nine of the ten models improve at −1.0 eV; seed 2 decreases by 1.0 point because its baseline model is already shift-tolerant. Augmentation also prevents the one-class collapse for seed 4, which reaches 94.0% clean balanced accuracy and 93.3% at −1.0 eV.
