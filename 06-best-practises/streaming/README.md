## Machine Learning for Streaming

* Scenario
* Creating the role 
* Create a Lambda function, test it
* Create a Kinesis stream
* Connect the function to the stream
* Send the records 

Links

* [Tutorial: Using Amazon Lambda with Amazon Kinesis](https://docs.amazonaws.cn/en_us/lambda/latest/dg/with-kinesis-example.html)

## Code snippets

### Sending data


```bash
KINESIS_STREAM_INPUT=credit_default_pred_events 
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data "Hi Kinesis, this is a test stream"
```

Decoding base64

```python
base64.b64decode(data_encoded).decode('utf-8')
```

Record example

```json
{
    "data": {
      "AGE_GROUP": "Youth",
      "YEARS_EMPLOYED_GROUP": "1-5 yrs",
      "PHONE_CHANGE_GROUP": "moderate",
      "REGION_RATING_CLIENT_W_CITY": 2,
      "REGION_RATING_CLIENT": 1,
      "EXT_SOURCE_3": 0.789,
      "EXT_SOURCE_2": 0.621,
      "EXT_SOURCE_1": 0.513,
      "FLOORSMAX_AVG": 0.8
    },
    "data_id": 101
  }
```

Sending this record

```bash
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data '{
        "data": {
      "AGE_GROUP": "Youth",
      "YEARS_EMPLOYED_GROUP": "1-5 yrs",
      "PHONE_CHANGE_GROUP": "moderate",
      "REGION_RATING_CLIENT_W_CITY": 2,
      "REGION_RATING_CLIENT": 1,
      "EXT_SOURCE_3": 0.789,
      "EXT_SOURCE_2": 0.621,
      "EXT_SOURCE_1": 0.513,
      "FLOORSMAX_AVG": 0.8
    },
    "data_id": 101
    }'
```

### Test event


```json
{
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49666265866161364034461169801489458194645781087095095298",
                "data": "ewogICAgICAgICJkYXRhIjogewogICAgICAiQUdFX0dST1VQIjogIllvdXRoIiwKICAgICAgIllFQVJTX0VNUExPWUVEX0dST1VQIjogIjEtNSB5cnMiLAogICAgICAiUEhPTkVfQ0hBTkdFX0dST1VQIjogIm1vZGVyYXRlIiwKICAgICAgIlJFR0lPTl9SQVRJTkdfQ0xJRU5UX1dfQ0lUWSI6IDIsCiAgICAgICJSRUdJT05fUkFUSU5HX0NMSUVOVCI6IDEsCiAgICAgICJFWFRfU09VUkNFXzMiOiAwLjc4OSwKICAgICAgIkVYVF9TT1VSQ0VfMiI6IDAuNjIxLAogICAgICAiRVhUX1NPVVJDRV8xIjogMC41MTMsCiAgICAgICJGTE9PUlNNQVhfQVZHIjogMC44CiAgICB9LAogICAgImRhdGFfaWQiOiAxMDEKICAgIH0=",
                "approximateArrivalTimestamp": 1755574559.151
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000000:49666265866161364034461169801489458194645781087095095298",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::928475935048:role/lambda-kinesis-iam-role",
            "awsRegion": "eu-west-1",
            "eventSourceARN": "arn:aws:kinesis:eu-west-1:928475935048:stream/credit_default_pred_events"
        }
    ]
}
```

### Reading from the stream

```bash
KINESIS_STREAM_OUTPUT='credit_default_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode
``` 


### Running the test

```bash
export PREDICTIONS_STREAM_NAME="credit_default_predictions"
export RUN_ID="fe69b7b9817240789feb57c59ff31cc5"
export TEST_RUN="True"

python test_event.py
```

### Putting everything to Docker

URL for testing:

* http://localhost:8080/2015-03-31/functions/function/invocations

```bash
docker build -t credit_default_predictions_stream:v1 .
```

```bash
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile default)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile default)
export AWS_DEFAULT_REGION=$(aws configure get region --profile default)
```

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e PREDICTIONS_STREAM_NAME="credit_default_predictions" \
    -e RUN_ID="fe69b7b9817240789feb57c59ff31cc5" \
    -e TEST_RUN="True" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    credit_default_predictions_stream:v1
```
### Pushing Docker images to ECR

Creating an ECR repo

```bash
aws ecr create-repository --repository-name credit-default-prediction-model 
```

Logging in

```bash
$(aws ecr get-login --no-include-email)
```

Pushing 

```bash
REMOTE_URI="928475935048.dkr.ecr.eu-west-1.amazonaws.com/credit-default-prediction-model"
REMOTE_TAG="v1"
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE="credit_default_predictions_stream:v1"
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```
```
echo $REMOTE_IMAGE
``

Test with ECR, lambda, kinesis, configured IAM s3 policy
```bash
KINESIS_STREAM_INPUT=credit_default_pred_events 
```

```bash
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --data '{
        "data": {
      "AGE_GROUP": "Youth",
      "YEARS_EMPLOYED_GROUP": "1-5 yrs",
      "PHONE_CHANGE_GROUP": "moderate",
      "REGION_RATING_CLIENT_W_CITY": 2,
      "REGION_RATING_CLIENT": 1,
      "EXT_SOURCE_3": 0.789,
      "EXT_SOURCE_2": 0.621,
      "EXT_SOURCE_1": 0.513,
      "FLOORSMAX_AVG": 0.8
    },
    "data_id": 101
    }'
```

```bash
KINESIS_STREAM_OUTPUT='credit_default_predictions'
SHARD='shardId-000000000000'

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT}
``` 

```bash
echo "eyJtb2RlbCI6ICJjcmVkaXQtZGVmYXVsdC1yaXNrLXByZWRpY3Rpb24iLCAidmVyc2lvbiI6ICJ2MS4wIiwgInByZWRpY3Rpb24iOiB7ImRhdGFfaWQiOiAxMDAxLCAiZGVmYXVsdF9wcm9iYWJpbGl0eSI6IDAuMDY4MzI2NTYyNjQzMDUxMTUsICJkZWZhdWx0X3Jpc2siOiAiTG93In19" | base64 -d | jq
```