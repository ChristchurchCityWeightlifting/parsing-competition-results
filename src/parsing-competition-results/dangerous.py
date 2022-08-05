"""Dangerous functions."""


def nuke_athlete(api: LifterAPI, confirm: bool = False) -> None:
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


def nuke_competitions(api: LifterAPI, confirm: bool = False) -> None:
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
