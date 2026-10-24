# Cycle-life dataset and analysis code for aqueous Zn/MnO₂ coin cells

[![data](https://img.shields.io/badge/data-33%20cells-1f6fb4)](#dataset)
[![python](https://img.shields.io/badge/python-3.10%2B-2a6f97)](#quick-start)
[![tests](https://img.shields.io/badge/tests-13%20passed-2a9d8f)](#tests)

This repository accompanies the manuscript

> **Cycle-life prediction for aqueous zinc-ion batteries from the first 90 cycles:
> voltage-resolved features, calibrated intervals and a bounded validity envelope**
> X. Wang, A. Moses, Q. Huang, B. Wang, L. Liu, J. Li, Y. Huang, D. Chen
> *Next Chemical Engineering* (submitted, 2026)

It contains the per-cycle cycling data of the 33-cell cohort, the code that
builds the labels and the features, the leave-one-cell-out evaluation, the
conformal calibration, and the scripts that regenerate the figures depending
only on these data.

---

## Dataset

| item | value |
|---|---|
| Cells | 33 Zn/MnO₂ CR2032 coin cells from one fabrication campaign |
| Temperature | 25 ± 2 °C (constant-temperature chamber) |
| Voltage window | 0.8–1.8 V |
| Applied current | 2.3–4.2 mA across tester channels (≈5–9 C) |
| Cycling | 391 cycles per cell, cycles 10–400 |
| Labels | 32 end-of-life events; cell 19 right-censored (81.4% retained at cycle 400) |
| End of life | first cycle with discharge capacity ≤ 80% of the peak of cycles 10–14 |

Each workbook (`data/cohort/<cell>.xlsx`) has one sheet with the columns
`循环次数` (cycle), `充电容量/mAh` (charge capacity) and `放电容量/mAh`
(discharge capacity). `data/metadata.csv` adds the derived quantities used in
Table 1 of the paper.

### Data dictionary — `data/metadata.csv`

| column | meaning |
|---|---|
| `cell_id` | cell identifier, 1–33 (matches the file name) |
| `file` | workbook name in `data/cohort` |
| `n_cycles` | number of recorded cycles (391 for every cell) |
| `first_cycle`, `last_cycle` | 10 and 400 for every cell |
| `q_peak_mAh` | largest discharge capacity among the first five recorded cycles |
| `eol_cycle` | first cycle with `Q_d ≤ 0.8 · Q_peak`; empty when right-censored |
| `right_censored` | `True` for cells without an end-of-life event by cycle 400 |
| `retention_400_pct` | discharge capacity at cycle 400 as a percentage of `q_peak_mAh` |
| `temperature_C` | 25 for every cell |

> **Note on the previous release.** The repository previously organised the same
> 33 workbooks into `训练集` / `验证集` / `测试集` (25 / 4 / 4). That split is not
> used in the paper, which validates by leaving one cell out; the files have been
> moved to `data/cohort/` and the old folders removed so that no file appears in
> a train/test partition.

---

## Repository layout

```
data/
  cohort/           33 per-cycle workbooks (391 rows each)
  metadata.csv      labels and cohort descriptors
  per_second/       expected layout of the per-second exports (files not included)
src/znlife/
  io.py             workbook readers
  screening.py      Q_peak, N_EOL, retention, Table 1
  features.py       six time-domain features; dQ(V) implementation
  models.py         leave-one-cell-out ridge, metrics, bootstrap, Wilcoxon
  conformal.py      CV+ intervals and coverage
  figures.py        Fig. 2a/2b, 4a, 6a
scripts/
  01_build_metadata.py
  02_extract_features.py
  03_fit_models.py
  04_make_figures.py
tests/              13 unit and dataset tests
results/            generated tables and figures
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/01_build_metadata.py     # data/metadata.csv, results/table1_cohort.csv
python scripts/02_extract_features.py   # results/features_time_domain.csv
python scripts/03_fit_models.py         # predictions, metrics, conformal coverage
python scripts/04_make_figures.py       # results/figures/*.png
python -m pytest -q tests               # 13 tests
```

---

## What this repository reproduces

Running the four scripts regenerates the following values. "Published" refers to
the tables of the manuscript.

| Quantity | Published | This repository |
|---|---|---|
| Cells / labelled cells | 33 / 32 | 33 / 32 |
| Peak capacity | 0.433 ± 0.031 mAh (0.367–0.503) | 0.433 ± 0.031 mAh (0.367–0.503) |
| Retention at cycle 400 | 54.1 ± 11.2% | 54.1 ± 11.2% |
| End of life (n = 32) | 182 ± 63 (median 176; 109–386) | 182 ± 63 (median 176; 109–386) |
| Six-feature ridge, MAE | 26.28 cycles | 26.28 cycles |
| Six-feature ridge, RMSE | 45.48 cycles | 45.39 cycles |
| Six-feature ridge, R² | 0.48 | 0.48 |
| Six-feature ridge, bias | −0.9 cycles | −0.85 cycles |
| Six-feature ridge, MAPE | 11.9% | 11.9% |
| Conformal coverage, 80/90% | 81.2 / 90.6% | 81.2 / 90.6% |

The RMSE differs by 0.09 cycles (0.2%); the remaining quantities agree to the
precision reported in the paper.

Three figures are regenerated from these data: Fig. 2a (capacity trajectories),
Fig. 2b (end-of-life distribution) and Fig. 4a (leave-one-cell-out parity), plus
a coverage plot corresponding to Fig. 6a.

## What is **not** included

The three voltage-resolved features ΔQ(V) are computed from the **per-second
tester exports** (voltage, current and time for every cycle), which are not part
of this repository because of their size. They are available from the
corresponding author on reasonable request; `data/per_second/README.md`
documents the expected file layout and the column names.

Consequently the following cannot be rebuilt from this repository alone:

* the three ΔQ(V) features and the nine-feature model (MAE 22.4 cycles);
* the serial LSTM → XGBoost model and its life-prediction results (MAE 25.8 cycles);
* the ablation and permutation-importance figures that involve ΔQ(V)
  (Fig. 3, Fig. 7);
* the transfer test to BatteryLife_Raw (Table 5, Fig. 11), which uses a
  third-party dataset (Zenodo
  [10.5281/zenodo.15013636](https://doi.org/10.5281/zenodo.15013636)).

`src/znlife/features.py` implements the ΔQ(V) extraction
(`capacity_above_voltage`, `dq_profile`, `voltage_resolved_from_exports`), so the
nine-feature model can be rebuilt once those exports are placed in
`data/per_second/`.

## Methods implemented here

* **Labels.** `Q_peak` is the largest discharge capacity among the first five
  recorded cycles; `N_EOL` is the first cycle at which the discharge capacity
  falls to 80% of `Q_peak`; cells that do not cross by cycle 400 are censored.
* **Features.** At the cycle-90 origin: state of health, linear fade slope
  (cycles 20–90), quadratic curvature (cycles 10–90), peak capacity, standard
  deviation of cycle-to-cycle capacity differences, and the initial capacity
  drop. No cycle index enters the feature vector.
* **Model.** Ridge regression on log `N_EOL`, with the penalty selected by
  generalised cross-validation inside each training fold and all features
  standardised on training cells only.
* **Validation.** Leave-one-cell-out over the 32 labelled cells; every reported
  metric is computed on out-of-fold predictions.
* **Intervals.** Split conformal (CV+) with the finite-sample correction
  `(1 − α)(1 + 1/(n − 1))`, calibrated on the residuals of the other cells.

## Tests

```bash
python -m pytest -q tests
```

The suite checks the file count (33), the cycle coverage (391 rows, cycles
10–400), the Table 1 values, the end-of-life definition on synthetic
trajectories, the trapezoidal integration used for Q(V), the leave-one-cell-out
fit, the metrics, and the conformal coverage.

## Citation

If you use these data or this code, please cite the article above and this
repository:

```
Wang, X. et al. Cycle-life dataset and analysis code for aqueous Zn/MnO2 coin
cells. GitHub (2026). https://github.com/wxf6688/data-set-of-Zn-ion-battery
```

`CITATION.cff` is provided for reference managers.

## Use of the data

The data are provided for research use with attribution: please cite the article
above. For other uses, contact the corresponding author.

## Contact

Ding Chen (corresponding author) — chending@hnu.edu.cn
College of Mechanical and Vehicle Engineering, Hunan University, Changsha, China.
