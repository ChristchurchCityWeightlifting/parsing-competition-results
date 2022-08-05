"""Main.py."""
import os
from pathlib import Path
from typing import Optional

from lifter_api import LifterAPI
import pandas as pd
from requests.exceptions import HTTPError
import streamlit as st

from utils.types import CompetitionType, AthleteType
from file import CompetitionFile, FILE_TYPES


BASE_DIR = Path(__file__).parent.parent.parent

data_path = BASE_DIR / "data"


def list_data_directories(data_dir: Path = data_path) -> list[Path]:
    """Provide a list of directories in side /data."""
    return [_ for _ in data_dir.iterdir() if _.is_dir()] + [data_dir]


def list_data_files(data_dir: Path = data_path) -> list[Path]:
    """Provide a list of files."""
    if data_dir is None:
        data_dir = data_path
    return [_ for _ in data_dir.iterdir() if not _.is_dir()]


def check_competition_exists(
    api: LifterAPI, competition: CompetitionType
) -> list[str]:
    """Search competition by date to ensure no duplicate competitions."""
    competitions = []
    next = "page=1"
    while next is not None:
        new_page = next.split("page=")[-1]
        response = api.competitions(page=new_page)
        competitions.extend(response["results"])
        next = response["next"]
    return [
        c["reference_id"]
        for c in competitions
        if competition["date_start"] == c["date_start"]
    ]


def check_and_create_competition(
    api: LifterAPI,
    competition: dict[str, str],
    override: Optional[bool] = False,
) -> dict[str, str] | None:
    """Create competition."""
    if override is False and check_competition_exists(competition):
        return None
    api.create_competition(**competition)
    return competition


def check_athlete_exists(api: LifterAPI, athlete: AthleteType) -> str | None:
    """Check if an athlete exists."""
    result = api.find_athlete(
        f"{athlete['first_name']} {athlete['last_name']}"
    )
    if result["count"] == 1:
        return result["results"][0]["reference_id"]
    # handling multiple athletes returned on find
    elif result["count"] > 1:
        options = {idx: r for idx, r in enumerate(result["results"])}
        print(options)
        while True:
            i = int(input("Enter number for athlete: "))
            if i in options.keys():
                return options[i]["reference_id"]


# TODO: move LIFT_SHEETNAME somewhere
LIFT_SHEETNAMES = ["Men's Results", "Women's Results"]


def main():
    """Run main."""
    st.header("Assessing Competition File")

    EXTRA_SELECT_DIR_OPTIONS = ["Upload"]
    selected_dir = st.radio(
        "Select Directory:",
        list_data_directories() + EXTRA_SELECT_DIR_OPTIONS,
    )

    if selected_dir == "Upload":
        selected_file = st.file_uploader("Upload file (.xls, .xlsx)")
    else:
        selected_file = st.selectbox(
            "Select File:", list_data_files(selected_dir)
        )

    if selected_dir == "Upload" or selected_dir.stem == "data":
        selected_file_type = st.selectbox("Select File Type:", FILE_TYPES)
    else:
        selected_file_type = selected_dir.stem

    comp = CompetitionFile(
        selected_file,
        selected_file_type,
    )
    if selected_file_type == FILE_TYPES[0]:
        default_sheets = LIFT_SHEETNAMES
    elif selected_file_type == FILE_TYPES[1]:
        default_sheets = comp.sheetnames

    sheet = st.multiselect(
        "Select Sheet(s): ", comp.sheetnames, default=default_sheets
    )
    df = comp.extract(*sheet)
    st.dataframe(df)

    st.subheader("Competition Data")
    st.write(comp.competition)
    st.subheader("Lift Data")
    st.dataframe(pd.DataFrame(comp.lifts))

    st.subheader("Uploading to Database")
    local = st.radio("Run locally?", [True, False])
    if local:
        os.environ["LOCAL_DEVELOPMENT"] = "1"
        api = LifterAPI(auth_token=os.getenv("API_TOKEN"))
        st.success("Running locally.")
    else:
        os.environ["LOCAL_DEVELOPMENT"] = "0"
        api = LifterAPI(auth_token=os.getenv("LIVE_API_TOKEN"))
        st.warning("WARNING: Running on LIVE!")
    os.environ["LOCAL_DEVELOPMENT"] = "1"

    competition_exists = check_competition_exists(api, comp.competition)
    competition_id = None
    if len(competition_exists) > 0:
        competition_id = st.selectbox(
            "Select Existing Competition", [None] + competition_exists, index=0
        )
        st.write(
            {
                k: v
                for k, v in api.get_competition(competition_id).items()
                if k in ("reference_id", "name", "date_start")
            }
        )
    else:
        st.write("No Competitions found with same date.")
        if st.button("Create Competition"):
            st.write("Created competition:")
            response = api.create_competition(**comp.competition)
            st.write(response)
            competition_id = response["reference_id"]

    if competition_id is not None:
        if st.button("Upload Results"):
            lifts = comp.lifts
            upload_progress = st.progress(0)
            for i, lift in enumerate(lifts):
                athlete = lift["athlete"]
                with st.spinner(
                    f"Adding {athlete['first_name']} {athlete['last_name'].upper()} ..."
                ):
                    athlete_id = check_athlete_exists(api, athlete)
                    if athlete_id is None:
                        athlete_id = api.create_athlete(**athlete)[
                            "reference_id"
                        ]
                        st.write(
                            f"{athlete['first_name']} {athlete['last_name'].upper()} created - '{athlete_id}'"
                        )
                    lift.pop("athlete")
                    try:
                        api.create_lift(
                            athlete_id=athlete_id,
                            competition_id=competition_id,
                            **lift,
                        )
                        st.write(
                            f"{athlete['first_name']} {athlete['last_name'].upper()} lift added."
                        )
                    except HTTPError as e:
                        check_lifts = api.lifts(competition_id=competition_id)
                        if athlete_id not in [
                            lift["athlete"] for lift in check_lifts
                        ]:
                            raise Exception(e)
                upload_progress.progress(i / (len(lifts) - 1))

            # celebrate!
            st.balloons()


if __name__ == "__main__":
    main()
