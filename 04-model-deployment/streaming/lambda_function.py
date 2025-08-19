import json
import os
import boto3
import pickle
import xgboost as xgb

# --- S3 CONFIG ---
s3_client = boto3.client("s3")
S3_BUCKET = "mlflow-credit-default-risk-prediction-artifact-store-v2"
RUN_ID = os.getenv("RUN_ID")  # Must be set in Lambda env vars

MODEL_KEY = f"{RUN_ID}/artifacts/xgb_credit_pred.bin"

# --- LOAD MODEL FROM S3 ONCE (outside handler) ---
print("Loading model bundle from S3...")
response = s3_client.get_object(Bucket=S3_BUCKET, Key=MODEL_KEY)
model_bundle = pickle.load(response["Body"])

model = model_bundle["model"]         # XGBoost Booster
dv = model_bundle["vectorizer"]       # DictVectorizer

print("Model and vectorizer loaded successfully.")


# --- PREDICT FUNCTION ---
def predict(features: dict) -> float:
    """
    Transform features with DictVectorizer and
    run XGBoost Booster prediction.
    Returns probability of default (float).
    """
    X = dv.transform([features])       # sparse matrix
    dmatrix = xgb.DMatrix(X)
    prediction = model.predict(dmatrix)[0]  # probability of class 1
    return float(prediction)


# --- LAMBDA HANDLER ---
def lambda_handler(event, context):
    """
    AWS Lambda entrypoint.
    event is expected to have 'features' key with dict of input features.
    """
    try:
        features = event["data"]
        probability = predict(features)

        result = {
            "default_probability": probability,
            "label": int(probability >= 0.5)  # threshold at 0.5
        }

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        print("Error during prediction:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }