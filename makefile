include etc/environment.sh

sam: sam.package sam.deploy
sam.package:
	sam package -t ${TEMPLATE} --output-template-file ${OUTPUT} --s3-bucket ${S3BUCKET}
sam.deploy:
	sam deploy -t ${OUTPUT} --stack-name ${STACK} --parameter-overrides ${PARAMS} --capabilities CAPABILITY_NAMED_IAM
sam.local.invoke:
	sam local invoke -t ${TEMPLATE} --parameter-overrides ${PARAMS} --env-vars etc/environment.json -e etc/event.json Fn | jq
sam.local.api:
	sam local start-api -t ${TEMPLATE} --parameter-overrides ${PARAMS}
lambda.invoke:
	aws --profile ${PROFILE} lambda invoke --function-name ${FN} --invocation-type RequestResponse --payload file://etc/event.json --cli-binary-format raw-in-base64-out --log-type Tail tmp/fn.json | jq "." > tmp/response.json
	cat tmp/response.json | jq -r ".LogResult" | base64 --decode
