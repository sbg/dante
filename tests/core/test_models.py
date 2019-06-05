import pytest

from dante.vendor.packaging.version import Version
from dante.vendor.packaging.specifiers import SpecifierSet

from dante.core.models import InstalledVersion, RequiredVersion

pytestmark = pytest.mark.models


def test_version_model():
    version_number = '1.2.3'
    min_version_number = '0.1.1'
    max_version_number = '1.2.3'

    v1 = SpecifierSet('=={}'.format(version_number))
    v2 = Version(version_number)
    v3 = '=={}'.format(version_number)
    v4 = version_number
    v5 = '==0.0.1+local-version'
    v6 = '>={},<{}'.format(min_version_number, max_version_number)
    v7 = SpecifierSet(
        '>={},<{}'.format(min_version_number, max_version_number)
    )

    installed1 = InstalledVersion(obj=str(v1))
    installed2 = InstalledVersion(obj=str(v2))
    installed3 = InstalledVersion(obj=str(v3))
    installed4 = InstalledVersion(obj=str(v4))
    installed5 = InstalledVersion(obj=str(v5))

    required1 = RequiredVersion(obj=str(v1))
    required2 = RequiredVersion(obj=str(v2))
    required3 = RequiredVersion(obj=str(v3))
    required4 = RequiredVersion(obj=str(v4))
    required5 = RequiredVersion(obj=str(v5))
    required6 = RequiredVersion(obj=str(v6))
    required7 = RequiredVersion(obj=str(v7))

    assert installed1.id == '1.2.3'
    assert installed2.id == '1.2.3'
    assert installed3.id == '1.2.3'
    assert installed4.id == '1.2.3'
    assert installed5.id == '0.0.1+local-version'

    assert installed1.specifier == '==1.2.3'
    assert installed2.specifier == '==1.2.3'
    assert installed3.specifier == '==1.2.3'
    assert installed4.specifier == '==1.2.3'
    assert installed5.specifier == '==0.0.1+local-version'

    assert required1.id == '==1.2.3'
    assert required2.id == '==1.2.3'
    assert required3.id == '==1.2.3'
    assert required4.id == '==1.2.3'
    assert required5.id == '0.0.1+local-version'
    assert required6.id == '>=0.1.1,<1.2.3'
    assert required7.id == '<1.2.3,>=0.1.1'

    assert required1.specifier == '==1.2.3'
    assert required2.specifier == '==1.2.3'
    assert required3.specifier == '==1.2.3'
    assert required4.specifier == '==1.2.3'
    assert required5.specifier == '0.0.1+local-version'
    assert required6.specifier == '>=0.1.1,<1.2.3'
    assert required7.specifier == '<1.2.3,>=0.1.1'

    assert installed1 == required1
    assert installed2 == required2
    assert installed3 == required3
    assert installed4 == required4
    assert installed5 == required5
