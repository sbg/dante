import sys

import dante
from dante.config import Config
from dante.core.operations import dependency_list


def check_all(args):
    """Run all predefined checks, can be overridden in the configuration
    :param args: Command arguments
    :return: None
    """
    list_all = args.all or False
    ignore_list = args.ignore or []
    checks_ok = []

    packages = dependency_list(list_all=list_all, ignore_list=ignore_list)

    if 'validate' in Config.checks:
        checks_ok.append(dante.commands.validate_command(
            args=args, packages=packages, exit_on_failure=False,
        ))

    if 'conflicts' in Config.checks:
        checks_ok.append(dante.commands.conflicts_command(
            args=args, packages=packages, exit_on_failure=False,
        ))

    if 'cyclic' in Config.checks:
        checks_ok.append(dante.commands.cyclic_command(
            args=args, packages=packages, exit_on_failure=False,
        ))

    if 'missing' in Config.checks:
        checks_ok.append(dante.commands.missing_requirements_command(
            args=args, packages=packages, exit_on_failure=False,
        ))

    if not all(checks_ok):
        sys.exit(1)
