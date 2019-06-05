from dante.config import Config
from dante.vendor import graphviz

NODE_FORMAT = (
    '<<table border="0">'
    '<tr><td><b>{package}</b></td></tr>'
    '<tr><td>{version}</td></tr>'
    '</table>>'
)
FILE_PATH_FORMAT = '{filename}.{format}'


def create_dependency_graph(packages=None, name=None, filename=None,
                            file_format=None, engine=None, strict=True,
                            graph_attr=None, node_attr=None, edge_attr=None):
    """Creates a dependency graph
    :param packages: Installed packages
    :param name: Graph name
    :param filename: Export filename
    :param file_format: Export format
    :param engine: Rendering engine
    :param strict: Rendering should merge multi-edges
    :param graph_attr: Graph attributes
    :param node_attr: Node attributes
    :param edge_attr: Edge attributes
    :return: Graph filepath
    """
    name = name or Config.graph_name
    filename = filename or Config.graph_filename
    file_format = file_format or Config.graph_format
    engine = engine or Config.graph_engine
    strict = strict or Config.graph_strict
    graph_attr = graph_attr or Config.graph_attributes
    node_attr = node_attr or Config.graph_node_attributes
    edge_attr = edge_attr or Config.graph_edge_attributes

    # Use current directory if filename is not provided
    if not filename:
        filename = name

    graph = graphviz.Digraph(
        name=name,
        filename=filename,
        format=file_format,
        engine=engine,
        strict=strict,
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    )

    for package in packages:
        graph.node(
            name=package.key,
            label=NODE_FORMAT.format(
                package=package.key,
                version=package.version_id
            )
        )
        for requirement in package.requirements:
            graph.edge(
                tail_name=package.key,
                head_name=requirement.key,
                label=str(requirement.specified_version)
            )
    return graph


def render_dependency_graph(graph, view=False):
    """Renders a dependency graph
    :param graph: Graph to render
    :param view: Display created graph
    :return: Saved render filepath
    """
    graph.render(view=view, cleanup=True)
    return FILE_PATH_FORMAT.format(
        filename=graph.filename,
        format=graph.format
    )
