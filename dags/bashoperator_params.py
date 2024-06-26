import airflow
# import datetime
import pathlib

from airflow import DAG
from airflow.utils.session import provide_session
from airflow.sensors.external_task import ExternalTaskSensor
from airflow import models
from airflow.operators.bash import BashOperator
from dependencies.utils import DAGS_FOLDER
from datetime import datetime
from airflow.operators.dummy import DummyOperator


default_args = {
    'owner': 'aprasetyo',
    'start_date': datetime(2024, 5, 10),
    'catchup': False
}

dag = DAG(
    'bashop_param',
    default_args = default_args,
    # schedule = timedelta(days=1)
    schedule = None
)
BashOperator(
    task_id = 'params_t1',
    bash_command ='echo "params_t1_222222"',
)
    # orders_path = pathlib.Path(DAGS_FOLDER).joinpath("scripts/bashop/orders.txt")
    # orders_conf = []

    # for order in open(orders_path).read().splitlines():
    #     if order != "":
    #         order = [o.strip() for o in order.split() if o != ">>"]
    #         orders_conf.append(order)

    # listed_tasks = set([task for tasks in orders_conf for task in tasks])
    # tasks = {}
    # for task in listed_tasks:
    #     tasks[task] = BashOperator(
    #         task_id=task,
    #         bash_command= 'echo "coba"',
    #         )
    #         # params={
    #         #     'exec_date': '{{ ds }}'
    #         # },
    #         # bash_command='echo "PYTHONPATH={dags} python {dags}/scripts/bashop/{task}.py"'.format(
    #         #     dags=DAGS_FOLDER, task=task
    #         # ),
    #     # )
