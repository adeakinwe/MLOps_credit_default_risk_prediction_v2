import os
import json
import base64
import boto3
import pickle
import xgboost as xgb
from sklearn.feature_extraction import DictVectorizer

# Define columns
cat_cols = ['AGE_GROUP', 'YEARS_EMPLOYED_GROUP', 'PHONE_CHANGE_GROUP']
num_cols = [
    'REGION_RATING_CLIENT_W_CITY',
    'REGION_RATING_CLIENT',
    'EXT_SOURCE_3',
    'EXT_SOURCE_2',
    'EXT_SOURCE_1',
    'FLOORSMAX_AVG'
]

# S3 bucket where artifacts are stored
S3_BUCKET = "mlflow-credit-default-risk-prediction-artifact-store-v2"
REGION = "eu-west-1"

s3_client = boto3.client("s3", region_name=REGION)

RUN_ID = os.getenv("RUN_ID")
print("RUN_ID:", RUN_ID)


def get_model_location(run_id: str) -> str:
    is_local = os.getenv("LOCAL", "false").lower() == "true"
    if is_local:
        """
        Returns the S3 key for the saved XGBoost model artifact.
        """
        print(">>>LOCAL PATH")
        model_location = os.getenv("MODEL_LOCATION")
        if model_location:
            return model_location
    else:
        """
        Returns the S3 key for the saved XGBoost model artifact.
        """
        print(">>>Fetching from S3 Bucket")
        return f"{run_id}/artifacts/xgb_credit_pred.bin"

def load_model(run_id: str = None, local: bool = False):
    """
    Loads XGBoost Booster + DictVectorizer.
    If `local=True`, loads from integration_test/model/.
    Otherwise, downloads from S3 using run_id.
    """
    if local:
        print("🔧 Running in LOCAL mode")
        # Local mode (Docker / integration tests)
        model_dir = os.getenv("MODEL_LOCATION", "integration_test/model")
        model_filename = os.getenv("MODEL_FILENAME", "xgb_credit_pred.bin")
        model_path = os.path.join(model_dir, model_filename)

        print(f"📂 Looking for model file at: {os.path.abspath(model_path)}")
        model_path = os.path.join("integration_test", "model", "xgb_credit_pred.bin")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Model file not found at {os.path.abspath(model_path)}")
        with open(model_path, "rb") as f:
            model_bundle = pickle.load(f)
    else:
        print("☁️ Running in S3/production mode")
        # Load from S3
        model_key = get_model_location(run_id)
        print(f"📥 Downloading model from s3://{S3_BUCKET}/{model_key}")

        region = os.getenv("AWS_DEFAULT_REGION") or "eu-west-1"
        s3_client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        response = s3_client.get_object(Bucket=S3_BUCKET, Key=model_key)
        model_bundle = pickle.load(response["Body"])

    booster: xgb.Booster = model_bundle["model"]
    dv: DictVectorizer = model_bundle["vectorizer"]

    print("✅ Model and vectorizer loaded successfully")
    return booster, dv


def prep_features(data: dict):
    features = {}
    for col in cat_cols:
        features[col] = str(data.get(col, ""))
    for col in num_cols:
        val = data.get(col)
        try:
            features[col] = float(val) if val is not None else 0.0
        except (ValueError, TypeError):
            features[col] = 0.0
    return features

def base64_decode(encoded_data: str):
    decoded_data = base64.b64decode(encoded_data).decode("utf-8")
    json_data = json.loads(decoded_data)
    return json_data


class ModelService:
    def __init__(self, booster, dv, model_version=None, callbacks=None):
        self.booster = booster
        self.dv = dv
        self.model_version = model_version
        self.callbacks = callbacks or []

    def prepare_features(self, data: dict):
        features = {}
        for col in cat_cols:
            features[col] = str(data.get(col, ""))
        for col in num_cols:
            val = data.get(col)
            try:
                features[col] = float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                features[col] = 0.0
        return features

    def predict(self, features: dict) -> float:
        X = self.dv.transform([features])  # sparse
        dmatrix = xgb.DMatrix(X)
        prob = self.booster.predict(dmatrix)[0]
        return float(prob)

    def lambda_handler(self, event):
        predictions_events = []

        for record in event["Records"]:
            encoded_data = record["kinesis"]["data"]
            data_event = base64_decode(encoded_data)
            data = data_event["data"]
            data_id = data_event["data_id"]

            features = self.prepare_features(data)
            prediction = self.predict(features)

            prediction_event = {
                "statusCode": 200,
                "data_id": data_id,
                "default_probability": prediction,
                "default_risk": "High" if prediction >= 0.5 else "Low",
            }

            for callback in self.callbacks:
                callback(prediction_event)

            predictions_events.append(prediction_event)

        return {"predictions": predictions_events}


def init(prediction_stream_name: str, run_id: str, test_run: bool):
    is_local = os.getenv("LOCAL", "false").lower() == "true"
    booster, dv = load_model(run_id, is_local)
    callbacks = []
    model_service = ModelService(booster=booster, dv=dv, model_version=run_id, callbacks=callbacks)
    return model_service
