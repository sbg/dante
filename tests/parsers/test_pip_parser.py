from pathlib import Path

import pytest

from dante.config import Config
from dante.parsers.pip import PipParser
from dante.core.models import (
    Requirement,
    RequiredVersion,
    RequirementCollection,
)

pytestmark = pytest.mark.pip_parser

FILE_DIR = Path(Config.PARENT_DIR) / 'tests' / 'files'


def test_parse_requirements_file():
    # preconditions
    num_packages = 3
    filepath = FILE_DIR / 'requirements.txt'
    version = RequiredVersion('1.0.0')

    expected_requirements = RequirementCollection([
        Requirement(
            key='package{}'.format(i),
            name='p{}'.format(i),
            obj=None,
            version=version
        ) for i in range(1, num_packages + 1)
    ])

    # action
    requirements = PipParser.parse_requirements_file(filepath=filepath)

    # verification
    assert expected_requirements == requirements


def test_save_lock_file(mocker, tmp_path):
    # preconditions
    num_packages = 6
    version = '1.0.0'
    filepath = tmp_path / 'requirements.lock'
    expected_filepath = FILE_DIR / 'requirements.lock'

    expected_data = expected_filepath.read_text()

    requirements = RequirementCollection([
        Requirement.from_requirement_string(
            requirement_string='package{}=={}'.format(i, version),
        ) for i in range(1, num_packages + 1)
    ])

    # action
    mocker.patch('dante.core.models.Requirement.version_id', version)
    PipParser.save_lock_file(
        requirements=requirements,
        filepath=filepath
    )

    # verification
    data = filepath.read_text()
    assert expected_data == data
