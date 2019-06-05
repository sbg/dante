import os
import pytest
from dante.commands.utils import validate_files

pytestmark = pytest.mark.utils


@pytest.mark.parametrize(
    'files', [['requirements-dev.txt'], ['requirements-dev.lock']],
)
def test_validate_files(files):
    if all(os.path.exists(file_) for file_ in files):
        assert validate_files(files=files, exit_on_failure=False)
    else:
        with pytest.raises(SystemExit):
            assert validate_files(files=files)
        assert not validate_files(files=files, exit_on_failure=False)
