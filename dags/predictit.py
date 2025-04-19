import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from src.api import PredictitAPI

default_args = {
    "owner": "Billy Moore",
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=1),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False
}

with DAG(
    dag_id="predictit_extraction",
    default_args=default_args
) as dag:
    pass