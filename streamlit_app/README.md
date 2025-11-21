# NYC Motor Vehicle Collisions Dashboard - Streamlit

This is a Streamlit-based interactive dashboard for visualizing NYC motor vehicle collision data.

## Features

- **Real-time Filtering**: Filter data by date range, year, borough, vehicle type, contributing factors, and injury type
- **KPI Metrics**: View total collisions, injuries, deaths, and vehicles involved
- **Interactive Visualizations**:
  - Time series of collisions over time
  - Collisions by borough
  - Collisions by hour of day
  - Severity distribution
  - Top contributing factors
- **DuckDB Integration**: Efficient out-of-core data processing for large datasets

## Running the App

### Option 1: Using the batch script (Windows)
```bash
run_streamlit.bat
```

### Option 2: Manual command
```bash
cd streamlit_app
streamlit run app.py
```

### Option 3: From project root
```bash
streamlit run streamlit_app/app.py
```

## Requirements

The app requires the `dashboard_data.parquet` file to be generated first. Run notebooks 01-07 in sequence to create this file.

## Configuration

The app uses the same configuration from `src/config.py` as the Dash version, specifically:
- `APP_TITLE`: Dashboard title
- `PROCESSED_DATA_DIR`: Location of the processed data files

## Performance

The app uses DuckDB for efficient SQL queries on the Parquet file, with Streamlit's caching to minimize redundant database calls:
- `@st.cache_resource`: Caches the database connection
- `@st.cache_data`: Caches query results and filter options
