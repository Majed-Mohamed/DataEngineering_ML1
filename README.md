# NYC Motor Vehicle Collisions Analysis

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/dash-2.14+-green.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📊 Project Overview

Complete data engineering pipeline for analyzing NYC Motor Vehicle Collisions using data from [NYC Open Data](https://data.cityofnewyork.us/). This project demonstrates the full data engineering workflow from API-based data ingestion to interactive dashboard deployment.

### Key Features
- ✅ **API-based Data Fetching** - No manual downloads required
- ✅ **Comprehensive Data Pipeline** - Load → Clean → Integrate → Engineer → Visualize
- ✅ **Modular Architecture** - Reusable Python modules in `src/`
- ✅ **Interactive Dashboard** - Built with Dash/Plotly
- ✅ **Production Ready** - Configured for Render deployment

### Project Workflow
1. **Data Ingestion** - Fetch from NYC Open Data API
2. **Exploratory Data Analysis** - Understand data quality and patterns
3. **Pre-Integration Cleaning** - Clean individual datasets
4. **Dataset Integration** - Merge on COLLISION_ID
5. **Post-Integration Cleaning** - Ensure consistency
6. **Feature Engineering** - Create analytical features
7. **Dashboard Development** - Interactive visualizations
8. **Deployment** - Public web application

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/Majed-Mohamed/DataEngineering_ML1.git
cd DataEngineering_ML1

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template (optional)
cp .env.example .env
```

### Run Data Pipeline

```bash
# Execute complete pipeline
python run_pipeline.py
```

### Run Dashboard Locally

```bash
# Start Dash application
python app/dash_app.py
```

Visit: http://localhost:8050

---

## 📁 Project Structure

```
DATAENGINEERING_ML1/
│
├── src/                          # Reusable Python modules
│   ├── config.py                 # Centralized configuration
│   ├── data_loader.py            # API data fetching
│   ├── data_cleaning.py          # Cleaning functions
│   ├── data_integration.py       # Dataset merging
│   └── feature_engineering.py    # Feature creation
│
├── notebooks/                    # Jupyter analysis notebooks
│   ├── 01_load_and_eda.ipynb
│   ├── 02_clean_crashes.ipynb
│   ├── 03_clean_persons.ipynb
│   ├── 04_integrate_datasets.ipynb
│   ├── 05_post_integration_cleaning.ipynb
│   ├── 06_feature_engineering.ipynb
│   └── 07_final_visual_analysis.ipynb
│
├── app/                          # Dash dashboard
│   ├── dash_app.py              # Main application
│   ├── components/              # UI components
│   │   ├── filters.py
│   │   ├── graphs.py
│   │   ├── layouts.py
│   │   └── callbacks.py
│   └── assets/                  # Static files
│       └── styles.css
│
├── data/                         # Data storage
│   ├── processed/               # Cleaned data
│   └── cache/                   # Temporary cache
│
├── deployment/                   # Deployment configs
│   ├── Procfile
│   ├── runtime.txt
│   └── render.yaml
│
├── tests/                        # Unit tests
│
└── run_pipeline.py              # Main pipeline script
```

---

## 📚 Data Sources

All data is fetched from NYC Open Data via API:

- **[Motor Vehicle Collisions - Crashes](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)**
- **[Motor Vehicle Collisions - Person](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu)**
- **[Motor Vehicle Collisions - Vehicles](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4)**

---

## 🔧 Development Workflow

### 1. Data Pipeline (Notebooks)

Work through notebooks sequentially (01 → 07)

### 2. Implement Core Functions

Edit modules in `src/` directory

### 3. Build Dashboard

Develop components in `app/components/`

### 4. Test Locally

```bash
pytest tests/
python app/dash_app.py
```

---

## 🚢 Deployment to Render

1. Push to GitHub
2. Connect repository to Render
3. Render auto-deploys on push to main

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

---

## 📊 Dashboard Features

- Interactive filters (date, borough, severity, vehicle type)
- Time series analysis
- Geographic heatmaps
- Borough comparisons
- Contributing factors analysis
- Key metrics and KPIs

---

## 📝 License

MIT License

---

## 📧 Contact

- Repository: [Majed-Mohamed/DataEngineering_ML1](https://github.com/Majed-Mohamed/DataEngineering_ML1)

---

## 📌 Project Status

**Current Phase:** ✅ Project Structure Setup Complete

**Next Steps:**
1. Implement data loading functions
2. Develop cleaning logic
3. Build integration pipeline
4. Create feature engineering
5. Design dashboard components
6. Deploy to production