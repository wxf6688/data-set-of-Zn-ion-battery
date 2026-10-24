"""Figure helpers.

Only figures that depend on the per-cycle data are implemented here:

* ``fig2a``  discharge-capacity trajectories of the 33 cells
* ``fig2b``  distribution of end-of-life cycles
* ``fig4a``  predicted against measured end of life (leave-one-cell-out)
* ``fig6a``  empirical against nominal coverage

Figures that need the per-second exports (Fig. 3, Fig. 7) or the nine-feature
model (Fig. 5, Fig. 8, Fig. 10, Fig. 11) are not reproduced by this release.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .io import CYCLE, Q_DISCHARGE

BLUE = "#1f6fb4"
ORANGE = "#e07b39"
GREY = "#9aa5b1"

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 300,
        "savefig.bbox": "tight",
    }
)


def fig2a(cells, path: Path, highlight=(1, 10, 30)) -> None:
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    for cid, df in sorted(cells.items()):
        ax.plot(df[CYCLE], df[Q_DISCHARGE], color=GREY, lw=0.5, alpha=0.7)
    for cid, colour in zip(highlight, (BLUE, ORANGE, "#2a9d8f")):
        df = cells[cid]
        ax.plot(df[CYCLE], df[Q_DISCHARGE], color=colour, lw=1.3, label=f"cell {cid}")
    ax.set_xlabel("Cycle")
    ax.set_ylabel("Discharge capacity (mAh)")
    ax.legend(frameon=False, fontsize=7)
    fig.savefig(path)
    plt.close(fig)


def fig2b(meta: pd.DataFrame, path: Path) -> None:
    eol = meta.dropna(subset=["eol_cycle"])["eol_cycle"]
    fig, ax = plt.subplots(figsize=(2.6, 2.4))
    ax.hist(eol, bins=np.arange(100, 401, 25), color=BLUE, edgecolor="white")
    ax.set_xlabel("End of life (cycles)")
    ax.set_ylabel("Cells")
    fig.savefig(path)
    plt.close(fig)


def fig4a(measured: np.ndarray, predicted: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(2.8, 2.8))
    ax.scatter(measured, predicted, s=16, color=BLUE, edgecolor="white", linewidth=0.4)
    lims = [90, 400]
    ax.plot(lims, lims, "--", color=GREY, lw=0.8)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Measured end of life (cycles)")
    ax.set_ylabel("Predicted end of life (cycles)")
    fig.savefig(path)
    plt.close(fig)


def fig6a(nominal: list[float], empirical: list[float], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(2.6, 2.6))
    ax.plot([0.75, 1.0], [0.75, 1.0], "--", color=GREY, lw=0.8)
    ax.plot(nominal, empirical, "o-", color=BLUE, ms=4, lw=1.0)
    for x, y in zip(nominal, empirical):
        ax.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(4, -8), fontsize=7)
    ax.set_xlabel("Nominal coverage")
    ax.set_ylabel("Empirical coverage")
    fig.savefig(path)
    plt.close(fig)
