"""Unit tests for end-of-life labelling and feature extraction."""

import numpy as np
import pandas as pd
import pytest

from znlife.features import (
    TIME_FEATURES,
    capacity_above_voltage,
    dq_profile,
    time_domain_features,
)
from znlife.io import CYCLE, Q_CHARGE, Q_DISCHARGE
from znlife.screening import end_of_life, peak_capacity


def synthetic_cell(eol: int = 150) -> pd.DataFrame:
    cycles = np.arange(10, 401)
    capacity = np.where(cycles < eol, 1.0, 0.79 + 0.0001 * (cycles - eol))
    return pd.DataFrame({CYCLE: cycles, Q_CHARGE: capacity, Q_DISCHARGE: capacity})


def test_end_of_life_is_first_crossing():
    df = synthetic_cell(eol=150)
    assert peak_capacity(df) == 1.0
    assert end_of_life(df) == 150


def test_censored_cell_returns_nan():
    df = synthetic_cell(eol=500)
    assert np.isnan(end_of_life(df))


def test_six_time_features_are_finite():
    features = time_domain_features(synthetic_cell())
    assert list(features) == TIME_FEATURES
    assert all(np.isfinite(list(features.values())))


def test_capacity_above_voltage_matches_linear_ramp():
    # Voltage falls linearly from 1.8 to 0.8 V in one hour at 1 mA.
    time_s = np.linspace(0, 3600, 1001)
    voltage = 1.8 - time_s / 3600.0
    current = np.full_like(time_s, 1.0)
    q = capacity_above_voltage(time_s, voltage, current, grid=np.array([0.85, 1.00, 1.50]))
    # Q(V) = I * t(V) / 3600 = 1.8 - V  (mAh)
    assert q[0] == pytest.approx(0.95, abs=2e-3)
    assert q[1] == pytest.approx(0.80, abs=2e-3)
    assert q[2] == pytest.approx(0.30, abs=2e-3)


def test_dq_profile_is_a_difference():
    early = np.array([1.0, 1.0, 1.0])
    origin = np.array([0.8, 0.9, 1.1])
    assert np.allclose(dq_profile(origin, early), [-0.2, -0.1, 0.1])
