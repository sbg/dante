from setuptools import setup, find_packages

install_requires = [
    'mismatch-package2'
]

setup(
    name='mismatch-package1',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
