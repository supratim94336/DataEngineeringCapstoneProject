# generic
from datetime import datetime, timedelta
import os
import shutil
import logging
# airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators import (SASToCSVOperator, TransferToS3Operator, SAS7ToParquet, StageToRedshiftOperator, DataQualityOperator)
from subdags.subdag_for_dimensions import load_dimension_subdag
from airflow.models import Variable
from helpers import SqlQueries
from airflow.operators.subdag_operator import SubDagOperator


default_args = {
    'owner': 'udacity',
    'start_date': datetime(2019, 8, 22, 7),
    'end_date': datetime(2019, 12, 31, 7),
    'email_on_retry': False,
    'retries': 3,
    'catchup': False,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': True,
    'wait_for_downstream': True
}

# dag is complete
dag = DAG('udacity_capstone',
          default_args=default_args,
          description='Data Engineering Capstone Project',
          schedule_interval='@daily'
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
    bucket_name=Variable.get("s3_bucket"),
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
    bucket_name=Variable.get("s3_bucket"),
    file_ext="parquet",
    provide_context=True
)

task_create_schema = PostgresOperator(
    task_id="create_schema",
    postgres_conn_id="redshift",
    sql=SqlQueries.create_schema,
    dag=dag
)

task_drop_table = PostgresOperator(
    task_id="drop_table",
    postgres_conn_id="redshift",
    sql=SqlQueries.drop_tables,
    dag=dag
)

task_create_table = PostgresOperator(
    task_id="create_table",
    postgres_conn_id="redshift",
    sql=SqlQueries.create_tables,
    dag=dag
)

load_dimension_subdag_task = SubDagOperator(
    subdag=load_dimension_subdag(
        parent_dag_name="udacity_capstone",
        task_id="load_dimensions",
        redshift_conn_id="redshift",
        start_date=datetime(2018, 1, 1)
    ),
    task_id="load_dimensions",
    dag=dag
)

# run quality check
run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    sql_stmt=SqlQueries.count_check,
    tables=SqlQueries.tables
)


def cleaning(**kwargs):
    folder = Variable.get("spark_path")
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.info(e)


clean_temp_files = PythonOperator(
        task_id='clean_temp_files',
        python_callable=cleaning,
        provide_context=True,
        dag=dag
    )

# grant_access = """
#                create group webappusers;
#                create user webappuser1 password 'webAppuser1pass' in group webappusers;
#                grant usage on schema project to group webappusers;
#                """
# grant_access_to_users = PostgresOperator(
#     task_id="grant_access",
#     postgres_conn_id="redshift",
#     sql=grant_access,
#     dag=dag
# )

# dummy for node end
end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# order
start_operator >> convert_sas_to_csv >> transfer_to_s3_csv >> task_create_schema
start_operator >> sas7bdat_to_parquet >> transfer_to_s3_parquet >> task_create_schema
task_create_schema >> task_drop_table >> task_create_table >> load_dimension_subdag_task >> run_quality_checks >> clean_temp_files >> end_operator
