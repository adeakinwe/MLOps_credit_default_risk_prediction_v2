``` INFRASTRUCTURE AS CODE - TERRAFORM ```

```bash
terraform init

terraform plan

terraform apply -var-file=vars/stg.tfvars
```

```bash
chmod +x deploy.sh

deploy.sh
```

```bash
export KINESIS_STREAM_INPUT=src-stream-tf-credit-default-risk-prediction
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
    "data_id": 102
    }'
```