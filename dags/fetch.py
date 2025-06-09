import datetime
import json

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator

lambda_function_fetch_name = 'predictit-fetch'
lambda_function_validate_name = 'predictit-validate'

# must define tasks to build the lambda payloads as we cannot use Airflow templating and
# serialise to json in the same step 
@task
def build_lambda_payload(**kwargs):
    filename = f"market_data_{kwargs['ts_nodash']}.json"
    return json.dumps({"filename": filename})

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

    lambda_payload = build_lambda_payload()

    lambda_fetch = LambdaInvokeFunctionOperator(
        task_id="lambda_fetch",
        function_name=lambda_function_fetch_name,
        payload=lambda_payload,
    )

    lambda_validate = LambdaInvokeFunctionOperator(
        task_id="lambda_validate",
        function_name=lambda_function_validate_name,
        payload=lambda_payload,
    )

    # trigger_snowflake_ingestion = TriggerDagRunOperator(
    #     task_id="trigger_snowflake_ingestion",
    #     trigger_dag_id="ingest",
    #     conf={"execution_timestamp": "{{ ts_nodash }}"},
    # )

    (
        initiate
        >> lambda_fetch
        >> lambda_validate
        # >> trigger_snowflake_ingestion
    )


dag = fetch_dag()
