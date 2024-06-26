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
        'bashop_param',
        default_args=default_args,
        schedule_interval=None,
        catchup=False,
) as param:
    
    start_task = DummyOperator(task_id='start_task', dag=param)
    end_task = DummyOperator(task_id='end_task', dag=param)
    
    params_t1 = BashOperator(
        task_id = 'params_t1',
        bash_command ='echo "params_t1_222222"',
        dag=param,
    )

    start_task >> params_t1 >> end_task
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
