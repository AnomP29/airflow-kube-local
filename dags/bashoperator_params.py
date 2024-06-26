import airflow
import datetime
import pathlib

from airflow import DAG
from airflow.utils.session import provide_session
from airflow.sensors.external_task import ExternalTaskSensor
from airflow import models
from airflow.operators.bash import BashOperator
from dependencies.utils import DAGS_FOLDER


default_args = {
    "owner": "anmp",
    "start_date": airflow.utils.dates.days_ago(1),
    "email_on_failure": True,
    "email_on_retry": False,
    "provide_context": True,
    "retries": 1,
}
with DAG(
    'bashop_param',
    default_args=default_args,
    schedule=None
) as base:

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
    #         bash_command="PYTHONPATH={dags} python {dags}/scripts/bashop/{task}.py".format(
    #             dags=DAGS_FOLDER, task=task
    #         ),
    #         params={
    #             'exec_date': '{{ ds }}'
    #         }
    #     )
