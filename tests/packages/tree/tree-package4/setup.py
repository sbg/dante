from setuptools import setup, find_packages

install_requires = [
    'tree-package5',
    'tree-package6',
]

setup(
    name='tree-package4',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
