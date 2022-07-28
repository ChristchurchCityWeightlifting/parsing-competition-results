"""Types."""

from typing import TypedDict


class CompetitionType(TypedDict):
    """Competition type."""

    name: str
    location: str
    date_start: str
    date_end: str


class AthleteType(TypedDict):
    first_name: str
    last_name: str
    yearborn: int


class LiftType(TypedDict):
    pass
