import sys

from dante import messages
from dante.config import Config
from dante.core.printer import Printer
from dante.core.operations import dependency_list, cyclic_dependencies


def cyclic_command(args, packages=None, exit_on_failure=True):
    """Runs detection of cyclical dependencies
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

    cyclic_paths = cyclic_dependencies(packages=packages)

    if cyclic_paths:
        printer.error(messages.CYCLIC_FOUND)
        for path in cyclic_paths:
            if path:
                path.append(path[0])
                path_message = ' -> '.join(map(lambda p: p.key, path))
                printer.info(message=path_message)
        if exit_on_failure:
            sys.exit(1)
        return False

    printer.success(messages.CYCLIC_OK)
    return True
