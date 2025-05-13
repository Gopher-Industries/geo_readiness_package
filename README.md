# Geo-Readiness & Map-Linking Pipeline

## Overview
This pipeline cleans raw addresses, geocodes them, validates results, and surfaces exceptions.

## Files
- `geo_profiling.sql`      – SQL analysis of missing/malformed data
- `address_cleaning.py`    – Normalize address components
- `geo_geocode.py`         – Batch geocoding script
- `GeoReadinessCheck.sql`  – Stored procedure for in-DB orchestration
- `geo_report_template.html` – HTML report skeleton
- `airflow_dag_geo_readiness.py` – Airflow DAG (optional)
- `sql_agent_job_config.json`    – SQL Agent job export (optional)
- `alert_config.yaml`      – Monitoring/alert rules
- `address_sample.csv`     – Sample address rows for testing

## Setup

1. Copy `.env.example` to `.env`, fill in:
   ```
   DATABASE_URL=postgres://user:pass@host:port/dbname
   GOOGLE_MAPS_API_KEY=your_api_key
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run profiling:
   ```bash
   psql $DATABASE_URL -f geo_profiling.sql
   ```
4. Clean & geocode in one go:
   ```bash
   python address_cleaning.py   # test only
   python geo_geocode.py
   ```
5. (Optional) Enable stored-procedure orchestration:
   ```sql
   psql $DATABASE_URL -f GeoReadinessCheck.sql
   SELECT dbo.GeoReadinessCheck();
   ```

## Scheduling

- **Airflow**: See `airflow_dag_geo_readiness.py`
- **SQL Agent**: Import `sql_agent_job_config.json`
- **pg_cron / pgAgent**: Use commented snippet in `GeoReadinessCheck.sql`

## Reporting

- After each run, open `geo_report_template.html` in Excel or your browser
- Exceptions appear in `geo_exceptions` table
