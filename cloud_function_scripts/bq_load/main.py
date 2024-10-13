from google.cloud import bigquery
import functions_framework
import json

@functions_framework.http
def load_data_cloudstorage_to_bigquery(request):
    try:
        # Obtendo o corpo da requisição como JSON
        request_json = request.get_json(silent=True)
        
        # Verifica se os campos necessários estão presentes
        if request_json and 'table_id' in request_json and 'uri' in request_json and 'tablefields' in request_json:
            # Extraindo as variáveis 'table_id' e 'uri'
            table_id_param = request_json['table_id']
            uri_param = request_json['uri']
            query_param = request_json['query']
            
            # Extraindo o array de 'tablefields' e preenchendo a lista 'schema'
            tablefields = request_json['tablefields']
            table_schema = []
            for field in tablefields:
                table_schema.append(bigquery.SchemaField(field, "STRING"))

            # Aqui você pode implementar o código para realizar a operação no BigQuery
            # Por exemplo, criar a tabela ou carregar dados

            client = bigquery.Client()
            job_config = bigquery.LoadJobConfig(
                schema=table_schema,
                skip_leading_rows=0,
                # The source format defaults to CSV, so the line below is optional.
                source_format=bigquery.SourceFormat.CSV,
            )

            table_id = table_id_param
            uri = uri_param

            load_job = client.load_table_from_uri(
            uri, table_id, job_config=job_config
            )

            load_job.result()  # Waits for the job to complete.

            destination_table = client.get_table(table_id)

            #query = """CALL dataset.proc_output()"""
            query = """CALL {}""".format(query_param)
            client.query(query)


            print("Total de  {} Linhas carregadas no processo.".format(destination_table.num_rows))
            return f'Processo Concluido, verifique o resultado !',200

        else:
            return 'Requisição inválida: Campos requeridos não encontrados', 400

    except Exception as e:
        return f'Erro: {str(e)}', 500

