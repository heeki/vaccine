S3BUCKET=bucket_for_sam_deployments
PROFILE=aws_cli_profile
STACK=stack_name
TEMPLATE=iac/lambda.yaml
OUTPUT=iac/lambda_output.yaml
P_EMAIL="your_email@example.com"
PARAMS="ParameterKey=emailAddress,ParameterValue=${P_EMAIL}"
