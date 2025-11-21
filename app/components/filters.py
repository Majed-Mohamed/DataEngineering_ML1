"""
Dashboard filter components
"""
from dash import dcc, html
import dash_bootstrap_components as dbc


def create_date_filter():
    """Date range filter (updated to remove deprecated FormGroup)"""
    return dbc.Row([
        dbc.Col([
            dbc.Label("Date Range"),
            dcc.DatePickerRange(
                id="date-filter",
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                display_format="YYYY-MM-DD",
                style={"width": "100%"}
            )
        ])
    ], className="mb-3")


def create_borough_filter():
    """Borough filter"""
    boroughs = ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"]

    return dbc.Row([
        dbc.Col([
            dbc.Label("Borough"),
            dcc.Dropdown(
                id="borough-filter",
                options=[{"label": b, "value": b} for b in boroughs],
                value=[],
                multi=True,
                placeholder="Select Borough(s)"
            )
        ])
    ], className="mb-3")


def create_severity_filter():
    """Severity filter"""
    return dbc.Row([
        dbc.Col([
            dbc.Label("Severity"),
            dcc.Checklist(
                id="severity-filter",
                options=[
                    {"label": "Injury", "value": "INJURY"},
                    {"label": "Fatality", "value": "FATAL"}
                ],
                value=["INJURY"],
                inline=True
            )
        ])
    ], className="mb-3")


def create_vehicle_type_filter():
    """Vehicle type filter"""
    vehicle_types = [
        "PASSENGER VEHICLE", "TAXI", "BUS",
        "MOTORCYCLE", "BICYCLE", "TRUCK", "OTHER"
    ]

    return dbc.Row([
        dbc.Col([
            dbc.Label("Vehicle Type"),
            dcc.Dropdown(
                id="vehicle-type-filter",
                options=[{"label": v, "value": v} for v in vehicle_types],
                value=[],
                multi=True,
                placeholder="Select Vehicle Type(s)"
            )
        ])
    ], className="mb-3")


def create_all_filters():
    """Combine all filters into a card"""
    return dbc.Card([
        dbc.CardBody([
            create_date_filter(),
            create_borough_filter(),
            create_severity_filter(),
            create_vehicle_type_filter()
        ])
    ], className="filter-panel")
