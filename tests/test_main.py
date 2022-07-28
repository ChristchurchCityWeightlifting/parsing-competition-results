"""Test."""

import pytest

from src.parse_weight_cateogory.main import parse_weight_cateogory


@pytest.mark.parametrize(
    "test_input,expected",
    [
        pytest.param("M 61", "M61", id="Male 61"),
        pytest.param("F 55", "W55", id="Female 55"),
        pytest.param("F 55", "F 55", id="Error Female 55", marks=pytest.mark.xfail),
    ],
)
def test_parse_weight_category(test_input, expected):
    """Test if this works."""
    assert expected == parse_weight_category(test_input)
