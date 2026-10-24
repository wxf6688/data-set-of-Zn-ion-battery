"""Checks on the released cohort: file count, cycle coverage and Table 1 values."""

from pathlib import Path

import numpy as np
import pandas as pd

from znlife.io import CYCLE, load_cohort
from znlife.screening import cohort_statistics, summarise

ROOT = Path(__file__).resolve().parents[1]


def test_thirty_three_cells():
    cells = load_cohort(ROOT / "data" / "cohort")
    assert len(cells) == 33
    assert sorted(cells) == list(range(1, 34))


def test_each_cell_covers_cycles_10_to_400():
    cells = load_cohort(ROOT / "data" / "cohort")
    for cid, df in cells.items():
        assert len(df) == 391, cid
        assert df[CYCLE].min() == 10, cid
        assert df[CYCLE].max() == 400, cid
        assert df[CYCLE].is_monotonic_increasing, cid


def test_labels_match_table_1():
    cells = load_cohort(ROOT / "data" / "cohort")
    meta = summarise(cells)
    labelled = meta.dropna(subset=["eol_cycle"])

    assert len(labelled) == 32
    assert meta.loc[meta.right_censored, "cell_id"].tolist() == [19]
    assert labelled.eol_cycle.min() == 109
    assert labelled.eol_cycle.max() == 386
    assert round(labelled.eol_cycle.median()) == 176
    assert round(labelled.eol_cycle.mean()) == 182
    assert round(meta.q_peak_mAh.mean(), 3) == 0.433
    assert round(meta.q_peak_mAh.std(ddof=0), 3) == 0.031


def test_table_1_renders():
    cells = load_cohort(ROOT / "data" / "cohort")
    table = cohort_statistics(summarise(cells))
    text = table.to_string()
    assert "109-386" in text
    assert "0.433" in text
