"""Build data/metadata.csv and results/table1_cohort.csv from data/cohort."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from znlife.io import load_cohort
from znlife.screening import cohort_statistics, summarise


def main() -> None:
    cells = load_cohort(ROOT / "data" / "cohort")
    meta = summarise(cells, temperature_c=25.0)

    meta.to_csv(ROOT / "data" / "metadata.csv", index=False)
    table1 = cohort_statistics(meta)
    table1.to_csv(ROOT / "results" / "table1_cohort.csv", index=False)

    print(f"cells: {len(meta)}")
    print(f"labelled: {len(meta) - int(meta.right_censored.sum())}")
    print(table1.to_string(index=False))


if __name__ == "__main__":
    main()
