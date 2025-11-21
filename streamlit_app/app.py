"""
NYC Motor Vehicle Collisions Dashboard
Streamlit application with DuckDB optimization, search bar, and Generate Report button
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import duckdb
from pathlib import Path
from datetime import datetime
import sys
import tempfile
import os

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
.main-header {font-size: 2.5rem; font-weight: bold; color: #0d6efd; margin-bottom:0.5rem;}
.sub-header {font-size:1rem; color:#6c757d; margin-bottom:2rem;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA CONNECTION
# ============================================================================

DATA_PATH = PROCESSED_DATA_DIR / "dashboard_data.parquet"
DRIVE_FILE_ID = "1qwjegnIt8eX1PQQmjRRDNK_GYGtX9hSp"

@st.cache_resource
def download_data_from_drive():
    if DATA_PATH.exists():
        return str(DATA_PATH)
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, "dashboard_data.parquet")
    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 1000000:
        return temp_file
    with st.spinner('📥 Downloading data from Google Drive...'):
        import gdown
        url = f'https://drive.google.com/uc?id={DRIVE_FILE_ID}'
        gdown.download(url, temp_file, quiet=True)
    return temp_file

@st.cache_resource
def get_db_connection():
    data_source = download_data_from_drive()
    if not data_source:
        return None
    con = duckdb.connect(database=':memory:')
    con.execute(f"CREATE OR REPLACE VIEW crashes AS SELECT * FROM '{data_source}'")
    return con

@st.cache_data(ttl=300)
def query_db(query):
    con = get_db_connection()
    if not con:
        return pd.DataFrame()
    return con.execute(query).df()

def get_column_name(candidates):
    con = get_db_connection()
    if not con:
        return None
    cols = [c[0] for c in con.execute("DESCRIBE crashes").fetchall()]
    for cand in candidates:
        if cand in cols:
            return f'"{cand}"'
    return None

# ============================================================================
# IDENTIFY KEY COLUMNS
# ============================================================================

DATE_COL = get_column_name(['CRASH DATE', 'CRASH_DATE', 'crash_date'])
BOROUGH_COL = get_column_name(['BOROUGH', 'borough_clean'])
SEVERITY_COL = get_column_name(['total_casualties', 'TOTAL_CASUALTIES'])
HOUR_COL = get_column_name(['crash_hour', 'CRASH_HOUR'])
FACTOR_COL = get_column_name(['CONTRIBUTING FACTOR VEHICLE 1', 'contributing_factor_vehicle_1'])
VEHICLE_TYPE_COL = get_column_name(['VEHICLE TYPE CODE 1', 'vehicle_type_code_1'])
SEVERITY_CAT_COL = get_column_name(['severity_category', 'SEVERITY_CATEGORY'])
INJURED_COL = get_column_name(['total_injured', 'NUMBER OF PERSONS INJURED', 'NUMBER_OF_PERSONS_INJURED'])
KILLED_COL = get_column_name(['total_killed', 'NUMBER OF PERSONS KILLED', 'NUMBER_OF_PERSONS_KILLED'])
VEHICLES_COL = get_column_name(['num_vehicles', 'number_of_vehicles'])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_dropdown_options(column, limit=None):
    if not column:
        return []
    limit_clause = f"LIMIT {limit}" if limit else ""
    df = query_db(f"SELECT DISTINCT {column} as val FROM crashes WHERE {column} IS NOT NULL ORDER BY 1 {limit_clause}")
    return df['val'].tolist() if not df.empty else []

def build_filter_clause(start_date, end_date, boroughs, years, vehicle_types, factors, injury_types, severity_min, search_text):
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
        type_list = "', '".join([t.replace("'", "''") for t in vehicle_types])
        clauses.append(f"{VEHICLE_TYPE_COL} IN ('{type_list}')")
    if factors and FACTOR_COL:
        factor_list = "', '".join([f.replace("'", "''") for f in factors])
        clauses.append(f"{FACTOR_COL} IN ('{factor_list}')")
    if injury_types and SEVERITY_CAT_COL:
        injury_list = "', '".join([i.replace("'", "''") for i in injury_types])
        clauses.append(f"{SEVERITY_CAT_COL} IN ('{injury_list}')")
    if severity_min and SEVERITY_COL:
        clauses.append(f"{SEVERITY_COL} >= {severity_min}")
    if search_text and DATE_COL:
        search_text_safe = search_text.replace("'", "''")
        clauses.append(f"{FACTOR_COL} LIKE '%{search_text_safe}%' OR {VEHICLE_TYPE_COL} LIKE '%{search_text_safe}%'")
    return " WHERE " + " AND ".join(clauses) if clauses else ""

def get_stats(where_clause):
    inj_part = f"SUM({INJURED_COL})" if INJURED_COL else "0"
    kill_part = f"SUM({KILLED_COL})" if KILLED_COL else "0"
    veh_part = f"SUM({VEHICLES_COL})" if VEHICLES_COL else (f"COUNT({VEHICLE_TYPE_COL})" if VEHICLE_TYPE_COL else "0")
    query = f"SELECT COUNT(*) as crashes, {inj_part} as injuries, {kill_part} as deaths, {veh_part} as vehicles FROM crashes {where_clause}"
    df = query_db(query)
    if df.empty:
        return 0,0,0,0
    return df['crashes'][0], df['injuries'][0] or 0, df['deaths'][0] or 0, df['vehicles'][0] or 0

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    st.markdown('<h1 class="main-header">🚗 NYC Motor Vehicle Collisions</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data Engineering & Visualization Dashboard (DuckDB + Streamlit)</p>', unsafe_allow_html=True)

    if not get_db_connection():
        st.error("⚠️ Unable to connect to data source!")
        return

    # -------------------------
    # SIDEBAR FILTERS
    # -------------------------
    st.sidebar.header("🔍 Filters & Search")
    min_date, max_date = datetime(2020,1,1), datetime(2024,12,31)
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    selected_years = st.sidebar.multiselect("Year", options=get_dropdown_options(DATE_COL))
    selected_boroughs = st.sidebar.multiselect("Boroughs", options=get_dropdown_options(BOROUGH_COL))
    selected_vehicles = st.sidebar.multiselect("Vehicle Type", options=get_dropdown_options(VEHICLE_TYPE_COL))
    selected_factors = st.sidebar.multiselect("Contributing Factor", options=get_dropdown_options(FACTOR_COL, limit=50))
    selected_injuries = st.sidebar.multiselect("Injury Type", options=get_dropdown_options(SEVERITY_CAT_COL))
    severity_min = st.sidebar.slider("Minimum Casualties", 0, 10, 0)
    search_text = st.sidebar.text_input("Search Vehicle or Factor")

    # -------------------------
    # GENERATE REPORT BUTTON
    # -------------------------
    if st.sidebar.button("📄 Generate Report"):
        where_clause = build_filter_clause(start_date, end_date, selected_boroughs, selected_years,
                                           selected_vehicles, selected_factors, selected_injuries,
                                           severity_min, search_text)

        # KPI Metrics
        crashes, injuries, deaths, vehicles = get_stats(where_clause)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Collisions", f"{crashes:,}")
        col2.metric("Total Injuries", f"{int(injuries):,}")
        col3.metric("Total Deaths", f"{int(deaths):,}")
        col4.metric("Vehicles Involved", f"{int(vehicles):,}")

        # Time Series
        if DATE_COL:
            df_time = query_db(f"SELECT {DATE_COL} as date, COUNT(*) as count FROM crashes {where_clause} GROUP BY 1 ORDER BY 1")
            if not df_time.empty:
                fig_time = px.line(df_time, x='date', y='count', labels={'date':'Date','count':'Collisions'})
                st.plotly_chart(fig_time, use_container_width=True)

if __name__ == "__main__":
    main()
