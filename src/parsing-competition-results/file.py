"""File class."""

# file_path is location of as a Path object
# file type to be the software type (e.g. OWLCMS, Excel)

import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

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

    def __init__(self, file_path: Path, file_type: str = "") -> None:
        self.file_path = file_path
        self.file_type = file_type.lower()
        self._competition_data = {
            "name": "",
            "location": "",
            "date_start": "",
            "date_end": "",
        }
        self._lifts_data = []

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

        else:
            return self._competition_data

    @competition.setter
    def competition(self, value: dict[str, str]) -> None:
        self._competition_data = {
            "name": value["name"],
            "location": value["location"],
            "date_start": convert_date(value["date_start"]),
            "date_end": convert_date(value["date_end"]),
        }

    def _results(self) -> tuple[list[dict], list[dict]]:
        """Parse to obtain athlete and lift data.

        Returns:
            tuple[dict, dict]: Result for athletes and lifts.
        """
        athletes = []
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
                    self._lifts_data.append(
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
                        self._lifts_data.append(
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

        return {"athletes": athletes, "lifts": self._lifts_data}

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

    @lifts.setter
    def lifts(
        self, value: dict[str, dict[str | str | int] | str | int]
    ) -> None:
        df = self.extract(*self.sheetnames)
        self._lift_data = []
        for _, rows in df.iterrows():
            lift = {}
            athlete = {}
            first_name = rows[value["athlete"]["first_name"]]
            last_name = rows[value["athlete"]["last_name"]]
            yearborn = rows[value["athlete"]["yearborn"]]
            lottery_number = rows[value["lottery_number"]]
            snatch_first = rows[value["snatch_first"]]
            snatch_second = rows[value["snatch_second"]]
            snatch_third = rows[value["snatch_third"]]
            cnj_first = rows[value["cnj_first"]]
            cnj_second = rows[value["cnj_second"]]
            cnj_third = rows[value["cnj_third"]]
            bodyweight = rows[value["bodyweight"]]
            # "weight_category": parse_weight_category_excelmacro(weight_class)
            team = rows[value["team"]]
            # "session_number": current_session
            session_number = 0

            if isinstance(lottery_number, int):
                st.write(f"first_name | {first_name} | {type(first_name)}")
                athlete["first_name"] = first_name
                st.write(f"last_name | {last_name} | {type(last_name)}")
                athlete["last_name"] = last_name
                st.write(f"yearborn | {yearborn} | {type(yearborn)}")
                athlete["yearborn"] = yearborn
                lift["athlete"] = athlete

                st.write(
                    f"lottery_number | {lottery_number} | {type(lottery_number)}"
                )
                lift["lottery_number"] = lottery_number

                st.write(
                    f"snatch_first | {snatch_first} | {type(snatch_first)}"
                )
                lift["snatch_first"] = determine_lift(snatch_first)
                lift["snatch_first_weight"] = parse_lift_number(snatch_first)

                st.write(
                    f"snatch_second | {snatch_second} | {type(snatch_second)}"
                )
                lift["snatch_second"] = determine_lift(snatch_second)
                lift["snatch_second_weight"] = parse_lift_number(snatch_second)

                st.write(
                    f"snatch_third | {snatch_third} | {type(snatch_third)}"
                )
                lift["snatch_third"] = determine_lift(snatch_third)
                lift["snatch_third_weight"] = parse_lift_number(snatch_third)

                st.write(f"cnj_first | {cnj_first} | {type(cnj_first)}")
                lift["cnj_first"] = determine_lift(cnj_first)
                lift["cnj_first_weight"] = parse_lift_number(cnj_first)

                st.write(f"cnj_second | {cnj_second} | {type(cnj_second)}")
                lift["cnj_second"] = determine_lift(cnj_second)
                lift["cnj_second_weight"] = parse_lift_number(cnj_second)

                st.write(f"cnj_third | {cnj_third} | {type(cnj_third)}")
                lift["cnj_third"] = determine_lift(cnj_third)
                lift["cnj_third_weight"] = parse_lift_number(cnj_third)

                st.write(f"bodyweight | {bodyweight} | {type(bodyweight)}")
                lift["bodyweight"] = float(bodyweight)
                # "weight_category": parse_weight_category_excelmacro(weight_class),
                st.write(f"team | {team} | {type(team)}")
                lift["team"] = team
                # "session_number": current_session,
                st.write(
                    f"session_number | {session_number} | {type(session_number)}"
                )
                lift["session_number"] = session_number
                self._lifts_data.append(lift)

    def __repr__(self) -> None:
        return str(self.competition()["name"])
