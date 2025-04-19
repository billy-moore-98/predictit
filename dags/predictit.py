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

predictit = PredictitAPI()

with DAG(
    dag_id="predictit_extraction",
    default_args=default_args,
    catchup=False
) as dag:
    
    fetch_market_data = PythonOperator(
        task_id='fetch_market_data',
        python_callable=predictit.poll_market_data,
        dag=dag
    )