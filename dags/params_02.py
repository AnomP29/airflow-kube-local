from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 10),
    'catchup': False
}

with DAG(
        'bashop_param2',
        default_args=default_args,
        schedule_interval=None,
        catchup=False,
) as param2:
    
    start_task = DummyOperator(task_id='start_task')
    end_task = DummyOperator(task_id='end_task')
    
    params_t1 = BashOperator(
        task_id = 'params_t2',
        bash_command ='echo "params_t2_222222"',
    )

    start_task >> params_t1 >> end_task
