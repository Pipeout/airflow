import os
import sys

import requests

sys.path.append("/opt/airflow")
from datetime import datetime

import boto3
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.trigger_dagrun import (
    TriggerDagRunOperator,
)
from airflow.sdk import DAG, task

with DAG(
    "orchestrator_dag",
    start_date=datetime(2025, 1, 13),
    catchup=False,
    is_paused_upon_creation=False,
    tags=["cleaning"],
) as dag:
    start = EmptyOperator(task_id="start")
    ssm = boto3.client("ssm")

    subnets = ssm.get_parameter(Name="/myapp/ecs/subnets")["Parameter"]["Value"].split(
        ","
    )
    sgs = [
        ssm.get_parameter(Name="/myapp/ecs/feature_engineering/security_group")[
            "Parameter"
        ]["Value"]
    ]

    feature_engineering = EcsRunTaskOperator(
        task_id="feature_engineering_task",
        reattach=True,
        task_definition="feature_engineering",
        overrides={
            "containerOverrides": [
                {
                    "name": "feat-eng-container",  # just the name, no actual overrides
                }
            ]
        },
        launch_type="FARGATE",
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": subnets,
                "securityGroups": sgs,
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
