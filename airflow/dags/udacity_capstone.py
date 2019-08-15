# generic
from datetime import datetime, timedelta
# airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator


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
# dummy for node end
end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

