FROM apache/airflow:3.1.5-python3.10
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow
COPY --chown=airflow:0 scripts/entrypoint.sh entrypoint.sh
COPY --chown=airflow:0 dags/ dags/
COPY --chown=airflow:0 preprocessing preprocessing/
COPY --chown=airflow:0 infra/requirements.txt requirements.txt

RUN pip install --no-cache-dir "apache-airflow-providers-fab" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.1.5/constraints-3.10.txt" \
  && pip install --no-cache-dir -r requirements.txt 
RUN chmod +x entrypoint.sh
EXPOSE 8080 5555 8795
ENTRYPOINT [ "./entrypoint.sh" ]
