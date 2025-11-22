"""
NYC Motor Vehicle Collisions Dashboard
View-based architecture with person-level filtering for logical consistency
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
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import APP_TITLE, PROCESSED_DATA_DIR

# Page Config

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS

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
</style>
""", unsafe_allow_html=True)

# Data Connection

DRIVE_FILE_ID = os.getenv('DRIVE_FILE_ID', '1qwjegnIt8eX1PQQmjRRDNK_GYGtX9hSp')
DATA_PATH = PROCESSED_DATA_DIR / "dashboard_data.parquet"

@st.cache_resource
def download_data_from_drive():
    """Download data from Google Drive if local file doesn't exist"""
    if DATA_PATH.exists():
        return str(DATA_PATH)
    
    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "dashboard_data.parquet")
        
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 1000000:
            return temp_file
        
        with st.spinner('📥 Downloading data from Google Drive...'):
            try:
                import gdown
                url = f'https://drive.google.com/uc?id={DRIVE_FILE_ID}'
                gdown.download(url, temp_file, quiet=True)
            except ImportError:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "gdown"])
                import gdown
                url = f'https://drive.google.com/uc?id={DRIVE_FILE_ID}'
                gdown.download(url, temp_file, quiet=True)
        
        return temp_file
    except Exception as e:
        st.error(f"❌ Error downloading data: {e}")
        return None

@st.cache_resource
def get_db_connection():
    """Create DuckDB connection with crash-level and person-level views"""
    data_source = download_data_from_drive()
    if not data_source:
        return None
    
    con = duckdb.connect(database=':memory:')
    
    try:
        # Create base raw view
        con.execute(f"CREATE OR REPLACE VIEW crashes_raw AS SELECT * FROM read_parquet('{data_source}')")
        
        # ✅ CRASH-LEVEL VIEW (one row per crash with aggregated person data)
        con.execute("""
            CREATE OR REPLACE VIEW crashes_aggregated AS
            SELECT 
                COLLISION_ID,
                "CRASH DATE" as crash_date,
                borough_clean,
                crash_hour,
                "CONTRIBUTING FACTOR VEHICLE 1" as contributing_factor,
                "VEHICLE TYPE CODE 1" as vehicle_1,
                -- Aggregate person-level data
                COUNT(*) as total_persons,
                SUM(CASE WHEN PERSON_INJURY = 'Injured' THEN 1 ELSE 0 END) as injured_count,
                SUM(CASE WHEN PERSON_INJURY = 'Killed' THEN 1 ELSE 0 END) as killed_count,
                SUM(CASE WHEN PERSON_INJURY = 'Unspecified' THEN 1 ELSE 0 END) as unspecified_count,
                -- Flags for crash-level filtering
                MAX(CASE WHEN PERSON_INJURY = 'Killed' THEN 1 ELSE 0 END) as has_fatality,
                MAX(CASE WHEN PERSON_INJURY = 'Injured' THEN 1 ELSE 0 END) as has_injury
            FROM crashes_raw
            GROUP BY 
                COLLISION_ID, "CRASH DATE", borough_clean, crash_hour,
                "CONTRIBUTING FACTOR VEHICLE 1",
                "VEHICLE TYPE CODE 1"
        """)
        
        # ✅ PERSON-LEVEL VIEW (for person-specific analysis)
        con.execute("""
            CREATE OR REPLACE VIEW persons AS
            SELECT 
                COLLISION_ID,
                "CRASH DATE" as crash_date,
                borough_clean,
                crash_hour,
                "CONTRIBUTING FACTOR VEHICLE 1" as contributing_factor,
                "VEHICLE TYPE CODE 1" as vehicle_1,
                PERSON_INJURY as injury_status,
                PERSON_TYPE as person_type
            FROM crashes_raw
        """)
        
        return con
        
    except Exception as e:
        st.error(f"❌ Error creating views: {e}")
        return None

@st.cache_data(ttl=300)
def query_db(query):
    """Execute a query and return pandas DataFrame"""
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

# Filter Builder

def escape_list(values):
    """Escape SQL string list safely"""
    return ", ".join([f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" for v in values])

def build_filter(start_date, end_date, boroughs, years, vehicles, factors, injury_filter):
    """Build WHERE clause with person-level filtering"""
    where = []
    
    # Date range
    if start_date and end_date:
        where.append(f"crash_date BETWEEN DATE '{start_date}' AND DATE '{end_date}'")
    
    # Boroughs
    if boroughs:
        where.append(f"borough_clean IN ({escape_list(boroughs)})")
    
    # Years
    if years:
        year_list = ", ".join(map(str, years))
        where.append(f"EXTRACT(YEAR FROM crash_date) IN ({year_list})")
    
    # Contributing factors
    if factors:
        where.append(f"contributing_factor IN ({escape_list(factors)})")
    
    # Vehicle types - check vehicle column (only vehicle_1 available)
    if vehicles:
        where.append(f"vehicle_1 IN ({escape_list(vehicles)})")
    
    if injury_filter:
        where.append(f"injury_status IN ({escape_list(injury_filter)})")
    
    return " AND ".join(where) if where else "1=1"

# KPI Queries

def get_kpis(start_date, end_date, boroughs, years, vehicles, factors, injury_filter):
    """Get KPI statistics with person-level filtering"""
    where = build_filter(start_date, end_date, boroughs, years, vehicles, factors, injury_filter)
    
    query = f"""
        SELECT 
            COUNT(DISTINCT COLLISION_ID) as total_crashes,
            SUM(CASE WHEN injury_status = 'Injured' THEN 1 ELSE 0 END) as total_injured,
            SUM(CASE WHEN injury_status = 'Killed' THEN 1 ELSE 0 END) as total_killed,
            COUNT(*) as total_persons
        FROM persons
        WHERE {where}
    """
    
    df = query_db(query)
    if df is None or df.empty:
        return 0, 0, 0, 0
    
    return (
        int(df['total_crashes'][0] or 0),
        int(df['total_injured'][0] or 0),
        int(df['total_killed'][0] or 0),
        int(df['total_persons'][0] or 0)
    )

# Chart Queries

def get_time_series(start_date, end_date, boroughs, years, vehicles, factors, injury_filter):
    """Time series of crashes over time"""
    where = build_filter(start_date, end_date, boroughs, years, vehicles, factors, injury_filter)
    
    query = f"""
        SELECT 
            crash_date::DATE as date,
            COUNT(DISTINCT COLLISION_ID) as count
        FROM persons
        WHERE {where}
        GROUP BY crash_date
        ORDER BY crash_date
    """
    
    return query_db(query)

def get_borough_distribution(start_date, end_date, boroughs, years, vehicles, factors, injury_filter):
    """Crashes by borough"""
    where = build_filter(start_date, end_date, boroughs, years, vehicles, factors, injury_filter)
    
    query = f"""
        SELECT 
            borough_clean as borough,
            COUNT(DISTINCT COLLISION_ID) as count
        FROM persons
        WHERE {where}
        GROUP BY borough_clean
        ORDER BY count DESC
    """
    
    return query_db(query)

def get_hourly_distribution(start_date, end_date, boroughs, years, vehicles, factors, injury_filter):
    """Crashes by hour of day"""
    where = build_filter(start_date, end_date, boroughs, years, vehicles, factors, injury_filter)
    
    query = f"""
        SELECT 
            crash_hour as hour,
            COUNT(DISTINCT COLLISION_ID) as count
        FROM persons
        WHERE {where} AND crash_hour IS NOT NULL
        GROUP BY crash_hour
        ORDER BY crash_hour
    """
    
    return query_db(query)

def get_contributing_factors(start_date, end_date, boroughs, years, vehicles, factors, injury_filter, limit=10):
    """Top contributing factors"""
    where = build_filter(start_date, end_date, boroughs, years, vehicles, factors, injury_filter)
    
    query = f"""
        SELECT 
            contributing_factor as factor,
            COUNT(DISTINCT COLLISION_ID) as count
        FROM persons
        WHERE {where} 
          AND contributing_factor IS NOT NULL
          AND contributing_factor != 'Unspecified'
        GROUP BY contributing_factor
        ORDER BY count DESC
        LIMIT {limit}
    """
    
    return query_db(query)

def get_person_injury_distribution(start_date, end_date, boroughs, years, vehicles, factors, injury_filter):
    """Person-level injury distribution"""
    where = build_filter(start_date, end_date, boroughs, years, vehicles, factors, injury_filter)
    
    query = f"""
        SELECT 
            injury_status as category,
            COUNT(*) as count
        FROM persons
        WHERE {where}
        GROUP BY injury_status
        ORDER BY count DESC
    """
    
    return query_db(query)

# Helper Functions

@st.cache_data
def get_dropdown_options(column, view='persons', limit=None):
    """Get unique values for filter dropdowns"""
    limit_clause = f"LIMIT {limit}" if limit else ""
    
    query = f"""
        SELECT DISTINCT {column} as val
        FROM {view}
        WHERE {column} IS NOT NULL
          AND LENGTH({column}) >= 3
          AND {column} NOT IN ('Unspecified', 'UNKNOWN', 'N/A')
        ORDER BY val
        {limit_clause}
    """
    
    df = query_db(query)
    return df['val'].tolist() if df is not None and not df.empty else []

@st.cache_data
def get_vehicle_options():
    """Get valid vehicle types"""
    query = """
        SELECT vehicle_1 as val, COUNT(*) as total_count
        FROM persons 
        WHERE vehicle_1 IS NOT NULL
          AND vehicle_1 IN (
            'Sedan', 'Station Wagon/Sport Utility Vehicle', '4 Dr Sedan', 
            'Pick-Up Truck', 'Box Truck', 'Tractor Truck Diesel', 'Motorcycle',
            'Ambulance', 'Convertible', '2 Dr Sedan', 'Garbage Or Refuse',
            'Moped', 'E-Bike', 'Tractor Truck Gasoline', 'Tow Truck / Wrecker',
            'E-Scooter', 'Chassis Cab', 'Tanker', 'Motorscooter', 'Concrete Mixer',
            'Refrigerated Van', 'Motorbike', 'School Bus', '3-Door', 'Armored Truck',
            'Truck', 'Beverage Truck', 'Fire Truck', 'Stake Or Rack', 'Trailer',
            'Tow Truck', 'Passenger Vehicle', 'Snow Plow', 'Multi-Wheeled Vehicle',
            'Firetruck', 'Bulk Agriculture', 'Commercial', 'Van', 'Taxi',
            'Bus', 'Bicycle', 'Scooter', 'Limousine', 'Flat Bed', 'Carry All',
            'Flat Rack', 'Lift Boom'
          )
        GROUP BY vehicle_1
        ORDER BY total_count DESC
        LIMIT 50
    """
    
    df = query_db(query)
    return df['val'].tolist() if df is not None and not df.empty else []

@st.cache_data
def get_year_options():
    """Get unique years"""
    query = "SELECT DISTINCT EXTRACT(YEAR FROM crash_date) as val FROM persons WHERE crash_date IS NOT NULL ORDER BY val DESC"
    df = query_db(query)
    if df is not None and not df.empty:
        # Filter out null values and convert to int
        return [int(v) for v in df['val'].tolist() if pd.notna(v)]
    return []

@st.cache_data
def get_date_range():
    """Get min and max dates"""
    query = "SELECT MIN(crash_date) as min_d, MAX(crash_date) as max_d FROM persons"
    df = query_db(query)
    if df is None or df.empty:
        return datetime(2020, 1, 1).date(), datetime(2024, 12, 31).date()
    return df['min_d'][0], df['max_d'][0]

# Query Parser

def parse_search_query(query):
    """Parse query language (key:value) into filter components"""
    if not query:
        return None, None, None, None, None
    
    found_boroughs = []
    extracted_years = []
    found_injuries = []
    found_vehicles = []
    found_factors = []
    
    pattern = r'(\w+):([^\s]+)'
    matches = re.findall(pattern, query)
    
    borough_map = {
        'manhattan': 'Manhattan', 'bronx': 'Bronx', 'brooklyn': 'Brooklyn',
        'queens': 'Queens', 'staten': 'Staten Island', 'statenisland': 'Staten Island'
    }
    
    injury_map = {
        'killed': 'Killed', 'fatal': 'Killed', 'death': 'Killed',
        'injured': 'Injured', 'injury': 'Injured',
        'unspecified': 'Unspecified'
    }
    
    for key, value in matches:
        key_lower = key.lower()
        value_lower = value.lower()
        
        if key_lower in ['borough', 'b', 'loc', 'location']:
            values = value_lower.split(',')
            for v in values:
                v = v.strip()
                if v in borough_map:
                    found_boroughs.append(borough_map[v])
        
        elif key_lower in ['year', 'y', 'yr']:
            if '-' in value and value.count('-') == 1:
                start, end = value.split('-')
                try:
                    extracted_years = list(range(int(start), int(end) + 1))
                except ValueError:
                    pass
            else:
                years = value.split(',')
                for y in years:
                    try:
                        extracted_years.append(int(y.strip()))
                    except ValueError:
                        pass
        
        elif key_lower in ['injury', 'i', 'status', 's']:
            values = value_lower.split(',')
            for v in values:
                v = v.strip()
                if v in injury_map:
                    found_injuries.append(injury_map[v])
        
        elif key_lower in ['vehicle', 'v', 'type']:
            values = value.split(',')
            found_vehicles.extend([v.strip() for v in values])
        
        elif key_lower in ['factor', 'f', 'cause']:
            values = value.split(',')
            found_factors.extend([v.strip() for v in values])
    
    found_boroughs = list(dict.fromkeys(found_boroughs))
    extracted_years = list(dict.fromkeys(extracted_years))
    found_injuries = list(dict.fromkeys(found_injuries))
    found_vehicles = list(dict.fromkeys(found_vehicles))
    found_factors = list(dict.fromkeys(found_factors))
    
    return found_boroughs, extracted_years, found_injuries, found_vehicles, found_factors

# Main Application

def main():
    # Header
    st.markdown('<h1 class="main-header">🚗 NYC Motor Vehicle Collisions</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Data Engineering & Visualization Dashboard | Query Language Interface</p>', unsafe_allow_html=True)
    
    # Check connection
    con = get_db_connection()
    if not con:
        st.error("⚠️ Unable to connect to data source!")
        return
    
    # Initialize session state
    if "run_report" not in st.session_state:
        st.session_state.run_report = False
    if "reset_flag" not in st.session_state:
        st.session_state.reset_flag = False

    def trigger_report():
        st.session_state.run_report = True
    
    def trigger_reset():
        st.session_state.run_report = False
        st.session_state.reset_flag = True
    
    st.sidebar.header("🔍 Filters")
    
    st.sidebar.markdown("### 🔎 Query Search")
    
    default_search = "" if st.session_state.reset_flag else st.session_state.get("search_input", "")
    if st.session_state.reset_flag:
        st.session_state.reset_flag = False
    
    search_query = st.sidebar.text_input(
        "Query Language", 
        value=default_search,
        placeholder="borough:Brooklyn year:2020 injury:killed",
        key="search_input",
        help="Syntax: key:value (e.g., borough:Brooklyn year:2020 injury:killed)"
    )
    
    with st.sidebar.expander("📜 Query Syntax Guide"):
        st.markdown("""
        **Format:** `key:value`
        
        **Keys:**
        - `borough:` or `b:` → Manhattan, Brooklyn, Queens, Bronx, Staten
        - `year:` or `y:` → 2020, 2020-2023, 2020,2021,2022
        - `injury:` or `i:` → killed, injured, unspecified
        - `vehicle:` or `v:` → Sedan, Motorcycle, etc.
        - `factor:` or `f:` → Contributing factor
        
        **Examples:**
        ```
        borough:Brooklyn year:2020
        year:2020-2023 injury:killed
        b:Manhattan,Bronx y:2022 i:injured
        ```
        """)
    
    search_boroughs, search_years, search_injuries, search_vehicles, search_factors = parse_search_query(search_query)
    
    if search_query and any([search_boroughs, search_years, search_injuries, search_vehicles, search_factors]):
        with st.sidebar.expander("✅ Parsed Filters", expanded=True):
            if search_boroughs:
                st.success(f"📍 Boroughs: {', '.join(search_boroughs)}")
            if search_years:
                st.success(f"📅 Years: {', '.join(map(str, search_years))}")
            if search_injuries:
                st.success(f"⚠️ Injury: {', '.join(search_injuries)}")
            if search_vehicles:
                st.success(f"🚗 Vehicles: {', '.join(search_vehicles)}")
            if search_factors:
                st.success(f"🚦 Factors: {', '.join(search_factors)}")
    elif search_query:
        st.sidebar.warning("⚠️ No valid filters parsed. Check syntax.")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Manual Filters")
    
    min_date, max_date = get_date_range()
    start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)
    
    year_options = get_year_options()
    selected_years = st.sidebar.multiselect("Year", options=year_options, default=[])
    
    borough_options = get_dropdown_options('borough_clean')
    selected_boroughs = st.sidebar.multiselect("Boroughs", options=borough_options, default=[])
    
    vehicle_options = get_vehicle_options()
    selected_vehicles = st.sidebar.multiselect("Vehicle Type", options=vehicle_options, default=[])
    
    factor_options = get_dropdown_options('contributing_factor', limit=50)
    selected_factors = st.sidebar.multiselect("Contributing Factor", options=factor_options, default=[])
    
    injury_options = ['Killed', 'Injured', 'Unspecified']
    selected_injuries = st.sidebar.multiselect(
        "Person Injury Status", 
        options=injury_options,
        default=[],
        help="Filter by person injury status"
    )
    
    st.sidebar.markdown("---")
    col_btn1, col_btn2 = st.sidebar.columns(2)
    with col_btn1:
        st.button("📊 Generate Report", on_click=trigger_report, type="primary", use_container_width=True)
    with col_btn2:
        st.button("🔄 Reset", on_click=trigger_reset, use_container_width=True)
    
    if st.session_state.run_report:
        final_boroughs = list(set((selected_boroughs or []) + (search_boroughs or [])))
        final_years = list(set((selected_years or []) + (search_years or [])))
        final_vehicles = list(set((selected_vehicles or []) + (search_vehicles or [])))
        final_factors = list(set((selected_factors or []) + (search_factors or [])))
        final_injuries = list(set((selected_injuries or []) + (search_injuries or [])))
        
        total_crashes, total_injured, total_killed, total_persons = get_kpis(
            start_date, end_date, final_boroughs, final_years, 
            final_vehicles, final_factors, final_injuries
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Crashes",
                value=f"{total_crashes:,}",
                help="Number of unique crashes matching filters"
            )
        
        with col2:
            st.metric(
                label="Total Injuries",
                value=f"{total_injured:,}",
                help="Total persons injured in matching crashes"
            )
        
        with col3:
            st.metric(
                label="Total Deaths",
                value=f"{total_killed:,}",
                help="Total persons killed in matching crashes"
            )
        
        with col4:
            st.metric(
                label="Person Records",
                value=f"{total_persons:,}",
                help="Total persons involved in matching crashes"
            )
        
        st.divider()
        
        st.subheader("📈 Crashes Over Time")
        df_time = get_time_series(start_date, end_date, final_boroughs, final_years, final_vehicles, final_factors, final_injuries)
        
        if df_time is not None and not df_time.empty:
            fig_time = px.line(
                df_time, x='date', y='count',
                labels={'date': 'Date', 'count': 'Number of Crashes'},
                title=f"Daily Crash Count (Total: {df_time['count'].sum():,} crashes)"
            )
            fig_time.update_traces(line_color='#0d6efd')
            fig_time.update_layout(hovermode='x unified', height=400)
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No data available for the selected filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏙️ Crashes by Borough")
            df_borough = get_borough_distribution(start_date, end_date, final_boroughs, final_years, final_vehicles, final_factors, final_injuries)
            
            if df_borough is not None and not df_borough.empty:
                fig_borough = px.bar(
                    df_borough, x='borough', y='count',
                    labels={'borough': 'Borough', 'count': 'Number of Crashes'},
                    color='count', color_continuous_scale='Blues'
                )
                fig_borough.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_borough, use_container_width=True)
            else:
                st.info("No data available")
        
        with col2:
            st.subheader("🕐 Crashes by Hour of Day")
            df_hourly = get_hourly_distribution(start_date, end_date, final_boroughs, final_years, final_vehicles, final_factors, final_injuries)
            
            if df_hourly is not None and not df_hourly.empty:
                fig_hourly = px.bar(
                    df_hourly, x='hour', y='count',
                    labels={'hour': 'Hour of Day', 'count': 'Number of Crashes'},
                    color='count', color_continuous_scale='Oranges'
                )
                fig_hourly.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_hourly, use_container_width=True)
            else:
                st.info("No data available")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⚠️ Person Injury Distribution")
            df_injury = get_person_injury_distribution(start_date, end_date, final_boroughs, final_years, final_vehicles, final_factors, final_injuries)
            
            if df_injury is not None and not df_injury.empty:
                color_map = {
                    'Killed': '#dc3545',
                    'Injured': '#fd7e14',
                    'Unspecified': '#6c757d'
                }
                fig_injury = px.pie(
                    df_injury, names='category', values='count',
                    color='category', color_discrete_map=color_map,
                    title="Person-Level Injury Status"
                )
                fig_injury.update_layout(height=400)
                st.plotly_chart(fig_injury, use_container_width=True)
                
                total_persons_chart = df_injury['count'].sum()
                st.caption(f"Total persons: {total_persons_chart:,}")
            else:
                st.info("No data available")
        
        with col2:
            st.subheader("🚦 Top Contributing Factors")
            df_factors = get_contributing_factors(start_date, end_date, final_boroughs, final_years, final_vehicles, final_factors, final_injuries)
            
            if df_factors is not None and not df_factors.empty:
                fig_factors = px.bar(
                    df_factors, y='factor', x='count',
                    labels={'factor': 'Contributing Factor', 'count': 'Number of Crashes'},
                    orientation='h', color='count', color_continuous_scale='Reds'
                )
                fig_factors.update_layout(
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    height=400
                )
                st.plotly_chart(fig_factors, use_container_width=True)
            else:
                st.info("No data available")
        
        st.divider()
        with st.expander("📊 Data Validation & Logic Explanation"):
            st.markdown("""
            ### 🔍 How Filtering Works:
            
            **Person-Level Filtering** (used consistently across ALL charts):
            - When you select "Killed" → Shows **ONLY killed persons** and their crashes
            - Injuries = 0 when filtering for "Killed" only
            - Deaths = Total Persons when filtering for "Killed" only
            - ✅ This ensures **100% LOGICAL CONSISTENCY**
            
            **Example:**
            - Filter: 2020 + Killed
            - Shows: Only persons who died
            - Total Crashes = Number of crashes with those killed persons
            - Total Injuries = 0 (since we filtered for killed only)
            - Total Deaths = Total Persons (all selected persons died)
            
            **Logical Consistency Checks:**
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                check1 = "✅" if total_crashes <= total_persons else "❌"
                st.text(f"{check1} Crashes ({total_crashes:,}) ≤ Persons ({total_persons:,})")
                
                check2 = "✅" if total_injured + total_killed <= total_persons else "❌"
                st.text(f"{check2} Injuries + Deaths ({total_injured + total_killed:,}) ≤ Persons")
            
            with col2:
                if total_crashes > 0:
                    avg = total_persons / total_crashes
                    st.text(f"📊 Avg persons per crash: {avg:.2f}")
                
                if df_time is not None and not df_time.empty:
                    time_sum = df_time['count'].sum()
                    match = "✅" if time_sum == total_crashes else "❌"
                    st.text(f"{match} Time series sum: {time_sum:,} = {total_crashes:,}")
    
    else:
        st.info("🎯 **Set your filters** in the sidebar and click **'📊 Generate Report'** to view analytics.")
        
        st.markdown("---")
        
        total_crashes_query = query_db("SELECT COUNT(DISTINCT COLLISION_ID) as cnt FROM persons")
        total_persons_query = query_db("SELECT COUNT(*) as cnt FROM persons")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if total_crashes_query is not None:
                st.metric("Total Crashes", f"{total_crashes_query['cnt'][0]:,}")
        
        with col2:
            if total_persons_query is not None:
                st.metric("Total Person Records", f"{int(total_persons_query['cnt'][0]):,}")
        
        with col3:
            date_range = query_db("SELECT MIN(crash_date) as min_d, MAX(crash_date) as max_d FROM persons")
            if date_range is not None:
                min_year = str(date_range['min_d'][0])[:4]
                max_year = str(date_range['max_d'][0])[:4]
                st.metric("Years Covered", f"{min_year} - {max_year}")
        
        with col4:
            boroughs = query_db("SELECT COUNT(DISTINCT borough_clean) as cnt FROM persons")
            if boroughs is not None:
                st.metric("NYC Boroughs", f"{boroughs['cnt'][0]}")
    
    st.divider()
    st.markdown("""
    <p style='text-align: center; color: #6c757d;'>
        Data Source: <a href='https://data.cityofnewyork.us/' target='_blank'>NYC Open Data</a> | 
        Built with Streamlit & DuckDB | 
        <strong>Person-Level Filtering</strong> - 100% Logical & Consistent ✅
    </p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
