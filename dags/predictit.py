import datetime
import os

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from src.api import PredictitAPI

s3_bucket = os.getenv('S3_BUCKET')

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
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S')
    filename = f'market_data_{timestamp}.json'
    predictit.store_to_s3(data, bucket=s3_bucket, filename=filename)
    kwargs['ti'].xcom_push(key='filename', value=filename)

with DAG(
    dag_id="predictit_extraction",
    default_args=default_args,
    catchup=False
) as dag:
    
    initiate = EmptyOperator(task_id='initiate')
    
    poll_market_data = PythonOperator(
        task_id='poll_market_data',
        python_callable=poll_markets_callable,
        retries=3,
        retry_delay=datetime.timedelta(seconds=30)
    )

    store_market_data = PythonOperator(
        task_id='store_market_data',
        python_callable=store_data_callable,
        retries=3,
        retry_delay=datetime.timedelta(seconds=30)
    )


    initiate >> poll_market_data >> store_market_data