"""Test."""

import pytest
from .utils import convert_date  e


@pytest.mark.parametrize(
    "test_input,output",
    [
        pytest.param("4/06/2022", "2022-06-04", id="Correct example"),
        pytest.param(
            "06/04/2022", "2022-06-04", id="Incorrect example", marks=pytest.mark.xfail
        ),
    ],
)
def test_convert_date(test_input, output):
    """Test convert date."""
    assert convert_date(test_input) == output
