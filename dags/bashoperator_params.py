import pathlib
import airflow


from airflow import DAG
from airflow.utils.session import provide_session
from airflow.sensors.external_task import ExternalTaskSensor
from airflow import models
from airflow.operators.bash import BashOperator
from dependencies.utils import DAGS_FOLDER

from datetime import datetime, timedelta
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 10),
    'catchup': False
}

with DAG(
        'bashop_param',
        default_args=default_args,
        schedule_interval=None,
        catchup=False,
) as param:
    
    start_task = DummyOperator(task_id='start_task')
    end_task = DummyOperator(task_id='end_task')
    
    
    # start_task >> params_t1 >> end_task
    orders_path = pathlib.Path(DAGS_FOLDER).joinpath("scripts/bashop/orders.txt")
    orders_conf = []

    for order in open(orders_path).read().splitlines():
        if order != "":
            order = [o.strip() for o in order.split() if o != ">>"]
            orders_conf.append(order)

    listed_tasks = set([task for tasks in orders_conf for task in tasks])
    tasks = {}
    for task in listed_tasks:
        EXEC_DATE = '{{ ds }}'
        tasks[task] = BashOperator(
            task_id=task,
            params={'exec_date': '{{ ds }}'},
            bash_command= 'echo {{ params.exec_date }}' + EXEC_DATE,
            # bash_command= "PYTHONPATH={dags} python {dags}/scripts/bashop/{task}.py --date {{ params.exec_date }}".format(
            #     dags=DAGS_FOLDER, task=task),
        )
