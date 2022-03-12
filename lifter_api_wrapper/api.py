import logging
from typing import List, Dict

import requests

from .base import BaseLifterAPI
from .defaults import URL, VERSION, ATHLETE_FIELDS, COMPETITION_FIELDS, LIFT_FIELDS
from .exceptions import (
    NotAllowedError,
)

logging.basicConfig(
    level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s"
)


class LifterAPI(BaseLifterAPI):
    """
    API for Lifter

    Contains all functionality for LifterAPI
    """

    def __init__(self, url=URL, version=VERSION, auth_token=None):
        super().__init__(url, version, auth_token)

    def athletes(self) -> List[Dict[str, str]]:
        response = requests.get(f"{self.url}/{self.version}/athletes")
        if response.status_code == 200:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def get_athlete(self, athlete_id: str) -> Dict[str, str]:
        response = requests.get(f"{self.url}/{self.version}/athletes/{athlete_id}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"detail": "Athlete does not exist."}
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def create_athlete(self, **kwargs) -> Dict[str, str]:
        self._verify_create_kwargs(kwargs, ATHLETE_FIELDS)
        response = requests.post(
            f"{self.url}/{self.version}/athletes",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [201, 200, 403, 401]:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def edit_athlete(self, athlete_id: str, **kwargs) -> Dict[str, str]:
        self._verify_edit_kwargs(kwargs, ATHLETE_FIELDS)
        response = requests.patch(
            f"{self.url}/{self.version}/athletes/{athlete_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [200, 403]:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def delete_athlete(self, athlete_id: str) -> Dict[str, str]:
        response = requests.delete(
            f"{self.url}/{self.version}/athletes/{athlete_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code in [200, 204]:
            return {"detail": "Athlete entry deleted."}
        elif response.status_code == 403:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    # TODO write competition functions

    def competitions(self) -> List[Dict[str, str]]:
        response = requests.get(f"{self.url}/{self.version}/competitions")
        if response.status_code == 200:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def get_competition(self, competition_id: str) -> Dict[str, str]:
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}"
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"detail": "Competition does not exist."}
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def create_competition(self, **kwargs) -> Dict[str, str]:
        self._verify_create_kwargs(kwargs, COMPETITION_FIELDS)
        response = requests.post(
            f"{self.url}/{self.version}/competitions",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [201, 200, 403, 401]:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def edit_competition(self, competition_id: str, **kwargs) -> Dict[str, str]:
        self._verify_edit_kwargs(kwargs, COMPETITION_FIELDS)
        response = requests.patch(
            f"{self.url}/{self.version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [201, 200, 403, 401]:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def delete_competition(self, competition_id: str) -> Dict[str, str]:
        response = requests.delete(
            f"{self.url}/{self.version}/competitions/{competition_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code in [200, 204]:
            return {"detail": "Competition entry deleted."}
        elif response.status_code == 403:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    # TODO write lift

    def lifts(self, competition_id: str) -> List[Dict[str, str]]:
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift"
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise NotAllowedError(message=f"{response.status_code=}")

    def get_lift(self, competition_id: str, lift_id: int) -> Dict[str, str]:
        response = requests.get(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift/{lift_id}"
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"detail": "Lift does not exist."}
        else:
            raise NotAllowedError(message=f"{response.status_code=}")

    def create_lift(self, competition_id: str, **kwargs) -> Dict[str, str]:
        self._verify_create_kwargs(kwargs, LIFT_FIELDS)
        response = requests.post(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [201, 200, 403, 401]:
            logging.debug("Lift created")
            return response.json()
        elif (
            self.get_competition(competition_id).get("detail")
            == "Competition does not exist."
        ):
            return self.get_competition(competition_id)
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def edit_lift(self, competition_id: str, lift_id: str, **kwargs):
        self._verify_edit_kwargs(kwargs, LIFT_FIELDS)
        response = requests.patch(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift/{lift_id}",
            headers=self._provide_authorization_header(),
            json=kwargs,
        )
        if response.status_code in [200, 403]:
            return response.json()
        elif (
            self.get_competition(competition_id).get("detail")
            == "Competition does not exist."
        ):
            return self.get_competition(competition_id)
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )

    def delete_lift(self, competition_id: str, lift_id: str):
        response = requests.delete(
            f"{self.url}/{self.version}/competitions/{competition_id}/lift/{lift_id}",
            headers=self._provide_authorization_header(),
        )
        if response.status_code in [200, 204]:
            return {"detail": "Lift entry deleted."}
        elif (
            self.get_competition(competition_id).get("detail")
            == "Competition does not exist."
        ):
            return self.get_competition(competition_id)
        elif response.status_code == 403:
            return response.json()
        else:
            raise NotAllowedError(
                message=f"status code returned: {response.status_code}"
            )
