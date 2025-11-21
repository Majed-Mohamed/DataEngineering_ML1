"""
Dashboard layout components
"""
from dash import html
import dash_bootstrap_components as dbc

from .filters import create_all_filters
from components.graphs import (
    create_time_series_chart,
    create_borough_comparison_chart,
    create_severity_chart,
    create_heatmap,
    create_contributing_factors_chart,
    create_hourly_distribution_chart,
)


def create_header():
    """Dashboard header"""
    return html.Div(
        className="dashboard-header",
        children=[
            html.H1("NYC Motor Vehicle Collisions Dashboard"),
            html.P("Explore collision patterns across NYC"),
        ],
    )


def create_stats_cards(df):
    """Simple KPI cards using real data if available."""
    total_collisions = len(df) if df is not None else 0
    total_injured = int(df.get("total_injured", 0).sum()) if df is not None else 0
    total_killed = int(df.get("total_killed", 0).sum()) if df is not None else 0
    unique_vehicles = (
        df["vehicle_type_code1"].nunique() if df is not None and "vehicle_type_code1" in df.columns else 0
    )

    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [html.H4("Total Collisions"), html.H2(f"{total_collisions:,}")]
                    ),
                    className="stat-card",
                ),
                md=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [html.H4("Total Injuries"), html.H2(f"{total_injured:,}")]
                    ),
                    className="stat-card",
                ),
                md=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [html.H4("Total Fatalities"), html.H2(f"{total_killed:,}")]
                    ),
                    className="stat-card",
                ),
                md=3,
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [html.H4("Vehicle Types"), html.H2(f"{unique_vehicles:,}")]
                    ),
                    className="stat-card",
                ),
                md=3,
            ),
        ],
        className="mb-4",
    )


def create_main_layout(df=None):
    """
    Main dashboard layout structure.
    """
    import pandas as pd

    if df is None:
        df = pd.DataFrame()

    return dbc.Container(
        [
            create_header(),
            create_stats_cards(df),

            html.Div(className="filter-panel mb-4", children=[create_all_filters()]),

            html.Div(
                className="graphs-section",
                children=[
                    html.Div(
                        id="time-series-chart",
                        className="graph-container mb-4",
                        children=[create_time_series_chart(df)],
                    ),
                    html.Div(
                        id="borough-comparison-chart",
                        className="graph-container mb-4",
                        children=[create_borough_comparison_chart(df)],
                    ),
                    html.Div(
                        id="severity-chart",
                        className="graph-container mb-4",
                        children=[create_severity_chart(df)],
                    ),
                    html.Div(
                        id="heatmap-chart",
                        className="graph-container mb-4",
                        children=[create_heatmap(df)],
                    ),
                    html.Div(
                        id="contributing-factors-chart",
                        className="graph-container mb-4",
                        children=[create_contributing_factors_chart(df)],
                    ),
                    html.Div(
                        id="hourly-distribution-chart",
                        className="graph-container mb-4",
                        children=[create_hourly_distribution_chart(df)],
                    ),
                ],
            ),

            html.Div(
                className="dashboard-footer mt-4",
                children=[html.P("Data source: NYC Open Data")],
            ),
        ],
        className="dashboard-container",
        fluid=True,
    )
