from setuptools import setup, find_packages

install_requires = [
    'tree-package3',
    'tree-package4',
]

setup(
    name='tree-package1',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
