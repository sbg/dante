import os
from setuptools import setup, find_packages
from dante.version import __version__

README_FILE = 'README.md'
DESCRIPTION = LONG_DESCRIPTION = 'Python dependency management utility'
if os.path.isfile(README_FILE):
    with open(README_FILE, 'r', encoding='utf-8') as readme_file:
        LONG_DESCRIPTION = readme_file.read()

setup(
    name='dante',
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    platforms=['Windows', 'POSIX', 'MacOs'],
    maintainer='Seven Bridges Genomics Inc.',
    maintainer_email='quicksilver.machine@gmail.com',
    url='https://github.com/sbg/dante',
    license='Apache Software License 2.0',
    install_requires=[],
    extras_require={},
    packages=find_packages(exclude=['tests*']),
    keywords=[
        'lock', 'dependency', 'pip',
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
