import datetime

from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from pathlib import Path

default_args = {
    "owner": "Billy Moore",
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=1),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
}


def read_sql_query(dir: str, name: str) -> str:
    root_dir = Path(__file__).parent.parent
    sql_path = root_dir / "sql" / dir / name
    with open(sql_path, "r") as f:
        sql = f.read()
    return sql


with DAG(dag_id="ingest", default_args=default_args):
    execution_timestamp = "{{ dag_run.conf['execution_timestamp'] }}"

    def snowflake_task_factory(
        task_id: str, filename: str, timestamp_param: bool = False
    ):
        return SnowflakeOperator(
            task_id=task_id,
            sql=read_sql_query("loading", filename),
            snowflake_conn_id="snowflake_predictit",
            params={"execution_timestamp": execution_timestamp}
            if timestamp_param
            else {},
        )

    load_stage_raw = snowflake_task_factory(
        "load_stage_raw", "load_stage_raw.sql", timestamp_param=True
    )
    load_stg_dim_markets = snowflake_task_factory(
        "load_stg_dim_markets", "load_stg_dim_markets.sql"
    )
    load_dim_markets = snowflake_task_factory(
        "load_dim_markets", "load_dim_markets.sql"
    )
    load_stg_dim_contracts = snowflake_task_factory(
        "load_stg_dim_contracts", "load_stg_dim_contracts.sql"
    )
    load_dim_contracts = snowflake_task_factory(
        "load_dim_contracts", "load_dim_contracts.sql"
    )
    load_fact_prices = snowflake_task_factory(
        "load_fact_prices", "load_fact_prices.sql"
    )

    (
        load_stage_raw
        >> load_stg_dim_markets
        >> load_dim_markets
        >> load_stg_dim_contracts
        >> load_dim_contracts
        >> load_fact_prices
    )
