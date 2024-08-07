FROM localhost:5000/airflow:v1

COPY requirements.txt /

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
