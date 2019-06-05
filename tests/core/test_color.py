import pytest

from dante.core import color

pytestmark = pytest.mark.color


def test_set_color():
    message = "message"
    message_color = color.DEFAULT_SUCCESS
    foreground_color = color.DEFAULT_FOREGROUND

    expected_result = "{message_color}{message}{foreground_color}".format(
        message_color=message_color,
        message=message,
        foreground_color=foreground_color,
    )
    result = color.set_color(
        message=message,
        message_color=message_color,
        foreground_color=foreground_color
    )
    assert result == expected_result
