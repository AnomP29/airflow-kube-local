import airflow
import datetime
import pathlib

from airflow import DAG
from airflow.utils.session import provide_session
from airflow.sensors.external_task import ExternalTaskSensor
from airflow import models
from airflow.operators.bash import BashOperator
from dependencies.utils import DAGS_FOLDER
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'aprasetyo',
    "start_date": airflow.utils.dates.days_ago(1),
    "provide_context": True,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=5),

}

with DAG(
    'bashop_param',
    catchup=False,
    default_args=default_args,
    schedule=None
) as dags:

    orders_path = pathlib.Path(DAGS_FOLDER).joinpath("scripts/bashop/orders.txt")
    orders_conf = []

    for order in open(orders_path).read().splitlines():
        if order != "":
            order = [o.strip() for o in order.split() if o != ">>"]
            orders_conf.append(order)

    listed_tasks = set([task for tasks in orders_conf for task in tasks])
    start_task = DummyOperator(task_id='start_task', dag=dag)
    end_task = DummyOperator(task_id='end_task', dag=dag)
    tasks = {}
    for task in listed_tasks:
        tasks[task] = BashOperator(
            task_id=task,
            bash_command= 'echo "coba"',
            )
            # params={
            #     'exec_date': '{{ ds }}'
            # },
            # bash_command='echo "PYTHONPATH={dags} python {dags}/scripts/bashop/{task}.py"'.format(
            #     dags=DAGS_FOLDER, task=task
            # ),
        # )
