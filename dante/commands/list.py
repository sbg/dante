from dante import messages
from dante.config import Config
from dante.core.printer import Printer
from dante.commands.utils import validate_files
from dante.core.operations import dependency_list
from dante.core.models import RequirementCollection


def list_command(args, packages=None, exit_on_failure=True):
    """List installed dependencies with configurable filters
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
            exit_on_failure=exit_on_failure
    ):
        return False

    requirements = RequirementCollection()
    for requirements_file in requirements_files:
        requirements.extend(
            RequirementCollection.from_file(filepath=requirements_file)
        )

    requirements = requirements if requirements else None
    packages = (
        packages or dependency_list(
            list_all=list_all,
            ignore_list=ignore_list,
            requirements=requirements
        )
    )

    headers = [messages.PACKAGE, messages.INSTALLED]
    tabular_data = [
        [
            printer.colored_message(
                message=package.key,
                message_color=printer.color_package
            ),
            package.version_id
        ]
        for package in packages
    ]

    if tabular_data:
        printer.table(headers=headers, tabular_data=tabular_data)
    else:
        printer.info(messages.PACKAGES_NOT_FOUND)

    return True
