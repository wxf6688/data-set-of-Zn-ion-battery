"""Regenerate the figures that depend only on the per-cycle data."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from znlife.conformal import LEVELS, coverage_table
from znlife.figures import fig2a, fig2b, fig4a, fig6a
from znlife.io import load_cohort


def main() -> None:
    out = ROOT / "results" / "figures"
    out.mkdir(parents=True, exist_ok=True)

    cells = load_cohort(ROOT / "data" / "cohort")
    meta = pd.read_csv(ROOT / "data" / "metadata.csv")
    predictions = pd.read_csv(ROOT / "results" / "predictions.csv")
    coverage = pd.read_csv(ROOT / "results" / "conformal_coverage.csv")

    fig2a(cells, out / "fig2a_trajectories.png")
    fig2b(meta, out / "fig2b_eol_distribution.png")
    fig4a(
        predictions["eol_cycle"].to_numpy(),
        predictions["predicted_eol"].to_numpy(),
        out / "fig4a_parity.png",
    )

    nominal = [1.0 - alpha for alpha in LEVELS.values()]
    fig6a(nominal, coverage["coverage_pct"].to_numpy() / 100.0, out / "fig6a_coverage.png")
    print("wrote", *sorted(p.name for p in out.glob("*.png")), sep="\n  ")


if __name__ == "__main__":
    main()
