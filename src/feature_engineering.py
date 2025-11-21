"""
Feature engineering functions for collision data analysis
"""

from typing import List

import numpy as np
import pandas as pd


def create_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-based features:
    - crash_year
    - crash_month
    - crash_day
    - crash_hour (if time is available)
    - crash_day_of_week
    - is_weekend
    """
    df = df.copy()

    # Prefer a datetime column if exists
    if "crash_datetime" in df.columns:
        dt = pd.to_datetime(df["crash_datetime"], errors="coerce")
    elif "crash_date" in df.columns:
        dt = pd.to_datetime(df["crash_date"], errors="coerce")
    else:
        return df  # nothing to do

    df["crash_year"] = dt.dt.year
    df["crash_month"] = dt.dt.month
    df["crash_day"] = dt.dt.day
    df["crash_day_of_week"] = dt.dt.dayofweek  # Monday=0
    df["is_weekend"] = df["crash_day_of_week"].isin([5, 6]).astype(int)

    # Crash hour: from crash_time or datetime
    if "crash_time" in df.columns and df["crash_time"].dtype == "object":
        # If crash_time is "HH:MM"
        t = pd.to_datetime(df["crash_time"], format="%H:%M", errors="coerce")
        df["crash_hour"] = t.dt.hour
    elif "crash_time" in df.columns and not np.issubdtype(df["crash_time"].dtype, np.number):
        # If it's datetime64[ns]
        df["crash_hour"] = pd.to_datetime(df["crash_time"], errors="coerce").dt.hour
    else:
        df["crash_hour"] = dt.dt.hour

    return df


def create_location_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create location-based features:
    - standardized borough
    - lat/lon bins for coarse spatial grouping
    """
    df = df.copy()

    # Borough normalization
    if "borough" in df.columns:
        df["borough"] = (
            df["borough"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    # Simple spatial bins if coordinates available
    if "latitude" in df.columns and "longitude" in df.columns:
        # Use coarse bins to avoid too many categories
        df["lat_bin"] = pd.cut(df["latitude"], bins=10, labels=False)
        df["lon_bin"] = pd.cut(df["longitude"], bins=10, labels=False)

    return df


def create_severity_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create severity-based features:
    - total_injured
    - total_killed
    - severity_score (e.g. injured + 3 * killed)
    """
    df = df.copy()

    # Use any columns that look like *injured or *killed
    injured_cols = [c for c in df.columns if "injured" in c]
    killed_cols = [c for c in df.columns if "killed" in c]

    for col in injured_cols + killed_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if injured_cols:
        df["total_injured"] = df[injured_cols].sum(axis=1)
    else:
        df["total_injured"] = 0

    if killed_cols:
        df["total_killed"] = df[killed_cols].sum(axis=1)
    else:
        df["total_killed"] = 0

    # Simple severity score: each death counts more
    df["severity_score"] = df["total_injured"] + 3 * df["total_killed"]

    return df


def create_vehicle_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create vehicle-related features:
    - num_vehicle_types (non-null vehicle_type* columns)
    - has_truck, has_bus, has_bicycle (simple flags if types present)
    """
    df = df.copy()

    vehicle_type_cols = [c for c in df.columns if "vehicle_type" in c]

    if not vehicle_type_cols:
        return df

    # Normalize vehicle type strings
    for col in vehicle_type_cols:
        df[col] = df[col].astype(str).str.upper().str.strip()

    # Number of non-null vehicle type entries per row
    df["num_vehicle_types"] = df[vehicle_type_cols].replace("NAN", np.nan).notna().sum(axis=1)

    # Flags
    pattern_truck = ("TRUCK", "TRACTOR", "PICK-UP")
    pattern_bus = ("BUS",)
    pattern_bike = ("BICYCLE", "BIKE")

    def contains_any(value: str, patterns) -> bool:
        v = str(value)
        return any(p in v for p in patterns)

    df["has_truck"] = df[vehicle_type_cols].apply(
        lambda row: any(contains_any(v, pattern_truck) for v in row), axis=1
    ).astype(int)

    df["has_bus"] = df[vehicle_type_cols].apply(
        lambda row: any(contains_any(v, pattern_bus) for v in row), axis=1
    ).astype(int)

    df["has_bicycle"] = df[vehicle_type_cols].apply(
        lambda row: any(contains_any(v, pattern_bike) for v in row), axis=1
    ).astype(int)

    return df


def engineer_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering steps in a pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Integrated and cleaned dataset.

    Returns
    -------
    pd.DataFrame
        Dataset with engineered features added.
    """
    df = create_temporal_features(df)
    df = create_location_features(df)
    df = create_severity_features(df)
    df = create_vehicle_features(df)
    return df
