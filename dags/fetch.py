import datetime
import json
import os

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator

lambda_function_fetch_name = 'predictit-fetch'
lambda_function_validate_name = 'predictit-validate'

@task
def check_lambda_result(lambda_result: str):
    lambda_result = json.loads(lambda_result)
    if not lambda_result:
        raise ValueError("No result returned from Lambda")
    status = lambda_result.get("StatusCode")
    if status != 200:
        raise ValueError(f"Lambda returned non-200 status code: {status}")
    return True

# must define tasks to build the lambda payloads as we cannot use Airflow templating and
# serialise to json in the same step 
@task
def build_fetch_payload(**kwargs):
    filename = f"market_data_{kwargs['ts_nodash']}.json"
    return json.dumps({"filename": filename})

@task
def build_validate_payload(**kwargs):
    execution_timestamp = kwargs['ts_nodash']
    return json.dumps({'execution_timestamp': execution_timestamp})

@dag(
    dag_id="fetch",
    schedule_interval="@daily",
    start_date=datetime.datetime(2025, 1, 1),
    catchup=False,
    default_args={
        "owner": "Billy Moore",
        #"retries": 1,
        #"retry_delay": datetime.timedelta(minutes=1),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    tags=["lambda", "fetch", "validate"],
)
def fetch_dag():
    initiate = EmptyOperator(task_id="initiate")

    fetch_payload = build_fetch_payload()

    validate_payload = build_validate_payload()

    lambda_fetch = LambdaInvokeFunctionOperator(
        task_id="lambda_fetch",
        function_name=lambda_function_fetch_name,
        payload=fetch_payload,
    )

    lambda_validate = LambdaInvokeFunctionOperator(
        task_id="lambda_validate",
        function_name=lambda_function_validate_name,
        payload=validate_payload,
    )

    # trigger_snowflake_ingestion = TriggerDagRunOperator(
    #     task_id="trigger_snowflake_ingestion",
    #     trigger_dag_id="ingest",
    #     conf={"execution_timestamp": "{{ ts_nodash }}"},
    # )

    # Wire tasks together
    fetch_result_check = check_lambda_result(lambda_fetch.output)
    validate_result_check = check_lambda_result(lambda_validate.output)

    (
        initiate
        >> lambda_fetch
        >> fetch_result_check
        >> lambda_validate
        >> validate_result_check
        # >> trigger_snowflake_ingestion
    )


dag = fetch_dag()
