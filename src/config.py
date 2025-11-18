"""
Centralized configuration for NYC Motor Vehicle Collisions project
"""
from pathlib import Path
import os

# Project paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# Ensure directories exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# NYC Open Data API URLs
CRASHES_URL = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"
PERSONS_URL = "https://data.cityofnewyork.us/resource/f55k-p6yu.json"
VEHICLES_URL = "https://data.cityofnewyork.us/resource/bm4k-52h4.json"

# API Configuration
API_LIMIT = 50000  # Records per request (NYC Open Data limit)
APP_TOKEN = os.getenv("NYC_APP_TOKEN", None)  # Optional: for higher rate limits

# Dashboard Configuration
APP_TITLE = "NYC Motor Vehicle Collisions Dashboard"
APP_PORT = int(os.getenv("PORT", 8050))
DEBUG_MODE = os.getenv("DEBUG", "True").lower() == "true"

# Data Processing
CHUNK_SIZE = 10000  # For processing large datasets
DATE_COLUMNS = ["crash_date", "crash_time"]
