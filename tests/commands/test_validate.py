from pathlib import Path
from argparse import Namespace

import pytest

from dante import messages
from dante.config import Config
from dante.commands import validate
from dante.core.models import RequirementCollection, Requirement, \
    RequiredVersion, PackageCollection, Package, InstalledVersion

pytestmark = pytest.mark.validate

FILE_DIR = Path(Config.PARENT_DIR) / 'tests' / 'files'

VALID_REQUIREMENTS_FILE = str(FILE_DIR / 'requirements.txt')
VALID_LOCK_FILE = str(FILE_DIR / 'requirements.lock')
INVALID_REQUIREMENTS_FILE = str(FILE_DIR / 'requirements-invalid.txt')
INVALID_LOCK_FILE = str(FILE_DIR / 'requirements-invalid.lock')


# noinspection PyBroadException
# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('args', [
    [False, True, None, [], []],
    [False, True, None, [VALID_REQUIREMENTS_FILE], [VALID_LOCK_FILE]],
    [False, True, None, [INVALID_REQUIREMENTS_FILE], [INVALID_LOCK_FILE]],
])
def test_validate(mocker, args):
    # preconditions
    _all = args[0]
    strict = args[1]
    ignore = args[2]
    requirements = args[3]
    lock = args[4]

    mocker.patch('dante.commands.validate.check_unlocked_requirements', True)
    mocker.patch('dante.commands.validate.check_unset_locks', True)
    mocker.patch(
        'dante.commands.validate.check_package_version_mismatch', True
    )
    mocker.patch(
        'dante.commands.validate.check_requirement_version_mismatch', True
    )
    mocker.patch('dante.commands.validate.check_unnecessary_packages', True)
    mocker.patch('dante.commands.validate.check_unnecessary_locks', True)
    mocker.patch('sys.exit')

    args = Namespace(
        all=_all,
        strict=strict,
        ignore=ignore,
        requirements=requirements,
        lock=lock,
    )

    # action
    try:
        success = validate.validate_command(args, exit_on_failure=False)
    except Exception:
        success = False

    # verification
    assert (
        not success
        if requirements == [VALID_REQUIREMENTS_FILE] and
        lock == [VALID_LOCK_FILE]
        else not success
    )
    if success:
        assert validate.check_unlocked_requirements.called
        assert validate.check_unset_locks.called
        assert validate.check_package_version_mismatch.called
        assert validate.check_requirement_version_mismatch.called
        assert validate.check_unnecessary_packages.called
        assert validate.check_unnecessary_locks.called


@pytest.mark.parametrize(
    'unlocked', [[], ['package1', 'package2', 'package3']]
)
def test_check_unlocked_requirements(capsys, unlocked):
    # preconditions
    requirements = RequirementCollection(
        Requirement.from_requirement_string(key)
        for key in unlocked
    )

    # action
    success = validate.check_unlocked_requirements(requirements=requirements)

    # verification
    captured = capsys.readouterr()
    assert success is False if unlocked else success
    if success:
        assert messages.UNLOCKED_REQUIREMENTS_OK in captured.out
    else:
        assert messages.UNLOCKED_REQUIREMENTS_FOUND in captured.out
        for requirement in unlocked:
            assert requirement in captured.out


@pytest.mark.parametrize(
    'test_data', [
        [['package1', 'package2'], ['package1', 'package2']],
        [['package1', 'package2'], ['package1']]
    ]
)
def test_check_unset_locks(capsys, test_data):
    # preconditions
    requirements_list, locked_list = test_data

    requirements = RequirementCollection([
        Requirement.from_requirement_string(key)
        for key in requirements_list
    ])
    locked = RequirementCollection([
        Requirement.from_requirement_string(key)
        for key in locked_list
    ])

    # action
    success = validate.check_unset_locks(
        requirements=requirements, locked=locked
    )

    # verification
    captured = capsys.readouterr()
    assert success is False if requirements_list != locked_list else success
    if success:
        assert messages.UNSET_LOCKS_OK in captured.out
    else:
        assert messages.UNSET_LOCKS_FOUND in captured.out
        for requirement in requirements_list:
            if requirement not in locked_list:
                assert requirement in captured.out


@pytest.mark.parametrize(
    'test_data', [
        ([('package1', '==1.0.0')], [('package1', '==1.0.0')]),
        ([('package1', '==1.0.0')], [('package1', '==2.0.0')]),
    ]
)
def test_check_version_mismatch(capsys, test_data):
    # preconditions
    package_list, locked_list = test_data

    packages = PackageCollection([
        Package(
            key=key, name=key, obj=None, version=InstalledVersion(version)
        )
        for key, version in package_list
    ])
    locked = RequirementCollection([
        Requirement(
            key=key, name=key, obj=None, version=RequiredVersion(version)
        )
        for key, version in locked_list
    ])

    # action
    success = validate.check_package_version_mismatch(
        packages=packages, locked=locked
    )

    # verification
    captured = capsys.readouterr()
    assert success is False if package_list != locked_list else success
    if success:
        assert messages.PACKAGE_VERSION_MISMATCH_OK in captured.out
    else:
        assert messages.PACKAGE_VERSION_MISMATCH_FOUND in captured.out
        for package in package_list:
            for lock in locked_list:
                if package[0] == lock[0] and package[1] != lock[1]:
                    assert package[0] in captured.out


@pytest.mark.parametrize(
    'test_data', [
        [
            ['package1', 'package2'],
            ['package1', 'package2'],
            ['package1', 'package2']
        ],
        [
            ['package1', 'package2', 'package3'],
            ['package1', 'package2'],
            ['package1', 'package2']
        ],
    ]
)
def test_check_unnecessary_requirements(capsys, test_data):
    # preconditions
    package_list, requirements_list, locked_list = test_data

    packages = PackageCollection([
        Package(key=key, name=key, obj=None, version=None)
        for key in package_list
    ])
    requirements = RequirementCollection([
        Requirement.from_requirement_string(key)
        for key in requirements_list
    ])
    locked = RequirementCollection([
        Requirement.from_requirement_string(key)
        for key in locked_list
    ])

    # action
    success = validate.check_unnecessary_packages(
        packages=packages,
        requirements=requirements,
        locked=locked,
    )

    # verification
    captured = capsys.readouterr()
    required = set(requirements_list + locked_list)
    assert success is False if len(package_list) > len(required) else success
    if success:
        assert messages.PACKAGE_NOT_REQUIRED_OK in captured.out
    else:
        assert messages.PACKAGE_NOT_REQUIRED_FOUND in captured.out
        for package in package_list:
            if package not in required:
                assert package in captured.out
