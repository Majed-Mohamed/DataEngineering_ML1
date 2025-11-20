"""
Dashboard graph/chart components
"""
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc

def create_time_series_chart(df=None, metric='count'):
    """
    Create time series visualization of collisions
    """
    # Placeholder figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=["2025-01-01", "2025-01-02", "2025-01-03"],
        y=[10, 15, 7],
        mode="lines+markers",
        name="Collisions"
    ))
    fig.update_layout(title="Time Series of Collisions")
    return dcc.Graph(figure=fig)


def create_borough_comparison_chart(df=None):
    """
    Create bar chart comparing collisions by borough
    """
    # Placeholder figure
    boroughs = ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"]
    counts = [120, 200, 150, 80, 50]

    fig = px.bar(x=boroughs, y=counts, labels={"x": "Borough", "y": "Collisions"}, title="Collisions by Borough")
    return dcc.Graph(figure=fig)


def create_severity_chart(df=None):
    """
    Create chart showing injury/fatality statistics
    """
    labels = ["Injury", "Fatality"]
    values = [500, 20]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.3))
    fig.update_layout(title="Severity Distribution")
    return dcc.Graph(figure=fig)


def create_heatmap(df=None):
    """
    Create geographic heatmap of collisions
    """
    # Placeholder figure using fake coordinates
    fig = px.density_mapbox(
        lat=[40.7128, 40.730610, 40.650002],
        lon=[-74.0060, -73.935242, -73.949997],
        z=[1, 2, 3],
        radius=10,
        center=dict(lat=40.7128, lon=-74.0060),
        zoom=10,
        mapbox_style="open-street-map",
        title="Collision Heatmap"
    )
    return dcc.Graph(figure=fig)


def create_contributing_factors_chart(df=None):
    """
    Create chart of top contributing factors
    """
    factors = ["Speeding", "Distracted Driving", "Alcohol", "Weather", "Other"]
    counts = [200, 150, 50, 30, 20]
    fig = px.bar(x=factors, y=counts, labels={"x": "Factor", "y": "Count"}, title="Top Contributing Factors")
    return dcc.Graph(figure=fig)


def create_hourly_distribution_chart(df=None):
    """
    Create chart showing collisions by hour of day
    """
    hours = list(range(24))
    collisions = [5, 2, 1, 1, 2, 5, 10, 20, 25, 30, 28, 27, 26, 24, 22, 20, 18, 15, 12, 10, 8, 7, 6, 5]
    fig = px.bar(x=hours, y=collisions, labels={"x": "Hour", "y": "Collisions"}, title="Collisions by Hour of Day")
    return dcc.Graph(figure=fig)
