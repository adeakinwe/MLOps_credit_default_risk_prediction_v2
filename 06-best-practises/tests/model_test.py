import lambda_function

def test_prepare_features():
    features = {
      "AGE_GROUP": "Youth",
      "YEARS_EMPLOYED_GROUP": "1-5 yrs",
      "PHONE_CHANGE_GROUP": "moderate",
      "REGION_RATING_CLIENT_W_CITY": 2,
      "REGION_RATING_CLIENT": 1,
      "EXT_SOURCE_3": 0.789,
      "EXT_SOURCE_2": 0.621,
      "EXT_SOURCE_1": 0.513,
      "FLOORSMAX_AVG": 0.8
    }
    
    actual_features = lambda_function.prepare_features(features)
    expected_features = features = {
      "AGE_GROUP": "Youth",
      "YEARS_EMPLOYED_GROUP": "1-5 yrs",
      "PHONE_CHANGE_GROUP": "moderate",
      "REGION_RATING_CLIENT_W_CITY": 2,
      "REGION_RATING_CLIENT": 1,
      "EXT_SOURCE_3": 0.789,
      "EXT_SOURCE_2": 0.621,
      "EXT_SOURCE_1": 0.513,
      "FLOORSMAX_AVG": 0.8
    }

    assert actual_features == expected_features

def test_setup():
    assert 3 > 2