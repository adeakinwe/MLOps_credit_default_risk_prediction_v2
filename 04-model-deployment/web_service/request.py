import requests

data = {
    "AGE_GROUP": "Youth",
    "YEARS_EMPLOYED_GROUP": "1-5 yrs",
    "PHONE_CHANGE_GROUP": "moderate",
    "REGION_RATING_CLIENT_W_CITY": 2,
    "REGION_RATING_CLIENT": 1,
    "EXT_SOURCE_3": 0.789,
    "EXT_SOURCE_2": 0.621,
    "EXT_SOURCE_1": 0.513,
    "FLOORS_MAX_AVG": 1.0
}

url = 'http://localhost:9696/predict'
response = requests.post(url, json=data)
print(response.json())