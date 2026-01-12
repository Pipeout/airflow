FROM python:3.13-slim 

WORKDIR /app

COPY infra/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

    
COPY . .
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8080 5555 8793


ENTRYPOINT [ "/app/entrypoint.sh" ]