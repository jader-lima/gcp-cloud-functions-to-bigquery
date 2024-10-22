########### VARIAVEIS ###########

PROJECT_ID=cloud-functions-datalake
REGION_PROJECT_ID=us-east1-cloud-functions-datalake
REGION=us-east1
ZONE=us-east1-a
BUCKET_DATALAKE=datalake_cloud_function
TRANSIENT_FILE_PATH=transient/olist/olist_customers_dataset.csv 
SILVER_PATH=silver/olist/customers/customer
BRONZE_PATH=bronze/olist/customers/customer
COMPOSER_ENV_NAME=airflow-enviroment
CLOUD_FUNCTION_1_NAME=csv_to_parquet
CLOUD_FUNCTION_2_NAME=olist_customer_transformation
SERVICE_ACCOUNT_NAME=service-account-composer
INPUT_FOLDER=transient
GS_PREFIX=gs://
CUSTOM_ROLE_NAME=customrolecomposer
CUSTOM_ROLE_TITLE="Custon Role Composer"
CUSTOM_ROLE_DESCRIPTION="Custom role for composer servless call cloud functions "
CUSTOM_ROLE_PERMISSIONS="cloudfunctions.functions.invoke,storage.objects.get,storage.objects.list,bigquery.jobs.create,bigquery.tables.get,iam.serviceAccounts.actAs"


###############criando conta de serviço e dando permissões adequadas #######################


PROJECT_ID=proj-cloud-functions-composer


PROJECT_ID=proj-cloud-functions-composer


gcloud config set project $PROJECT_ID


gcloud iam service-accounts create ci-cd-service-account \
    --description="Service account for GitHub Actions CI/CD" \
    --display-name="CI/CD Service Account"



gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:ci-cd-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"
    
gcloud iam service-accounts keys create ~/ci-cd-service-account-key.json \
    --iam-account=ci-cd-service-account@$PROJECT_ID.iam.gserviceaccount.com


gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ci-cd-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/serviceusage.serviceUsageAdmin"


gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ci-cd-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.roleAdmin"



        gcloud services enable serviceusage.googleapis.com


########################## Configurar o Projeto no GCP ############################# 
gcloud config set project $PROJECT_ID

########################## Habilitar a API de Cloud Functions ############################# 
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable composer.googleapis.com


##################################### criar buckets do projeto ####################################

gcloud storage buckets create gs://$BUCKET_DATALAKE --default-storage-class=nearline --location=$REGION


######################################  upload arquivos zip  #######################################
 

faça o file upload da pasta inputs para console GCP 


unzip inputs/inputs.zip -d inputs

###################################### copia de arquivos para bucket #########################################

TARGET=$INPUT_FOLDER
BUCKET_PATH=$BUCKET_DATALAKE/$INPUT_FOLDER
gsutil cp -r $TARGET gs://$BUCKET_PATH








########## function ###########

gcloud functions deploy csv_to_parquet \
    --cpu=.333  \
    --memory=512 \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --trigger-http --allow-unauthenticated \
    --region $REGION \
    --entry-point csv_to_parquet
    
    
    
gcloud functions deploy olist_customer_transformation \
    --cpu=.333  \
    --memory=512 \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --trigger-http --allow-unauthenticated \
    --region $REGION \
    --entry-point olist_customer_transformation



REGION_PROJECT_ID=us-east1-cloud-functions-datalake
BUCKET_DATALAKE=datalake_cloud_function

BUCKET=$BUCKET_DATALAKE
BRONZE_FILE_PATH=bronze/olist/customers/
SILVER_FILE_PATH=silver/olist/customers/

curl -m 70 -X POST https://$REGION_PROJECT_ID.cloudfunctions.net/olist_customer_transformation \
-H "Content-Type: application/json" \
-d "{
    \"bucket\": \"$BUCKET\",
    \"source-file-path\": \"$BRONZE_FILE_PATH\",
    \"destination-file-path\": \"$SILVER_FILE_PATH\"
   }"


BUCKET=$BUCKET_DATALAKE
TRANSIENT_FILE_PATH=transient/olist/olist_customers_dataset.csv
SILVER_FILE_PATH=silver/olist/customers/customer

curl -m 70 -X POST https://$REGION_PROJECT_ID.cloudfunctions.net/csv_to_parquet \
-H "Content-Type: application/json" \
-d "{
    \"bucket\": \"$BUCKET\",
    \"transient-file-path\": \"$TRANSIENT_FILE_PATH\",
    \"silver-path\": \"$SILVER_FILE_PATH\"
   }"


curl -m 70 -X POST https://$REGION_PROJECT_ID.cloudfunctions.net/olist_customer_transformation \
-H "Content-Type: application/json" \
-d "{
    \"bucket\": \"$BUCKET\",
    \"source-file-path\": \"$BRONZE_FILE_PATH\",
    \"destination-file-path\": \"$SILVER_FILE_PATH\"
   }"






########### conta de serviço para execução da cloud scheduler  #####################

gcloud iam service-accounts create  $SERVICE_ACCOUNT_NAME \
--display-name=$SERVICE_ACCOUNT_DESCRIPTION


########### cria a custon role  #####################

gcloud iam roles create $CUSTOM_ROLE_NAME --project $PROJECT_ID \
--title "$CUSTOM_ROLE_TITLE" \
--description "$CUSTOM_ROLE_DESCRIPTION" \
--permissions "$CUSTOM_ROLE_PERMISSIONS"

########### associa a custon role com a service account #####################

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member=serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com \
--role=projects/$PROJECT_ID/roles/$CUSTOM_ROLE_NAME

############ fim conta tentativa 2 ##################




########### conta de serviço para o composer ##################

gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --project $PROJECT_ID \
  --description="Service account for Google Composer environment" \
  --display-name="My Composer Service Account"


gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/composer.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker"


gcloud functions add-iam-policy-binding $CLOUD_FUNCTION_1_NAME \
  --region=$REGION \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker"

gcloud functions add-iam-policy-binding $CLOUD_FUNCTION_2_NAME \
  --region=$REGION \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker"



gcloud functions add-invoker-policy-binding $CLOUD_FUNCTION_1_NAME \
      --project=$PROJECT_ID \
      --region="us-east1" \
      --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

gcloud functions add-invoker-policy-binding $CLOUD_FUNCTION_2_NAME \
      --project=$PROJECT_ID \
      --region="us-east1" \
      --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"



# Permissão para criar e gerenciar ambientes Composer
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/composer.admin"

# Permissão para criar e configurar instâncias e recursos na VPC
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/compute.networkAdmin"

  --role="roles/storage.admin"

# Permissão para criar e gerenciar recursos no projeto, como buckets e instâncias
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/editor"

# Permissão para acessar e usar recursos necessários para o IAM
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

 Permissão para interagir com o Cloud Storage, necessário para buckets e logs
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Permissão para criar e gerenciar recursos no projeto, como buckets e instâncias
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/editor"

# Permissão para acessar e usar recursos necessários para o IAM
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"




######## AMBIENTE ########### 

gcloud config set project $PROJECT_ID


gcloud composer environments create $COMPOSER_ENV_NAME \
  --project $PROJECT_ID \
  --location $REGION \
  --environment-size small \
  --image-version composer-3-airflow-2.9.3 \
  --service-account $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

  
 ####### VARIAVEIS ############# 
  
gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set PROJECT_ID $PROJECT_ID

gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set REGION $REGION

gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set CLOUD_FUNCTION_1_NAME $CLOUD_FUNCTION_1_NAME

gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set CLOUD_FUNCTION_2_NAME $CLOUD_FUNCTION_2_NAME

gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set BUCKET_NAME $BUCKET_DATALAKE

gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set TRANSIENT_FILE_PATH $TRANSIENT_FILE_PATH 

gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set BRONZE_PATH $BRONZE_PATH


gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set SILVER_PATH $SILVER_PATH

gcloud composer environments run $COMPOSER_ENV_NAME \
  --location $REGION variables -- \
  set REGION_PROJECT_ID $REGION_PROJECT_ID


 ###################criar conexão http ##################### 

HTTP_CONNECTION=http_default
CONNECTION_TYPE=http
HOST=https://$REGION_PROJECT_ID.cloudfunctions.net


gcloud composer environments run $COMPOSER_ENV_NAME --location $REGION connections -- add $HTTP_CONNECTION --conn-type $CONNECTION_TYPE --conn-host $HOST

