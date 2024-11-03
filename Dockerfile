FROM python:3.9-alpine

RUN apk update && \
    apk add --no-cache mysql-client mariadb-connector-c-dev gcc musl-dev linux-headers

RUN pip install mysql-connector-python faker

WORKDIR /app
COPY db_create.py /app/db_create.py

CMD ["python3", "/app/db_create.py"]