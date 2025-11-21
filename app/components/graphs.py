"""
Dashboard graph/chart components
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc


def _is_empty(df):
    return df is None or len(df) == 0


def create_time_series_chart(df=None):
    """
    Time series of collisions over time (by crash_date).
    """
    if _is_empty(df) or "crash_date" not in df.columns:
        # Simple placeholder
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=["2020-01-01", "2020-01-02", "2020-01-03"],
                y=[10, 15, 7],
                mode="lines+markers",
                name="Collisions",
            )
        )
        fig.update_layout(title="Time Series of Collisions (placeholder)")
        return dcc.Graph(figure=fig)

    ts = (
        df.groupby("crash_date")
        .size()
        .reset_index(name="collisions")
        .sort_values("crash_date")
    )
    fig = px.line(
        ts,
        x="crash_date",
        y="collisions",
        title="Collisions over Time",
        labels={"crash_date": "Crash Date", "collisions": "Number of Collisions"},
    )
    fig.update_traces(mode="lines+markers")
    return dcc.Graph(figure=fig)


def create_borough_comparison_chart(df=None):
    """
    Bar chart comparing collisions by borough.
    """
    if _is_empty(df) or "borough" not in df.columns:
        boroughs = ["MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"]
        counts = [120, 200, 150, 80, 50]
        fig = px.bar(
            x=boroughs,
            y=counts,
            labels={"x": "Borough", "y": "Collisions"},
            title="Collisions by Borough (placeholder)",
        )
        return dcc.Graph(figure=fig)

    agg = (
        df["borough"]
        .fillna("UNKNOWN")
        .value_counts()
        .reset_index(name="collisions")
        .rename(columns={"index": "borough"})
    )

    fig = px.bar(
        agg,
        x="borough",
        y="collisions",
        title="Collisions by Borough",
        labels={"borough": "Borough", "collisions": "Number of Collisions"},
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    return dcc.Graph(figure=fig)


def create_severity_chart(df=None):
    """
    Show total injuries vs total deaths.
    """
    if _is_empty(df):
        labels = ["Injury", "Fatality"]
        values = [500, 20]
    else:
        injuries = df.get("total_injured", pd.Series([0])).sum()
        deaths = df.get("total_killed", pd.Series([0])).sum()
        labels = ["Injuries", "Fatalities"]
        values = [injuries, deaths]

    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.3))
    fig.update_layout(title="Severity Distribution")
    return dcc.Graph(figure=fig)


def create_heatmap(df=None):
    """
    Geographic scatter map of collisions.
    """
    if (
        _is_empty(df)
        or "latitude" not in df.columns
        or "longitude" not in df.columns
    ):
        # Simple placeholder scatter
        fig = px.scatter(
            x=[-74.0, -73.95, -73.9],
            y=[40.7, 40.72, 40.75],
            title="Collision Locations (placeholder)",
            labels={"x": "Longitude", "y": "Latitude"},
        )
        return dcc.Graph(figure=fig)

    # Use scatter_mapbox; user can set MAPBOX token, but this still works for basic style
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="severity_score" if "severity_score" in df.columns else None,
        size="total_injured" if "total_injured" in df.columns else None,
        zoom=9,
        mapbox_style="carto-positron",
        title="Crash Locations with Severity",
    )
    return dcc.Graph(figure=fig)


# in app/components/graphs.py

def create_contributing_factors_chart(df=None):
    """
    Create chart of top contributing factors using real data if available.
    Falls back to a simple placeholder if df is empty or column is missing.
    """
    # If there is no data or no relevant column, keep the old placeholder
    if df is None or 'contributing_factor_vehicle_1' not in df.columns:
        factors = ["Speeding", "Distracted Driving", "Alcohol", "Weather", "Other"]
        counts = [200, 150, 50, 30, 20]
        fig = px.bar(
            x=factors,
            y=counts,
            labels={"x": "Factor", "y": "Count"},
            title="Top Contributing Factors"
        )
        return dcc.Graph(figure=fig)

    # Use real data
    factor_series = (
        df['contributing_factor_vehicle_1']
        .fillna("Unspecified")
        .value_counts()
        .nlargest(10)
    )

    factor_df = factor_series.reset_index()
    factor_df.columns = ['factor', 'count']   # make sure names are unique

    fig = px.bar(
        factor_df,
        x='factor',
        y='count',
        labels={"factor": "Contributing Factor", "count": "Number of Collisions"},
        title="Top 10 Contributing Factors (Vehicle 1)"
    )
    fig.update_layout(xaxis_tickangle=-45)

    return dcc.Graph(figure=fig)



def create_hourly_distribution_chart(df=None):
    """
    Create chart showing collisions by hour of day using real data.
    Expects a 'crash_hour' column in the dataframe.
    """
    from dash import dcc

    if df is None or df.empty or "crash_hour" not in df.columns:
        # Fallback placeholder if no data
        hours = list(range(24))
        collisions = [5, 2, 1, 1, 2, 5, 10, 20, 25, 30, 28, 27,
                      26, 24, 22, 20, 18, 15, 12, 10, 8, 7, 6, 5]
        hourly_df = pd.DataFrame({"crash_hour": hours, "collisions": collisions})
    else:
        # Group by crash_hour and count collisions
        hourly_df = (
            df.groupby("crash_hour")
              .size()
              .reset_index(name="collisions")
              .sort_values("crash_hour")
        )

    fig = px.bar(
        hourly_df,
        x="crash_hour",
        y="collisions",
        labels={"crash_hour": "Hour of Day", "collisions": "Number of Collisions"},
        title="Collisions by Hour of Day",
    )

    return dcc.Graph(figure=fig)

