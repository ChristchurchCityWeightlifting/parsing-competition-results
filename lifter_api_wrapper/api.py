import json
import logging
from tabnanny import check
from typing import List, Dict

import requests
from requests.auth import HTTPDigestAuth

from .exceptions import NotAllowedException, TokenNotValidException

URL = "http://0.0.0.0:8000"
VERSION = "v1"

logging.basicConfig(
    level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s"
)


class LifterAPI:
    """
    API for Lifter
    """

    def __init__(
        self,
        url: str = URL,
        version: str = VERSION,
        auth_token: str = None,
    ) -> None:
        self.url = url
        self.version = version
        self.__auth_token = auth_token  # request token
        self.__access_token = "_"  # can't be blank

    def __verify_access_token(self) -> bool:
        """Checks if the access token is true and valid.

        Will return True if the access token is verfied and current; returns False if the access token needs to be refreshed.

        Returns:
            bool: result of above logic
        """
        response = requests.post(
            f"{self.url}/api/token/verify", json={"token": self.__access_token}
        )
        return response.json().get("code") != "token_not_valid"

    def __obtain_access_token(self) -> str:
        """This obtains the access key.

        Also checks if the current access key is valid as not to refresh another key for no reason

        Raises:
            TokenNotValidException: There was a problems with the refresh token. Most likely, it is not valid

        Returns:
            str: Access token
        """
        if not self.__verify_access_token():
            response = requests.post(
                f"{self.url}/api/token/refresh/",
                data={"refresh": f"{self.__auth_token}"},
            )
            if response.status_code == 401:
                # the refresh token is no longer valid
                raise TokenNotValidException

            self.__access_token = response.json()["access"]
        return self.__access_token

    def athletes(self) -> List[str]:
        response = requests.get(f"{self.url}/{self.version}/athletes")
        if response.status_code == 200:
            return response.json()
        else:
            raise NotAllowedException

    def get_athlete(self, athlete_id: str) -> Dict[str, str]:
        response = requests.get(f"{self.url}/{self.version}/athletes/{athlete_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise NotAllowedException

    def create_athlete(self, **kwargs) -> Dict[str, str]:
        # TODO: verify kwargs?
        headers = {}
        headers["Authorization"] = f"Bearer {self.__obtain_access_token()}"
        response = requests.post(
            f"{self.url}/{self.version}/athletes",
            headers=headers,
            json=kwargs,
        )
        logging.debug(headers)
        logging.debug(response.status_code)
        if response.status_code in [201, 200, 403, 401]:
            return response.json()
        else:
            raise NotAllowedException

    def edit_athlete(self, athlete_id: str, **kwargs) -> Dict[str, str]:
        response = requests.patch(
            f"{self.url}/{self.version}/athletes/{athlete_id}", params=kwargs
        )
        if response.status_code in [200, 403]:
            return response.json()
        else:
            raise NotAllowedException

    def delete_athlete(self, athlete_id: str):
        response = requests.delete(f"{self.url}/{self.version}/athletes/{athlete_id}")
        if response.status_code == 200:
            return {"detail": "Athlete entry deleted."}
        elif response.status_code == 403:
            return response.json()
        else:
            raise NotAllowedException

    # TODO: competition CRUD
    # TODO: how to add lifts to competitions
