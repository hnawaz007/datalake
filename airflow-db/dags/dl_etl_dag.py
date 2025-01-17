from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'Haq',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# Define the SQL query to return a value
query = """WITH is_empty AS (
            SELECT COUNT(*) AS row_count
            FROM iceberg.raw.sales
            )
            SELECT
                CASE
                    WHEN row_count > 0
                     THEN 'SELECT 1'
                    WHEN row_count = 0
                    THEN 'ALTER TABLE iceberg.raw.sales EXECUTE add_files(location => ''s3://datalake/data/sales_summary_updated.parquet'', format => ''PARQUET'')'
                END AS vars
             from is_empty """
             
# Define the Python function to get sql query
def get_sql_from_xcom(**kwargs):
    ti = kwargs['ti']
    sql_query = ti.xcom_pull(task_ids='get_table_rowcount')
    if sql_query:
        return sql_query[0][0]
    else:
        return None
    

# Define the DAG
with DAG(
    'datalake_etl_pipeline',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:
    

    create_schema_iceberg = SQLExecuteQueryOperator(
        task_id='create_iceberg_schema',
        conn_id='trino_conn',
        sql="""
            CREATE SCHEMA IF NOT EXISTS iceberg.raw
            WITH (location = 's3a://warehouse/')
            """,
        autocommit=True,
        dag=dag
    )

    create_raw_iceberg_sales = SQLExecuteQueryOperator(
        task_id='create_iceberg_sales_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS iceberg.raw.sales (
               ProductCategoryName varchar,
               ProductSubcategoryName varchar,
               ProductName varchar,
               SalesTerritoryCountry varchar,
               SalesAmount DOUBLE,
               OrderDate BIGINT
            )
             WITH ( format = 'PARQUET', location = 's3a://warehouse/raw/sales'
            )
        """,
        dag=dag
    )

    # Task to execute the SQL query
    get_table_rowcount = SQLExecuteQueryOperator(
        task_id='get_table_rowcount',
        sql=query,
        conn_id='trino_conn',  # Replace with your connection ID
    )

    get_sql_from_xcom_task = PythonOperator(
        task_id='get_sql_from_xcom_task',
        python_callable=get_sql_from_xcom,
        provide_context=True
        )

    add_table_data  = SQLExecuteQueryOperator(
        task_id='update_add_data',
        sql="{{ ti.xcom_pull(task_ids='get_sql_from_xcom_task') }}",
        conn_id='trino_conn', 
    )
    
    # dbt tasks
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt run --profiles-dir {DBT_PROFILE_DIR} --project-dir {DBT_PROJECT_DIR}",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"dbt test --profiles-dir {DBT_PROFILE_DIR} --project-dir {DBT_PROJECT_DIR}",
    )

    # Set task dependencies
    create_schema_iceberg >> create_raw_iceberg_sales >> get_table_rowcount >> get_sql_from_xcom_task >> add_table_data >> dbt_run >> dbt_test