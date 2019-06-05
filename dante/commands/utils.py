import os
import sys

from dante.core.printer import Printer


def validate_files(files, printer=None, exit_on_failure=True):
    """Validate all provided files exist
    :param files: List of files
    :param printer: Printer object
    :param exit_on_failure: Enable/disable exiting application on failure
    :return: Whether the files are valid
    """
    invalid_files = []
    printer = printer or Printer()
    for file_ in files:
        if not os.path.exists(file_):
            if exit_on_failure:
                printer.error('File "{}" not found'.format(file_))
            invalid_files.append(file_)
    return (
        True if not invalid_files
        else sys.exit(1) if exit_on_failure
        else False
    )
