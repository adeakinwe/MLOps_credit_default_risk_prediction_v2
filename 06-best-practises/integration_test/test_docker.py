import requests
import json

event = {
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

url = "http://localhost:8080/2015-03-31/functions/function/invocations"
response = requests.post(url, json=event)
actual_response = response.json()
print(json.dumps(actual_response, indent=2))

expected_response = {
    'predictions': [
        {'statusCode': 200,
         'data_id': 101,
         'default_probability': 0.07159064710140228,
         'default_risk': 'Low'
         }
    ]
}

assert actual_response == expected_response
