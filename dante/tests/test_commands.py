import faker
import pytest

from dante.core import commands
from dante.core.commands import VERSION_ANY


pytestmark = pytest.mark.commands
generator = faker.Factory.create()


def test_get_package_tree():
    # action
    tree = commands.get_package_tree()

    # verification
    assert 'pytest' in [package.key for package in tree]


def test_get_package_tree_with_ignore_list():
    # preconditions
    ignore_list = ['pip', 'faker', 'pytest']

    # action
    tree = commands.get_package_tree(ignore_list=ignore_list)

    # verification
    installed_keys = [package.key for package in tree]
    assert 'pip' not in installed_keys
    assert 'faker' not in installed_keys
    assert 'pytest' not in installed_keys


def test_get_package_tree_with_include_only():
    # preconditions
    include_only = ['pip', 'pytest']

    # action
    tree = commands.get_package_tree(include_only=include_only)

    # verification
    installed_keys = [package.key for package in tree]
    assert 'pip' in installed_keys
    assert 'pytest' in installed_keys
    assert 'faker' not in installed_keys


def test_get_all_packages():
    # preconditions
    include_only = ['pip', 'pytest', 'faker']
    tree = commands.get_package_tree(include_only=include_only)

    # action
    packages = commands.get_all_packages(tree=tree)

    # verification
    assert set(packages) == set(tree)


def test_get_main_packages():
    # preconditions
    include_only = ['py', 'pip', 'pytest', 'faker']
    tree = commands.get_package_tree(include_only=include_only)

    # action
    tree = commands.get_main_packages(tree=tree)

    # verification
    installed_keys = [package.key for package in tree]
    assert 'pip' in installed_keys
    assert 'faker' in installed_keys
    assert 'pytest' in installed_keys
    assert 'py' not in installed_keys


def test_get_secondary_packages():
    # preconditions
    include_only = ['py', 'pip', 'pytest', 'faker']
    tree = commands.get_package_tree(include_only=include_only)

    # action
    tree = commands.get_secondary_packages(tree=tree)

    # verification
    installed_keys = [package.key for package in tree]
    assert 'py' in installed_keys
    assert 'pip' not in installed_keys
    assert 'faker' not in installed_keys
    assert 'pytest' not in installed_keys


def test_get_installed_package_version():
    # preconditions
    include_only = ['pytest']
    tree = commands.get_package_tree(include_only=include_only)
    packages = commands.get_all_packages(tree=tree)
    dist_package = list(packages.keys())[0]
    req_packages = packages[dist_package]

    # action and verification
    version = commands.get_installed_package_version(package=dist_package)
    assert version == dist_package.version
    for package in req_packages:
        version = commands.get_installed_package_version(package=package)
        assert version == package.installed_version


def test_get_required_package_version():
    # preconditions
    include_only = ['pytest']
    tree = commands.get_package_tree(include_only=include_only)
    packages = commands.get_all_packages(tree=tree)

    dist_package = list(tree.keys())[0]
    req_packages = packages[dist_package]

    # action and verification
    for package in req_packages:
        version = commands.get_required_package_version(package=package)
        assert version == (package.version_spec or VERSION_ANY)


def test_package_list():
    # preconditions
    include_only = ['pip', 'pytest', 'faker']
    tree = commands.get_package_tree(include_only=include_only)
    packages = commands.get_all_packages(tree=tree)

    expected_packages = [
        {
            'name': package.key.lower(),
            'version': commands.get_installed_package_version(package=package)
        } for package in list(packages.keys())
    ]

    # action
    package_list = commands.get_package_list(tree=tree)

    # verification
    for expected_package in expected_packages:
        package = next((
            package for package in package_list
            if package['name'] == expected_package['name']
        ), None)

        assert package['version'] == expected_package['version']


def test_get_conflicting_dependencies():
    # preconditions
    include_only = ['pip', 'pytest']
    tree = commands.get_package_tree(include_only=include_only)

    # action
    conflicting_dependencies = commands.get_conflicting_dependencies(tree=tree)

    # verification
    assert conflicting_dependencies is None


def test_get_cyclic_dependencies():
    # preconditions
    include_only = ['pip', 'pytest']
    tree = commands.get_package_tree(include_only=include_only)

    # action
    cyclic_dependencies = commands.get_cyclic_dependencies(tree=tree)

    # verification
    assert cyclic_dependencies is None


def test_get_package_dependencies():
    # preconditions
    include_only = ['pytest']
    tree = commands.get_package_tree(include_only=include_only)

    key_tree = dict((k.key, v) for k, v in tree.items())
    package = next((item for item in tree if item.key == 'pytest'), None)

    expected_dependencies = {
        package: {}
    }

    for dependency in tree[package]:
        expected_dependencies[package].update({
            dependency: {}
        })

    # action
    dependencies = commands.get_package_dependencies(
        key_tree=key_tree,
        package=package
    )

    # verification
    assert dependencies == expected_dependencies


def test_get_dependencies():
    # preconditions
    include_only = ['pytest']
    tree = commands.get_package_tree(include_only=include_only)

    package = next(
        (package for package in tree if package.key == 'pytest'), None)

    package_dependencies = {
        package: {}
    }

    for dependency in tree[package]:
        package_dependencies[package].update({
            dependency: {}
        })

    expected_dependencies = [
        {
            'name': 'pytest',
            'children': package_dependencies
        }
    ]

    # action
    dependencies = commands.get_dependencies(tree=tree)

    # verification
    assert dependencies == expected_dependencies


def test_get_dependencies_for_package():
    # preconditions
    include_only = ['pytest']
    tree = commands.get_package_tree(include_only=include_only)

    package = next(
        (package for package in tree if package.key == 'pytest'), None)

    package_dependencies = {
        package: {}
    }

    for dependency in tree[package]:
        package_dependencies[package].update({
            dependency: {}
        })

    expected_dependencies = [
        {
            'name': 'pytest',
            'children': package_dependencies
        }
    ]

    # action
    dependencies = commands.get_dependencies(tree=tree, package_name='pytest')

    # verification
    assert dependencies == expected_dependencies


def test_parse_requirement_file():
    # preconditions
    requirements_file = 'dante/tests/requirements_files/requirements.txt'
    expected_requirements = ['pip']

    # action
    requirements = commands.parse_requirement_file(requirements_file)

    # verification
    for requirement in expected_requirements:
        assert requirement in requirements


def test_get_missing_requirements():
    # preconditions
    include_only = ['py', 'pip', 'pytest', 'faker']
    tree = commands.get_package_tree(include_only=include_only)
    required_packages = {
        'py': {},
        'pip': {},
        'pytest': {}
    }
    main_packages = commands.get_main_packages(tree=tree)

    # action
    missing_requirements = commands.get_missing_requirements(
        required_packages, main_packages)

    # verification
    assert 'faker' in [package.key for package in missing_requirements]


def test_get_unpinned_requirements():
    # preconditions
    include_only = ['py', 'pip', 'pytest']
    tree = commands.get_package_tree(include_only=include_only)

    required_packages = {
        'py': {},
        'pip': {},
        'pytest': None
    }

    # action
    unpinned_requirements = commands.get_unpinned_requirements(
        tree, required_packages)

    # verification
    unpinned_keys = [
        package['package_name'] for package in unpinned_requirements]

    assert 'pytest' in unpinned_keys
    assert 'py' not in unpinned_keys
    assert 'pip' not in unpinned_keys


def test_get_unset_constraints():
    # preconditions
    include_only = ['py', 'pip', 'pytest']
    tree = commands.get_package_tree(include_only=include_only)
    secondary_packages = commands.get_secondary_packages(tree)
    required_packages = {}
    constrained_packages = {}

    # action
    unset_constraints = commands.get_unset_constraints(
        required_packages, constrained_packages, secondary_packages)

    # verification
    assert 'py' in [package.key for package in unset_constraints]


def test_get_constraints_not_limited():
    # preconditions
    constrained_packages = {
        'py': None
    }

    # action
    constraints_not_limited = commands.get_constraints_not_limited(
        constrained_packages
    )

    # verification
    assert 'py' in constraints_not_limited


def test_get_requirements_packages():
    # preconditions
    requirements_files = [
        'dante/tests/requirements_files/requirements.txt',
        'dante/tests/requirements_files/requirements-dev.txt'
    ]

    # action
    packages = commands.get_requirements_packages(requirements_files)

    # verification
    assert 'pip' in packages
    assert 'pytest' in packages


def test_get_constraints_packages():
    # preconditions
    constraints_files = [
        'dante/tests/requirements_files/constraints.txt',
        'dante/tests/requirements_files/constraints-dev.txt'
    ]

    # action
    packages = commands.get_constraints_packages(constraints_files)

    # verification
    assert 'py' in packages


def test_get_outdated_package_table_data(given):
    # preconditions
    printer = given.printer.exists()
    include_only = ['py', 'pip', 'pytest']
    tree = commands.get_package_tree(include_only=include_only)
    required_version = generator.random_int()
    installed_version = generator.random_int()
    latest_version = generator.random_int()
    secondary_packages = commands.get_secondary_packages(tree)
    required_packages = {
        'pip': required_version
    }

    outdated_packages = [{
        'name': 'pip',
        'version': installed_version,
        'latest_version': latest_version
    }]

    expected_result = [[
        printer.printable_package('pip'), required_version, installed_version,
        latest_version
    ]]

    # action
    outdated_table_data = commands.get_outdated_package_table_data(
        required_packages, secondary_packages, outdated_packages)

    # verification
    assert outdated_table_data == expected_result
