FROM apache/airflow:3.1.5

USER root 

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \


USER airflow 

RUN pip install --no-cache-dir \
  pandas \
  s3fs \
  boto3

WORKDIR /opt/airflow 

COPY dags/ dags/
COPY preprocessing/ preprocessing

COPY scripts/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8080 5555 8793


ENTRYPOINT [ "/app/entrypoint.sh" ]
