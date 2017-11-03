import pytest

from dante.core import commands
from dante.core import utils


pytestmark = pytest.mark.utils


def test_filter_tree():
    # preconditions
    tree = commands.get_package_tree()

    # action
    filtered_tree = utils.filter_tree(tree=tree, list_all=True)

    # verification
    assert set(filtered_tree) == set(tree)


def test_filter_tree_only_top_level():
    # preconditions
    tree = commands.get_package_tree()

    # action
    filtered_tree = utils.filter_tree(tree=tree, list_all=False)

    # verification
    assert not set(filtered_tree) == set(tree)


def test_filter_tree_only_specified():
    # preconditions
    tree = commands.get_package_tree()
    show_only = {'pip'}

    # action
    filtered_tree = utils.filter_tree(tree=tree, show_only=show_only)

    # verification
    assert len(filtered_tree) == 1
    assert 'pip' in [package.key for package in filtered_tree]
