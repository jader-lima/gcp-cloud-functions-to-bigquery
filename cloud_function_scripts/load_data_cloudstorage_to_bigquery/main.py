import functions_framework
import json
import pandas as pd
import io
from google.cloud import storage
import pandas_gbq


@functions_framework.http
def load_data_cloudstorage_to_bigquery(request):
    try:
        request_json = request.get_json(silent=True)
        
        if request_json and 'bucket' in request_json and 'source-file-path' in request_json and 'dataset' in request_json and 'table' in request_json and 'project_id' in request_json:
            bucket_name = request_json['bucket']
            source_file_path = request_json['source-file-path']  # path sem wildcard
            dataset = request_json['dataset']
            table = request_json['table']
            project_id  = request_json['project_id']

            # Criação do cliente de storage
            client = storage.Client()
            bucket = client.bucket(bucket_name)

            # Listar todos os arquivos .parquet no caminho fornecido (subdiretório)
            blobs = bucket.list_blobs(prefix=source_file_path)

            # Processar cada arquivo .parquet
            bq_destination = f"{dataset}.{table}"
            for blob in blobs:
                if blob.name.endswith('.parquet'):
                    parquet_data = blob.download_as_bytes()
                    df = pd.read_parquet(io.BytesIO(parquet_data))

                    # Fazer algum processamento no DataFrame (df)
                    # Exemplo: Processamento de transformação dos dados

                    # Preparar para salvar no diretório de destino
                    parquet_buffer = io.BytesIO()
                    df.to_parquet(parquet_buffer, index=False, engine='pyarrow')

                    # Write DataFrame to BigQuery
                    pandas_gbq.to_gbq(df, bq_destination, project_id=project_id, if_exists='replace', chunksize=5000)
                   

            return f'Todos os arquivos .parquet foram processados e salvos em {bq_destination}', 200

        else:
            return 'Requisição inválida: Campos requeridos não encontrados', 400
    except Exception as e:
        return f'Erro: {str(e)}', 500


