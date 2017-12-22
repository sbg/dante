import faker
import pytest


pytestmark = pytest.mark.printer
generator = faker.Factory.create()


def test_printable_message(given):
    # preconditions
    printer = given.printer.exists()
    message = generator.slug()

    expected_output = '{}{}{}'.format(
        printer.foreground_color,
        message,
        printer.foreground_color
    )

    # action
    result = printer.printable_message(message=message)

    # verification
    assert result == expected_output


def test_printable_package(given):
    # preconditions
    printer = given.printer.exists()
    package_name = generator.slug()

    expected_output = '{}{}{}'.format(
        printer.package_color,
        package_name,
        printer.foreground_color
    )

    # action
    result = printer.printable_package(package_name=package_name)

    # verification
    assert result == expected_output


def test_printable_package_versioned(given):
    # preconditions
    printer = given.printer.exists()
    package_name = generator.slug()
    package_version = generator.random_int()

    expected_output = '{}=={}'.format(
        printer.printable_package(package_name=package_name),
        package_version
    )

    # action
    result = printer.printable_package_versioned(
        package_name=package_name, package_version=package_version)

    # verification
    assert result == expected_output


def test_info(given, capsys):
    # preconditions
    printer = given.printer.exists()
    message = generator.slug()
    expected_output = '{}{}{}'.format(
        printer.foreground_color,
        message,
        printer.foreground_color
    )

    # action
    printer.info(message=message)

    # verification
    out, _ = capsys.readouterr()
    assert str.strip(out) == expected_output


def test_warning(given, capsys):
    # preconditions
    printer = given.printer.exists()
    message = generator.slug()
    expected_output = '{}WARNING: {}{}'.format(
        printer.warning_color,
        message,
        printer.foreground_color
    )

    # action
    printer.warning(message=message)

    # verification
    out, _ = capsys.readouterr()
    assert str.strip(out) == expected_output


def test_success(given, capsys):
    # preconditions
    printer = given.printer.exists()
    message = generator.slug()
    expected_output = '{}{}{}'.format(
        printer.success_color,
        message,
        printer.foreground_color
    )

    # action
    printer.success(message=message)

    # verification
    out, _ = capsys.readouterr()
    assert str.strip(out) == expected_output


def test_package(given, capsys):
    # preconditions
    printer = given.printer.exists()
    package_name = generator.slug()
    expected_output = '{}{}{}'.format(
        printer.package_color,
        package_name,
        printer.foreground_color
    )

    # action
    printer.package(package_name=package_name)

    # verification
    out, _ = capsys.readouterr()
    assert str.strip(out) == expected_output


def test_package_versioned(given, capsys):
    # preconditions
    printer = given.printer.exists()
    package_name = generator.slug()
    package_version = generator.random_int()

    expected_output = "{}=={}".format(
        printer.printable_package(package_name),
        package_version
    )

    # action
    printer.package_versioned(
        package_name=package_name,
        package_version=package_version
    )

    # verification
    out, _ = capsys.readouterr()
    assert str.strip(out) == expected_output


def test_dependency_package(given, capsys):
    # preconditions
    printer = given.printer.exists()
    package_name = generator.slug()
    installed_version = generator.random_int()
    required_version = generator.random_int()
    indent = generator.random_int()

    expected_output = '{}{}{} [Installed: {} | Required: {}]'.format(
        printer.package_color,
        package_name,
        printer.foreground_color,
        installed_version,
        required_version
    )

    # action
    printer.dependency_package(
        package_name=package_name,
        required_version=required_version,
        installed_version=installed_version,
        indent=indent
    )

    # verification
    out, _ = capsys.readouterr()
    assert str.strip(out) == expected_output


def test_table(given, capsys):
    # preconditions
    printer = given.printer.exists()
    headers = ['a', 'b', 'c']
    tabular_data = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]

    expected_result = 'a  b  c\n-  -  -\n1  2  3\n4  5  6\n7  8  9'

    # action
    printer.table(tabular_data=tabular_data, headers=headers)

    # verification
    out, _ = capsys.readouterr()
    assert out.strip() == expected_result


def test_package_list(given, capsys):
    # preconditions
    printer = given.printer.exists()
    package_list = [
        {
            'name': 'package_one',
            'version': 1
        },
        {
            'name': 'package_two',
            'version': '1.2.3'
        }
    ]
    expected_result = '{}package_one{}==1\n{}package_two{}==1.2.3\n'.format(
        printer.package_color, printer.foreground_color,
        printer.package_color, printer.foreground_color
    )

    # action
    printer.package_list(package_list=package_list)

    # verification
    out, _ = capsys.readouterr()
    assert out == expected_result
