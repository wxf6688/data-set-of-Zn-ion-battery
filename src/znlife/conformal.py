"""Split-conformal (CV+) intervals from leave-one-out residuals.

For a nominal level ``1 - alpha`` the interval around prediction i is
``y_i +/- q_i``, where ``q_i`` is the empirical quantile of the absolute
residuals of the *other* cells at level ``(1 - alpha) * (1 + 1/(n-1))``.
The residuals come from models that never saw cell i, which is the
cross-conformal construction used in Section 3.4 of the paper.
"""

from __future__ import annotations

import numpy as np

LEVELS = {"80%": 0.20, "90%": 0.10, "95%": 0.05}


def cv_plus_intervals(residuals: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    """Half-widths and coverage flags for every cell at level ``1 - alpha``."""
    residuals = np.asarray(residuals, float)
    n = len(residuals)
    q = np.empty(n, float)
    covered = np.empty(n, bool)
    for i in range(n):
        others = np.abs(np.delete(residuals, i))
        level = min((1.0 - alpha) * (1.0 + 1.0 / (n - 1)), 1.0)
        q[i] = np.quantile(others, level)
        covered[i] = abs(residuals[i]) <= q[i]
    return q, covered


def coverage_table(residuals: np.ndarray) -> list[dict[str, float]]:
    """Empirical coverage and mean width at the 80, 90 and 95% levels."""
    rows = []
    for label, alpha in LEVELS.items():
        q, covered = cv_plus_intervals(residuals, alpha)
        rows.append(
            {
                "nominal": label,
                "coverage_pct": round(100.0 * covered.mean(), 1),
                "n_covered": int(covered.sum()),
                "mean_width_cycles": round(2.0 * q.mean(), 0),
            }
        )
    return rows
