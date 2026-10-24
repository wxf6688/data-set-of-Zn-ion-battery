"""Unit tests for the leave-one-cell-out fit, the metrics and the intervals."""

import numpy as np

from znlife.conformal import coverage_table, cv_plus_intervals
from znlife.models import loocv_ridge, metrics


def test_loocv_recovers_a_linear_relation():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, 3))
    y = 100 + 20 * X[:, 0] - 10 * X[:, 1] + rng.normal(scale=0.5, size=40)
    predictions, _ = loocv_ridge(X, y, log_target=False)
    assert np.mean(np.abs(predictions - y)) < 1.0


def test_metrics_are_consistent():
    y = np.array([100.0, 200.0, 300.0])
    prediction = np.array([110.0, 190.0, 330.0])
    scores = metrics(y, prediction)
    assert scores["mae"] == 50.0 / 3.0
    assert scores["bias"] == 10.0
    assert scores["rmse"] > scores["mae"]


def test_conformal_coverage_is_near_nominal():
    rng = np.random.default_rng(1)
    residuals = rng.normal(scale=10.0, size=400)
    rows = {row["nominal"]: row["coverage_pct"] for row in coverage_table(residuals)}
    assert 75 <= rows["80%"] <= 85
    assert 86 <= rows["90%"] <= 94
    assert 92 <= rows["95%"] <= 98


def test_cv_plus_interval_is_wider_at_higher_coverage():
    residuals = np.array([-5.0, -2.0, 0.5, 1.5, 3.0, 8.0])
    q80, _ = cv_plus_intervals(residuals, 0.20)
    q95, _ = cv_plus_intervals(residuals, 0.05)
    assert q95.mean() > q80.mean()
