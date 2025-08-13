import json

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

def predict_endpoint():
    return 0.51

def lambda_handler(event,context):
    data = event['data']
    data_id = event['data_id']

    features = prepare_features(data)
    prediction = predict_endpoint()
    return {
        'statusCode': 200,
        'data_id': data_id,
        'default_probability': float(prediction),
        'default_risk': 'High' if prediction >= 0.5 else 'Low'
    }