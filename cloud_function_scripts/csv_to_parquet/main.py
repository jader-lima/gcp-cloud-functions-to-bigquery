import functions_framework
import json
import pandas as pd
import io
from google.cloud import storage

@functions_framework.http
def csv_to_parquet(request):
    try:
        request_json = request.get_json(silent=True)
        
        if request_json and 'bucket' in request_json and 'source-file-path' in request_json and 'destination-file-path' in request_json:
            bucket = request_json['bucket']
            source_file_path = request_json['source-file-path']
            destination_file_path = request_json['destination-file-path']

            client = storage.Client()
            bucket = client.bucket(bucket)
            
            blob = bucket.blob(source_file_path)
            csv_data = blob.download_as_text()
            
            df = pd.read_csv(io.StringIO(csv_data))

            parquet_buffer = io.BytesIO()
            
            df.to_parquet(parquet_buffer, index=False, engine='pyarrow')
            
            parquet_buffer.seek(0)

            output_blob = bucket.blob(destination_file_path + '.parquet')

            output_blob.upload_from_file(parquet_buffer, content_type='application/octet-stream')

            return f'Processo Concluido, verifique o resultado!', 200

        else:
            return 'Requisição inválida: Campos requeridos não encontrados', 400
    except Exception as e:
        return f'Erro: {str(e)}', 500
