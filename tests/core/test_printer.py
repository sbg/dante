import pytest
from faker import Faker

from dante.core import color
from dante.core.printer import Printer

pytestmark = pytest.mark.printer

generator = Faker()
printer = Printer()


def test_colored_message():
    # preconditions
    message = generator.slug()
    message_color = color.DEFAULT_PACKAGE

    # action
    colored = printer.colored_message(
        message=message,
        message_color=message_color
    )

    # verification
    assert "{}{}{}".format(
        message_color,
        message,
        color.DEFAULT_FOREGROUND
    ) == colored


def test_print_message(capsys):
    # preconditions
    message = generator.slug()
    message_color = color.DEFAULT_PACKAGE

    # action
    printer.print_message(message=message, message_color=message_color)

    # verification
    captured = capsys.readouterr()
    assert captured.out == "{}{}{}\n".format(
        message_color,
        message,
        color.DEFAULT_FOREGROUND
    )


def test_info(capsys):
    # preconditions
    message = generator.slug()

    # action
    printer.info(message=message)

    # verification
    captured = capsys.readouterr()
    assert captured.out == "{}{}{}\n".format(
        printer.color_info,
        message,
        color.DEFAULT_FOREGROUND
    )


def test_success(capsys):
    # preconditions
    message = generator.slug()

    # action
    printer.success(message=message)

    # verification
    captured = capsys.readouterr()
    assert captured.out == "{}{}{}\n".format(
        printer.color_success,
        message,
        color.DEFAULT_FOREGROUND
    )


def test_error(capsys):
    # preconditions
    message = generator.slug()

    # action
    printer.error(message=message)

    # verification
    captured = capsys.readouterr()
    assert captured.out == "{}{}{}\n".format(
        printer.color_error,
        message,
        color.DEFAULT_FOREGROUND
    )


def test_warning(capsys):
    # preconditions
    message = generator.slug()

    # action
    printer.warning(message=message)

    # verification
    captured = capsys.readouterr()
    assert captured.out == "{}{}{}\n".format(
        printer.color_warning,
        message,
        color.DEFAULT_FOREGROUND
    )


def test_package(capsys):
    # preconditions
    message = generator.slug()

    # action
    printer.package(message=message)

    # verification
    captured = capsys.readouterr()
    assert captured.out == "{}{}{}\n".format(
        printer.color_package,
        message,
        color.DEFAULT_FOREGROUND
    )


def test_tabulate_data():
    # preconditions
    headers = ['normal_title', 'short_title', 'longest_title']
    tabular_data = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', 'longer_than_usual'],
    ]

    expected = (
        'normal_title  short_title  longest_title\n'
        '------------  -----------  -----------------\n'
        '1             2            3\n'
        '4             5            6\n'
        '7             8            longer_than_usual'
    )

    # action
    # noinspection PyProtectedMember
    tabulated = printer._tabulate_data(
        headers=headers,
        tabular_data=tabular_data,
        column_spacing=2,
        divider='-'
    )

    # verification
    assert expected == tabulated


def test_table(capsys):
    # preconditions
    headers = ['normal_title', 'short_title', 'longest_title']
    tabular_data = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', 'longer_than_usual'],
    ]

    expected = (
        'normal_title  short_title  longest_title\n'
        '------------  -----------  -----------------\n'
        '1             2            3\n'
        '4             5            6\n'
        '7             8            longer_than_usual\n'
    )

    # action
    printer.table(headers=headers, tabular_data=tabular_data)

    # verification
    captured = capsys.readouterr()
    assert expected == captured.out
