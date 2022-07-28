"""Main.py."""

import os
from pathlib import Path
from typing import Optional

from lifter_api import LifterAPI
import math
import pandas as pd
from requests.exceptions import HTTPError
from rich import print

from utils.helpers import convert_date
from utils.types import CompetitionType, AthleteType

BASE_DIR = Path(__file__).parent.parent.parent

data_path = BASE_DIR / "data"
excel_files = [x for x in data_path.iterdir() if str(x).split(".")[-1] == "xls"]

api = LifterAPI(auth_token=os.getenv("API_TOKEN"))


def _make_bold(string: str) -> str:
    """Use ** to add itallics."""
    lst = string.split("**")
    for i, s in enumerate(lst):
        if i % 2:
            lst[i] = f"[bold]{s}[/bold]"
    return "".join(lst)


def print_fail(string: str) -> None:
    """Fail."""
    print(f"[red]{_make_bold(string)}[/]")


def print_warning(string: str) -> None:
    """Warn."""
    print(f"[yellow]{_make_bold(string)}[/]")


def print_success(string: str):
    """Success."""
    print(f"[green]{_make_bold(string)}[/]")


def nuke_athletes(confirm: bool = False) -> None:
    """Delete all athletes."""
    if confirm is True:
        athletes = []
        next = "page=1"
        while next is not None:
            new_page = next.split("page=")[-1]
            response = api.athletes(page=new_page)
            athletes.extend(response["results"])
            next = response["next"]
        for athlete in athletes:
            response = api.delete_athlete(athlete["reference_id"])
            print(response)
    else:
        print_warning("Please set confirm=True flag.")


def nuke_competitions(confirm: bool = False) -> None:
    """Delete all competitions."""
    if confirm is True:
        competitions = []
        next = "page=1"
        while next is not None:
            new_page = next.split("page=")[-1]
            response = api.competitions(page=new_page)
            competitions.extend(response["results"])
            next = response["next"]
        for competition in competitions:
            response = api.delete_competition(competition["reference_id"])
            print(response)
    else:
        print_warning("Please set confirm=True flag.")


def get_existing_competitions() -> list[CompetitionType]:
    """Get existing competitions."""
    competitions = []
    next = "page=1"
    while next is not None:
        new_page = next.split("page=")[-1]
        response = api.competitions(page=new_page)
        competitions.extend(response["results"])
        next = response["next"]
    return competitions


def check_competition_exists(competition: CompetitionType) -> bool:
    """Search competition by date to ensure no duplicate competitions."""
    competitions = get_existing_competitions()
    date_starts = [competition["date_start"] for competition in competitions]
    return competition["date_start"] in date_starts


def check_and_create_competition(
    competition: dict[str, str], override: Optional[bool] = False
) -> dict[str, str] | None:
    """Create competition."""
    if override is True:
        print_warning("**WARNING**: Override set to True.")

    if override is False and check_competition_exists(competition):
        print_fail(
            f"**{competition['name']}** might already exist. Use override=True to override."
        )
        return None
    api.create_competition(**competition)
    print_success(f"**{competition['name']}** successfully created!")
    return competition


def check_athlete_exists(athlete: AthleteType) -> str | None:
    result = api.find_athlete(f"{athlete['first_name']} {athlete['last_name']}")
    if result["count"] == 1:
        return result["results"][0]["reference_id"]
    # handling multiple athletes returned on find
    elif result["count"] > 1:
        print_warning("Multiple Athletes detected.")
        options = {idx: r for idx, r in enumerate(result["results"])}
        print(options)
        while True:
            i = int(input("Enter number for athlete: "))
            if i in options.keys():
                return options[i]["reference_id"]


def parse_lift_number(lift_number: float) -> int:
    if math.isnan(lift_number):
        return int(0)
    return int(abs(lift_number))


def determine_lift(lift_number: float) -> str:
    if lift_number > 0:
        return "LIFT"
    elif lift_number < 0:
        return "NOLIFT"
    elif lift_number == 0 or math.isnan(lift_number):
        return "DNA"
    else:
        Exception("Something went wrong!")


def parse_weight_category(weight_category: str):
    if ">" in weight_category:
        weight_category = weight_category.replace(">", "")
        weight_category += "+"
    if weight_category[0] == "F":
        weight_category = weight_category.replace("F", "W")
    weight_category = weight_category.replace(" ", "")
    return weight_category


def parse_sheet(excel_file: Path, override: bool = False) -> dict[str, str]:
    COMPETITION_SHEETNAME = "Competition"
    LIFT_SHEETNAME = ["Men's Results", "Women's Results"]

    comp_df = pd.read_excel(excel_file, COMPETITION_SHEETNAME)
    competition = {
        "name": comp_df.columns[1],
        "location": comp_df.iloc[0][1],
        "date_start": convert_date(comp_df.iloc[1][1]),
        "date_end": convert_date(comp_df.iloc[1][1]),
    }
    if override is True:
        print_warning("**WARNING**: Override set to True.")

    if override is False and check_competition_exists(competition):
        print_fail(
            f"**{competition['name']}** might already exist. Use override=True to override."
        )
        return None
    competition = api.create_competition(**competition)
    print_success(f"**{competition['name']}** successfully created!")

    lift_df = []
    for sheet in LIFT_SHEETNAME:
        lift_df.append(pd.read_excel(excel_file, sheet))
    lift_df = pd.concat(lift_df).reset_index()
    for _, rows in lift_df.iterrows():
        if type(rows["Lot"]) is int:
            athlete = {
                "first_name": rows["First Name"],
                "last_name": rows["Last Name"],
                "yearborn": int(rows["Born"]),
            }
            athlete_id = check_athlete_exists(athlete)
            if athlete_id is None:
                athlete_id = api.create_athlete(**athlete)["reference_id"]
                print_success(
                    f"**{athlete['first_name']} {athlete['last_name'].upper()}** successfully created!"
                )
            else:
                print_fail(
                    f"**{athlete['first_name']} {athlete['last_name'].upper()}** might already exist."
                )

                # try and except

            lift = {
                "lottery_number": rows["Lot"],
                "snatch_first": determine_lift(rows["Snatch"]),
                "snatch_first_weight": parse_lift_number(rows["Snatch"]),
                "snatch_second": determine_lift(rows["Unnamed: 9"]),
                "snatch_second_weight": parse_lift_number(rows["Unnamed: 9"]),
                "snatch_third": determine_lift(rows["Unnamed: 10"]),
                "snatch_third_weight": parse_lift_number(rows["Unnamed: 10"]),
                "cnj_first": determine_lift(rows["Clean&Jerk"]),
                "cnj_first_weight": parse_lift_number(rows["Clean&Jerk"]),
                "cnj_second": determine_lift(rows["Unnamed: 14"]),
                "cnj_second_weight": parse_lift_number(rows["Unnamed: 14"]),
                "cnj_third": determine_lift(rows["Unnamed: 15"]),
                "cnj_third_weight": parse_lift_number(rows["Unnamed: 15"]),
                "bodyweight": float(rows["B.W."]),
                "weight_category": parse_weight_category(rows["Cat."]),
                "team": rows["Team"],
                "session_number": 0,
            }
            try:
                lift_result = api.create_lift(
                    athlete_id=athlete_id,
                    competition_id=competition["reference_id"],
                    **lift,
                )
                print_success(
                    f"Lift: **{lift_result['reference_id']}** created for **{athlete['first_name']} {athlete['last_name'].upper()}** "
                )
            except HTTPError:
                lifts = api.lifts(competition_id=competition["reference_id"])
                if athlete_id not in [lift["athlete"] for lift in lifts]:
                    raise
                print(
                    f"**{athlete['first_name']} {athlete['last_name'].upper()}** has already lifted in this competition."
                )

    return lift_df


def main():
    nuke_athletes(confirm=True)
    nuke_competitions(confirm=True)
    parse_sheet(excel_file=excel_files[1])
    parse_sheet(excel_file=excel_files[0])


if __name__ == "__main__":
    main()
