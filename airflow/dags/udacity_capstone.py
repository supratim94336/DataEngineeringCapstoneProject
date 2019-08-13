from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
# spark
import logging
from pyspark.sql import SparkSession


access_key = Variable.get('AWS_KEY')
secret_key = Variable.get('AWS_SECRET')

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
dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='@hourly'
          )

# dummy for node 0
start_operator = DummyOperator(task_id='Begin_execution', dag=dag)


def run_spark(*args, **kwargs):
    spark = SparkSession.builder \
        .config("spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:2.7.0") \
        .appName("demo") \
        .getOrCreate()

    spark.sparkContext._jsc.hadoopConfiguration().set(
        "fs.s3a.access.key", access_key)
    spark.sparkContext._jsc.hadoopConfiguration().set(
        "fs.s3a.secret.key", secret_key)

    filepath = "s3a://supratim94336-bucket/parquet/"
    df_all = spark.read.parquet(filepath)
    logging.info(df_all.toPandas().head(50))


run_spark_task = PythonOperator(
    task_id='run_spark_task',
    dag=dag,
    python_callable=run_spark,
    provide_context=True
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

start_operator >> run_spark_task
run_spark_task >> end_operator
