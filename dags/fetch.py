import datetime
import json
import os

from airflow import DAG
from airflow.operators.dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.lambda_function import (
    AwsLambdaInvokeFunctionOperator,
)

lambda_function_fetch_name = os.getenv("LAMBDA_FUNCTION_FETCH_NAME")
lambda_function_validate_name = os.getenv("LAMBDA_FUNCTION_VALIDATE_NAME")

default_args = {
    "owner": "Billy Moore",
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=1),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
}


# callable to check the result of lambda functions
def check_lambda_result(task_id, **context):
    result = context["ti"].xcom_pull(task_ids=task_id)
    if result is None:
        raise ValueError(f"Lambda function {task_id} failed to return a result.")
    payload = result.get("Payload")
    if payload:
        response = json.loads(payload.read())
        if response.get("StatusCode") != 200:
            raise ValueError(
                f"Lambda function {task_id} failed with status code: {response.get('StatusCode')}"
            )
    else:
        raise ValueError(f"Lambda function {task_id} returned no payload.")


with DAG(
    dag_id="fetch",
    default_args=default_args,
    catchup=False,
    schedule_interval="@hourly",
) as dag:
    initiate = EmptyOperator(task_id="initiate")

    lambda_fetch = AwsLambdaInvokeFunctionOperator(
        task_id="lambda_fetch",
        function_name=lambda_function_fetch_name,
        payload={"filename": "market_data_{{ ts_nodash }}.json"},
    )

    check_fetch = PythonOperator(
        task_id="check_fetch",
        python_callable=check_lambda_result,
        op_kwargs={"task_id": "lambda_fetch"},
    )

    lambda_validate = AwsLambdaInvokeFunctionOperator(
        task_id="lambda_validate",
        function_name=lambda_function_validate_name,
        payload={"filename": "market_data_{{ ts_nodash }}.json"},
    )

    check_validate = PythonOperator(
        task_id="check_validate",
        python_callable=check_lambda_result,
        op_kwargs={"task_id": "lambda_validate"},
    )

    trigger_snowflake_ingestion = TriggerDagRunOperator(
        task_id="trigger_snowflake_ingestion",
        trigger_dag_id="ingest",
        conf={"execution_timestamp": "{{ ts_nodash }}"},
    )

    (
        initiate
        >> lambda_fetch
        >> check_fetch
        >> lambda_validate
        >> check_validate
        >> trigger_snowflake_ingestion
    )
