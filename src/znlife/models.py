"""Leave-one-cell-out fitting and error metrics."""

from __future__ import annotations

import numpy as np
from scipy import stats
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler

ALPHAS = np.logspace(-3, 3, 61)


def loocv_ridge(
    X: np.ndarray,
    y: np.ndarray,
    alphas: np.ndarray = ALPHAS,
    log_target: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Leave-one-cell-out ridge regression with in-fold scaling.

    The penalty is chosen by generalised cross-validation (the efficient
    leave-one-out criterion used by :class:`sklearn.linear_model.RidgeCV`)
    inside each training fold.  No information from the held-out cell enters
    the scaling or the penalty.

    Returns
    -------
    predictions, penalties
    """
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    n = len(y)
    predictions = np.empty(n, float)
    penalties = np.empty(n, float)

    target = np.log(y) if log_target else y
    for i in range(n):
        train = np.arange(n) != i
        scaler = StandardScaler().fit(X[train])
        model = RidgeCV(alphas=alphas).fit(scaler.transform(X[train]), target[train])
        predicted = model.predict(scaler.transform(X[[i]]))[0]
        predictions[i] = np.exp(predicted) if log_target else predicted
        penalties[i] = model.alpha_
    return predictions, penalties


def metrics(y: np.ndarray, prediction: np.ndarray) -> dict[str, float]:
    """MAE, RMSE, R2, bias and MAPE in the units of *y* (cycles)."""
    y = np.asarray(y, float)
    prediction = np.asarray(prediction, float)
    residual = prediction - y
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return {
        "n": int(len(y)),
        "mae": float(np.mean(np.abs(residual))),
        "rmse": float(np.sqrt(np.mean(residual**2))),
        "r2": float(1.0 - ss_res / ss_tot),
        "bias": float(np.mean(residual)),
        "mape": float(np.mean(np.abs(residual) / y) * 100.0),
    }


def bootstrap_mae_ci(
    y: np.ndarray, prediction: np.ndarray, n_boot: int = 5000, seed: int = 42
) -> tuple[float, float]:
    """Percentile bootstrap confidence interval of the mean absolute error."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y, float)
    prediction = np.asarray(prediction, float)
    n = len(y)
    values = np.empty(n_boot, float)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        values[b] = np.mean(np.abs(prediction[idx] - y[idx]))
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def paired_wilcoxon(error_a: np.ndarray, error_b: np.ndarray) -> tuple[float, float]:
    """Two-sided Wilcoxon signed-rank test on paired per-cell absolute errors."""
    result = stats.wilcoxon(np.asarray(error_a), np.asarray(error_b))
    return float(result.statistic), float(result.pvalue)
