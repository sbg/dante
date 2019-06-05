from setuptools import setup, find_packages

install_requires = [
    'cyclic-package1'
]

setup(
    name='cyclic-package3',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
