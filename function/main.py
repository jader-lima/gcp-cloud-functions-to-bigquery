from googleapiclient.discovery import build
import functions_framework
import json

@functions_framework.http
def create_dataflow_job(request):
    try:
        # Parse JSON da requisição
        request_json = request.get_json(silent=True)
        
        # Verificar se todos os parâmetros obrigatórios estão presentes
        required_params = ['project', 'job', 'template', 'parameters', 'worker_machine_type', 'num_workers', 'max_workers', 'staging_location', 'temp_location', 'region']
        if request_json and all(param in request_json for param in required_params):
            
            project_param = request_json['project']
            job_param = request_json['job']
            template_param = request_json['template']
            parameters_param = request_json['parameters']
            worker_machine_type_param = request_json['worker_machine_type']
            num_workers_param = request_json['num_workers']
            max_workers_param = request_json['max_workers']
            staging_location_param = request_json['staging_location']
            temp_location_param = request_json['temp_location']
            region_param = request_json['region']  

            # Cria o serviço Dataflow com o endpoint correto
            dataflow = build("dataflow", "v1b3")
            request = (
                dataflow.projects()
                .locations()
                .templates()
                .launch(
                    projectId=project_param,
                    location=region_param,  # Certifique-se de que o `region_param` contém o local válido (ex: us-east1)
                    gcsPath=template_param,
                    body={
                        "jobName": job_param,
                        "parameters": parameters_param,
                        "environment": {
                            "tempLocation": temp_location_param,  # Local temporário
                            "machineType": worker_machine_type_param,  # Tipo de máquina
                            "numWorkers": num_workers_param,  # Número de workers mínimos
                            "maxWorkers": max_workers_param,  # Número máximo de workers
                        },
                    },
                )
            )

            response = request.execute()
            return f'Process Finished! Job created, verify Google Dataflow in some minutes!', 200

        else:
            return 'Invalid Requisition: Verify all fields in requisition body!', 400

    except Exception as e:
        return f'Error: {str(e)}', 500
