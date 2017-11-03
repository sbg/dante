import pipdeptree


def filter_tree(tree, list_all=True, show_only=None):
    """Filter the tree.
    :param dict tree: the package tree
    :param bool list_all: whether to list all the pgks at the root
                          level or only those that are the
                          sub-dependencies
    :param set show_only: set of select packages to be shown in the
                          output. This is optional arg, default: None.
    :returns: reversed tree
    :rtype: dict
    """
    tree = pipdeptree.sorted_tree(tree)
    branch_keys = set(r.key for r in pipdeptree.flatten(tree.values()))
    nodes = tree.keys()
    node_keys = [node.key for node in nodes]

    if show_only:
        node_keys = [node.key for node in nodes
                     if node.key in show_only or
                     node.project_name in show_only]
    elif not list_all:
        node_keys = [node.key for node in nodes if node.key not in
                     branch_keys]

    return dict([(node, deps) for node, deps in tree.items()
                 if node.key in node_keys])
