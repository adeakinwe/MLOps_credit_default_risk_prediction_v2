import json
import os
import boto3
import base64
import pickle
import xgboost as xgb

# --- CONFIG ---
s3_client = boto3.client("s3")
S3_BUCKET = "mlflow-credit-default-risk-prediction-artifact-store-v2"
RUN_ID = os.getenv("RUN_ID")  # Must be set in Lambda env vars

MODEL_KEY = f"{RUN_ID}/artifacts/xgb_credit_pred.bin"

PREDICTIONS_STREAM_NAME = os.getenv("PREDICTIONS_STREAM_NAME", "ride_predictions")
TEST_RUN = os.getenv("TEST_RUN", "false").lower() == "true"

s3_client = boto3.client("s3")
kinesis_client = boto3.client("kinesis")

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


# === Lambda Handler ===
def lambda_handler(event, context):
    predictions = []
    try:
        print("Incoming event:", json.dumps(event)[:500])  # truncate long logs

        # Case 1: Kinesis Event
        if "Records" in event:
            for record in event["Records"]:
                encoded_data = record["kinesis"]["data"]
                decoded_data = base64.b64decode(encoded_data).decode("utf-8")
                credit_pred_event = json.loads(decoded_data)

                data = credit_pred_event["data"]
                data_id = credit_pred_event.get("data_id", "N/A")

                prob = predict(data)

                prediction_event = {
                    "model": "credit-default-risk-prediction",
                    "version": "v1.0",
                    "prediction": {
                        "data_id": data_id,
                        "default_probability": prob,
                        "default_risk": "High" if prob >= 0.5 else "Low",
                    },
                }

                if not TEST_RUN:
                    kinesis_client.put_record(
                        StreamName=PREDICTIONS_STREAM_NAME,
                        Data=json.dumps(prediction_event),
                        PartitionKey=str(data_id),
                    )

                predictions.append(prediction_event)

        # Case 2: Direct Test Event
        else:
            features = event.get("data") or event.get("features") or event
            if not isinstance(features, dict):
                raise ValueError("Invalid input format. Must be a dict.")

            data_id = event.get("data_id", "test-event")
            prob = predict(features)

            prediction_event = {
                "model": "credit-default-risk-prediction",
                "version": "v1.0",
                "prediction": {
                    "data_id": data_id,
                    "default_probability": prob,
                    "default_risk": "High" if prob >= 0.5 else "Low",
                },
            }
            predictions.append(prediction_event)

        return {
            "statusCode": 200,
            "predictions": predictions
        }

    except Exception as e:
        print("Error during prediction:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }