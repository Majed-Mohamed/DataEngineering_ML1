"""
Reusable data cleaning functions for NYC collision data
"""
import pandas as pd
import numpy as np
from typing import List


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names"""
    # TODO: Implement column name cleaning
    pass


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = 'drop',
    threshold: float = 0.5
) -> pd.DataFrame:
    """
    Handle missing values
    
    Parameters:
    -----------
    strategy : str
        'drop', 'fill', or 'flag'
    threshold : float
        Drop columns with missing > threshold
    """
    # TODO: Implement missing value handling
    pass


def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """Remove duplicate rows"""
    # TODO: Implement duplicate removal
    pass


def clean_crash_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean crashes dataset
    Apply all cleaning steps specific to crashes
    """
    # TODO: Implement crashes cleaning logic
    pass


def clean_persons_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean persons dataset
    Apply all cleaning steps specific to persons
    """
    # TODO: Implement persons cleaning logic
    pass


def clean_vehicles_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean vehicles dataset
    Apply all cleaning steps specific to vehicles
    """
    # TODO: Implement vehicles cleaning logic
    pass
