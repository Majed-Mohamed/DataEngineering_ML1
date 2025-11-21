"""
Reusable data cleaning functions for NYC collision data
"""

from typing import List

import numpy as np
import pandas as pd


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names:
    - Strip whitespace
    - Lowercase
    - Replace spaces and special chars with underscores
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("-", "_")
        .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
    )
    return df


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop",
    threshold: float = 0.5,
) -> pd.DataFrame:
    """
    Handle missing values.

    Parameters
    ----------
    strategy : str
        'drop'  -> drop columns with missing ratio > threshold
        'fill'  -> fill numeric with median, categorical with mode
        'flag'  -> add *_was_missing flags, then fill like 'fill'
    threshold : float
        Columns with missing ratio > threshold are dropped (for 'drop' & 'flag')
    """
    df = df.copy()

    # 1) Optionally drop very sparse columns
    missing_ratio = df.isna().mean()
    cols_to_drop = missing_ratio[missing_ratio > threshold].index

    if len(cols_to_drop) > 0:
        df = df.drop(columns=cols_to_drop)

    if strategy in {"fill", "flag"}:
        # 2) For 'flag', create indicator columns before filling
        if strategy == "flag":
            for col in df.columns:
                if df[col].isna().any():
                    df[f"{col}_was_missing"] = df[col].isna().astype(int)

        # 3) Fill missing values
        for col in df.columns:
            if df[col].dtype in [np.float64, np.int64, "float64", "int64"]:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
            else:
                # For object / category columns
                if df[col].isna().all():
                    # If everything is NaN, leave it as is
                    continue
                mode_val = df[col].mode(dropna=True)
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val.iloc[0])

    # strategy == 'drop' already handled by dropping columns
    return df


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """
    Remove duplicate rows.

    Parameters
    ----------
    subset : list of str, optional
        Columns to consider for identifying duplicates.
        If None, all columns are used.
    """
    df = df.copy()
    df = df.drop_duplicates(subset=subset).reset_index(drop=True)
    return df


def clean_crash_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean crashes dataset:
    - Standardize column names
    - Convert date/time
    - Remove rows with missing essential fields
    - Remove clearly invalid coordinates
    """
    df = clean_column_names(df)

    # Convert CRASH_DATE to datetime
    if "crash_date" in df.columns:
        df["crash_date"] = pd.to_datetime(df["crash_date"], errors="coerce")

    # Convert CRASH_TIME to proper time (if exists)
    if "crash_time" in df.columns:
        # Some times are "HH:MM"; others might be malformed
        df["crash_time"] = pd.to_datetime(
            df["crash_time"], format="%H:%M", errors="coerce"
        ).dt.time

    # Essential: we need a valid crash_date
    if "crash_date" in df.columns:
        df = df.dropna(subset=["crash_date"])

    # Convert numeric injury / death columns
    numeric_cols = [
        col
        for col in df.columns
        if "injured" in col or "killed" in col or col.endswith("_injured") or col.endswith("_killed")
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Remove obviously invalid coordinates (0 or NaN, or far outside NYC)
    if "latitude" in df.columns and "longitude" in df.columns:
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

        # Remove rows with both coords missing
        df = df.dropna(subset=["latitude", "longitude"])

        # Remove (0,0) or values clearly out of NYC bounding box
        df = df[
            (df["latitude"].between(40.0, 41.2))
            & (df["longitude"].between(-75.0, -72.0))
        ]

    # Remove duplicates based on collision id if present
    if "collision_id" in df.columns:
        df = remove_duplicates(df, subset=["collision_id", "crash_date", "crash_time"])

    return df


def clean_persons_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean persons dataset:
    - Standardize column names
    - Ensure collision_id present
    - Clean age / injury columns
    """
    df = clean_column_names(df)

    # Drop rows without collision_id
    if "collision_id" in df.columns:
        df = df.dropna(subset=["collision_id"])

    # Person age
    if "person_age" in df.columns:
        df["person_age"] = pd.to_numeric(df["person_age"], errors="coerce")
        # Ages outside [0, 110] seem unrealistic; set to NaN
        df.loc[(df["person_age"] < 0) | (df["person_age"] > 110), "person_age"] = np.nan

    # Injury column: normalize strings
    if "person_injury" in df.columns:
        df["person_injury"] = (
            df["person_injury"]
            .astype(str)
            .str.strip()
            .str.title()
        )

    # Person type normalization
    if "person_type" in df.columns:
        df["person_type"] = (
            df["person_type"]
            .astype(str)
            .str.strip()
            .str.title()
        )

    df = remove_duplicates(df)
    return df


def clean_vehicles_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean vehicles dataset:
    - Standardize column names
    - Clean vehicle year
    - Normalize vehicle type strings
    """
    df = clean_column_names(df)

    # Vehicle year
    for col in ["vehicle_year", "vehicle_year_1", "vehicle_year_2"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            # Simple plausibility filter
            df.loc[(df[col] < 1950) | (df[col] > 2030), col] = np.nan

    # Normalize any 'vehicle_type' columns
    type_cols = [c for c in df.columns if "vehicle_type" in c]
    for col in type_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    # Drop rows without collision_id if present
    if "collision_id" in df.columns:
        df = df.dropna(subset=["collision_id"])

    df = remove_duplicates(df)
    return df
