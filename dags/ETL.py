import os
import sys

import requests

sys.path.append("/opt/airflow")
from datetime import datetime

from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.trigger_dagrun import (
    TriggerDagRunOperator,
)
from airflow.sdk import DAG, task

TRAINING_URL = "http://training:8081/training"
FEATURE_ENGINEERING_URL = "http://feature_engineering:8001/feature_engineering"

with DAG(
    "orchestrator_dag",
    start_date=datetime(2025, 1, 13),
    catchup=False,
    is_paused_upon_creation=False,
    tags=["cleaning"],
) as dag:
    start = EmptyOperator(task_id="start")

    feature_engineering = EcsRunTaskOperator(
        task_id="feature_engineering_task",
        reattach=True,
        task_definition="feature_engineering",
        overrides={},
        launch_type="FARGATE",
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": ["subnet-0bb7d7337317f5166", "subnet-0b4ddab295713df12"],
                "securityGroups": "sg-0a51e609c6dc78d75",
                "assignPublicIp": "ENABLED",
            },
        },
        cluster="pipeout-cluster",
        wait_for_completion=True,
    )

    end = EmptyOperator(task_id="end")

    start >> feature_engineering >> training >> end


with DAG(
    "training_dag",
    description="Dag that will train the models once the datasets are properly clean",
    start_date=datetime(2025, 1, 13),
    catchup=False,
    is_paused_upon_creation=False,
    tags=["training"],
) as training_dag:
    start = EmptyOperator(task_id="start")

    @task(task_id="train")
    def run_training():
        requests.post(TRAINING_URL)

    end = EmptyOperator(task_id="end")

    start >> run_training() >> end
