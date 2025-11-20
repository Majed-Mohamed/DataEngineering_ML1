from dash import Input, Output, State
from components.graphs import (
    create_time_series_chart,
    create_borough_comparison_chart,
    create_severity_chart,
    create_heatmap,
    create_contributing_factors_chart,
    create_hourly_distribution_chart
)
import pandas as pd

def register_callbacks(app, df):
    """
    Register all dashboard callbacks
    
    Parameters:
    -----------
    app : Dash app instance
    df : pandas DataFrame with processed data
    """

    # Update all graphs when any filter changes
    @app.callback(
        [
            Output('time-series-chart', 'children'),
            Output('borough-comparison-chart', 'children'),
            Output('severity-chart', 'children'),
            Output('heatmap-chart', 'children'),
            Output('contributing-factors-chart', 'children'),
            Output('hourly-distribution-chart', 'children')
        ],
        [
            Input('date-filter', 'start_date'),
            Input('date-filter', 'end_date'),
            Input('borough-filter', 'value'),
            Input('severity-filter', 'value'),
            Input('vehicle-type-filter', 'value')
        ]
    )
    def update_graphs(start_date, end_date, boroughs, severity, vehicle_types):
        # Start with the full DataFrame
        filtered_df = df.copy()

        # Filter by date
        if start_date:
            filtered_df = filtered_df[filtered_df['CRASH_DATE'] >= start_date]
        if end_date:
            filtered_df = filtered_df[filtered_df['CRASH_DATE'] <= end_date]

        # Filter by borough
        if boroughs:
            filtered_df = filtered_df[filtered_df['BOROUGH'].isin(boroughs)]

        # Filter by severity
        if severity:
            severity_map = {'INJURY': 'NUMBER OF PERSONS INJURED', 'FATAL': 'NUMBER OF PERSONS KILLED'}
            cols_to_check = [severity_map[s] for s in severity if s in severity_map]
            filtered_df = filtered_df[filtered_df[cols_to_check].sum(axis=1) > 0]

        # Filter by vehicle types
        if vehicle_types:
            filtered_df = filtered_df[filtered_df['VEHICLE_TYPE'].isin(vehicle_types)]

        # Return updated graphs
        return (
            create_time_series_chart(filtered_df),
            create_borough_comparison_chart(filtered_df),
            create_severity_chart(filtered_df),
            create_heatmap(filtered_df),
            create_contributing_factors_chart(filtered_df),
            create_hourly_distribution_chart(filtered_df)
        )
