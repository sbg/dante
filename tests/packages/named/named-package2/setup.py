from setuptools import setup, find_packages

install_requires = []

setup(
    name='named-package2',
    version='0.0.1+local-version',
    install_requires=install_requires,
    packages=find_packages(),
)
