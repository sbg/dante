from setuptools import setup, find_packages

install_requires = [
    'cyclic-package2'
]

setup(
    name='cyclic-package1',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
