"""Readers for the per-cycle workbooks of the 33-cell Zn/MnO2 cohort.

Each workbook contains one sheet with four columns:
    循环次数        cycle index (10-400)
    充电容量/mAh    charge capacity per cycle (mAh)
    放电容量/mAh    discharge capacity per cycle (mAh)

Only the discharge capacity is used for end-of-life labelling; the charge
capacity is used by the sequence stage of the model.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CYCLE = "cycle"
Q_CHARGE = "q_charge_mAh"
Q_DISCHARGE = "q_discharge_mAh"

#: Chinese headers used in the released workbooks -> canonical column names.
HEADER_MAP = {
    "循环次数": CYCLE,
    "充电容量/mAh": Q_CHARGE,
    "放电容量/mAh": Q_DISCHARGE,
}

COLUMNS = [CYCLE, Q_CHARGE, Q_DISCHARGE]


def read_workbook(path: str | Path) -> pd.DataFrame:
    """Read one workbook and return a tidy frame with the three canonical columns."""
    path = Path(path)
    df = pd.read_excel(path, sheet_name=0, engine="openpyxl")
    df = df.rename(columns=HEADER_MAP)
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name}: missing columns {missing}")
    df = df[COLUMNS].dropna(subset=[CYCLE]).astype(float)
    df = df.sort_values(CYCLE).reset_index(drop=True)
    return df


def cell_id(path: str | Path) -> int:
    """Cell identifier encoded in the file name (1.xlsx -> 1)."""
    return int(Path(path).stem)


def load_cohort(directory: str | Path = "data/cohort") -> dict[int, pd.DataFrame]:
    """Load every workbook in *directory*, keyed by cell identifier."""
    directory = Path(directory)
    files = sorted(directory.glob("*.xlsx"), key=cell_id)
    if not files:
        raise FileNotFoundError(f"no .xlsx files in {directory.resolve()}")
    return {cell_id(f): read_workbook(f) for f in files}


def cycle_at(df: pd.DataFrame, cycle: float, column: str = Q_DISCHARGE) -> float:
    """Capacity at *cycle*, linearly interpolated if the exact cycle is absent."""
    return float(np.interp(cycle, df[CYCLE].to_numpy(), df[column].to_numpy()))
