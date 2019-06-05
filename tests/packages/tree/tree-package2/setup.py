from setuptools import setup, find_packages

install_requires = [
    'tree-package3',
    'tree-package7'
]

setup(
    name='tree-package2',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
