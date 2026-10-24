"""End-of-life labelling and cohort statistics.

The definitions follow Section 3.1 of the paper:
    Q_peak   = largest discharge capacity among the first five recorded cycles
    SOH(t)   = Q_d(t) / Q_peak
    N_EOL    = first cycle at which SOH <= 0.80
Cells that do not cross the threshold by cycle 400 are right-censored and carry
no label.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .io import CYCLE, Q_DISCHARGE, cycle_at

EOL_FRACTION = 0.80
CYCLE_LIMIT = 400
PEAK_WINDOW = 5


def peak_capacity(df: pd.DataFrame, window: int = PEAK_WINDOW) -> float:
    """Largest discharge capacity among the first *window* recorded cycles."""
    return float(df[Q_DISCHARGE].iloc[:window].max())


def end_of_life(
    df: pd.DataFrame,
    q_peak: float | None = None,
    fraction: float = EOL_FRACTION,
    limit: float = CYCLE_LIMIT,
) -> float:
    """Cycle at which the discharge capacity first reaches *fraction* of Q_peak.

    Returns ``nan`` when the cell does not cross the threshold within *limit*
    cycles (right-censored).
    """
    q_peak = peak_capacity(df) if q_peak is None else q_peak
    below = df[df[Q_DISCHARGE] <= fraction * q_peak]
    if below.empty:
        return float("nan")
    cycle = float(below[CYCLE].iloc[0])
    return cycle if cycle <= limit else float("nan")


def retention(df: pd.DataFrame, q_peak: float | None = None, at: float = CYCLE_LIMIT) -> float:
    """Capacity retention at *at* cycles, as a percentage of Q_peak."""
    q_peak = peak_capacity(df) if q_peak is None else q_peak
    return 100.0 * cycle_at(df, at) / q_peak


def summarise(cells: dict[int, pd.DataFrame], temperature_c: float = 25.0) -> pd.DataFrame:
    """One row per cell with the quantities reported in Table 1."""
    rows = []
    for cid, df in sorted(cells.items()):
        q_peak = peak_capacity(df)
        eol = end_of_life(df, q_peak)
        rows.append(
            {
                "cell_id": cid,
                "file": f"{cid}.xlsx",
                "n_cycles": len(df),
                "first_cycle": int(df[CYCLE].min()),
                "last_cycle": int(df[CYCLE].max()),
                "q_peak_mAh": round(q_peak, 4),
                "eol_cycle": eol,
                "right_censored": bool(np.isnan(eol)),
                "retention_400_pct": round(retention(df, q_peak), 2),
                "temperature_C": temperature_c,
            }
        )
    return pd.DataFrame(rows)


def cohort_statistics(meta: pd.DataFrame) -> pd.DataFrame:
    """Table 1 of the paper, computed from the metadata frame."""
    labelled = meta.dropna(subset=["eol_cycle"])
    eol = labelled["eol_cycle"].to_numpy()
    return pd.DataFrame(
        [
            ("Cells analysed", f"{len(meta)} (one fabrication campaign)"),
            (
                "Peak discharge capacity",
                f"{meta.q_peak_mAh.mean():.3f} ± {meta.q_peak_mAh.std(ddof=0):.3f} mAh "
                f"({meta.q_peak_mAh.min():.3f}-{meta.q_peak_mAh.max():.3f})",
            ),
            (
                "Capacity retention at cycle 400",
                f"{meta.retention_400_pct.mean():.1f} ± {meta.retention_400_pct.std(ddof=0):.1f}%",
            ),
            (
                "End of life (n = %d)" % len(labelled),
                f"{eol.mean():.0f} ± {eol.std(ddof=0):.0f} cycles "
                f"(median {np.median(eol):.0f}; range {eol.min():.0f}-{eol.max():.0f})",
            ),
            (
                "Right-censored cells",
                f"{int(meta.right_censored.sum())} "
                f"({', '.join('cell %d' % c for c in meta.loc[meta.right_censored, 'cell_id'])})",
            ),
            ("Temperature", f"{meta.temperature_C.iloc[0]:.0f} ± 2 °C"),
            ("Prediction origin", "cycle 90 (all labelled cells still alive)"),
        ],
        columns=["Quantity", "Value"],
    )
