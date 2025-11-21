"""
Common utility functions for notebooks and modules

This module provides reusable utility functions for data loading, saving,
and display operations used across notebooks and scripts.
"""

# Standard library imports
import sys
from pathlib import Path
from typing import Optional, Union

# Third-party imports
import pandas as pd
import numpy as np

# Local imports
try:
    from . import config
except ImportError:
    import config

# Use config values
PROCESSED_DATA_DIR = config.PROCESSED_DATA_DIR
CACHE_DIR = config.CACHE_DIR


def setup_notebook_path() -> None:
    """
    Add src directory to Python path for notebook imports
    
    This function should be called at the start of each notebook to ensure
    that modules from the src/ directory can be imported.
    
    Example:
    --------
    >>> from src.utils import setup_notebook_path
    >>> setup_notebook_path()
    ✅ Added to path: /path/to/project/src
    """
    project_root = Path.cwd().parent
    src_path = str(project_root / 'src')
    
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"✅ Added to path: {src_path}")
    else:
        print(f"ℹ️  Already in path: {src_path}")


def load_processed_data(filename: str) -> pd.DataFrame:
    """
    Load processed parquet file from data/processed/ directory
    
    Parameters:
    -----------
    filename : str
        Name of parquet file (e.g., '01_cleaned_crashes.parquet')
    
    Returns:
    --------
    pd.DataFrame
        Loaded DataFrame
    
    Raises:
    -------
    FileNotFoundError
        If the specified file doesn't exist
    
    Example:
    --------
    >>> crashes = load_processed_data('01_cleaned_crashes.parquet')
    📂 Loading: /path/to/data/processed/01_cleaned_crashes.parquet
    ✅ Loaded: 1,234,567 records
    """
    path = PROCESSED_DATA_DIR / filename
    
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}\n"
            f"Make sure you've run the previous notebook to generate this file."
        )
    
    print(f"📂 Loading: {path}")
    df = pd.read_parquet(path)
    print(f"✅ Loaded: {len(df):,} records")
    
    return df


def save_processed_data(
    df: pd.DataFrame,
    filename: str,
    verbose: bool = True
) -> Path:
    """
    Save DataFrame to data/processed/ directory as parquet
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to save
    filename : str
        Output filename (e.g., '01_cleaned_crashes.parquet')
    verbose : bool, default=True
        Whether to print save information
    
    Returns:
    --------
    Path
        Path to saved file
    
    Example:
    --------
    >>> save_processed_data(crashes_clean, '01_cleaned_crashes.parquet')
    ✅ Saved: /path/to/data/processed/01_cleaned_crashes.parquet
       Size: 125.34 MB
       Shape: (1234567, 29)
    """
    # Ensure directory exists
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    output_path = PROCESSED_DATA_DIR / filename
    df.to_parquet(output_path, index=False, compression='snappy')
    
    if verbose:
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Saved: {output_path}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Shape: {df.shape}")
        print(f"   Records: {len(df):,}")
    
    return output_path


def display_dataframe_info(
    df: pd.DataFrame,
    name: str = "DataFrame",
    show_sample: bool = True
) -> None:
    """
    Display comprehensive DataFrame information
    
    Shows shape, memory usage, data types, and missing values summary.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to analyze
    name : str, default='DataFrame'
        Name to display in header
    show_sample : bool, default=True
        Whether to show first few rows
    
    Example:
    --------
    >>> display_dataframe_info(crashes_df, "Crashes Dataset")
    ============================================================
    Crashes Dataset Information
    ============================================================
    Shape: (1234567, 29)
    Memory: 342.56 MB
    ...
    """
    print(f"\n{'='*60}")
    print(f"{name} Information")
    print(f"{'='*60}")
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Memory: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")
    
    # Data types
    print(f"\nData Types:")
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  {dtype}: {count} columns")
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"\nMissing Values:")
        missing_pct = (missing / len(df)) * 100
        missing_df = pd.DataFrame({
            'Missing': missing[missing > 0],
            'Percentage': missing_pct[missing > 0]
        }).sort_values('Missing', ascending=False)
        print(missing_df.to_string())
    else:
        print(f"\n✅ No missing values")
    
    # Duplicate rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"\n⚠️  Duplicate rows: {duplicates:,} ({duplicates/len(df)*100:.2f}%)")
    else:
        print(f"\n✅ No duplicate rows")
    
    print(f"{'='*60}\n")
    
    # Show sample
    if show_sample:
        print("Sample Data (first 3 rows):")
        print(df.head(3).to_string())
        print()


def get_missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get detailed missing value statistics
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to analyze
    
    Returns:
    --------
    pd.DataFrame
        Summary with columns: column, missing_count, missing_percent, dtype
    
    Example:
    --------
    >>> summary = get_missing_value_summary(crashes_df)
    >>> print(summary)
    """
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    
    summary = pd.DataFrame({
        'column': df.columns,
        'missing_count': missing.values,
        'missing_percent': missing_pct.values,
        'dtype': df.dtypes.values
    })
    
    # Filter to only columns with missing values and sort
    summary = summary[summary['missing_count'] > 0].sort_values(
        'missing_count', 
        ascending=False
    ).reset_index(drop=True)
    
    return summary


def compare_dataframes(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    name1: str = "Before",
    name2: str = "After"
) -> None:
    """
    Compare two DataFrames and display differences
    
    Useful for showing before/after cleaning operations.
    
    Parameters:
    -----------
    df1 : pd.DataFrame
        First DataFrame
    df2 : pd.DataFrame
        Second DataFrame
    name1 : str, default='Before'
        Name for first DataFrame
    name2 : str, default='After'
        Name for second DataFrame
    
    Example:
    --------
    >>> compare_dataframes(crashes_raw, crashes_clean, "Raw", "Cleaned")
    """
    print(f"\n{'='*60}")
    print(f"Comparison: {name1} vs {name2}")
    print(f"{'='*60}")
    
    # Shape comparison
    print(f"\nShape:")
    print(f"  {name1}: {df1.shape[0]:,} rows × {df1.shape[1]} columns")
    print(f"  {name2}: {df2.shape[0]:,} rows × {df2.shape[1]} columns")
    
    rows_diff = df2.shape[0] - df1.shape[0]
    cols_diff = df2.shape[1] - df1.shape[1]
    
    if rows_diff != 0:
        sign = "+" if rows_diff > 0 else ""
        print(f"  Change: {sign}{rows_diff:,} rows ({rows_diff/df1.shape[0]*100:+.2f}%)")
    if cols_diff != 0:
        sign = "+" if cols_diff > 0 else ""
        print(f"  Change: {sign}{cols_diff} columns")
    
    # Memory comparison
    mem1 = df1.memory_usage(deep=True).sum() / (1024**2)
    mem2 = df2.memory_usage(deep=True).sum() / (1024**2)
    print(f"\nMemory Usage:")
    print(f"  {name1}: {mem1:.2f} MB")
    print(f"  {name2}: {mem2:.2f} MB")
    print(f"  Change: {mem2-mem1:+.2f} MB ({(mem2-mem1)/mem1*100:+.2f}%)")
    
    # Column differences
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    
    removed = cols1 - cols2
    added = cols2 - cols1
    
    if removed or added:
        print(f"\nColumn Changes:")
        if removed:
            print(f"  Removed: {', '.join(sorted(removed))}")
        if added:
            print(f"  Added: {', '.join(sorted(added))}")
    
    print(f"{'='*60}\n")


def get_data_summary(df: pd.DataFrame, name: str = "Dataset") -> dict:
    """
    Get comprehensive summary statistics for a DataFrame
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to summarize
    name : str, default='Dataset'
        Name of the dataset
    
    Returns:
    --------
    dict
        Dictionary with summary statistics
    
    Example:
    --------
    >>> summary = get_data_summary(crashes_df, "Crashes")
    >>> print(summary['total_rows'])
    1234567
    """
    summary = {
        'name': name,
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_mb': df.memory_usage(deep=True).sum() / (1024**2),
        'duplicate_rows': df.duplicated().sum(),
        'total_missing': df.isnull().sum().sum(),
        'columns_with_missing': (df.isnull().sum() > 0).sum(),
        'numeric_columns': len(df.select_dtypes(include=['int64', 'float64']).columns),
        'categorical_columns': len(df.select_dtypes(include=['object']).columns),
        'datetime_columns': len(df.select_dtypes(include=['datetime64']).columns)
    }
    
    return summary


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, create if it doesn't
    
    Parameters:
    -----------
    directory : str or Path
        Directory path
    
    Returns:
    --------
    Path
        Path object for the directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clear_cache() -> None:
    """
    Clear all cached data files
    
    Removes all files from the cache directory but keeps the directory.
    """
    if CACHE_DIR.exists():
        count = 0
        for file in CACHE_DIR.glob('*'):
            if file.is_file():
                file.unlink()
                count += 1
        print(f"✅ Cleared {count} cached files from {CACHE_DIR}")
    else:
        print(f"ℹ️  Cache directory doesn't exist: {CACHE_DIR}")
