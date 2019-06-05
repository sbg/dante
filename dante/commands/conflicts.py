import sys

from dante import messages
from dante.config import Config
from dante.core.printer import Printer
from dante.core.operations import dependency_list, conflicting_dependencies


def conflicts_command(args, packages=None, exit_on_failure=True):
    """Runs detection of dependency conflicts
    :param args: Command arguments
    :param packages: Collection of packages
    :param exit_on_failure: Enable/disable exiting application on failure
    :return: None
    """
    list_all = args.all or False
    ignore_list = (
        args.ignore or Config.ignore_list if not list_all else []
    )

    printer = Printer()
    packages = (
        packages or dependency_list(list_all=list_all, ignore_list=ignore_list)
    )

    conflicting = [
        (package, required_by)
        for package, required_by
        in conflicting_dependencies(packages=packages)
    ]

    headers = [
        messages.PACKAGE,
        messages.INSTALLED,
        messages.REQUIRED,
        messages.REQUIRED_BY,
    ]

    tabular_data = [
        [
            printer.colored_message(
                message=package.key,
                message_color=printer.color_package
            ),
            package.version_id,
            required_version,
            required_by.key,
        ]
        for package, requirement in conflicting
        for required_by, required_version in requirement
    ]

    if tabular_data:
        printer.error(messages.CONFLICTS_FOUND)
        printer.table(headers=headers, tabular_data=tabular_data)
        if exit_on_failure:
            sys.exit(1)
        return False

    printer.success(messages.CONFLICTS_OK)
    return True
