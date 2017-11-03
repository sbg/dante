from setuptools import setup, find_packages

version = '1.0'

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
    description='Python dependency management helper',
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dante = dante.__main__:main'
        ]
    }
)
