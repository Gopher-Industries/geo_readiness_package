# airflow_dag_geo_readiness.py
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'db-team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

with DAG(
    'geo_readiness_pipeline',
    default_args=default_args,
    description='Clean, geocode & report address data',
    schedule_interval='0 3 * * *',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    t1_profile = BashOperator(
        task_id='run_profiling',
        bash_command='psql $DATABASE_URL -f /opt/scripts/geo_profiling.sql'
    )

    t2_geocode = BashOperator(
        task_id='run_geocode',
        bash_command='python /opt/scripts/geo_geocode.py'
    )

    t3_report = BashOperator(
        task_id='generate_report',
        bash_command='psql $DATABASE_URL -c "\copy (SELECT * FROM geo_summary ORDER BY snapshot_time DESC LIMIT 1) TO /opt/reports/geo_summary.csv WITH CSV HEADER"'
    )

    t1_profile >> t2_geocode >> t3_report
