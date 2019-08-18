from airflow import DAG
from airflow.operators import StageToRedshiftOperator
from helpers import SqlQueries
from airflow.models import Variable
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python_operator import PythonOperator
import logging


def load_dimension_subdag(
        parent_dag_name,
        task_id,
        redshift_conn_id,
        *args, **kwargs):
    """
    A python function with arguments, which creates a dag
    :param parent_dag_name: imp ({parent_dag_name}.{task_id})
    :param task_id: imp {task_id}
    :param redshift_conn_id: {any connection id}
    :param args: {verbose}
    :param kwargs: {verbose and context variables}
    :return:
    """
    dag = DAG(
        f"{parent_dag_name}.{task_id}",
        **kwargs
    )

    copy_ports = StageToRedshiftOperator(
        task_id='copy_ports',
        dag=dag,
        redshift_conn_id="redshift",
        aws_credentials_id="aws_default",
        file='i94port.csv',
        delimiter=',',
        table='i94ports',
        s3_bucket="udacity-data-lakes-supratim",
        s3_key="csv",
        sql_stmt=SqlQueries.copy_csv_cmd,
        provide_context=True)

    copy_visa = StageToRedshiftOperator(
        task_id='copy_visa',
        dag=dag,
        redshift_conn_id="redshift",
        aws_credentials_id="aws_default",
        file='i94visa.csv',
        delimiter=',',
        table='i94visa',
        s3_bucket="udacity-data-lakes-supratim",
        s3_key="csv",
        sql_stmt=SqlQueries.copy_csv_cmd,
        provide_context=True)

    copy_modes = StageToRedshiftOperator(
        task_id='copy_modes',
        dag=dag,
        redshift_conn_id="redshift",
        aws_credentials_id="aws_default",
        file='i94mode.csv',
        delimiter=',',
        table='i94mode',
        s3_bucket="udacity-data-lakes-supratim",
        s3_key="csv",
        sql_stmt=SqlQueries.copy_csv_cmd,
        provide_context=True)

    copy_addr = StageToRedshiftOperator(
        task_id='copy_addr',
        dag=dag,
        redshift_conn_id="redshift",
        aws_credentials_id="aws_default",
        file='i94addr.csv',
        delimiter=',',
        table='i94addr',
        s3_bucket="udacity-data-lakes-supratim",
        s3_key="csv",
        sql_stmt=SqlQueries.copy_csv_cmd,
        provide_context=True)

    copy_country_codes = StageToRedshiftOperator(
        task_id='copy_country_codes',
        dag=dag,
        redshift_conn_id="redshift",
        aws_credentials_id="aws_default",
        file='i94cit&i94res.csv',
        delimiter=',',
        table='i94res',
        s3_bucket="udacity-data-lakes-supratim",
        s3_key="csv",
        sql_stmt=SqlQueries.copy_csv_cmd,
        provide_context=True)

    copy_cities_demographics = StageToRedshiftOperator(
        task_id='copy_cities_demographics',
        dag=dag,
        redshift_conn_id="redshift",
        aws_credentials_id="aws_default",
        file='us-cities-demographics.csv',
        delimiter=';',
        table='us_cities_demographics',
        s3_bucket="udacity-data-lakes-supratim",
        s3_key="csv",
        sql_stmt=SqlQueries.copy_csv_cmd,
        provide_context=True)

    copy_airports = StageToRedshiftOperator(
        task_id='copy_airports',
        dag=dag,
        redshift_conn_id="redshift",
        aws_credentials_id="aws_default",
        file='airport_codes.csv',
        delimiter=',',
        table='airport_codes',
        s3_bucket="udacity-data-lakes-supratim",
        s3_key="csv",
        sql_stmt=SqlQueries.copy_csv_cmd,
        provide_context=True)

    def parquet_to_redshift(table, s3_bucket, s3_key, iam_role,
                            sql_stmt, redshift_conn_id, **kwargs):
        redshift = PostgresHook(postgres_conn_id=redshift_conn_id)
        logging.info("Copying data from S3 to Redshift")
        s3_path = "s3://{}/{}".format(s3_bucket, s3_key)
        formatted_sql = sql_stmt.format(
            table,
            s3_path,
            iam_role
        )
        redshift.run(formatted_sql)

    copy_immigration = PythonOperator(
        task_id='copy_immigration',
        python_callable=parquet_to_redshift,  # changed
        provide_context=True,
        op_kwargs={'table': "immigration",
                   's3_bucket': 'udacity-data-lakes-supratim',
                   's3_key': 'parquet',
                   'iam_role': Variable.get('iam_role'),
                   'sql_stmt': SqlQueries.copy_parquet_cmd,
                   'redshift_conn_id': 'redshift'},
        dag=dag
    )

    copy_ports
    copy_visa
    copy_modes
    copy_addr
    copy_country_codes
    copy_airports
    copy_cities_demographics
    copy_immigration

    return dag