include etc/environment.sh

sched: sched.build sched.deploy
sched.build:
	sam build --profile ${PROFILE} --template ${SCHED_TEMPLATE} --parameter-overrides ${SCHED_PARAMS} --build-dir build --manifest requirements.txt --use-container
	sam package -t build/template.yaml --output-template-file ${SCHED_OUTPUT} --s3-bucket ${S3BUCKET}
sched.deploy:
	sam deploy -t ${SCHED_OUTPUT} --stack-name ${SCHED_STACK} --parameter-overrides ${SCHED_PARAMS} --capabilities CAPABILITY_NAMED_IAM
sched.local.invoke:
	sam local invoke --profile ${PROFILE} -t build/template.yaml --parameter-overrides ${SCHED_PARAMS} --env-vars etc/environment.json -e etc/event_sched.json Fn --debug | jq
sched.invoke:
	aws --profile ${PROFILE} lambda invoke --function-name ${SCHED_FN} --invocation-type RequestResponse --payload file://etc/event.json --cli-binary-format raw-in-base64-out --log-type Tail tmp/fn.json | jq "." > tmp/response.json
	cat tmp/response.json | jq -r ".LogResult" | base64 --decode

api: api.package api.deploy
api.package:
	sam package -t ${API_TEMPLATE} --output-template-file ${API_OUTPUT} --s3-bucket ${S3BUCKET}
api.deploy:
	sam deploy -t ${API_OUTPUT} --stack-name ${API_STACK} --parameter-overrides ${API_PARAMS} --capabilities CAPABILITY_NAMED_IAM
api.local.invoke:
	sam local invoke --profile ${PROFILE} -t ${API_TEMPLATE} --parameter-overrides ${API_PARAMS} --env-vars etc/environment.json -e etc/event_api.json Fn | jq
api.local.api:
	sam local start-api -t ${API_TEMPLATE} --parameter-overrides ${API_PARAMS}
api.invoke:
	aws --profile ${PROFILE} lambda invoke --function-name ${API_FN} --invocation-type RequestResponse --payload file://etc/event.json --cli-binary-format raw-in-base64-out --log-type Tail tmp/fn.json | jq "." > tmp/response.json
	cat tmp/response.json | jq -r ".LogResult" | base64 --decode
