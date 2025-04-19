import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
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

def poll_markets_callable(**kwargs):
    data = predictit.poll_market_data()
    kwargs['ti'].xcom_push(key='market_data', value=data)

def store_data_callable(**kwargs):
    data = kwargs['ti'].xcom_pull(key='market_data', task_ids='poll_market_data')
    predictit.store_to_s3(data)

with DAG(
    dag_id="predictit_extraction",
    default_args=default_args,
    catchup=False
) as dag:
    
    initiate = EmptyOperator(task_id='initiate')
    
    poll_market_data = PythonOperator(
        task_id='poll_market_data',
        python_callable=poll_markets_callable
    )

    store_market_data = PythonOperator(
        task_id='store_market_data',
        python_callable=store_data_callable
    )


    initiate >> poll_market_data >> store_market_data