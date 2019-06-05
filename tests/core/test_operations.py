from pathlib import Path
from collections import OrderedDict

import pytest

from dante.config import Config
from dante.core import operations
from dante.core.graph import FILE_PATH_FORMAT
from dante.core.models import (
    PackageCollection, Requirement, RequirementCollection
)

from dante.vendor import pkg_resources

pytestmark = pytest.mark.operations

INSTALLER = 'pip install --no-deps'
DANTE = Path(Config.PARENT_DIR)
PACKAGES_DIR = Path(Path(Config.PARENT_DIR) / 'tests' / 'packages')


def prepare_working_set(venv, packages):
    for package in packages:
        venv.install_package(package, installer=INSTALLER)

    installed = venv.installed_packages()
    venv_path = installed['pip'].source_path

    working_set = pkg_resources.WorkingSet([])
    working_set.add_entry(venv_path)
    return working_set


def prepare_packages(venv, mocker, packages):
    working_set = prepare_working_set(venv, packages)
    mocker.patch('dante.vendor.pkg_resources.working_set', working_set)
    return PackageCollection.from_distributions(
        packages=[package for package in working_set],
        ignore_list=Config.ignore_list
    )


def list_recursive(d, depth=0):
    """Retrieve OrderedDict requirement keys and
    depth at which they were found
    """
    for requirement, v in d.items():
        if isinstance(v, OrderedDict):
            depth += 1
            for found in list_recursive(v, depth):
                yield found
            depth -= 1
        yield (requirement.key, depth)


def test_dependency_list(virtualenv, mocker):
    # preconditions
    package1_path = PACKAGES_DIR / 'dependencies' / 'dependency-package1'
    package2_path = PACKAGES_DIR / 'dependencies' / 'dependency-package2'

    working_set = prepare_working_set(
        venv=virtualenv,
        packages=[package1_path, package2_path]
    )
    requirements = RequirementCollection(
        [Requirement.from_requirement_string('dependency-package1')]
    )
    mocker.patch('dante.vendor.pkg_resources.working_set', working_set)

    # action
    installed_dependencies = operations.dependency_list()
    installed_dependencies_with_requirements = operations.dependency_list(
        requirements=requirements
    )

    # verification
    assert (
        ['dependency-package1', 'dependency-package2'] ==
        installed_dependencies.keys()
    )
    assert (
        ['dependency-package1'] ==
        installed_dependencies_with_requirements.keys()
    )


def test_required_by(virtualenv, mocker):
    # preconditions
    package_dep_path = PACKAGES_DIR / 'conflicting' / 'conflicting-dep'
    package_1_path = PACKAGES_DIR / 'conflicting' / 'conflicting-package1'

    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[package_dep_path, package_1_path]
    )

    package_1 = packages.get(key='conflicting-package1')
    requirement_dep = package_1.requirements.get('conflicting-dep')

    # action
    required_by = operations.required_by(
        requirement=requirement_dep,
        packages=packages
    )

    # verification
    assert required_by == [(package_1, requirement_dep.version)]


def test_conflicting_dependencies(virtualenv, mocker):
    # preconditions
    package_dep_path = PACKAGES_DIR / 'conflicting' / 'conflicting-dep'
    package_1_path = PACKAGES_DIR / 'conflicting' / 'conflicting-package1'
    package_2_path = PACKAGES_DIR / 'conflicting' / 'conflicting-package2'
    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[package_dep_path, package_1_path, package_2_path]
    )
    package_1 = packages.get(key='conflicting-package1')
    package_2 = packages.get(key='conflicting-package2')
    requirement_dep_1 = package_1.requirements.get('conflicting-dep')
    requirement_dep_2 = package_2.requirements.get('conflicting-dep')

    # action
    conflicting = operations.conflicting_dependencies(packages=packages)

    # verification
    assert conflicting == [(
        requirement_dep_1, [
            (package_1, requirement_dep_1.version),
            (package_2, requirement_dep_2.version)
        ]
    )]


@pytest.mark.parametrize(
    ['allow_named_versions', 'named_version_patterns'],
    [
        [True,  []],
        [False, []],
        [True,  ['0.*version']],
        [False, ['0.*version']],
    ]
)
def test_conflicting_dependencies_named(
        virtualenv, mocker, allow_named_versions, named_version_patterns
):
    # preconditions
    package_1_path = PACKAGES_DIR / 'named' / 'named-package1'
    package_2_path = PACKAGES_DIR / 'named' / 'named-package2'
    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[package_1_path, package_2_path]
    )

    # action
    conflicting = operations.conflicting_dependencies(
        packages=packages,
        allow_named_versions=allow_named_versions,
        named_version_patterns=named_version_patterns
    )

    # verification
    assert (
        conflicting == []
        if allow_named_versions and named_version_patterns
        else conflicting
    )


def test_cyclic_dependencies(virtualenv, mocker):
    # preconditions
    cyclic_package1_path = PACKAGES_DIR / 'cyclic' / 'cyclic-package1'
    cyclic_package2_path = PACKAGES_DIR / 'cyclic' / 'cyclic-package2'
    cyclic_package3_path = PACKAGES_DIR / 'cyclic' / 'cyclic-package3'
    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[
            cyclic_package1_path, cyclic_package2_path, cyclic_package3_path
        ]
    )
    cyclic_package1 = packages.get('cyclic-package1')
    cyclic_package2 = packages.get('cyclic-package2')
    cyclic_package3 = packages.get('cyclic-package3')

    # action
    cyclic = operations.cyclic_dependencies(packages=packages)

    # verification
    assert cyclic == [[cyclic_package1, cyclic_package2, cyclic_package3]]


def test_missing_requirements(virtualenv, mocker):
    # preconditions
    missing_package1_path = PACKAGES_DIR / 'missing' / 'missing-package1'
    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[missing_package1_path]
    )
    package1 = packages.get(key='missing-package1')
    requirement_dep = package1.requirements.get('missing-dep')

    # action
    missing = operations.missing_requirements(
        packages=packages,
        requirements=packages.requirements
    )

    # verification
    assert missing == [
        (requirement_dep, [(package1, requirement_dep.version)])
    ]


def test_unset_requirements(virtualenv, mocker):
    # preconditions
    example_package_path = PACKAGES_DIR / 'example-package'
    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[example_package_path]
    )
    requirements = RequirementCollection()

    # action
    unset = operations.unset_requirements(
        packages=packages,
        requirements=requirements
    )

    # verification
    assert ['example-package'] == unset.keys()


def test_unlocked_requirements():
    # preconditions
    requirement_file_path = str(PACKAGES_DIR / 'requirements-unset.txt')
    requirements = RequirementCollection.from_file(
        filepath=requirement_file_path
    )

    # action
    unlocked = operations.unlocked_requirements(requirements=requirements)

    # verification
    assert ['package2', 'package3'] == unlocked.keys()


def test_unset_locks():
    # preconditions
    requirement_file_path = str(PACKAGES_DIR / 'requirements-unset.txt')
    lock_file_path = str(PACKAGES_DIR / 'requirements-unset.lock')
    requirements = RequirementCollection.from_file(
        filepath=requirement_file_path
    )
    locked = RequirementCollection.from_file(
        filepath=lock_file_path
    )

    # action
    unset = operations.unset_locks(requirements=requirements, locked=locked)

    # verification
    assert ['package2', 'package3'] == unset.keys()


def test_package_dependency_tree(virtualenv, mocker):
    """Prepared package tree structure:

    package1
        package3
        package4
            package5
            package6
    package2
        package3
        package7
            package8
    """
    # preconditions
    tree_package1_path = PACKAGES_DIR / 'tree' / 'tree-package1'
    tree_package2_path = PACKAGES_DIR / 'tree' / 'tree-package2'
    tree_package3_path = PACKAGES_DIR / 'tree' / 'tree-package3'
    tree_package4_path = PACKAGES_DIR / 'tree' / 'tree-package4'
    tree_package5_path = PACKAGES_DIR / 'tree' / 'tree-package5'
    tree_package6_path = PACKAGES_DIR / 'tree' / 'tree-package6'
    tree_package7_path = PACKAGES_DIR / 'tree' / 'tree-package7'
    tree_package8_path = PACKAGES_DIR / 'tree' / 'tree-package8'

    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[
            tree_package1_path,
            tree_package2_path,
            tree_package3_path,
            tree_package4_path,
            tree_package5_path,
            tree_package6_path,
            tree_package7_path,
            tree_package8_path,
        ]
    )

    package1 = packages.get('tree-package1')
    requirements = package1.requirements.flatten()
    requirement3 = requirements.get('tree-package3')
    requirement4 = requirements.get('tree-package4')
    requirement5 = requirements.get('tree-package5')
    requirement6 = requirements.get('tree-package6')

    expected_tree = OrderedDict([
        (requirement3, OrderedDict()),
        (requirement4, OrderedDict([
            (requirement5, OrderedDict()),
            (requirement6, OrderedDict()),
        ]))
    ])

    # action
    tree = operations.package_dependency_tree(dependency=package1)

    # verification
    assert (
        [k for k in list_recursive(expected_tree)] ==
        [k for k in list_recursive(tree)]
    )


def test_dependency_tree(virtualenv, mocker):
    """Prepared package tree structure:

    package1
        package3
        package4
            package5
            package6
    package2
        package3
        package7
            package8
    """
    # preconditions
    tree_package1_path = PACKAGES_DIR / 'tree' / 'tree-package1'
    tree_package2_path = PACKAGES_DIR / 'tree' / 'tree-package2'
    tree_package3_path = PACKAGES_DIR / 'tree' / 'tree-package3'
    tree_package4_path = PACKAGES_DIR / 'tree' / 'tree-package4'
    tree_package5_path = PACKAGES_DIR / 'tree' / 'tree-package5'
    tree_package6_path = PACKAGES_DIR / 'tree' / 'tree-package6'
    tree_package7_path = PACKAGES_DIR / 'tree' / 'tree-package7'
    tree_package8_path = PACKAGES_DIR / 'tree' / 'tree-package8'

    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[
            tree_package1_path,
            tree_package2_path,
            tree_package3_path,
            tree_package4_path,
            tree_package5_path,
            tree_package6_path,
            tree_package7_path,
            tree_package8_path,
        ]
    )

    package1 = packages.get('tree-package1')
    package2 = packages.get('tree-package2')
    requirements1 = package1.requirements.flatten()
    requirements2 = package2.requirements.flatten()

    requirement3 = requirements1.get('tree-package3')
    requirement4 = requirements1.get('tree-package4')
    requirement5 = requirements1.get('tree-package5')
    requirement6 = requirements1.get('tree-package6')
    requirement7 = requirements2.get('tree-package7')
    requirement8 = requirements2.get('tree-package8')

    expected_tree = OrderedDict([
        (
            package1, OrderedDict([
                (requirement3, OrderedDict()),
                (requirement4, OrderedDict([
                    (requirement5, OrderedDict()),
                    (requirement6, OrderedDict()),
                ]))
            ])
        ),
        (
            package2, OrderedDict([
                (requirement3, OrderedDict()),
                (requirement7, OrderedDict([
                    (requirement8, OrderedDict()),
                ]))
            ])
        ),
    ])

    # action
    tree = operations.dependency_tree(packages=packages)

    # verification
    assert (
            [k for k in list_recursive(expected_tree)] ==
            [k for k in list_recursive(tree)]
    )


def test_locked_requirements(virtualenv, mocker):
    # preconditions
    locked_package1_path = PACKAGES_DIR / 'locked' / 'locked-package1'
    locked_package2_path = PACKAGES_DIR / 'locked' / 'locked-package2'
    locked_package3_path = PACKAGES_DIR / 'locked' / 'locked-package3'

    expected_result = ['locked-package1', 'locked-package2', 'locked-package3']

    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[
            locked_package1_path,
            locked_package2_path,
            locked_package3_path,
        ]
    )
    requirements_empty = RequirementCollection()
    requirements = RequirementCollection()

    package_1 = packages.get(key='locked-package1')
    requirement_1 = Requirement.from_package(package_1)
    requirements.append(requirement_1)

    # action
    locked_no_requirements = operations.locked_requirements(
        packages=packages,
        requirements=requirements_empty
    )
    locked = operations.locked_requirements(
        packages=packages,
        requirements=requirements
    )

    # verification
    assert expected_result == locked_no_requirements.keys()
    assert expected_result == locked.keys()
    for lock in locked_no_requirements:
        assert lock.version.specifier == '==1.0.0'
    for lock in locked:
        assert lock.version.specifier == '==1.0.0'


def test_lock_version_mismatch(virtualenv, mocker):
    # preconditions
    mismatch_package1_path = PACKAGES_DIR / 'mismatch' / 'mismatch-package1'
    mismatch_package2_path = PACKAGES_DIR / 'mismatch' / 'mismatch-package2'
    mismatch_package3_path = PACKAGES_DIR / 'mismatch' / 'mismatch-package3'
    requirements_file_path = PACKAGES_DIR / 'requirements-mismatch.lock'

    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[
            mismatch_package1_path,
            mismatch_package2_path,
            mismatch_package3_path,
        ]
    )

    expected_mismatch = [
        (packages.get('mismatch-package2'), '==2.0.0'),
        (packages.get('mismatch-package3'), '>=3.0.0'),
    ]

    requirements = RequirementCollection.from_file(
        filepath=requirements_file_path
    )

    # action
    mismatch = operations.lock_version_mismatch(
        packages=packages, locked=requirements
    )

    # verification
    assert expected_mismatch == mismatch


def test_unnecessary_requirements(virtualenv, mocker):
    # preconditions
    example_package_path = PACKAGES_DIR / 'example-package'
    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[example_package_path]
    )
    requirements = RequirementCollection()
    locked = RequirementCollection()

    # action
    unnecessary = operations.unnecessary_packages(
        packages=packages,
        requirements=requirements,
        locked=locked
    )

    # verification
    assert ['example-package'] == unnecessary.keys()


def test_create_graph(virtualenv, mocker, tmp_path):
    # preconditions
    file_format = 'png'
    filename = str(tmp_path / 'graph')
    locked_package1_path = PACKAGES_DIR / 'locked' / 'locked-package1'
    locked_package2_path = PACKAGES_DIR / 'locked' / 'locked-package2'
    locked_package3_path = PACKAGES_DIR / 'locked' / 'locked-package3'

    packages = prepare_packages(
        venv=virtualenv,
        mocker=mocker,
        packages=[
            locked_package1_path,
            locked_package2_path,
            locked_package3_path
        ]
    )
    # action
    graph = operations.get_graph(
        packages=packages,
        filename=filename,
        file_format=file_format
    )

    # verification
    body = ''.join(graph.body)
    for key in packages.keys():
        assert key in body


def test_render_graph(tmp_path):
    # preconditions
    file_format = 'png'
    filename = str(tmp_path / 'graph')

    # action
    graph = operations.get_graph(filename=filename, file_format=file_format)
    graph_filepath = operations.render_graph(graph=graph)

    # verification
    assert graph_filepath.endswith(FILE_PATH_FORMAT.format(
        filename=filename, format=file_format
    ))
