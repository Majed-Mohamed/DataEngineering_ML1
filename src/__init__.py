"""
NYC Motor Vehicle Collisions Data Engineering Project
Source code package
"""

__version__ = "1.0.0"
__author__ = "DataEngineering_ML1 Team"

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

from .utils import (
    setup_notebook_path,
    load_processed_data,
    save_processed_data,
    display_dataframe_info,
)

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
