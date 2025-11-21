from dash import Input, Output
from components.graphs import (
    create_time_series_chart,
    create_borough_comparison_chart,
    create_severity_chart,
    create_heatmap,
    create_contributing_factors_chart,
    create_hourly_distribution_chart,
)


def register_callbacks(app, df):
    """Register all dashboard callbacks."""

    @app.callback(
        [
            Output("time-series-chart", "children"),
            Output("borough-comparison-chart", "children"),
            Output("severity-chart", "children"),
            Output("heatmap-chart", "children"),
            Output("contributing-factors-chart", "children"),
            Output("hourly-distribution-chart", "children"),
        ],
        [
            Input("date-filter", "start_date"),
            Input("date-filter", "end_date"),
            Input("borough-filter", "value"),
            Input("severity-filter", "value"),
            Input("vehicle-type-filter", "value"),
        ],
    )
    def update_graphs(start_date, end_date, boroughs, severity, vehicle_types):
        # Start fresh
        filtered_df = df.copy()

        # DATE FILTER
        if start_date:
            filtered_df = filtered_df[filtered_df["crash_date"] >= start_date]
        if end_date:
            filtered_df = filtered_df[filtered_df["crash_date"] <= end_date]

        # BOROUGH FILTER
        if boroughs:
            filtered_df = filtered_df[filtered_df["borough"].isin(boroughs)]

        # SEVERITY FILTER
        if severity:
            mask = False
            if "INJURY" in severity:
                mask = mask | (filtered_df["total_injured"] > 0)
            if "FATAL" in severity:
                mask = mask | (filtered_df["total_killed"] > 0)
            filtered_df = filtered_df[mask]

        # VEHICLE TYPE FILTER
        if vehicle_types:
            mask = (
                filtered_df["vehicle_type_code1"].isin(vehicle_types)
                | filtered_df["vehicle_type_code2"].isin(vehicle_types)
            )
            filtered_df = filtered_df[mask]

        return (
            create_time_series_chart(filtered_df),
            create_borough_comparison_chart(filtered_df),
            create_severity_chart(filtered_df),
            create_heatmap(filtered_df),
            create_contributing_factors_chart(filtered_df),
            create_hourly_distribution_chart(filtered_df),
        )
