FROM python:3.13-slim

WORKDIR /app


RUN pip install --no-cache-dir \
  airflow \
  pandas \
  s3fs \
  boto3

COPY . .
COPY scripts/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8080 5555 8793


ENTRYPOINT [ "/app/entrypoint.sh" ]
