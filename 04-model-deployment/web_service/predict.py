import xgboost as xgb  # optional if your model is xgboost, but pyfunc hides details
from flask import Flask, request, jsonify
import mlflow

RUN_ID = 'fe69b7b9817240789feb57c59ff31cc5'

'''
UNCOMMENT TO LOAD MODEL FROM MLFLOW TRACKING SERVER

# Set MLflow tracking URI
MLFLOW_TRACKING_URI = 'http://localhost:8004'
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Load MLflow pyfunc model
logged_model = f"runs:/{RUN_ID}/models/xgboost_model"
model = mlflow.pyfunc.load_model(logged_model)
'''

# Load artifact from s3 bucket
logged_model = f"s3://mlflow-credit-default-risk-prediction-artifact-store-v2/{RUN_ID}/artifacts/models/xgboost_model"
model = mlflow.pyfunc.load_model(logged_model)

# Feature columns
cat_cols = ['AGE_GROUP', 'YEARS_EMPLOYED_GROUP', 'PHONE_CHANGE_GROUP']
num_cols = [
    'REGION_RATING_CLIENT_W_CITY',
    'REGION_RATING_CLIENT',
    'EXT_SOURCE_3',
    'EXT_SOURCE_2',
    'EXT_SOURCE_1',
    'FLOORS_MAX_AVG'
]

def prepare_features(data):
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

app = Flask('credit-default-risk-prediction-service')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    data = request.get_json()
    features = prepare_features(data)

    # MLflow pyfunc expects a dataframe-like input (list of dicts works)
    prediction = model.predict([features])[0]

    result = {
        'default_probability': float(prediction),
        'default_risk': 'High' if prediction >= 0.5 else 'Low'
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8005)