import os

from lifter_api_wrapper import LifterAPI


lifter_api = LifterAPI()

test_athlete = {
    "first_name": "Test",
    "last_name": "USER",
    "yearborn": 1900,
}

alter_athlete = {
    "yearborn": 1901,
}

test_comp = {
    "date_start": "2022-03-02",
    "date_end": "2022-03-02",
    "location": "test location",
    "competition_name": "Test name",
}

# lifter_api = LifterAPI()
lifter_api = LifterAPI(auth_token=os.getenv("API_TOKEN"))

response = lifter_api.create_competition(**test_comp)


print(response)
print(type(response))
print(isinstance(response, dict))
