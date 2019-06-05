from setuptools import setup, find_packages

install_requires = ['named-package2>2.0.0']

setup(
    name='named-package1',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
