import datetime
from pathlib import Path

from airflow.decorators import dag
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


def read_sql_query(dir: str, name: str) -> str:
    dag_dir = Path(__file__).parent
    sql_path = dag_dir / "sql" / dir / name
    with open(sql_path, "r") as f:
        return f.read()


@dag(
    dag_id="ingest",
    start_date=datetime.datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args={
        "owner": "Billy Moore",
        "retries": 1,
        "retry_delay": datetime.timedelta(minutes=1),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    tags=["snowflake", "predictit"],
)
def ingest_dag():
    execution_timestamp = "{{ dag_run.conf['execution_timestamp'] }}"

    load_stage_raw = SQLExecuteQueryOperator(
        task_id="load_stage_raw",
        sql=read_sql_query("loading", "load_stage_raw.sql"),
        params={"execution_timestamp": execution_timestamp},
        conn_id="snowflake_default",
    )

    load_stg_dim_markets = SQLExecuteQueryOperator(
        task_id="load_stg_dim_markets",
        sql=read_sql_query("loading", "load_stg_dim_markets.sql"),
        conn_id="snowflake_default",
    )

    load_dim_markets = SQLExecuteQueryOperator(
        task_id="load_dim_markets",
        sql=read_sql_query("loading", "load_dim_markets.sql"),
        conn_id="snowflake_default",
    )

    load_stg_dim_contracts = SQLExecuteQueryOperator(
        task_id="load_stg_dim_contracts",
        sql=read_sql_query("loading", "load_stg_dim_contracts.sql"),
        conn_id="snowflake_default",
    )

    load_dim_contracts = SQLExecuteQueryOperator(
        task_id="load_dim_contracts",
        sql=read_sql_query("loading", "load_dim_contracts.sql"),
        conn_id="snowflake_default",
    )

    load_fact_prices = SQLExecuteQueryOperator(
        task_id="load_fact_prices",
        sql=read_sql_query("loading", "load_fact_prices.sql"),
        conn_id="snowflake_default",
    )

    # Set task dependencies
    (
        load_stage_raw
        >> load_stg_dim_markets
        >> load_dim_markets
        >> load_stg_dim_contracts
        >> load_dim_contracts
        >> load_fact_prices
    )


dag = ingest_dag()
