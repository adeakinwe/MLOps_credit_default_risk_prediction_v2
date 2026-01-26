import pandas as pd
import mlflow
from flask import Flask, request, jsonify
from flask_cors import CORS

RUN_ID = 'fe69b7b9817240789feb57c59ff31cc5'

# Load model from S3 artifact
logged_model = f"s3://mlflow-credit-default-risk-prediction-artifact-store-v2/{RUN_ID}/artifacts/models/xgboost_model"
model = mlflow.pyfunc.load_model(logged_model)

# Columns
cat_cols = ['AGE_GROUP', 'YEARS_EMPLOYED_GROUP', 'PHONE_CHANGE_GROUP']
num_cols = [
    'REGION_RATING_CLIENT_W_CITY',
    'REGION_RATING_CLIENT',
    'EXT_SOURCE_3',
    'EXT_SOURCE_2',
    'EXT_SOURCE_1',
    'FLOORS_MAX_AVG'
]

# Map categorical columns to integer codes (safer than categories)
def prepare_features(data):
    features = {}
    # Convert categorical columns to integer codes
    for col in cat_cols:
        val = str(data.get(col, "Unknown"))
        features[col] = [hash(val) % 1000]  # simple encoding
    # Numerical columns
    for col in num_cols:
        val = data.get(col)
        try:
            features[col] = [float(val) if val is not None else 0.0]
        except (ValueError, TypeError):
            features[col] = [0.0]
    return pd.DataFrame(features)

app = Flask("credit-default-risk-prediction-service")
CORS(app)

@app.route("/predict", methods=["POST"])
def predict_endpoint():
    data = request.get_json()
    features_df = prepare_features(data)
    prediction = model.predict(features_df)[0]

    result = {
        "default_probability": float(prediction),
        "default_risk": "High" if prediction >= 0.5 else "Low",
        "riskLevel": 3 if prediction >= 0.5 else 1
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)