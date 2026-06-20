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
    "training_orchestrator_dag",
    start_date=datetime(2025, 1, 13),
    catchup=False,
    is_paused_upon_creation=False,
    tags=["cleaning"],
) as dag:
    start = EmptyOperator(task_id="start")

    preprocessing = EcsRunTaskOperator(
        task_id="preprocessing_task_mapped",
        reattach=True,
        task_definition="preprocessing",
        overrides={},
        region_name="us-east-2",
        launch_type="FARGATE",
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": os.getenv("ECS_TARGET_SUBNETS", "").split(","),
                "securityGroups": os.getenv("ECS_TARGET_SECURITY_GROUPS", "").split(
                    ","
                ),
                "assignPublicIp": "ENABLED",
            },
        },
        cluster="pipeout-cluster",
        wait_for_completion=True,
    )

    feature_engineering = EcsRunTaskOperator(
        task_id="feature_engineering_task_mapped",
        reattach=True,
        task_definition="feature_engineering",
        overrides={},
        region_name="us-east-2",
        launch_type="FARGATE",
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": os.getenv("ECS_TARGET_SUBNETS", "").split(","),
                "securityGroups": os.getenv("ECS_TARGET_SECURITY_GROUPS", "").split(
                    ","
                ),
                "assignPublicIp": "ENABLED",
            },
        },
        cluster="pipeout-cluster",
        wait_for_completion=True,
    )
    training = EcsRunTaskOperator(
        task_id="model_training_task_mapped",
        reattach=True,
        task_definition="model_training",
        overrides={},
        region_name="us-east-2",
        launch_type="FARGATE",
        network_configuration={
            "awsvpcConfiguration": {
                "subnets": os.getenv("ECS_TARGET_SUBNETS", "").split(","),
                "securityGroups": os.getenv("ECS_TARGET_SECURITY_GROUPS", "").split(
                    ","
                ),
                "assignPublicIp": "ENABLED",
            },
        },
        cluster="pipeout-cluster",
        wait_for_completion=True,
    )

    end = EmptyOperator(task_id="end")
    start >> preprocessing >> feature_engineering >> training >> end
