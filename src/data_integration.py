"""
Dataset integration and merging logic
"""

from typing import Optional, List, Dict

import pandas as pd


def integrate_datasets(
    crashes: pd.DataFrame,
    persons: pd.DataFrame,
    vehicles: Optional[pd.DataFrame] = None,
    merge_key: str = "collision_id",
) -> pd.DataFrame:
    """
    Integrate crashes, persons, and vehicles datasets.

    Parameters
    ----------
    crashes : pd.DataFrame
        Cleaned crashes dataset (one row per collision_id ideally).
    persons : pd.DataFrame
        Cleaned persons dataset (may have multiple rows per collision_id).
    vehicles : pd.DataFrame, optional
        Cleaned vehicles dataset (may have multiple rows per collision_id).
    merge_key : str
        Key column for merging (default: 'collision_id').

    Returns
    -------
    pd.DataFrame
        Integrated dataset.
    """
    # Ensure merge_key exists
    for name, df in [("crashes", crashes), ("persons", persons), ("vehicles", vehicles)]:
        if df is not None and merge_key not in df.columns:
            raise KeyError(f"merge_key '{merge_key}' not found in {name} dataset")

    # Start with crashes
    integrated = crashes.copy()

    # Merge persons with suffix to avoid column name collisions
    integrated = integrated.merge(
        persons,
        on=merge_key,
        how="left",
        suffixes=("", "_person"),
    )

    # Merge vehicles if provided
    if vehicles is not None:
        integrated = integrated.merge(
            vehicles,
            on=merge_key,
            how="left",
            suffixes=("", "_veh"),
        )

    return integrated


def validate_integration(df: pd.DataFrame, merge_key: str = "collision_id") -> Dict[str, float]:
    """
    Validate integrated dataset.
    Check for data quality issues after merging.

    Returns
    -------
    dict
        Validation report with metrics.
    """
    report: Dict[str, float] = {}

    report["num_rows"] = len(df)
    report["num_columns"] = df.shape[1]

    if merge_key in df.columns:
        report["num_unique_collision_ids"] = df[merge_key].nunique()
        report["missing_collision_id"] = df[merge_key].isna().sum()
        report["duplicate_collision_id_rows"] = df.duplicated(subset=[merge_key]).sum()
    else:
        report["num_unique_collision_ids"] = 0
        report["missing_collision_id"] = None
        report["duplicate_collision_id_rows"] = None

    # Overall missingness
    report["overall_missing_ratio"] = float(df.isna().mean().mean())

    # Columns completely empty
    empty_cols = df.columns[df.isna().all()].tolist()
    report["num_empty_columns"] = len(empty_cols)

    return report


def post_integration_cleaning(
    df: pd.DataFrame,
    missing_threshold: float = 0.9,
    drop_empty_cols: bool = True,
) -> pd.DataFrame:
    """
    Clean data after integration:
    - Drop fully empty columns
    - Drop columns with too high missing ratio
    - Remove duplicate rows based only on hashable columns
      (to avoid errors from dict / list columns)
    """

    df = df.copy()

    # 1) Drop completely empty columns
    if drop_empty_cols:
        df = df.dropna(axis=1, how="all")

    # 2) Drop columns with missing ratio above threshold
    missing_ratio = df.isna().mean()
    cols_to_drop = missing_ratio[missing_ratio > missing_threshold].index
    if len(cols_to_drop) > 0:
        df = df.drop(columns=cols_to_drop)

    # 3) Drop duplicates using only hashable (non-dict/list/set) columns
    hashable_cols = []
    for col in df.columns:
        sample = df[col].dropna().head(20)
        # If any value in the sample is dict/list/set → skip this column
        if not sample.apply(lambda x: isinstance(x, (dict, list, set))).any():
            hashable_cols.append(col)

    if hashable_cols:
        df = df.drop_duplicates(subset=hashable_cols).reset_index(drop=True)
    else:
        # If somehow all columns are unhashable, just skip duplicate removal
        df = df.reset_index(drop=True)

    return df

