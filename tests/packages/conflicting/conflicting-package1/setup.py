from setuptools import setup, find_packages

install_requires = [
    'conflicting-dep>1.0.0'
]

setup(
    name='conflicting-package1',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
