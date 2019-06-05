from setuptools import setup, find_packages

install_requires = [
    'locked-package3'
]

setup(
    name='locked-package2',
    version='1.0.0',
    install_requires=install_requires,
    packages=find_packages(),
)
