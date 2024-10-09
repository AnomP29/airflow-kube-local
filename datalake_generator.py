import pathlib
import os
import airflow

from airflow import DAG, models
from airflow.models.dag import DagModel
from airflow.operators.bash import BashOperator
from dependencies.slack_notification import task_fail_slack_alert
from ruamel.yaml import YAML
from datetime import timedelta
from dependencies.utils import DAGS_FOLDER


large_tables = [
    'partner_ekyc_integration_record',
    'notification2',
    'insider_push_engagement_report',
    'ciam_user_backoffice_activity',
]


def create_dag(dag_id, bash_command, encryption_command, queue_pool, db, table, schedule, is_paused):
    default_args = {
        "owner": "data_engineer",
        "start_date": airflow.utils.dates.days_ago(8),
        # 'start_date': datetime(2024, 10, 1),
        "retries": 2,
        "retry_delay": timedelta(seconds=120),
    }

    dag = DAG(
        dag_id,
        description="Data Lake from DB {db} to BigQuery".format(
            db=db
        ),
        # schedule_interval=schedule,
        default_args=default_args,
    catchup=True,
        # is_paused_upon_creation=is_paused,
    )

    bash_args = {
        "task_id": table,
        "on_failure_callback": task_fail_slack_alert,
        "pool": queue_pool,
        "bash_command": bash_command,
        "execution_timeout": timedelta(hours=2),
    }

    if table in large_tables:
        executor_conf = {
            "KubernetesExecutor": {
                "request_memory": "16Gi",
                "request_cpu": "4",
            }
        }
        bash_args["executor_config"] = executor_conf
        bash_args["queue"] = "kubernetes"

    with dag:
        task = BashOperator(**bash_args)

        if encryption_command != '':
            encryption = BashOperator(
                task_id=table + "_encryption",
                on_failure_callback=task_fail_slack_alert,
                pool=queue_pool,
                bash_command=encryption_command
            )

            task >> encryption #type: ignore

        else:
            task #type: ignore

    dag_model = DagModel(dag_id=dag_id)
    dag_model.set_is_paused(is_paused)

    return dag


current_path = pathlib.Path(DAGS_FOLDER).absolute()
config_dir_path = current_path.joinpath("datalake_configs")

for db in config_dir_path.glob("*.y*ml"):
    yml_conf = YAML().load(db.open("r"))

    queue_pool = "datalake"

    for table in yml_conf["tables"]:
        dag_id = "pipelines-datalake-{db}-production-to-bq.{table}".format(
            db=yml_conf["database"], table=table["name"]
        )

        if "entity" in yml_conf:
            dag_id = "pipelines-datalake-{entity}-{db}-production-to-bq.{table}".format(
            entity=yml_conf["entity"], db=yml_conf["database"], table=table["name"]
        )

        schema = ""
        pipeline_script = "scripts/pipeline_datalake_mysql.py"
        if yml_conf["type"] == "postgresql":
            pipeline_script = "scripts/pipeline_datalake_postgresql.py"
            try:
                schema = f"--schema={table['schema']}"
            except:
                schema = f"--schema={yml_conf['schema']}"

        if yml_conf["database"] == "bprs":
            pipeline_script = "scripts/pipeline_datalake_mysql_rbs.py"

        if yml_conf["database"] == "BPRS_HIJRA":
            queue_pool = "datalake_iba"
            pipeline_script = "scripts/pipeline_datalake_mssql.py"

        bash_command = "PYTHONPATH={dags} python {dags}/{pipeline_script} --db={db} {schema} --dataset={dataset} --table={table} ".format(
            dags=DAGS_FOLDER,
            pipeline_script=pipeline_script,
            db=yml_conf["database"],
            schema=schema,
            dataset=yml_conf["dataset"],
            table=table["name"],
        )

        encryption_command = ''
        if table.get("encryption", default=False):
            if yml_conf["dataset"] == 'hijra_lake':
                encryption_script = "scripts/encrypt_hijra.py"
            else:
                encryption_script = "scripts/encrypt_p2p.py"

            encryption_command = "PYTHONPATH={dags} python {dags}/{encryption_script} --dataset={dataset} --table={table}".format(
                dags=DAGS_FOLDER,
                encryption_script=encryption_script,
                dataset=yml_conf["dataset"],
                table=table["name"],
            )

        try:
            schedule = table["schedule"]
        except:
            schedule = yml_conf["schedule"]

        is_paused = table["status"] != 'on'

        globals()[dag_id] = create_dag(dag_id, bash_command, encryption_command, queue_pool, yml_conf["database"], table["name"], schedule, is_paused)
