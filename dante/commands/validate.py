import sys

from dante import messages
from dante.config import Config
from dante.core.printer import Printer
from dante.commands.utils import validate_files
from dante.core.models import RequirementCollection
from dante.core.operations import (
    dependency_list,
    unlocked_requirements,
    unset_locks,
    lock_version_mismatch,
    required_version_mismatch,
    unnecessary_packages,
    unnecessary_locks
)


def validate_command(args, packages=None, exit_on_failure=True):
    """Runs requirement file validation
    :param args: Command arguments
    :param packages: Collection of packages
    :param exit_on_failure: Enable/disable exiting application on failure
    :return: None
    """
    list_all = args.all or False
    strict = args.strict or False
    ignore_list = (
        args.ignore or Config.ignore_list if not list_all else []
    )
    requirements_files = (
        args.requirements or Config.requirements_files if not list_all else []
    )
    lock_files = (
        args.lock or Config.lock_files if not list_all else []
    )

    printer = Printer()
    if not validate_files(
            files=requirements_files,
            printer=printer,
            exit_on_failure=exit_on_failure
        ) or not validate_files(
            files=lock_files,
            printer=printer,
            exit_on_failure=exit_on_failure):
        return False

    try:
        requirements = RequirementCollection.from_files(
            filepaths=requirements_files
        )
        locked = RequirementCollection.from_files(filepaths=lock_files)
    except Exception as e:
        # Always exit on invalid requirements
        printer.error('{}: {}'.format(messages.REQUIREMENTS_PARSING_ERROR, e))
        sys.exit(1)

    checks_ok = []
    packages = (
        packages or dependency_list(list_all=list_all, ignore_list=ignore_list)
    )

    checks_ok.append(check_unlocked_requirements(
        requirements=requirements,
        printer=printer,
    ))
    checks_ok.append(check_unset_locks(
        requirements=requirements,
        locked=locked,
        printer=printer,
    ))
    checks_ok.append(check_package_version_mismatch(
        packages=packages,
        locked=locked,
        printer=printer,
    ))
    checks_ok.append(check_requirement_version_mismatch(
        requirements=requirements,
        locked=locked,
        printer=printer,
    ))

    if strict:
        checks_ok.append(check_unnecessary_packages(
            packages=packages,
            requirements=requirements,
            locked=locked,
            printer=printer,
        ))
        checks_ok.append(check_unnecessary_locks(
            requirements=requirements,
            locked=locked,
            printer=printer,
        ))

    return (
        sys.exit(1) if exit_on_failure else False
        if not all(checks_ok)
        else True
    )


def check_unlocked_requirements(requirements, printer=None):
    """Run validation that checks if there are requirements that are not locked
        to a version
    :param requirements: Collection of requirements
    :param printer: Printer object
    :return: Whether the validation was successful
    """
    printer = printer or Printer()
    requirements_unlocked = unlocked_requirements(requirements=requirements)

    headers = [
        messages.PACKAGE,
        messages.INSTALLED,
    ]

    tabular_data = [
        [
            printer.colored_message(
                message=package.key,
                message_color=printer.color_package
            ),
            package.version_id,
        ]
        for package in requirements_unlocked
    ]

    if tabular_data:
        printer.error(messages.UNLOCKED_REQUIREMENTS_FOUND)
        printer.table(
            headers=headers,
            tabular_data=tabular_data
        )
        return False

    printer.success(messages.UNLOCKED_REQUIREMENTS_OK)
    return True


def check_unset_locks(requirements, locked, printer=None):
    """Run validation that checks if there are requirements missing in
        locked requirements
    :param requirements: Collection of requirements
    :param locked: Collection of locked requirements
    :param printer: Printer object
    :return: Whether the validation was successful
    """
    printer = printer or Printer()
    locks_unset = unset_locks(requirements=requirements, locked=locked)

    headers = [
        messages.PACKAGE,
        messages.INSTALLED,
    ]

    tabular_data = [
        [
            printer.colored_message(
                message=package.key,
                message_color=printer.color_package
            ),
            package.version_id,
        ]
        for package in locks_unset
    ]

    if tabular_data:
        printer.error(messages.UNSET_LOCKS_FOUND)
        printer.table(
            headers=headers,
            tabular_data=tabular_data
        )
        return False

    printer.success(messages.UNSET_LOCKS_OK)
    return True


def check_package_version_mismatch(packages, locked, printer=None):
    """Run validation that checks if there are mismatches between installed
        packages and locked requirements
    :param packages: Collection of packages
    :param locked: Collection of locked requirements
    :param printer: Printer object
    :return: Whether the validation was successful
    """
    printer = printer or Printer()
    locked_versions = lock_version_mismatch(
        packages=packages, locked=locked
    )

    headers = [
        messages.PACKAGE,
        messages.INSTALLED,
        messages.REQUIRED,
    ]

    tabular_data = [
        [
            printer.colored_message(
                message=package.key,
                message_color=printer.color_package
            ),
            package.version_id,
            required,
        ]
        for package, required in locked_versions
    ]

    if tabular_data:
        printer.error(messages.PACKAGE_VERSION_MISMATCH_FOUND)
        printer.table(
            headers=headers,
            tabular_data=tabular_data
        )
        return False

    printer.success(messages.PACKAGE_VERSION_MISMATCH_OK)
    return True


def check_requirement_version_mismatch(requirements, locked, printer=None):
    """Run validation that checks if there are version mismatches between
        requirements and locked requirements
    :param requirements: Collection of requirements
    :param locked: Collection of locked requirements
    :param printer: Printer object
    :return: Whether the validation was successful
    """
    printer = printer or Printer()
    locked_versions = required_version_mismatch(
        requirements=requirements,
        locked=locked
    )

    headers = [
        messages.PACKAGE,
        messages.REQUIRED,
        messages.LOCKED,
    ]

    tabular_data = [
        [
            printer.colored_message(
                message=requirement.key,
                message_color=printer.color_package
            ),
            requirement.specified_version,
            required,
        ]
        for requirement, required in locked_versions
    ]

    if tabular_data:
        printer.error(messages.REQUIREMENT_VERSION_MISMATCH_FOUND)
        printer.table(
            headers=headers,
            tabular_data=tabular_data
        )
        return False

    printer.success(messages.REQUIREMENT_VERSION_MISMATCH_OK)
    return True


def check_unnecessary_packages(
        packages, requirements, locked, printer=None):
    """Run validation that checks if there are unnecessary installed packages
        in the environment that are not required by anything
    :param packages: Collection of packages
    :param requirements: Collection of requirements
    :param locked: Collection of locked requirements
    :param printer: Printer object
    :return: Whether the validation was successful
    """
    printer = printer or Printer()
    lock_not_required = unnecessary_packages(
        packages=packages, requirements=requirements, locked=locked
    )

    headers = [
        messages.PACKAGE,
        messages.INSTALLED,
    ]

    tabular_data = [
        [
            printer.colored_message(
                message=package.key,
                message_color=printer.color_package
            ),
            package.version_id,
        ]
        for package in lock_not_required
    ]

    if tabular_data:
        printer.warning(messages.PACKAGE_NOT_REQUIRED_FOUND)
        printer.table(
            headers=headers,
            tabular_data=tabular_data
        )
        return False

    printer.success(messages.PACKAGE_NOT_REQUIRED_OK)
    return True


def check_unnecessary_locks(requirements, locked, printer=None):
    """Run validation that checks if there are unnecessary locked requirements
        that are not required by anything
    :param requirements: Collection of requirements
    :param locked: Collection of locked requirements
    :param printer: Printer object
    :return: Whether the validation was successful
    """
    printer = printer or Printer()
    lock_not_required = unnecessary_locks(
        requirements=requirements, locked=locked
    )

    headers = [
        messages.PACKAGE,
        messages.LOCKED,
    ]

    tabular_data = [
        [
            printer.colored_message(
                message=requirement.key,
                message_color=printer.color_package
            ),
            requirement.specified_version,
        ]
        for requirement in lock_not_required
    ]

    if tabular_data:
        printer.warning(messages.LOCK_NOT_REQUIRED_FOUND)
        printer.table(
            headers=headers,
            tabular_data=tabular_data
        )
        return False

    printer.success(messages.LOCK_NOT_REQUIRED_OK)
    return True
