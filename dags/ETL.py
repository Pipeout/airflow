
import os
import sys

sys.path.append("/opt/airflow")
from datetime import datetime, timedelta

from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import DAG, task

from preprocessing.jobs.cleaning import cleaning_pipeline
from preprocessing.jobs.selection import selection_pipeline

with DAG (
  "preprocessing",

  default_args={
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
  },
  description="Dag that will clean the datasets and make them available to training",
  schedule=timedelta(days=1),
  start_date=datetime(2025, 1, 13),
  catchup=False,
  is_paused_upon_creation=False,
  tags=['cleaning']

) as dag:

  start = EmptyOperator(task_id="start")

  @task(task_id='cleaning')
  def run_cleaning():
    cleaning_pipeline()

  @task(task_id='selection')
  def run_selection():
    selection_pipeline()

  end = EmptyOperator(task_id="end")

  start >> run_cleaning() >> run_selection() >> end
