"""Utility functions."""

from typing import Union

import math
import datetime


def convert_date(date_string: Union[str, datetime.datetime]):
    """Convert datestring from 'D/MM/YYYY' to 'YYYY-MM-DD'.

    >>> convert_date('5/06/2022')
    2022-06-05

    Args:
        date_string (str): Input entry date.

    Returns:
        (str): Date for the API.
    """
    dt_input = date_string
    if not isinstance(date_string, datetime.datetime):
        input_format = "%d/%m/%Y"
        dt_input = datetime.datetime.strptime(date_string, input_format)
    output_format = "%Y-%m-%d"
    output = datetime.datetime.strftime(dt_input, output_format)
    return output


def parse_lift_number(lift_number: float) -> int:
    """Parse the lift weight.

    >>> parse_lift_number(float('nan'))
    0
    >>> parse_lift_number(100)
    100

    Args:
        lift_number (float): Input lift weight number.

    Returns:
        (int): Lift weight number for the API.
    """
    if math.isnan(lift_number):
        return int(0)
    return int(abs(lift_number))


def determine_lift(lift_number: float) -> str:
    """Determine the lift status.

    >>> determine_lift(0)
    "DNA"
    >>> determine_lift(100)
    "LIFT"
    >>> determine_lift(-100)
    "NOLIFT"

    Args:
        lift_number (float): Input lift weight number.

    Returns:
        (int): Lift status.
    """
    if lift_number > 0:
        return "LIFT"
    elif lift_number < 0:
        return "NOLIFT"
    elif lift_number == 0 or math.isnan(lift_number):
        return "DNA"
    else:
        raise Exception("Something went wrong!")


def parse_weight_category(weight_category: str) -> str:
    """Determine the weight category.

    >>> parse_weight_category("M > 109")
    "M109+"

    Args:
        weight_category (str): The weight category.

    Returns:
        (str): Weight category for API.
    """
    if ">" in weight_category:
        weight_category = weight_category.replace(">", "")
        weight_category += "+"
    if weight_category[0] == "F":
        weight_category = weight_category.replace("F", "W")
    weight_category = weight_category.replace(" ", "")
    return weight_category


def parse_weight_category_excelmacro(weight_category: str) -> str:
    """Determine the weight category for excel macro type files.

    >>> parse_weight_category_excelmacro("53Kg")
    "F53"

    Args:
        weight_category (str): The weight category.

    Returns:
        (str): Weight category for API.
    """
    CONVERSION = {
        "48kg": "W48",
        "53kg": "W53",
        "58kg": "W58",
        "63kg": "W63",
        "75kg": "W75",
        "69kgw": "W69",
        "90kg": "W90",
        "90+kg": "W90+",
        "56kg": "M56",
        "62kg": "M62",
        "69kgm": "M69",
        "77kg": "M77",
        "85kg": "M85",
        "94kg": "M94",
        "105kg": "M105",
        "105+kg": "M105+",
    }
    return CONVERSION[weight_category.lower()]


def name_parser(name: str) -> dict:
    """Parse name and return first and last name.

    >>> name_parse("Karu Te Moana")
    { "first_name": "Karu", "last_name": "Te Moana"}

    Args:
        name (str): The full name.

    Returns:
        dict: The first and last name.
    """
    lst = name.split(" ")
    if len(lst) == 1:
        first_name = lst[0]
        last_name = ""
    first_name = lst[0]
    last_name = lst[-1]
    middle = lst[1:-1]
    if len(middle) != 0:
        if "Te" in middle:
            last_name = " ".join(middle) + " " + last_name
        else:
            first_name += " " + " ".join(middle)
    return {"first_name": first_name, "last_name": last_name}
