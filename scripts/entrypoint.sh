#!/bin/bash
set -e # Stop script immediately if any command fails

echo "Constraint: Initializing the Airflow database..."
airflow db migrate

echo "Constraint: Creating Admin User..."
# Only create the user if it doesn't exist yet to avoid errors on restart
# if ! airflow users list | grep -q "admin"; then
#     airflow users create \
#     --username admin \
#     --firstname Admin \
#     --lastname User \
#     --role Admin \
#     --email admin@example.com \
#     --password admin
#     echo "Admin user created: admin / admin"
# else
#     echo "Admin user already exists."
# fi

echo "Constraint: Starting Airflow Standalone (Webserver + Scheduler)..."
# 'exec' ensures Airflow becomes the main process (PID 1) of the container
exec airflow standalone