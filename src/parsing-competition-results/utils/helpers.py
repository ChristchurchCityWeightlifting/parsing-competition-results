"""Utility functions."""

from datetime import datetime


def convert_date(date_string: str):
    """Convert datestring from 'D/MM/YYYY' to 'YYYY-MM-DD'."""
    input_format = "%d/%M/%Y"
    output_format = "%Y-%M-%d"
    dt_input = datetime.strptime(date_string, input_format)
    output = datetime.strftime(dt_input, output_format)
    return output
