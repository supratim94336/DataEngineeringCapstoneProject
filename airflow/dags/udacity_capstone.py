# generic
from datetime import datetime, timedelta
# airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators import (SASToCSVOperator, TransferToS3Operator, SAS7ToParquet)
from airflow.models import Variable
from helpers import SqlQueries


default_args = {
    'owner': 'udacity',
    'start_date': datetime(2018, 1, 1),
    'end_date': datetime(2018, 12, 1),
    'email_on_retry': False,
    'retries': 3,
    'catchup': False,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': False,
    'wait_for_downstream': True
}

# dag is complete
dag = DAG('udacity_capstone',
          default_args=default_args,
          description='Data Engineering Capstone Project',
          schedule_interval='@yearly'
          )

# dummy for node 0
start_operator = DummyOperator(task_id='Begin_execution', dag=dag)

# convert sas descriptor to csv
convert_sas_to_csv = SASToCSVOperator(
    task_id='sas_to_csv',
    dag=dag,
    input_path=Variable.get("sas_file"),
    output_path=Variable.get("temp_output"),
    provide_context=True
)

# transfer files to csv
transfer_to_s3_csv = TransferToS3Operator(
    task_id='transfer_to_s3_csv',
    dag=dag,
    aws_credentials_id="aws_default",
    input_path=Variable.get("temp_output"),
    bucket_name="supratim94336-bucket",
    file_ext="csv",
    provide_context=True
)

sas7bdat_to_parquet = SAS7ToParquet (
    task_id='sas7bdat_to_parquet',
    dag=dag,
    input_path=Variable.get("temp_input"),
    output_path=Variable.get("spark_path"),
    provide_context=True
)

transfer_to_s3_parquet = TransferToS3Operator(
    task_id='transfer_to_s3_parquet',
    dag=dag,
    aws_credentials_id="aws_default",
    input_path=Variable.get("spark_path"),
    bucket_name="supratim94336-bucket",
    file_ext="parquet",
    provide_context=True
)

task_create_table = PostgresOperator(
    task_id="create_table",
    postgres_conn_id="redshift",
    sql=SqlQueries.create_tables,
    dag=dag
)

# dummy for node end
end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# order
start_operator >> convert_sas_to_csv >> transfer_to_s3_csv >> task_create_table
start_operator >> sas7bdat_to_parquet >> transfer_to_s3_parquet >> task_create_table
task_create_table >> end_operator
