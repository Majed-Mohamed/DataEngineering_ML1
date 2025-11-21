"""
Main Dash application for NYC Motor Vehicle Collisions Dashboard
"""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import sys

from components.layouts import create_main_layout
from components.callbacks import register_callbacks

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# ✅ UPDATED LINE
from config import APP_TITLE, APP_PORT, DEBUG_MODE, PROCESSED_DATA_DIR

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = APP_TITLE

# For deployment
server = app.server

# Load processed data for dashboard
data_file = PROCESSED_DATA_DIR / "dashboard_filtered.parquet"
try:
    df = pd.read_parquet(data_file)
    print(f"Data loaded successfully. Shape: {df.shape}")
except FileNotFoundError:
    print(f"ERROR: {data_file} not found. Using empty DataFrame.")
    df = pd.DataFrame()

# Layout + callbacks
app.layout = create_main_layout(df)
register_callbacks(app, df)

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, port=APP_PORT, host="0.0.0.0")

