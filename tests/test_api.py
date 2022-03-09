import os

import pytest

from lifter_api_wrapper import LifterAPI

# TODO: need to mock data on the API


class TestLifterAPIAthlete:

    test_athlete = {
        "first_name": "Test",
        "last_name": "USER",
        "yearborn": 1900,
    }

    alter_athlete = {
        "yearborn": 1901,
    }

    @pytest.fixture
    def unauthenticated_api_user(self):
        return LifterAPI()

    @pytest.fixture
    def authenticated_api_user(self):
        return LifterAPI(auth_token=os.getenv("API_TOKEN"))

    def test_athletes_unauthenticated(self, unauthenticated_api_user):
        """Return a list of athletes"""
        athletes = unauthenticated_api_user.athletes()
        assert isinstance(athletes, list) == True

    def test_get_athlete_unauthenticated(self, unauthenticated_api_user):
        """Return athlete detail based on ID"""
        athlete_id = unauthenticated_api_user.athletes()[-1]["url"].split("/")[-1]
        athlete_details = unauthenticated_api_user.get_athlete(athlete_id)
        assert isinstance(athlete_details, dict) == True

    def test_create_athlete_unauthenticated(self, unauthenticated_api_user):
        """Cannot create athelete as unauthenticated"""
        athlete = unauthenticated_api_user.create_athlete(**self.test_athlete)
        assert athlete["detail"] == "Authentication credentials were not provided."

    def test_edit_athlete_unauthenticated(self, unauthenticated_api_user):
        """Cannot edit athelete as unauthenticated"""
        athlete_id = unauthenticated_api_user.athletes()[-1]["url"].split("/")[-1]
        athlete = unauthenticated_api_user.edit_athlete(
            athlete_id, **self.alter_athlete
        )
        assert athlete["detail"] == "Authentication credentials were not provided."

    def test_delete_athlete_unauthenticated(self, unauthenticated_api_user):
        """Cannot delete athelete as unauthenticated"""
        athlete_id = unauthenticated_api_user.athletes()[-1]["url"].split("/")[-1]
        athlete = unauthenticated_api_user.delete_athlete(athlete_id)
        assert athlete["detail"] == "Authentication credentials were not provided."

    def test_create_athlete_authenticated(self, authenticated_api_user):
        """Able to create athlete as authenticated"""
        # TODO: create not working
        athlete = authenticated_api_user.create_athlete(**self.test_athlete)
        athlete_id = authenticated_api_user.athletes()[-1]["url"].split("/")[-1]
        athlete_detail = authenticated_api_user.get_athlete(athlete_id)
        assert athlete_detail["first_name"] == self.test_athlete["first_name"]

        # clean up test user


class TestLiftAPICompetition:

    test_competition = {
        "first_name": "Test",
        "last_name": "USER",
        "yearborn": 1900,
    }

    alter_competition = {
        "yearborn": 1901,
    }

    @pytest.fixture
    def unauthenticated_api_user(self):
        return LifterAPI()

    @pytest.fixture
    def authenticated_api_user(self):
        return LifterAPI(
            username=os.getenv("API_USERNAME"), password=os.getenv("API_PASSWORD")
        )
