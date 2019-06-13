from dante import messages
from dante.core import color
from dante.config import Config
from dante.core.printer import Printer
from dante.commands.utils import validate_files
from dante.core.models import RequirementCollection
from dante.core.operations import dependency_list, locked_requirements


def lock_command(args, packages=None, exit_on_failure=True):
    """Display or save locked requirements for current environment
    :param args: Command arguments
    :param packages: Collection of packages
    :param exit_on_failure: Enable/disable exiting application on failure
    :return: None
    """
    requirements_files = (
        args.requirements or Config.requirements_files or []
    )
    ignore_list = (
        args.ignore or Config.ignore_list or []
    )
    save_lock = args.save or False
    lock_filepath = args.file or Config.lock_file_path

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

    lock_ignore_list = [
        key for key in ignore_list if key not in requirements.keys()
    ]

    packages = (
        packages or
        dependency_list(ignore_list=lock_ignore_list)
    )

    locked = locked_requirements(
        packages=packages, requirements=requirements
    )

    if save_lock:
        locked.save_lock_file(filepath=lock_filepath)
        printer.success(message=messages.LOCK_EXPORTED.format(
            file_path=lock_filepath
        ))
    else:
        for item in locked:
            printer.info("{}=={}".format(
                printer.colored_message(item.key, color.DEFAULT_PACKAGE),
                item.version_id
            ))

    return True
