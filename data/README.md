# Data Directory

## Structure

- **`processed/`**: Contains cleaned and processed data files ready for the dashboard
  - `crashes_cleaned.parquet`: Cleaned crashes dataset
  - `persons_cleaned.parquet`: Cleaned persons dataset
  - `integrated.parquet`: Merged dataset
  - `dashboard_data.parquet`: Final dataset with engineered features

- **`cache/`**: Temporary cache for API responses (Git-ignored)
  - Used during development to avoid repeated API calls
  - Automatically populated by `data_loader.py`

## Data Pipeline

1. **Load**: Fetch data from NYC Open Data API using `src/data_loader.py`
2. **Clean**: Process individual datasets (notebooks 02-03)
3. **Integrate**: Merge datasets on COLLISION_ID (notebook 04)
4. **Post-clean**: Final cleaning after integration (notebook 05)
5. **Engineer**: Create features for analysis (notebook 06)
6. **Export**: Save final dataset for dashboard

## Data Sources

All data is fetched from NYC Open Data:
- [Motor Vehicle Collisions - Crashes](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)
- [Motor Vehicle Collisions - Person](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu)
- [Motor Vehicle Collisions - Vehicles](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4)

## Notes

- Raw data is never stored locally, only fetched via API
- Cache files are temporary and can be deleted anytime
- Processed files should be version controlled (or use Git LFS for large files)
