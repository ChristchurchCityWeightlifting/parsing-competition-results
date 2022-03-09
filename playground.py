import os

from lifter_api_wrapper import LifterAPI


lifter_api = LifterAPI()

test_athlete = {
    "first_name": "Test",
    "last_name": "USER",
    "yearborn": 1900,
}

# lifter_api = LifterAPI()
lifter_api = LifterAPI(auth_token=os.getenv("API_TOKEN"))

print(lifter_api.create_athlete(**test_athlete))
