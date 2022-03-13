from typing import List, Dict

import requests

from ..defaults import ATHLETE_FIELDS
from ..exceptions import NotAllowedError

# TODO: write docstrings


class AthleteMixin:
    """Contains all code for athlete API"""

    def athletes(self) -> List[Dict[str, str]]:
        """Lists all athletes

        Raises:
            NotAllowedError: some error

        Returns:
            List[Dict[str, str]]: List of athletes
        """
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
