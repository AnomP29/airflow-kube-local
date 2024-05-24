import datetime

from typing import Optional

from airflow import DAG
from airflow.configuration import conf
from airflow.utils.trigger_rule import TriggerRule

# from dependencies.slack_notification import task_fail_slack_alert


DAGS_FOLDER = conf.get("core", "dags_folder")


# def make_dbt_task(
#     dag: DAG,
#     task_id: str,
#     command: str,
#     selector: Optional[str] = None,
#     vars: Optional[str] = None,
#     threads: Optional[int] = None,
#     trigger_rule: TriggerRule = TriggerRule.ALL_DONE,
# ):
#     from airflow.providers.cncf.kubernetes.operators.pod import (
#         KubernetesPodOperator,
#     )
#     from kubernetes.client import models as k8s

#     args = ["--no-write-json", "--no-use-colors", command]
#     if selector:
#         args += ["--select", selector]
#     if vars:
#         args += ["--vars", vars]
#     if threads:
#         args += ["--threads", str(threads)]
#     return KubernetesPodOperator(
#         dag=dag,
#         name=task_id,
#         task_id=task_id,
#         trigger_rule=trigger_rule,
#         execution_timeout=datetime.timedelta(hours=2),
#         startup_timeout_seconds=3600,
#         on_failure_callback=task_fail_slack_alert,
#         namespace="airflow-prod",
#         image="asia.gcr.io/alami-group-data/dbt-model:latest",
#         image_pull_policy="Always",
#         random_name_suffix=True,
#         get_logs=True,
#         in_cluster=True,
#         annotations={
#             "cluster-autoscaler.kubernetes.io/safe-to-evict": "true",
#         },
#         node_selector={
#             "iam.gke.io/gke-metadata-server-enabled": "true",
#             "cloud.google.com/gke-nodepool": "preemptible-pool-e2",
#         },
#         container_resources=k8s.V1ResourceRequirements(
#             requests={"cpu": "200m", "memory": "256Mi"}
#         ),
#         service_account_name="composer-cluster-sa",
#         env_vars=[
#             k8s.V1EnvVar(
#                 "EXECUTION_DATE",
#                 "{{ (dag_run.logical_date + macros.timedelta(days=1)) | ts }}",
#             )
#         ],
#         arguments=args,
#     )
