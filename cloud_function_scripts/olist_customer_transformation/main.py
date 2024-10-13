import functions_framework
import json
import pandas as pd
import io
from google.cloud import storage

@functions_framework.http
def olist_customer_transformation(request):
    try:
        request_json = request.get_json(silent=True)
        
        if request_json and 'bucket' in request_json and 'source-file-path' in request_json and 'destination-file-path' in request_json:
            bucket_name = request_json['bucket']
            source_file_path = request_json['source-file-path']  # path sem wildcard
            destination_file_path = request_json['destination-file-path']

            # Criação do cliente de storage
            client = storage.Client()
            bucket = client.bucket(bucket_name)

            # Listar todos os arquivos .parquet no caminho fornecido (subdiretório)
            blobs = bucket.list_blobs(prefix=source_file_path)

            # Processar cada arquivo .parquet
            for blob in blobs:
                if blob.name.endswith('.parquet'):
                    parquet_data = blob.download_as_bytes()
                    df = pd.read_parquet(io.BytesIO(parquet_data))

                    # Fazer algum processamento no DataFrame (df)
                    # Exemplo: Processamento de transformação dos dados

                    # Preparar para salvar no diretório de destino
                    parquet_buffer = io.BytesIO()
                    df.to_parquet(parquet_buffer, index=False, engine='pyarrow')

                    parquet_buffer.seek(0)

                    output_blob = bucket.blob(f"{destination_file_path}/{blob.name.split('/')[-1]}")

                    # Fazer upload do arquivo processado
                    output_blob.upload_from_file(parquet_buffer, content_type='application/octet-stream')

            return f'Todos os arquivos .parquet foram processados e salvos em {destination_file_path}', 200

        else:
            return 'Requisição inválida: Campos requeridos não encontrados', 400
    except Exception as e:
        return f'Erro: {str(e)}', 500
