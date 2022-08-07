"""Main.py."""
import datetime
import os
from pathlib import Path
from typing import Optional

from lifter_api import LifterAPI
from requests.exceptions import HTTPError
import streamlit as st

from utils.types import CompetitionType, AthleteType
from file import CompetitionFile

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


def main():
    """Run main."""
    st.header("Assessing Competition File")
    st.graphviz_chart(
        """
        digraph {
            competition -> lift
            athlete -> lift
        }
        """
    )

    data_dir = BASE_DIR / "data"

    selected_dir = st.radio(
        "Select Directory:",
        [data_dir, "Upload"],
    )

    if selected_dir == "Upload":
        selected_file = st.file_uploader("Upload file (.xls, .xlsx)")
    else:
        directories = [x for x in selected_dir.iterdir() if x.is_dir()]
        selected_directory = st.selectbox("Select Directory:", directories)
        files = list(selected_directory.glob("**/*.xls[x]"))
        idx = 0
        for i, file in enumerate(files):
            if "result" in str(file):
                idx = i
                break
        selected_file = st.selectbox("Select File:", files, index=idx)

    comp = CompetitionFile(
        selected_file,
    )
    sheet = st.multiselect(
        "Select Sheet(s): ", comp.sheetnames, default=comp.sheetnames
    )

    df = comp.extract(*sheet)
    with st.sidebar:
        st.dataframe(df)

    items = list(df.columns) + [
        item for _, row in df.iterrows() for item in row
    ]

    # def contains_number(string: str) -> bool:
    #     return any([char.isdigit() for char in string])

    st.subheader("Competition Data")
    if not any(list(comp.competition.values())):
        competition_input = {}
        competition_input["name"] = st.selectbox(
            "name",
            [item for item in items if isinstance(item, str)],
        )
        competition_input["location"] = st.selectbox(
            "location",
            [item for item in items if isinstance(item, str)],
            index=21,
        )
        dates = [
            item
            for item in items
            if isinstance(item, datetime.datetime)
            # unlikely to have date as a string
            # or isinstance(item, str)
            # and contains_number(item)
        ]
        competition_input["date_start"] = st.selectbox("date_start", dates)
        competition_input["date_end"] = st.selectbox(
            "date_end",
            sorted(dates, reverse=True),
        )
        comp.competition = competition_input

    st.write(comp.competition)
    st.dataframe(df)

    st.subheader("Lift Data")
    if len(comp.lifts) == 0:
        lifts_input = {}
        lifts_input["athlete"] = {}

        lifts_input["athlete"]["first_name"] = st.selectbox(
            "athlete first_name", df.columns, index=1
        )
        lifts_input["athlete"]["last_name"] = st.selectbox(
            "athlete last_name", df.columns, index=2
        )
        lifts_input["athlete"]["yearborn"] = st.selectbox(
            "athlete yearborn", df.columns, index=2
        )

        col1, col2 = st.columns(2)

        with col1:
            lifts_input["snatch_first"] = st.selectbox(
                "snatch_first", df.columns, index=5
            )
            lifts_input["snatch_second"] = st.selectbox(
                "snatch_second", df.columns, index=6
            )
            lifts_input["snatch_third"] = st.selectbox(
                "snatch_third", df.columns, index=7
            )

        with col2:
            lifts_input["cnj_first"] = st.selectbox(
                "cnj_first", df.columns, index=8
            )
            lifts_input["cnj_second"] = st.selectbox(
                "cnj_second", df.columns, index=9
            )
            lifts_input["cnj_third"] = st.selectbox(
                "cnj_third", df.columns, index=10
            )

        lifts_input["lottery_number"] = st.selectbox(
            "lottery_number", df.columns, index=0
        )
        lifts_input["bodyweight"] = st.selectbox(
            "bodyweight", df.columns, index=4
        )
        lifts_input["team"] = st.selectbox("team", df.columns, index=3)

        lifts_input["weigth_category"] = st.selectbox(
            "weigth_category", df.columns, index=3
        )
        lifts_input["session_number"] = st.selectbox(
            "session_number", df.columns, index=3
        )
    with st.empty():
        comp.lifts = lifts_input
        st.success("Success in parsing lifts")

    st.dataframe(comp.lifts)
    st.dataframe(comp.athletes)

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
