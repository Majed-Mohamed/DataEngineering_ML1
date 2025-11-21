"""
NYC Motor Vehicle Collisions Dashboard
Streamlit application with DuckDB optimization
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import duckdb
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import APP_TITLE, PROCESSED_DATA_DIR

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0d6efd;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6c757d;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid;
        margin-bottom: 1rem;
    }
    .metric-card.primary { border-left-color: #0d6efd; }
    .metric-card.warning { border-left-color: #ffc107; }
    .metric-card.danger { border-left-color: #dc3545; }
    .metric-card.info { border-left-color: #0dcaf0; }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA CONNECTION
# ============================================================================

# Google Drive URL for the data file
DRIVE_URL = "https://drive.google.com/uc?export=download&id=1qwjegnIt8eX1PQQmjRRDNK_GYGtX9hSp"
DATA_PATH = PROCESSED_DATA_DIR / "dashboard_data.parquet"

@st.cache_resource
def get_db_connection():
    """Create a DuckDB connection and register the view"""
    # Try local file first, then Google Drive
    data_source = None
    
    if DATA_PATH.exists():
        data_source = str(DATA_PATH)
    else:
        # Use Google Drive URL for deployment
        data_source = DRIVE_URL
    
    if not data_source:
        return None
    
    con = duckdb.connect(database=':memory:')
    try:
        con.execute(f"CREATE OR REPLACE VIEW crashes AS SELECT * FROM '{data_source}'")
        return con
    except Exception as e:
        st.error(f"❌ Error connecting to database: {e}")
        return None

@st.cache_data(ttl=300)
def query_db(query):
    """Execute a query and return a pandas DataFrame"""
    con = get_db_connection()
    if not con:
        return None
    
    try:
        df = con.execute(query).df()
        return df
    except Exception as e:
        st.error(f"❌ Error executing query: {e}")
        with st.expander("Show Query"):
            st.code(query, language="sql")
        return None

@st.cache_data
def get_column_name(candidates):
    """Dynamically find the correct column name from a list of candidates"""
    con = get_db_connection()
    if not con:
        return None
    
    try:
        cols = [c[0] for c in con.execute("DESCRIBE crashes").fetchall()]
        for cand in candidates:
            if cand in cols:
                return f'"{cand}"'
        return None
    except:
        return None

# Identify key columns dynamically
DATE_COL = get_column_name(['CRASH DATE', 'CRASH_DATE', 'crash_date'])
BOROUGH_COL = get_column_name(['borough_clean', 'BOROUGH', 'borough'])
SEVERITY_COL = get_column_name(['total_casualties', 'TOTAL_CASUALTIES'])
HOUR_COL = get_column_name(['crash_hour', 'CRASH_HOUR'])
FACTOR_COL = get_column_name(['CONTRIBUTING FACTOR VEHICLE 1', 'contributing_factor_vehicle_1'])
VEHICLE_TYPE_COL = get_column_name(['VEHICLE TYPE CODE 1', 'vehicle_type_code_1'])
SEVERITY_CAT_COL = get_column_name(['severity_category', 'SEVERITY_CATEGORY'])

# Stats columns
INJURED_COL = get_column_name(['total_injured', 'NUMBER OF PERSONS INJURED', 'NUMBER_OF_PERSONS_INJURED'])
KILLED_COL = get_column_name(['total_killed', 'NUMBER OF PERSONS KILLED', 'NUMBER_OF_PERSONS_KILLED'])
VEHICLES_COL = get_column_name(['num_vehicles', 'number_of_vehicles'])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data
def get_dropdown_options(column, limit=None):
    """Get unique values for filter options"""
    if not column:
        return []
    
    limit_clause = f"LIMIT {limit}" if limit else ""
    query = f"""
        SELECT DISTINCT {column} as val 
        FROM crashes 
        WHERE {column} IS NOT NULL 
        ORDER BY 1 
        {limit_clause}
    """
    df = query_db(query)
    if df is None or df.empty:
        return []
    
    return df['val'].tolist()

@st.cache_data
def get_vehicle_options():
    """Get cleaned vehicle type options"""
    if not VEHICLE_TYPE_COL:
        return []
    
    query = f"""
        SELECT {VEHICLE_TYPE_COL} as val, COUNT(*) as count
        FROM crashes 
        WHERE {VEHICLE_TYPE_COL} IS NOT NULL 
          AND LENGTH({VEHICLE_TYPE_COL}) > 3
        GROUP BY 1 
        ORDER BY 2 DESC 
        LIMIT 30
    """
    df = query_db(query)
    if df is None or df.empty:
        return []
    
    return df['val'].tolist()

@st.cache_data
def get_year_options():
    """Get unique years"""
    if not DATE_COL:
        return []
    
    query = f"SELECT DISTINCT EXTRACT(YEAR FROM {DATE_COL}) as val FROM crashes ORDER BY 1 DESC"
    df = query_db(query)
    if df is None or df.empty:
        return []
    
    return [int(val) for val in df['val'].tolist()]

@st.cache_data
def get_date_range():
    """Get min and max dates"""
    if not DATE_COL:
        return datetime(2020, 1, 1).date(), datetime(2024, 12, 31).date()
    
    query = f"SELECT MIN({DATE_COL}) as min_d, MAX({DATE_COL}) as max_d FROM crashes"
    df = query_db(query)
    if df is None or df.empty:
        return datetime(2020, 1, 1).date(), datetime(2024, 12, 31).date()
    
    return df['min_d'][0], df['max_d'][0]

def build_filter_clause(start_date, end_date, boroughs, years, vehicle_types, factors, injury_types, severity_min):
    """Build SQL WHERE clause based on filters"""
    clauses = []
    
    if start_date and end_date and DATE_COL:
        clauses.append(f"{DATE_COL} BETWEEN '{start_date}' AND '{end_date}'")
    
    if boroughs and BOROUGH_COL:
        borough_list = "', '".join(boroughs)
        clauses.append(f"{BOROUGH_COL} IN ('{borough_list}')")
    
    if years and DATE_COL:
        year_list = ", ".join([str(y) for y in years])
        clauses.append(f"EXTRACT(YEAR FROM {DATE_COL}) IN ({year_list})")
    
    if vehicle_types and VEHICLE_TYPE_COL:
        safe_types = [t.replace("'", "''") for t in vehicle_types]
        type_list = "', '".join(safe_types)
        clauses.append(f"{VEHICLE_TYPE_COL} IN ('{type_list}')")
    
    if factors and FACTOR_COL:
        safe_factors = [f.replace("'", "''") for f in factors]
        factor_list = "', '".join(safe_factors)
        clauses.append(f"{FACTOR_COL} IN ('{factor_list}')")
    
    if injury_types and SEVERITY_CAT_COL:
        safe_injuries = [i.replace("'", "''") for i in injury_types]
        injury_list = "', '".join(safe_injuries)
        clauses.append(f"{SEVERITY_CAT_COL} IN ('{injury_list}')")
    
    if severity_min and SEVERITY_COL:
        clauses.append(f"{SEVERITY_COL} >= {severity_min}")
    
    return " WHERE " + " AND ".join(clauses) if clauses else ""

def get_stats(where_clause):
    """Get KPI statistics"""
    inj_part = f"SUM({INJURED_COL})" if INJURED_COL else "0"
    kill_part = f"SUM({KILLED_COL})" if KILLED_COL else "0"
    
    if VEHICLES_COL:
        veh_part = f"SUM({VEHICLES_COL})"
    elif VEHICLE_TYPE_COL:
        veh_part = f"COUNT({VEHICLE_TYPE_COL})"
    else:
        veh_part = "0"
    
    query = f"""
        SELECT 
            COUNT(*) as crashes,
            {inj_part} as injuries,
            {kill_part} as deaths,
            {veh_part} as vehicles
        FROM crashes
        {where_clause}
    """
    df_stats = query_db(query)
    
    if df_stats is None or df_stats.empty:
        return 0, 0, 0, 0
    
    return (
        df_stats['crashes'][0],
        df_stats['injuries'][0] or 0,
        df_stats['deaths'][0] or 0,
        df_stats['vehicles'][0] or 0
    )

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">🚗 NYC Motor Vehicle Collisions</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data Engineering & Visualization Dashboard (Powered by DuckDB)</p>', unsafe_allow_html=True)
    
    # Check if data exists (either local or Google Drive)
    con = get_db_connection()
    if not con:
        st.error("⚠️ Unable to connect to data source!")
        st.info("""
        Data loading failed. Please check:
        1. Local file: data/processed/dashboard_data.parquet
        2. Google Drive: Data file should be accessible
        """)
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range
    min_date, max_date = get_date_range()
    start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
    
    # Year filter
    year_options = get_year_options()
    selected_years = st.sidebar.multiselect("Year", options=year_options, default=[])
    
    # Borough filter
    borough_options = get_dropdown_options(BOROUGH_COL)
    selected_boroughs = st.sidebar.multiselect("Boroughs", options=borough_options, default=[])
    
    # Vehicle Type filter
    vehicle_options = get_vehicle_options()
    selected_vehicles = st.sidebar.multiselect("Vehicle Type", options=vehicle_options, default=[])
    
    # Contributing Factor filter
    factor_options = get_dropdown_options(FACTOR_COL, limit=50)
    selected_factors = st.sidebar.multiselect("Contributing Factor", options=factor_options, default=[])
    
    # Injury Type filter
    injury_options = get_dropdown_options(SEVERITY_CAT_COL)
    selected_injuries = st.sidebar.multiselect("Injury Type", options=injury_options, default=[])
    
    # Severity slider
    severity_min = st.sidebar.slider("Minimum Casualties", min_value=0, max_value=10, value=0)
    
    # Reset button
    if st.sidebar.button("🔄 Reset Filters"):
        st.rerun()
    
    # Build filter clause
    where_clause = build_filter_clause(
        start_date, end_date, 
        selected_boroughs, selected_years, 
        selected_vehicles, selected_factors, 
        selected_injuries, severity_min
    )
    
    # Get stats
    total_crashes, total_injuries, total_deaths, total_vehicles = get_stats(where_clause)
    
    # Display KPI metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Collisions",
            value=f"{total_crashes:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Injuries",
            value=f"{int(total_injuries):,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Deaths",
            value=f"{int(total_deaths):,}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Vehicles Involved (Est.)",
            value=f"{int(total_vehicles):,}",
            delta=None
        )
    
    st.divider()
    
    # Time series chart
    st.subheader("📈 Collisions Over Time")
    if DATE_COL:
        query = f"""
            SELECT {DATE_COL} as date, COUNT(*) as count 
            FROM crashes 
            {where_clause}
            GROUP BY 1 ORDER BY 1
        """
        df_time = query_db(query)
        if df_time is not None and not df_time.empty:
            fig_time = px.line(
                df_time, x='date', y='count',
                labels={'date': 'Date', 'count': 'Number of Collisions'}
            )
            fig_time.update_traces(line_color='#0d6efd')
            fig_time.update_layout(hovermode='x unified', height=400)
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No data available for the selected filters")
    
    # Borough and Hourly charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏙️ By Borough")
        if BOROUGH_COL:
            query = f"""
                SELECT {BOROUGH_COL} as borough, COUNT(*) as count 
                FROM crashes 
                {where_clause}
                GROUP BY 1 ORDER BY 2 DESC
            """
            df_borough = query_db(query)
            if df_borough is not None and not df_borough.empty:
                fig_borough = px.bar(
                    df_borough, x='borough', y='count',
                    labels={'borough': 'Borough', 'count': 'Collisions'},
                    color='count', color_continuous_scale='Blues'
                )
                fig_borough.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_borough, use_container_width=True)
            else:
                st.info("No data available")
    
    with col2:
        st.subheader("🕐 By Hour of Day")
        if HOUR_COL:
            query = f"""
                SELECT {HOUR_COL} as hour, COUNT(*) as count 
                FROM crashes 
                {where_clause}
                GROUP BY 1 ORDER BY 1
            """
            df_hourly = query_db(query)
            if df_hourly is not None and not df_hourly.empty:
                fig_hourly = px.bar(
                    df_hourly, x='hour', y='count',
                    labels={'hour': 'Hour of Day', 'count': 'Collisions'},
                    color='count', color_continuous_scale='Oranges'
                )
                fig_hourly.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_hourly, use_container_width=True)
            else:
                st.info("No data available")
    
    # Severity and Factors charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Severity Distribution")
        if SEVERITY_CAT_COL:
            query = f"""
                SELECT {SEVERITY_CAT_COL} as category, COUNT(*) as count 
                FROM crashes 
                {where_clause}
                GROUP BY 1 ORDER BY 2 DESC
            """
            df_severity = query_db(query)
            if df_severity is not None and not df_severity.empty:
                fig_severity = px.pie(
                    df_severity, names='category', values='count',
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig_severity.update_layout(height=400)
                st.plotly_chart(fig_severity, use_container_width=True)
            else:
                st.info("No data available")
    
    with col2:
        st.subheader("🚦 Contributing Factors")
        if FACTOR_COL:
            query = f"""
                SELECT {FACTOR_COL} as factor, COUNT(*) as count 
                FROM crashes 
                {where_clause} AND {FACTOR_COL} != 'Unspecified'
                GROUP BY 1 ORDER BY 2 DESC
                LIMIT 10
            """
            df_factors = query_db(query)
            if df_factors is not None and not df_factors.empty:
                fig_factors = px.bar(
                    df_factors, y='factor', x='count',
                    labels={'factor': 'Contributing Factor', 'count': 'Count'},
                    orientation='h',
                    color='count', color_continuous_scale='Reds'
                )
                fig_factors.update_layout(
                    showlegend=False, 
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig_factors, use_container_width=True)
            else:
                st.info("No data available")
    
    # Footer
    st.divider()
    st.markdown("""
    <p style='text-align: center; color: #6c757d;'>
        Data Source: <a href='https://data.cityofnewyork.us/' target='_blank'>NYC Open Data</a> | 
        Built with Streamlit & Plotly | Powered by DuckDB
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
