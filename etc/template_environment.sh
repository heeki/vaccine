S3BUCKET=bucket-for-sam-deployments
PROFILE=aws-cli-profile

SCHED_STACK=vaccine-lambda
SCHED_TEMPLATE=iac/lambda.yaml
SCHED_OUTPUT=iac/lambda_output.yaml
P_EMAIL="your_email@example.com"
P_ISENABLED="ENABLED"
SCHED_PARAMS="ParameterKey=emailAddress,ParameterValue=${P_EMAIL} ParameterKey=isEnabled,ParameterValue=${P_ISENABLED}"
SCHED_FN=vaccine-lambda-Fn-XXXXXXXXXXXXX

API_STACK=vaccine-api
API_TEMPLATE=iac/apigw.yaml
API_OUTPUT=iac/apigw_output.yaml
P_STAGE=dev
P_SWAGGER_BUCKET=bucket-for-swagger-specs
$(eval P_SWAGGER_KEY=$(shell shasum -a 256 iac/swagger.yaml | awk '{print $$1}'))
P_AUTHSIMPLE=false
P_PVERSION=2.0
API_PARAMS="ParameterKey=apiStage,ParameterValue=${P_STAGE} ParameterKey=swaggerBucket,ParameterValue=${P_SWAGGER_BUCKET} ParameterKey=swaggerKey,ParameterValue=${P_SWAGGER_KEY} ParameterKey=enableSimple,ParameterValue=${P_AUTHSIMPLE} ParameterKey=payloadVersion,ParameterValue=${P_PVERSION}"
API_FN=vaccine-api-Fn-XXXXXXXXXXXXX
