# NYC Motor Vehicle Collisions – Data Engineering Project (ML1)

This project analyzes NYC motor vehicle collision data and builds an end-to-end
data engineering pipeline plus an interactive dashboard.

The work is based on the NYC Open Data collisions datasets (crashes and persons
tables). Our goal is to clean, integrate, and enrich the data so we can answer
a set of research questions about where, when, and why crashes occur in New York
City.

---

## Project Team

- Omar — data pipeline, feature engineering, dashboard filters & callbacks  
- Majed — project skeleton, configuration and deployment setup  
- Karam — data integration and joins between crashes and persons  
- Aisha — initial project structure and configuration files  
- Habiba — data cleaning and exploratory analysis  

Each team member also proposed at least two research questions that are
answered in the final analysis notebook and/or on the dashboard.

---

## Repository Structure

```text
DataEngineering_ML1/
├── app/                      # Dash web application
│   ├── assets/               # CSS styles
│   ├── components/           # Layouts, filters, graphs, callbacks
│   └── dash_app.py           # Dash entry point (server)
│
├── data/
│   ├── cache/                # Temporary data (ignored by git)
│   └── processed/            # Final processed parquet files (local only)
│       └── .gitkeep          # Placeholder so the folder exists in git
│
├── docs/                     # Project description / assignment PDF
│
├── notebooks/
│   └── data/
│       ├── 01_load_and_eda.ipynb
│       ├── 02_clean_crashes.ipynb
│       ├── 03_clean_persons.ipynb
│       ├── 04_integrate_datasets.ipynb
│       ├── 05_post_integration_cleaning.ipynb
│       ├── 06_feature_engineering.ipynb
│       └── 07_final_visual_analysis.ipynb
│
├── src/
│   ├── config.py             # Paths, app title, port, etc.
│   ├── data_loader.py        # Loading raw data
│   ├── data_cleaning.py      # Cleaning crashes & persons tables
│   ├── data_integration.py   # Joining datasets and building master table
│   └── feature_engineering.py# Extra features for analysis/dashboard
│
├── tests/                    # Simple unit tests for the pipeline
├── deployment/               # Render / Heroku configuration (if deployed)
├── run_pipeline.py           # Orchestrates the full data pipeline
├── requirements.txt          # Python dependencies
└── README.md                 # You are here 🙂

Data Pipeline:

The pipeline is split into clearly defined steps, implemented in src/ and
demonstrated in the Jupyter notebooks:
	1.	Load & EDA (01_load_and_eda.ipynb)
	•	Load the raw crashes and persons datasets.
	•	Inspect schema, basic statistics, and initial data quality issues.
	2.	Cleaning (02 & 03)
	•	02_clean_crashes.ipynb and 03_clean_persons.ipynb handle:
	•	Missing values
	•	Invalid / inconsistent codes
	•	Outliers (e.g. negative injuries)
	•	Date/time parsing
	3.	Integration (04)
	•	Join crashes and persons on collision_id.
	•	Build a unified table with crash, location, time, vehicle, and person info.
	4.	Post-Integration Cleaning (05)
	•	Remove remaining duplicates and inconsistent rows.
	•	Ensure final schema is suitable for analysis and dashboard.
	5.	Feature Engineering (06 / src/feature_engineering.py)
	•	Add derived features, e.g.:
	•	crash_year, crash_month, crash_day_of_week, is_weekend
	•	total_injured, total_killed, severity_score
	•	Simple vehicle-type indicators (has_truck, has_bus, has_bicycle)
	•	Save processed datasets as parquet in data/processed/
(these files are ignored by git and recreated locally via the pipeline).
	6.	Final Visual Analysis (07)
	•	Answer the research questions with plots and commentary.
	•	Many of these questions also appear as interactive views in the dashboard.

You can re-run the entire pipeline with: python run_pipeline.py

Dashboard:

The interactive dashboard is built with Dash + Plotly and lives in app/.

To run it locally:# 1. Activate virtualenv (if not already)
source .venv/bin/activate          # macOS / Linux
# or
.\.venv\Scripts\activate           # Windows

# 2. Install requirements (first time only)
pip install -r requirements.txt

# 3. Make sure processed parquet data exists
python run_pipeline.py             # or run the notebooks in order

# 4. Start the Dash app
python app/dash_app.py
Then open the browser at: http://127.0.0.1:8050/
Dashboard Features
	•	Filters panel
	•	Date range selector
	•	Borough multi-select
	•	Severity (injury / fatal) checklist
	•	Injury type (pedestrian / cyclist / motorist)
	•	Vehicle type dropdown
	•	Free-text “search” field
	•	Generate Report button that updates all charts at once
	•	Main views
	•	Time series of collisions over time
	•	Collisions by borough
	•	Severity distribution (injuries vs fatalities)
	•	Contributing factors (top causes)
	•	Hour-of-day distribution
	•	Simple geographic heatmap of crash locations
    The graphs are designed to support the research questions defined by the team
(e.g. “Which borough has the most severe injuries?”, “At what times do crashes
spike on weekends?”, etc.).
Research Questions (Examples)

Each team member proposed two research questions; include:
	# RQ1: How do collision counts change over time (daily & monthly trends)?
    # RQ2: Are motor vehicle collisions increasing or decreasing across recent years?
    # RQ3: Which borough has the highest number of motor vehicle collisions?
    # RQ4: How do injury and fatality rates vary across NYC boroughs?
    # RQ5: Which hours of the day have the highest and lowest collision rates?
    # RQ6: What are the most common contributing factors behind NYC collisions?
    # RQ7: How do pedestrian, cyclist, and motorist injuries differ across boroughs?
    # RQ8: Which vehicle types are most frequently involved in collisions?
    # RQ9: How does collision density vary geographically across NYC neighborhoods?
    # RQ10: Do environmental or behavioral contributing factors correlate with higher crash severity?

These questions are answered with a combination of static plots in
07_final_visual_analysis.ipynb and interactive views in the dashboard.
Reproducibility
	•	All processing code is written as reusable functions in src/.
	•	Notebooks call these functions for transparency.
	•	Large parquet datasets in data/processed/ are not tracked by git to keep
the repository lightweight; they are regenerated locally via the pipeline.
How to Run Tests

Basic tests for the main pipeline steps are provided in tests/:pytest

Notes for the Instructor / TA
	•	The “Generate Report” button triggers a single callback that reads all filter
values and updates every graph at once.
	•	All borough, severity, and vehicle selections are synchronized between
notebooks and dashboard.
	•	The repository is cleaned from large parquet files via .gitignore; only
small configuration and placeholder files are versioned.
