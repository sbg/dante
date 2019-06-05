import argparse


def cli():
    """Returns argument parser for dante
    :return: argument parser object
    """
    from dante import commands, __version__

    parser = argparse.ArgumentParser(
        description='Python dependency management utility'
    )
    parser.add_argument(
        '-v', '--version', action='version', version=__version__
    )
    parser.add_argument(
        '-a', '--all', action='store_true', help='Show all packages'
    )
    parser.add_argument(
        '-i', '--ignore', action='append', help='Ignore dependency'
    )

    subparsers = parser.add_subparsers()

    # CONFIG
    parser_config = subparsers.add_parser(
        name='config',
        help='Print configuration'
    )
    parser_config.set_defaults(func=commands.config_command)

    # CONFLICTS
    parser_conflicts = subparsers.add_parser(
        name='conflicts',
        help='Check for conflicts in required dependencies'
    )
    parser_conflicts.set_defaults(func=commands.conflicts_command)

    # CYCLIC
    parser_cyclic = subparsers.add_parser(
        name='cyclic',
        help='Check for cyclic dependencies'
    )
    parser_cyclic.set_defaults(func=commands.cyclic_command)

    # LIST
    parser_list = subparsers.add_parser(
        name='list',
        help='List all dependencies'
    )
    parser_list.add_argument(
        '-r',
        '--requirements',
        action='append',
        help='Requirement file(s)'
    )
    parser_list.set_defaults(func=commands.list_command)

    # DEPENDENCY TREE
    parser_dependency = subparsers.add_parser(
        name='tree',
        help='Show dependency tree'
    )
    parser_dependency.add_argument(
        '-p', '--package', help='Show dependency tree for specified package'
    )
    parser_dependency.add_argument(
        '-r',
        '--requirements',
        action='append',
        help='Requirement file(s)'
    )
    parser_dependency.set_defaults(func=commands.tree_command)

    # MISSING
    parser_missing = subparsers.add_parser(
        name='missing',
        help='Show missing dependencies'
    )
    parser_missing.add_argument(
        '-r',
        '--requirements',
        action='append',
        help='Requirement file(s)'
    )
    parser_missing.set_defaults(func=commands.missing_requirements_command)

    # CHECK
    parser_check = subparsers.add_parser(
        name='check',
        help='Run a complete list of checks'
    )
    parser_check.add_argument(
        '-r',
        '--requirements',
        action='append',
        help='Requirement file(s)'
    )
    parser_check.add_argument(
        '-l',
        '--lock',
        action='append',
        help='Lock file(s)'
    )
    parser_check.set_defaults(func=commands.check_all)
    parser_check.add_argument(
        '-s',
        '--strict',
        action='store_true',
        help='Packages not required cause an error'
    )

    # LOCK
    parser_lock = subparsers.add_parser(
        'lock',
        help='Display or generate lock file from environment '
             'and/or requirements file(s)'
    )
    parser_lock.add_argument(
        '-r',
        '--requirements',
        action='append',
        help='Requirements file(s)'
    )
    parser_lock.add_argument(
        '-s',
        '--save',
        action='store_true',
        help='Generate lock file'
    )
    parser_lock.add_argument(
        '-f',
        '--file',
        help='Specify path for lock file'
    )
    parser_lock.set_defaults(func=commands.lock_command)

    # VALIDATE
    parser_validate = subparsers.add_parser(
        'validate',
        help='Validate requirements and lock files'
    )
    parser_validate.add_argument(
        '-r',
        '--requirements',
        action='append',
        help='Requirement file(s)'
    )
    parser_validate.add_argument(
        '-l',
        '--lock',
        action='append',
        help='Lock file(s)'
    )
    parser_validate.add_argument(
        '-s',
        '--strict',
        action='store_true',
        help='Packages not required cause an error'
    )
    parser_validate.set_defaults(func=commands.validate_command)

    # GRAPH
    parser_graph = subparsers.add_parser(
        name='graph',
        help='Export a dependency graph using graphviz'
    )
    parser_graph.set_defaults(func=commands.graph_command)
    parser_graph.add_argument(
        '-s',
        '--strict',
        action='store_true',
        help='Rendering should merge multi-edges'
    )
    parser_graph.add_argument(
        '-r',
        '--render',
        action='store_true',
        help='Render graph'
    )
    parser_graph.add_argument(
        '-v',
        '--view',
        action='store_true',
        help='Display graph after rendering'
    )
    parser_graph.add_argument('--name', help='Graph name')
    parser_graph.add_argument('--filename', help='Export filename')
    parser_graph.add_argument('--format', help='Export format')
    parser_graph.add_argument('--engine', help='Rendering engine')
    parser_graph.add_argument('--graph_attr', help='Graph attributes')
    parser_graph.add_argument('--node_attr', help='Node attributes')
    parser_graph.add_argument('--edge_attr', help='Edge attributes')

    return parser
