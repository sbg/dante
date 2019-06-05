from setuptools import setup, find_packages

install_requires = [
    'locked-package2'
]

setup(
    name='locked-package1',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
