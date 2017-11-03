"""Test configuration module"""
import pytest

from dante.tests.verificators import Verificator
from dante.tests.preconditions import Precondition


@pytest.fixture
def given():
    return Precondition()


@pytest.fixture
def verify():
    return Verificator()
