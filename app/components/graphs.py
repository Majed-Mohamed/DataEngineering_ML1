"""
Dashboard graph/chart components
"""
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc


def create_time_series_chart(df, metric='count'):
    """
    Create time series visualization of collisions
    """
    # TODO: Implement time series chart
    pass


def create_borough_comparison_chart(df):
    """
    Create bar chart comparing collisions by borough
    """
    # TODO: Implement borough comparison
    pass


def create_heatmap(df):
    """
    Create geographic heatmap of collisions
    """
    # TODO: Implement heatmap
    pass


def create_severity_chart(df):
    """
    Create chart showing injury/fatality statistics
    """
    # TODO: Implement severity chart
    pass


def create_contributing_factors_chart(df):
    """
    Create chart of top contributing factors
    """
    # TODO: Implement contributing factors chart
    pass


def create_hourly_distribution_chart(df):
    """
    Create chart showing collisions by hour of day
    """
    # TODO: Implement hourly distribution
    pass
