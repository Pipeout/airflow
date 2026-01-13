FROM apache/airflow:slim-3.1.6rc1-python3.13
#FROM apache/airflow:2.10.4-python3.11
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow
COPY --chown=airflow:0 scripts/entrypoint.sh entrypoint.sh/
COPY --chown=airflow:0 dags/ dags/
COPY --chown=airflow:0 preprocessing preprocessing/
COPY --chown=airflow:0 infra/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080 5555 8795
ENTRYPOINT [ "entrypoint.sh" ]
