"""Extract the six time-domain features at the cycle-90 origin.

Writes results/features_time_domain.csv, one row per cell.

The three voltage-resolved features dQ(V) need the per-second exports, which
are not part of this release (see data/per_second/README.md).  When those files
are present, ``znlife.features.voltage_resolved_from_exports`` computes them.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from znlife.features import TIME_FEATURES, feature_table
from znlife.io import load_cohort


def main() -> None:
    cells = load_cohort(ROOT / "data" / "cohort")
    features = feature_table(cells, origin=90)
    features.to_csv(ROOT / "results" / "features_time_domain.csv", index=False)

    print(features[TIME_FEATURES].describe().T[["mean", "std", "min", "max"]].to_string())
    print(f"\nwrote {len(features)} rows")


if __name__ == "__main__":
    main()
