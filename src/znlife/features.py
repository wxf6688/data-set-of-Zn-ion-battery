"""Feature extraction at the prediction origin.

Two families are implemented:

* six time-domain summaries of the per-cycle capacity trajectory, computed from
  the workbooks in ``data/cohort`` (these are the features behind the row
  "Six time-domain features (no dQ(V))" of Table 3 and behind Table 5);
* three voltage-resolved summaries of dQ(V) = Q_c0(V) - Q_c10(V), computed from
  the per-second exports.  The per-second exports are not part of this data
  release; see ``data/per_second/README.md`` for the expected layout.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .io import CYCLE, Q_DISCHARGE, cycle_at
from .screening import peak_capacity

_trapezoid = getattr(np, "trapezoid", None) or np.trapz

ORIGIN = 90
DELTA_WINDOW = (10, 90)
VOLTAGE_GRID = np.arange(0.85, 1.601, 0.05)

TIME_FEATURES = [
    "soh_at_origin",
    "fade_slope",
    "curvature",
    "q_peak",
    "dq_step_std",
    "initial_drop",
]

DQ_FEATURES = ["dq_mean", "dq_std", "dq_min"]

ALL_FEATURES = TIME_FEATURES + DQ_FEATURES


def time_domain_features(df: pd.DataFrame, origin: int = ORIGIN) -> dict[str, float]:
    """The six features of Section 3.2, computed from one per-cycle workbook.

    Parameters
    ----------
    df
        Tidy frame returned by :func:`znlife.io.read_workbook`.
    origin
        Prediction origin in cycles; features use only cycles <= origin.
    """
    q_peak = peak_capacity(df)
    q = df[Q_DISCHARGE].to_numpy() / q_peak
    c = df[CYCLE].to_numpy()

    fit_window = (c >= 20) & (c <= origin)
    quad_window = (c >= 10) & (c <= origin)
    if fit_window.sum() < 2 or quad_window.sum() < 3:
        raise ValueError("not enough cycles before the origin to fit the trajectory")

    slope = np.polyfit(c[fit_window], q[fit_window], 1)[0]
    curvature = np.polyfit(c[quad_window], q[quad_window], 2)[0]

    return {
        "soh_at_origin": float(cycle_at(df, origin) / q_peak),
        "fade_slope": float(slope),
        "curvature": float(curvature),
        "q_peak": float(q_peak),
        "dq_step_std": float(np.std(np.diff(q[quad_window]))),
        "initial_drop": float(1.0 - cycle_at(df, 20) / q_peak),
    }


# --------------------------------------------------------------------------- dQ(V)
def capacity_above_voltage(
    time_s: np.ndarray,
    voltage_v: np.ndarray,
    current_ma: np.ndarray,
    grid: np.ndarray = VOLTAGE_GRID,
) -> np.ndarray:
    """Capacity delivered above each voltage of *grid* during one discharge.

    The discharge branch is taken as the contiguous part of the record that
    starts at the highest voltage and ends at the cut-off.  Current is
    integrated with the trapezoidal rule and converted from mA*s to mAh.

    Returns an array of len(grid) in mAh.
    """
    time_s = np.asarray(time_s, float)
    voltage_v = np.asarray(voltage_v, float)
    current_ma = np.asarray(current_ma, float)

    out = np.empty(len(grid), float)
    for k, threshold in enumerate(grid):
        mask = voltage_v >= threshold
        if mask.sum() < 2:
            out[k] = 0.0
            continue
        t = time_s[mask]
        i = np.abs(current_ma[mask])
        out[k] = _trapezoid(i, t) / 3600.0
    return out


def dq_profile(q_origin: np.ndarray, q_early: np.ndarray) -> np.ndarray:
    """dQ(V) = Q_c0(V) - Q_c10(V) on the voltage grid."""
    return np.asarray(q_origin, float) - np.asarray(q_early, float)


def voltage_resolved_features(
    q_origin: np.ndarray, q_early: np.ndarray
) -> dict[str, float]:
    """Mean, standard deviation and minimum of the dQ(V) profile."""
    dq = dq_profile(q_origin, q_early)
    return {
        "dq_mean": float(dq.mean()),
        "dq_std": float(dq.std()),
        "dq_min": float(dq.min()),
    }


def voltage_resolved_from_exports(
    path_origin: str, path_early: str, grid: np.ndarray = VOLTAGE_GRID
) -> dict[str, float]:
    """Compute the three dQ(V) features from two per-second export files.

    Expected columns (any order, header row required)::

        time_s, voltage_V, current_mA

    Only the discharge branch is used.  These files are distributed separately
    from the per-cycle release; see ``data/per_second/README.md``.
    """
    frames = []
    for path in (path_origin, path_early):
        frame = pd.read_csv(path) if str(path).endswith(".csv") else pd.read_excel(path)
        frame.columns = [c.strip() for c in frame.columns]
        frames.append(frame)
    q_origin = capacity_above_voltage(
        frames[0]["time_s"], frames[0]["voltage_V"], frames[0]["current_mA"], grid
    )
    q_early = capacity_above_voltage(
        frames[1]["time_s"], frames[1]["voltage_V"], frames[1]["current_mA"], grid
    )
    return voltage_resolved_features(q_origin, q_early)


def feature_table(cells: dict[int, pd.DataFrame], origin: int = ORIGIN) -> pd.DataFrame:
    """Six time-domain features for every cell, one row per cell."""
    rows = []
    for cid, df in sorted(cells.items()):
        feat = time_domain_features(df, origin=origin)
        feat["cell_id"] = cid
        rows.append(feat)
    return pd.DataFrame(rows)[["cell_id"] + TIME_FEATURES]
