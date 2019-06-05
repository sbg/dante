import sys

from dante import messages
from dante.config import Config
from dante.core.printer import Printer
from dante.core.operations import (
    dependency_list,
    get_graph,
    render_graph,
)


def graph_command(args, packages=None, exit_on_failure=True):
    """Return or render a dependency graph
    :param args: Command arguments
    :param packages: Collection of packages
    :param exit_on_failure: Enable/disable exiting application on failure
    :return: None
    """
    list_all = args.all or False
    ignore_list = (
        args.ignore or Config.ignore_list if not list_all else []
    )

    name = args.name or Config.graph_name
    filename = args.filename or Config.graph_filename
    file_format = args.format or Config.graph_format
    engine = args.engine or Config.graph_engine
    strict = args.strict or Config.graph_strict
    graph_attr = args.graph_attr or Config.graph_attributes
    node_attr = args.node_attr or Config.graph_node_attributes
    edge_attr = args.edge_attr or Config.graph_edge_attributes
    view = args.view or False
    render = args.render or False

    printer = Printer()
    packages = (
        packages or dependency_list(list_all=list_all, ignore_list=ignore_list)
    )

    graph = get_graph(
        packages=packages, name=name, filename=filename,
        file_format=file_format, engine=engine, strict=strict,
        graph_attr=graph_attr, node_attr=node_attr, edge_attr=edge_attr,
    )

    if render:
        try:
            filepath = render_graph(graph=graph, view=view)
            printer.success(
                messages.GRAPH_EXPORTED.format(
                    file_path=filepath,
                    format=file_format
                )
            )
        except Exception as e:
            printer.error(messages.GRAPH_FAILED_TO_RENDER.format(error=e))
            return sys.exit(1) if exit_on_failure else ''

    else:
        printer.print_message(message=graph)
