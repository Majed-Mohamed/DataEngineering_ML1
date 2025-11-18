"""
Main Dash application for NYC Motor Vehicle Collisions Dashboard
"""
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.config import APP_TITLE, APP_PORT, DEBUG_MODE, PROCESSED_DATA_DIR

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

# For deployment
server = app.server

# TODO: Load processed data
# df = pd.read_parquet(PROCESSED_DATA_DIR / "dashboard_data.parquet")

# TODO: Define app layout
app.layout = html.Div([
    html.H1("NYC Motor Vehicle Collisions Dashboard"),
    html.P("Dashboard under construction...")
])

# TODO: Define callbacks

if __name__ == "__main__":
    app.run_server(debug=DEBUG_MODE, port=APP_PORT, host='0.0.0.0')
