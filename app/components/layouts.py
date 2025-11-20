"""
Dashboard layout components
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from .filters import create_all_filters
from components.graphs import (
    create_time_series_chart,
    create_borough_comparison_chart,
    create_severity_chart,
    create_heatmap,
    create_contributing_factors_chart,
    create_hourly_distribution_chart
)


def create_header():
    """
    Create dashboard header with title and description
    """
    return html.Div(className="dashboard-header", children=[
        html.H1("NYC Motor Vehicle Collisions Dashboard"),
        html.P("Explore collision patterns across NYC")
    ])


def create_stats_cards(df):
    """
    Create KPI cards showing key statistics
    """
    # Placeholder cards
    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Total Collisions", className="card-title"),
                html.P("1234", className="card-text")
            ])
        ], className="stat-card"), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Injuries", className="card-title"),
                html.P("567", className="card-text")
            ])
        ], className="stat-card"), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Fatalities", className="card-title"),
                html.P("12", className="card-text")
            ])
        ], className="stat-card"), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Vehicles Involved", className="card-title"),
                html.P("789", className="card-text")
            ])
        ], className="stat-card"), width=3)
    ], className="mb-4")


def create_graph_placeholder(title):
    """
    Create a placeholder card for a graph
    """
    return dbc.Card([
        dbc.CardBody([
            html.H5(title, className="card-title"),
            html.P("Graph will appear here", className="card-text")
        ])
    ], className="graph-container mb-4")


def create_main_layout(df=None):
    """
    Create main dashboard layout structure with filters, graphs, header, and footer.
    Uses placeholder graphs if no DataFrame is provided.
    """
    # If no data, use empty DataFrame for placeholders
    if df is None:
        import pandas as pd
        df = pd.DataFrame()

    layout = dbc.Container([
        # Header
        create_header(),
        
        # Stats cards
        create_stats_cards(df),
        
        # Filters
        html.Div(className="filter-panel mb-4", children=[
            create_all_filters()
        ]),

        # Graphs section with IDs for callbacks and initial placeholder graphs
        html.Div(className="graphs-section", children=[
            html.Div(id="time-series-chart", className="graph-container mb-4",
                     children=[create_time_series_chart(df)]),
            html.Div(id="borough-comparison-chart", className="graph-container mb-4",
                     children=[create_borough_comparison_chart(df)]),
            html.Div(id="severity-chart", className="graph-container mb-4",
                     children=[create_severity_chart(df)]),
            html.Div(id="heatmap-chart", className="graph-container mb-4",
                     children=[create_heatmap(df)]),
            html.Div(id="contributing-factors-chart", className="graph-container mb-4",
                     children=[create_contributing_factors_chart(df)]),
            html.Div(id="hourly-distribution-chart", className="graph-container mb-4",
                     children=[create_hourly_distribution_chart(df)]),
        ]),

        # Footer
        html.Div(className="dashboard-footer mt-4", children=[
            html.P("Data source: NYC Open Data")
        ])
    ], className="dashboard-container")

    return layout
