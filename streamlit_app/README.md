# NYC Motor Vehicle Collisions Dashboard

Interactive Streamlit dashboard for NYC motor vehicle collision data analysis.

## Features

- **Query Language**: key:value syntax (e.g., `borough:Brooklyn year:2020 injury:killed`)
- **Person-Level Filtering**: Logical consistency with injury status filtering
- **KPI Metrics**: Total collisions, injuries, deaths, and person records
- **Interactive Visualizations**: Time series, borough distribution, hourly patterns, injury breakdown, contributing factors
- **DuckDB Integration**: Efficient SQL queries with view-based architecture

## Running the App

### Windows
```bash
run_streamlit.bat
```

### Manual
```bash
streamlit run streamlit_app/app.py
```

## Requirements

Requires `dashboard_data.parquet` file. Run notebooks 01-07 to generate.

## Architecture

- View-based design with `crashes_aggregated` and `persons` views
- Person-level filtering for logical consistency
- Cached database connection and query results
- Query language parser for precise filtering
