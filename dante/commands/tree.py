import sys

from dante import messages
from dante.config import Config
from dante.core.operations import (
    dependency_list,
    dependency_tree,
    package_dependency_tree
)
from dante.core.printer import Printer
from dante.commands.utils import validate_files
from dante.core.models import RequirementCollection


def tree_command(args, packages=None, exit_on_failure=True):
    """Display dependency tree for a single package or the entire environment
    :param args: Command arguments
    :param packages: Collection of packages
    :param exit_on_failure: Enable/disable exiting application on failure
    :return: None
    """
    list_all = args.all or False
    package_key = args.package
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

    package_string = '{package} [{installed}: {version}]'
    requirement_string = (
        '{spacing}{package} [{installed}: {version} | {required}: {spec}]'
    )

    packages = (
        packages or dependency_list(list_all=list_all, ignore_list=ignore_list)
    )

    if package_key:
        package = packages.get(key=package_key)
        if not package:
            printer.error(
                messages.PACKAGE_NOT_FOUND.format(package=package_key)
            )
            sys.exit(1)

        tree = {
            package: package_dependency_tree(dependency=package)
        }
    else:
        tree = dependency_tree(
            packages=packages,
            requirements=requirements if requirements else None
        )

    if not tree:
        printer.info(messages.PACKAGES_NOT_FOUND)

    def print_dependency_tree(requirements_list, indent=0):
        spacing = ' ' * indent
        for requirement in requirements_list:
            printer.info(
                requirement_string
                .format(
                    spacing=spacing,
                    package=printer.colored_message(
                        message=requirement.key,
                        message_color=printer.color_package
                    ),
                    installed=messages.INSTALLED,
                    version=requirement.version_id,
                    required=messages.REQUIRED,
                    spec=requirement.specified_version
                ),
            )
            print_dependency_tree(requirements_list[requirement], indent + 2)

    for dependency in tree:
        printer.info(
            package_string
            .format(
                package=printer.colored_message(
                    message=dependency.key,
                    message_color=printer.color_package
                ),
                installed=messages.INSTALLED,
                version=dependency.version
            )
        )
        print_dependency_tree(tree[dependency], indent=2)

    return True
