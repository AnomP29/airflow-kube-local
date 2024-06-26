from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'aprasetyo',
    'start_date': datetime(2024, 5, 10),
    'catchup': False
}

dag = DAG(
    'bashop_param_04',
    default_args = default_args,
    # schedule = timedelta(days=1)
    schedule = None
)

start_task = DummyOperator(task_id='start_task', dag=dag)
end_task = DummyOperator(task_id='end_task', dag=dag)

t1 = BashOperator(
    task_id = 'test_01',
    bash_command ='echo "t01_"',
    dag = dag
)


t2 = BashOperator(
    task_id = 'test_02',
    bash_command ='echo "t02_"',
    dag = dag
)

start_task >> t1 >> t2 >> end_task