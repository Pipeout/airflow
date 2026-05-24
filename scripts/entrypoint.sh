#!/bin/bash
set -e # Stop script immediately if any command fails

echo "Constraint: Initializing the Airflow database..."
airflow db migrate

echo "Constraint: Creating Admin User..."

echo "Constraint: Starting Airflow Standalone (Webserver + Scheduler)..."
# 'exec' ensures Airflow becomes the main process (PID 1) of the container
exec airflow standalone
