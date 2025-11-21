"""
NYC Motor Vehicle Collisions Data Engineering Project
Source code package

This package provides a complete data engineering pipeline for analyzing
NYC motor vehicle collision data from NYC Open Data.
"""

__version__ = "1.0.0"
__author__ = "DataEngineering_ML1 Team"

# Package-level imports for convenient access
# Import order: standard library → third-party → local modules

# Configuration
from .config import (
    PROCESSED_DATA_DIR,
    CACHE_DIR,
    CRASHES_URL,
    PERSONS_URL,
    VEHICLES_URL,
    APP_TITLE,
    APP_PORT,
)

# Utility functions
from .utils import (
    setup_notebook_path,
    load_processed_data,
    save_processed_data,
    display_dataframe_info,
)

# Define public API
__all__ = [
    # Configuration
    'PROCESSED_DATA_DIR',
    'CACHE_DIR',
    'CRASHES_URL',
    'PERSONS_URL',
    'VEHICLES_URL',
    'APP_TITLE',
    'APP_PORT',
    
    # Utilities
    'setup_notebook_path',
    'load_processed_data',
    'save_processed_data',
    'display_dataframe_info',
]
