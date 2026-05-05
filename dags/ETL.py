import os
import sys

import requests

sys.path.append("/opt/airflow")
from datetime import datetime, timedelta

from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.trigger_dagrun import (
    TriggerDagRunOperator,
)
from airflow.sdk import DAG, task
from preprocessing.jobs.cleaning import cleaning_pipeline
from preprocessing.jobs.selection import selection_pipeline

TRAINING_URL = "http://train:8081/train"

with DAG(
    "preprocessing",
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="Dag that will clean the datasets and make them available to training",
    schedule=timedelta(days=1),
    start_date=datetime(2025, 1, 13),
    catchup=False,
    is_paused_upon_creation=False,
    tags=["cleaning"],
) as dag:
    start = EmptyOperator(task_id="start")

    @task(task_id="cleaning")
    def run_cleaning():
        cleaning_pipeline()

    @task(task_id="selection")
    def run_selection():
        selection_pipeline()

    trigger_training = TriggerDagRunOperator(
        task_id="trigger_training",
        trigger_dag_id="training_dag",
        wait_for_completion=True,
    )

    end = EmptyOperator(task_id="end")

    start >> run_cleaning() >> run_selection() >> trigger_training >> end


with DAG(
    "training_dag",
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="Dag that will train the models once the datasets are properly clean",
    schedule=timedelta(days=1),
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
