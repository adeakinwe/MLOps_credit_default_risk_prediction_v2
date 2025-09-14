""" importing model.py file """
import model


def test_prepare_features():
    """
    function to assert if expected features conforms with actual features
    """
    features = {
        "AGE_GROUP": "Youth",
        "YEARS_EMPLOYED_GROUP": "1-5 yrs",
        "PHONE_CHANGE_GROUP": "moderate",
        "REGION_RATING_CLIENT_W_CITY": 2,
        "REGION_RATING_CLIENT": 1,
        "EXT_SOURCE_3": 0.789,
        "EXT_SOURCE_2": 0.621,
        "EXT_SOURCE_1": 0.513,
        "FLOORSMAX_AVG": 0.8,
    }

    actual_features = model.prep_features(features)
    expected_features = {
        "AGE_GROUP": "Youth",
        "YEARS_EMPLOYED_GROUP": "1-5 yrs",
        "PHONE_CHANGE_GROUP": "moderate",
        "REGION_RATING_CLIENT_W_CITY": 2,
        "REGION_RATING_CLIENT": 1,
        "EXT_SOURCE_3": 0.789,
        "EXT_SOURCE_2": 0.621,
        "EXT_SOURCE_1": 0.513,
        "FLOORSMAX_AVG": 0.8,
    }

    assert actual_features == expected_features


def test_base64_decode():
    """
    check if encoded data is same as expected data after decoding
    """
    encoded_data = "ewogICAgICAgICJkYXRhIjogewogICAgICAiQUdFX0dST1VQIjogIllvdXRoIiwKICAgICAgIllFQVJTX0VNUExPWUVEX0dST1VQIjogIjEtNSB5cnMiLAogICAgICAiUEhPTkVfQ0hBTkdFX0dST1VQIjogIm1vZGVyYXRlIiwKICAgICAgIlJFR0lPTl9SQVRJTkdfQ0xJRU5UX1dfQ0lUWSI6IDIsCiAgICAgICJSRUdJT05fUkFUSU5HX0NMSUVOVCI6IDEsCiAgICAgICJFWFRfU09VUkNFXzMiOiAwLjc4OSwKICAgICAgIkVYVF9TT1VSQ0VfMiI6IDAuNjIxLAogICAgICAiRVhUX1NPVVJDRV8xIjogMC41MTMsCiAgICAgICJGTE9PUlNNQVhfQVZHIjogMC44CiAgICB9LAogICAgImRhdGFfaWQiOiAxMDEKICAgIH0="
    decoded_data = model.base64_decode(encoded_data)

    expected_data = {
        "data": {
            "AGE_GROUP": "Youth",
            "YEARS_EMPLOYED_GROUP": "1-5 yrs",
            "PHONE_CHANGE_GROUP": "moderate",
            "REGION_RATING_CLIENT_W_CITY": 2,
            "REGION_RATING_CLIENT": 1,
            "EXT_SOURCE_3": 0.789,
            "EXT_SOURCE_2": 0.621,
            "EXT_SOURCE_1": 0.513,
            "FLOORSMAX_AVG": 0.8,
        },
        "data_id": 101,
    }
    assert expected_data == decoded_data


def test_setup():
    """
    basic test for setup
    """
    a, b = 3, 1
    assert a > b
