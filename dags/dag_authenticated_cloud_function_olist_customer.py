import logging
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.models import Variable
import json
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import google.auth



PROJECT_ID = Variable.get("PROJECT_ID")
REGION = Variable.get("REGION")
CLOUD_FUNCTION_1_NAME = Variable.get("CLOUD_FUNCTION_1_NAME")
CLOUD_FUNCTION_2_NAME = Variable.get("CLOUD_FUNCTION_2_NAME")

BUCKET = Variable.get("BUCKET_NAME")
TRANSIENT_FILE_PATH = Variable.get("TRANSIENT_FILE_PATH")
SILVER_PATH = Variable.get("SILVER_PATH")
BRONZE_PATH = Variable.get("BRONZE_PATH")
DATASET = Variable.get("BIGQUERY_DATASET")
TABLE = Variable.get("BIGQUERY_TABLE_CUSTOMER")

# Montando os dados de input
input_data_ingestion_customer = json.dumps({"bucket": BUCKET,"source-file-path": TRANSIENT_FILE_PATH,"destination-file-path": BRONZE_PATH})
input_data_transformation_customer = json.dumps({"bucket": BUCKET,"source-file-path": BRONZE_PATH,"destination-file-path": SILVER_PATH})
input_data_bigquery_ingestion_customer = json.dumps({"bucket": BUCKET,"source-file-path": SILVER_PATH,"dataset": DATASET,"table": TABLE,"project_id": PROJECT_ID})


#'https://<REGION>-<PROJECT_ID>.cloudfunctions.net/<CLOUD_FUNCTION_NAME>'
# Formar a URL da Cloud Function dinamicamente
CLOUD_FUNCTION_1_URL = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{CLOUD_FUNCTION_1_NAME}"
CLOUD_FUNCTION_2_URL = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{CLOUD_FUNCTION_2_NAME}"
CLOUD_FUNCTION_3_URL = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/{CLOUD_FUNCTION_3_NAME}"

def get_auth_token(cloud_function_url):
    credentials, project = google.auth.default()
    auth_req = Request()
    
    target_audience = cloud_function_url
    token = id_token.fetch_id_token(auth_req, target_audience)
    
    return token


# Criação da DAG
with DAG(
    'olist_cloud_function_authenticated_dag',
    default_args={'retries': 1},
    description='DAG to invoke Cloud Function',
    schedule_interval='0 8 * * *',  
    start_date=days_ago(1),
    catchup=False,
) as dag:

    auth_token_1 = get_auth_token(CLOUD_FUNCTION_1_URL)

    ingestion_customer = SimpleHttpOperator(
        task_id= 'ingestion_customer_task',
        method='POST',
        http_conn_id='http_default',
        endpoint=CLOUD_FUNCTION_1_NAME,
        execution_timeout=timedelta(seconds=600),
        headers={'Authorization': f"Bearer {auth_token_1}", "Content-Type": "application/json"},
        data=input_data_ingestion_customer, 
    )

    auth_token_2 = get_auth_token(CLOUD_FUNCTION_2_URL)


    transformation_customer = SimpleHttpOperator(
        task_id= 'transformation_customer_task',
        method='POST',
        http_conn_id='http_default',
        endpoint=CLOUD_FUNCTION_2_NAME,
        execution_timeout=timedelta(seconds=600),
        headers={'Authorization': f"Bearer {auth_token_2}", "Content-Type": "application/json"},
        data=input_data_transformation_customer, 
    )

    auth_token_3 = get_auth_token(CLOUD_FUNCTION_3_URL)


    bigquery_ingestion_customer = SimpleHttpOperator(
        task_id= 'bigquery_ingestion_customer_task',
        method='POST',
        http_conn_id='http_default',
        endpoint=CLOUD_FUNCTION_3_NAME,
        execution_timeout=timedelta(seconds=600),
        headers={'Authorization': f"Bearer {auth_token_3}", "Content-Type": "application/json"},
        data=input_data_bigquery_ingestion_customer, 
    )

    (
        ingestion_customer >> 
        transformation_customer >>
        bigquery_ingestion_customer
    )


