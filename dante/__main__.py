"""Dante entry point"""

import sys
import argparse

try:
    import colorama
except ImportError:
    colorama = None

from dante.core import commands


def get_parser():
    """Returns argument parser for dante
    :return: argument parser object
    """
    parser = argparse.ArgumentParser(
        description='Python dependency management utility'
    )
    parser.add_argument(
        '-i',
        '--ignore',
        action='append',
        help='Ignore specified dependencies'
    )
    subparsers = parser.add_subparsers()

    # CONFLICTS
    parser_conflicts = subparsers.add_parser(
        'conflicts',
        help='Check for conflicts in required dependencies'
    )
    parser_conflicts.set_defaults(func=commands.check_conflicts)

    # LIST
    parser_list = subparsers.add_parser(
        'list',
        help='List all dependencies'
    )
    parser_list.add_argument(
        '-m',
        '--main',
        action='store_true',
        help='List all top level dependencies'
    )
    parser_list.add_argument(
        '-s',
        '--secondary',
        action='store_true',
        help='List all secondary dependencies'
    )
    parser_list.set_defaults(func=commands.list_dependencies)

    # UPGRADES
    parser_upgrades = subparsers.add_parser(
        'upgrades',
        help='Check for upgrades for all dependencies'
    )
    parser_upgrades.add_argument(
        '-r',
        '--requirements',
        action='append',
        help='Requirements file(s) to check for versions'
    )
    parser_upgrades.set_defaults(func=commands.check_for_upgrades)

    # DEPENDENCIES
    parser_dependency = subparsers.add_parser(
        'dependencies',
        help='Show dependency tree'
    )
    parser_dependency.add_argument(
        '-p',
        '--package_name',
        help='List dependency tree for specified package'
    )
    parser_dependency.set_defaults(func=commands.print_dependency_tree)

    # CHECK
    parser_check = subparsers.add_parser(
        'check',
        help='Check requirement and constraint files for possible errors'
    )
    parser_check.add_argument(
        '-r',
        '--requirements',
        action='append',
        help='Requirement file(s) to check'
    )
    parser_check.add_argument(
        '-c',
        '--constraints',
        action='append',
        help='Constraint file(s) to check'
    )
    parser_check.set_defaults(func=commands.check)

    return parser


def main():
    """Dante main function"""
    if colorama:
        colorama.init(autoreset=True)

    parser = get_parser()
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()


if __name__ == '__main__':
    sys.exit(main())
