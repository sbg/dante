import io
import os
from setuptools import setup, find_packages


version = '1.0.0'

VERSION_FILE = 'VERSION'
if os.path.isfile(VERSION_FILE):
    with io.open(VERSION_FILE, 'r', encoding='utf-8') as f:
        version = f.read()


description = long_description = 'Python dependency management utility'
README_FILE = 'README.rst'
if os.path.isfile(README_FILE):
    with io.open(README_FILE, 'r', encoding='utf-8') as f:
        long_description = f.read()


changelog = ''
CHANGELOG_FILE = 'HISTORY.rst'
if os.path.isfile(CHANGELOG_FILE):
    with io.open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
        changelog = f.read()


long_description = '{}\n\n{}'.format(long_description, changelog)

install_requires = [
    'pip>=9.0.1, <10',
    'pipdeptree>=0.10.1, <0.11',
]

extras_require = {
    'color': ['colorama>=0.3.9, <0.4'],
}

setup(
    name='dante',
    version=version,
    description=description,
    long_description=long_description,
    platforms=['Windows', 'POSIX', 'MacOs'],
    maintainer='Seven Bridges Genomics Inc.',
    maintainer_email='dejan.knezevic@sbgenomics.com',
    url='https://github.com/sbg/dante',
    license='Apache Software License 2.0',
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(exclude=['*.tests']),
    keywords=[
        'constraint', 'dependency', 'pip',
        'requirement', 'sbg', 'sevenbridges'
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'dante = dante.__main__:main'
        ]
    }
)
