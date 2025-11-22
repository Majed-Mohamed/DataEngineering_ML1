# NYC Motor Vehicle Collisions Analysis

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)

## ��� Project Overview

Complete data engineering pipeline for analyzing NYC Motor Vehicle Collisions using data from [NYC Open Data](https://data.cityofnewyork.us/). This project demonstrates the full workflow from data ingestion to interactive dashboard deployment.

### Key Features
- ✅ **API-based Data Fetching**: Automated data retrieval from NYC Open Data
- ✅ **Comprehensive Pipeline**: Load → Clean → Integrate → Engineer → Visualize
- ✅ **Interactive Dashboard**: Streamlit with query language interface
- ✅ **Person-Level Filtering**: Logical consistency across all analyses
- ✅ **Query Language**: Precise filtering with key:value syntax
- ✅ **DuckDB Integration**: Efficient SQL queries with view-based architecture

### Project Workflow
1. **Data Ingestion**: Fetch from NYC Open Data API
2. **Exploratory Analysis**: Understand data quality and patterns
3. **Data Cleaning**: Clean crashes, persons, and vehicles datasets
4. **Dataset Integration**: Merge on COLLISION_ID
5. **Post-Integration Cleaning**: Ensure consistency
6. **Feature Engineering**: Create analytical features
7. **Dashboard**: Interactive visualizations with Streamlit

---

## ��� Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone repository
git clone https://github.com/Majed-Mohamed/DataEngineering_ML1.git
cd DataEngineering_ML1

# Install dependencies
pip install -r requirements.txt
```

### Run Dashboard

```bash
# Windows
run_streamlit.bat

# Manual
streamlit run streamlit_app/app.py
```

Visit: http://localhost:8501

---

## ��� Project Structure

```
DataEngineering_ML1/
│
├── src/                          # Reusable Python modules
│   ├── config.py                 # Configuration
│   ├── utils.py                  # Utility functions
│   └── __init__.py
│
├── notebooks/                    # Jupyter notebooks
│   ├── 01_load_and_eda.ipynb
│   ├── 02_clean_crashes.ipynb
│   ├── 03_clean_persons.ipynb
│   ├── 04_integrate_datasets.ipynb
│   ├── 05_post_integration_cleaning.ipynb
│   ├── 06_feature_engineering.ipynb
│   └── 07_final_visual_analysis.ipynb
│
├── streamlit_app/               # Dashboard
│   ├── app.py                   # Main application
│   └── README.md
│
├── data/                        # Data storage
│   ├── processed/              # Processed data (dashboard_data.parquet)
│   ├── cache/                  # Temporary cache
│   └── temp/                   # Temporary files
│
├── docs/                        # Documentation
│   └── REQUIREMENTS_COMPLIANCE.md
│
├── deployment/                  # Deployment files
│
├── requirements.txt             # Python dependencies
└── run_streamlit.bat           # Windows launcher
```

---

## ��� Data Sources

Data fetched from NYC Open Data via API:

- **[Motor Vehicle Collisions - Crashes](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)**
- **[Motor Vehicle Collisions - Person](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu)**
- **[Motor Vehicle Collisions - Vehicles](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4)**

---

## ��� Dashboard Features

### Query Language
Use key:value syntax for precise filtering:
- `borough:Brooklyn year:2020`
- `year:2020-2023 injury:killed`
- `borough:Manhattan,Bronx injury:injured`

### Visualizations
- Time series analysis
- Borough distribution
- Hourly patterns
- Injury breakdown
- Contributing factors

### KPI Metrics
- Total collisions
- Total injuries
- Total deaths
- Person records

---

## ��� Development Workflow

### 1. Run Data Pipeline
Execute notebooks 01-07 in sequence to generate `dashboard_data.parquet`

### 2. Develop Dashboard
Edit `streamlit_app/app.py`

### 3. Test Locally
```bash
streamlit run streamlit_app/app.py
```

---

## ��� License

MIT License

---

## ��� Contact

Repository: [Majed-Mohamed/DataEngineering_ML1](https://github.com/Majed-Mohamed/DataEngineering_ML1)

---

## ��� Project Status

**Current Phase:** ✅ Complete - Dashboard operational with person-level filtering
