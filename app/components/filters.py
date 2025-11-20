"""
Dashboard filter components
"""
from dash import dcc, html
import dash_bootstrap_components as dbc


def create_date_filter():
    """
    Create a date range filter component
    """
    return dbc.FormGroup([
        dbc.Label("Date Range"),
        dcc.DatePickerRange(
            id="date-filter",
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            display_format="YYYY-MM-DD",
            style={"width": "100%"}
        )
    ])


def create_borough_filter():
    """
    Create borough selection filter
    """
    boroughs = ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"]
    
    return dbc.FormGroup([
        dbc.Label("Borough"),
        dcc.Dropdown(
            id="borough-filter",
            options=[{"label": b, "value": b} for b in boroughs],
            value=[],  # default empty selection
            multi=True,
            placeholder="Select Borough(s)"
        )
    ])


def create_severity_filter():
    """
    Create severity filter (injuries/fatalities)
    """
    return dbc.FormGroup([
        dbc.Label("Severity"),
        dcc.Checklist(
            id="severity-filter",
            options=[
                {"label": "Injury", "value": "INJURY"},
                {"label": "Fatality", "value": "FATAL"}
            ],
            value=["INJURY"],  # default selected
            inline=True
        )
    ])


def create_vehicle_type_filter():
    """
    Create vehicle type filter
    """
    vehicle_types = [
        "PASSENGER VEHICLE", "TAXI", "BUS", "MOTORCYCLE", "BICYCLE", "TRUCK", "OTHER"
    ]
    
    return dbc.FormGroup([
        dbc.Label("Vehicle Type"),
        dcc.Dropdown(
            id="vehicle-type-filter",
            options=[{"label": v, "value": v} for v in vehicle_types],
            value=[],  # default empty selection
            multi=True,
            placeholder="Select Vehicle Type(s)"
        )
    ])


def create_all_filters():
    """
    Combine all filters into a filter panel
    """
    return dbc.Card([
        dbc.CardBody([
            create_date_filter(),
            create_borough_filter(),
            create_severity_filter(),
            create_vehicle_type_filter()
        ])
    ], className="filter-panel")
