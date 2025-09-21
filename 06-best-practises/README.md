```bash
docker build -t credit_default_predictions_stream:v2 .
```

```TESTING WITH DOCKER FOR LOCALLY SAVED MODEL```

```bash
aws s3 cp --recursive s3://mlflow-credit-default-risk-prediction-artifact-store-v2/fe69b7b9817240789feb57c59ff31cc5/artifacts/ model
```

```bash
export LOCAL=true
```

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e MODEL_LOCATION="/app/model" \
    -e LOCAL="true" \
    -v $(pwd)/model:/app/model \
    credit_default_predictions_stream:v2
```

```TESTING WITH DOCKER FOR MODEL SAVED IN S3```

```bash
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile default)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile default)
export AWS_DEFAULT_REGION=$(aws configure get region --profile default)
export PREDICTIONS_STREAM_NAME=credit_default_predictions
export RUN_ID=fe69b7b9817240789feb57c59ff31cc5
export LOCAL=false
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
    credit_default_predictions_stream:v2
```

```bash
pip install -r requirements-test.txt
```

```bash
git init

pre-commit sample-config > .pre-commit-config.yaml

pre-commit install
```

```bash
chmod +x integration_test/run-make.sh

integration_test/run-make.sh
```

``` INFRASTRUCTURE AS CODE - TERRAFORM```
```bash
terraform init

terraform plan

terraform apply
```