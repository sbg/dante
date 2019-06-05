import sys

from dante import messages
from dante.config import Config
from dante.core.printer import Printer
from dante.core.models import RequirementCollection
from dante.commands.utils import validate_files
from dante.core.operations import dependency_list, missing_requirements


def missing_requirements_command(args, packages=None, exit_on_failure=True):
    """Runs detection of required packages that are not installed
    :param args: Command arguments
    :param packages: Collection of packages
    :param exit_on_failure: Enable/disable exiting application on failure
    :return: None
    """
    list_all = args.all or False
    requirements_files = (
        args.requirements or Config.requirements_files if not list_all else []
    )
    ignore_list = (
        args.ignore or Config.ignore_list if not list_all else []
    )

    printer = Printer()
    if not validate_files(
            files=requirements_files,
            printer=printer,
            exit_on_failure=exit_on_failure):
        return False

    requirements = RequirementCollection()
    for requirements_file in requirements_files:
        requirements.extend(
            RequirementCollection.from_file(filepath=requirements_file)
        )

    packages = (
        packages or dependency_list(list_all=list_all, ignore_list=ignore_list)
    )

    missing = [
        (package, required_by)
        for package, required_by
        in missing_requirements(packages=packages, requirements=requirements)
    ]

    headers = [
        messages.PACKAGE,
        messages.REQUIRED,
        messages.REQUIRED_BY,
    ]

    tabular_data = []
    for package, requirers in missing:
        if requirers:
            for required_by, required_version in requirers:
                tabular_data.append([
                    printer.colored_message(
                        message=package.key,
                        message_color=printer.color_package
                    ),
                    required_version,
                    required_by.key,
                ])
        else:
            tabular_data.append([
                printer.colored_message(
                    message=package.key,
                    message_color=printer.color_package
                ),
                package.version.specifier,
                "Requirements",
            ])

    if tabular_data:
        printer.error(messages.MISSING_FOUND)
        printer.table(headers=headers, tabular_data=tabular_data)
        if exit_on_failure:
            sys.exit(1)
        return False

    printer.success(messages.MISSING_OK)
    return True
