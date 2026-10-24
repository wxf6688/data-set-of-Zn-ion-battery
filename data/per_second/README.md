# Per-second exports (not included in this release)

The voltage-resolved features dQ(V) are computed from the per-second records of
the tester: one file per cell and per cycle, with the discharge branch sampled
at 1 s intervals.

These exports are **not** part of this repository. They are available from the
corresponding author (Ding Chen, chending@hnu.edu.cn) on reasonable request.

## Expected layout

```
data/per_second/
    cell01_cycle010.csv
    cell01_cycle090.csv
    ...
```

Each file must contain a header row with the following columns (other columns
are ignored):

| column     | unit | meaning                       |
|------------|------|-------------------------------|
| `time_s`   | s    | elapsed time                  |
| `voltage_V`| V    | cell voltage                  |
| `current_mA`| mA  | applied current (sign ignored)|

With those files in place, the three dQ(V) features are computed by

```python
from znlife.features import voltage_resolved_from_exports

features = voltage_resolved_from_exports(
    "data/per_second/cell01_cycle090.csv",
    "data/per_second/cell01_cycle010.csv",
)
```

which returns the mean, standard deviation and minimum of dQ(V) on the
0.85–1.60 V grid used in the paper.
