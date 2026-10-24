"""Fit the six-feature ridge model under leave-one-cell-out validation.

Writes:
    results/predictions.csv          one row per labelled cell
    results/model_six_feature.csv    MAE, RMSE, R2, bias, MAPE, bootstrap CI
    results/conformal_coverage.csv   coverage at 80, 90 and 95% nominal
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from znlife.conformal import coverage_table
from znlife.features import TIME_FEATURES, feature_table
from znlife.io import load_cohort
from znlife.models import bootstrap_mae_ci, loocv_ridge, metrics


def main() -> None:
    cells = load_cohort(ROOT / "data" / "cohort")
    features = feature_table(cells, origin=90)
    meta = pd.read_csv(ROOT / "data" / "metadata.csv")

    data = features.merge(meta[["cell_id", "eol_cycle", "right_censored"]], on="cell_id")
    data = data.dropna(subset=["eol_cycle"]).reset_index(drop=True)

    X = data[TIME_FEATURES].to_numpy(float)
    y = data["eol_cycle"].to_numpy(float)
    predictions, penalties = loocv_ridge(X, y)

    scores = metrics(y, predictions)
    low, high = bootstrap_mae_ci(y, predictions)
    scores["mae_ci_low"] = round(low, 2)
    scores["mae_ci_high"] = round(high, 2)

    out = data[["cell_id", "eol_cycle"]].copy()
    out["predicted_eol"] = np.round(predictions, 2)
    out["residual"] = np.round(predictions - y, 2)
    out["alpha"] = np.round(penalties, 4)
    out.to_csv(ROOT / "results" / "predictions.csv", index=False)

    pd.DataFrame([scores]).to_csv(ROOT / "results" / "model_six_feature.csv", index=False)
    coverage = pd.DataFrame(coverage_table(predictions - y))
    coverage.to_csv(ROOT / "results" / "conformal_coverage.csv", index=False)

    print(pd.DataFrame([scores]).to_string(index=False))
    print()
    print(coverage.to_string(index=False))


if __name__ == "__main__":
    main()
