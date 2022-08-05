"""File class."""

# file_path is location of as a Path object
# file type to be the software type (e.g. OWLCMS, Excel)

import datetime
from pathlib import Path

import pandas as pd

from utils.helpers import (
    convert_date,
    parse_lift_number,
    determine_lift,
    parse_weight_category,
    name_parser,
    parse_weight_category_excelmacro,
)

FILE_TYPES = ["owlcms", "excelmacro"]


class BaseCompetitionFile:
    """Base methods for CompetitionFile."""

    @property
    def sheetnames(self) -> list[str]:
        """Provide a list of sheetnames in the Excel file.

        Results:
            list[str]: List of sheetnames of Excel file.
        """
        return pd.ExcelFile(self.file_path).sheet_names

    def extract(self, *args) -> pd.DataFrame:
        """Extract an information from Excel file given the sheetnames.

        Args:
            *args: Excel sheetnames as serperate arguments.

        Result:
            pd.DataFrame: Pandas dataframe concat of sheetnames provided.
        """
        dfs = (pd.read_excel(self.file_path, arg) for arg in args)
        return pd.concat(dfs, ignore_index=True)


class CompetitionFile(BaseCompetitionFile):
    """Competition data access as a object.

    >>>  comp = CompetitionFile(file_location)
    >>>  comp.competition()
    >>> {'competition_data': 'as a dictionary'}
    """

    def __init__(self, file_path: Path, file_type: str) -> None:
        self.file_path = file_path
        self.file_type = file_type.lower()
        if self.file_type not in FILE_TYPES:
            raise Exception(
                f"Can only have following file types: {FILE_TYPES}"
            )

    @property
    def competition(self) -> dict[str, str]:
        """Provide competition data from excel file.

        Returns:
             dict[str, str]: Competition data.
        """
        if self.file_type == FILE_TYPES[0]:
            COMPETITION_SHEETNAME = "Competition"
            df = self.extract(COMPETITION_SHEETNAME)
            dates = []
            for _, item in df["Unnamed: 3"].iteritems():
                if isinstance(item, str) and "Weigh-in" in item:
                    dates.append(item.split(" ")[2])
            dates.sort(reverse=True)
            competition = {
                "name": df.columns[1],
                "location": df.iloc[0][1],
                "date_start": convert_date(df.iloc[1][1]),
                "date_end": dates[0],
            }
            return competition

        elif self.file_type == FILE_TYPES[1]:
            df = self.extract(*self.sheetnames)
            dates = [
                item
                for _, item in df["Unnamed: 1"].iteritems()
                if isinstance(item, datetime.datetime)
            ]
            dates.sort(reverse=True)
            competition = {
                "name": df.columns[0],
                "date_end": convert_date(dates[0]),
                "date_start": convert_date(df.iloc[0][1]),
                "location": df.iloc[0][8],
            }
            return competition

    def _results(self) -> tuple[list[dict], list[dict]]:
        """Parse to obtain athlete and lift data.

        Returns:
            tuple[dict, dict]: Result for athletes and lifts.
        """
        athletes = []
        lifts = []
        if self.file_type == FILE_TYPES[0]:
            LIFT_SHEETNAMES = ["Men's Results", "Women's Results"]
            df = self.extract(*LIFT_SHEETNAMES)
            for _, rows in df.iterrows():
                if type(rows["Lot"]) is int:
                    athlete = {
                        "first_name": rows["First Name"],
                        "last_name": rows["Last Name"],
                        "yearborn": int(rows["Born"]),
                    }
                    athletes.append(athlete)
                    lifts.append(
                        {
                            "athlete": athlete,
                            "lottery_number": rows["Lot"],
                            "snatch_first": determine_lift(rows["Snatch"]),
                            "snatch_first_weight": parse_lift_number(
                                rows["Snatch"]
                            ),
                            "snatch_second": determine_lift(
                                rows["Unnamed: 9"]
                            ),
                            "snatch_second_weight": parse_lift_number(
                                rows["Unnamed: 9"]
                            ),
                            "snatch_third": determine_lift(
                                rows["Unnamed: 10"]
                            ),
                            "snatch_third_weight": parse_lift_number(
                                rows["Unnamed: 10"]
                            ),
                            "cnj_first": determine_lift(rows["Clean&Jerk"]),
                            "cnj_first_weight": parse_lift_number(
                                rows["Clean&Jerk"]
                            ),
                            "cnj_second": determine_lift(rows["Unnamed: 14"]),
                            "cnj_second_weight": parse_lift_number(
                                rows["Unnamed: 14"]
                            ),
                            "cnj_third": determine_lift(rows["Unnamed: 15"]),
                            "cnj_third_weight": parse_lift_number(
                                rows["Unnamed: 15"]
                            ),
                            "bodyweight": float(rows["B.W."]),
                            "weight_category": parse_weight_category(
                                rows["Cat."]
                            ),
                            "team": rows["Team"],
                            "session_number": 0,
                        }
                    )
        elif self.file_type == FILE_TYPES[1]:
            LIFT_SHEETNAMES = self.sheetnames
            df = self.extract(*LIFT_SHEETNAMES)
            for _, rows in df.iterrows():
                name = rows["Unnamed: 1"]
                if (
                    not isinstance(name, datetime.datetime)
                    and isinstance(name, str)
                    and name != "Name"
                ):
                    if not name[0].isnumeric():
                        athlete = {
                            "first_name": name_parser(name)["first_name"],
                            "last_name": name_parser(name)["last_name"],
                            "yearborn": rows["Unnamed: 2"],
                        }
                        athletes.append(athlete)
                if (
                    isinstance(rows["Unnamed: 3"], str)
                    and "Session" in rows["Unnamed: 3"]
                ):
                    current_session = rows["Unnamed: 4"]
                    weight_class = None
                if (
                    not isinstance(name, datetime.datetime)
                    and isinstance(name, str)
                    and name != "Name"
                ):
                    if name[0].isnumeric():
                        weight_class = rows["Unnamed: 1"]
                    if not name[0].isnumeric():
                        if weight_class is None:
                            raise Exception(
                                f"No weightclass set for this session: {current_session}"
                            )
                        if weight_class.lower() == "69kg":
                            raise Exception(
                                "Please change weight class to either '69kgm' or '69kgw' to indicate male and female (respectively)."
                            )
                        lifts.append(
                            {
                                "athlete": athlete,
                                "lottery_number": rows[df.columns[0]],
                                "snatch_first": determine_lift(
                                    rows["Unnamed: 5"]
                                ),
                                "snatch_first_weight": parse_lift_number(
                                    rows["Unnamed: 5"]
                                ),
                                "snatch_second": determine_lift(
                                    rows["Unnamed: 6"]
                                ),
                                "snatch_second_weight": parse_lift_number(
                                    rows["Unnamed: 6"]
                                ),
                                "snatch_third": determine_lift(
                                    rows["Unnamed: 7"]
                                ),
                                "snatch_third_weight": parse_lift_number(
                                    rows["Unnamed: 7"]
                                ),
                                "cnj_first": determine_lift(
                                    rows["Unnamed: 8"]
                                ),
                                "cnj_first_weight": parse_lift_number(
                                    rows["Unnamed: 8"]
                                ),
                                "cnj_second": determine_lift(
                                    rows["Unnamed: 9"]
                                ),
                                "cnj_second_weight": parse_lift_number(
                                    rows["Unnamed: 9"]
                                ),
                                "cnj_third": determine_lift(
                                    rows["Unnamed: 10"]
                                ),
                                "cnj_third_weight": parse_lift_number(
                                    rows["Unnamed: 10"]
                                ),
                                "bodyweight": float(rows["Unnamed: 4"]),
                                "weight_category": parse_weight_category_excelmacro(
                                    weight_class
                                ),
                                "team": rows["Unnamed: 3"],
                                "session_number": current_session,
                            }
                        )

        return {"athletes": athletes, "lifts": lifts}

    @property
    def athletes(self) -> list[dict]:
        """Provide athlete data.

        Returns:
            list[dict]: Athelte data.
        """
        return self._results()["athletes"]

    @property
    def lifts(self) -> list[dict]:
        """Provide lift data.

        Returns:
            list[dict]: Lift data.
        """
        return self._results()["lifts"]

    def __repr__(self) -> None:
        return str(self.competition()["name"])
