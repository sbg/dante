# Dante

[![PyPI version](https://badge.fury.io/py/dante.svg)](https://badge.fury.io/py/dante)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/sbg/dante/blob/master/LICENSE)
[![Downloads](https://pepy.tech/badge/dante)](https://pepy.tech/project/dante)

Dante is a dependency management and validation tool for python projects.

## Purpose

Dante was written to simplify dependency management in python by using lock
files to keep consistent environments for both development and deployment. It
does not manage installation of environments and packages but focuses on
validation.

Dante will help you keep track of dependencies with just a few simple commands.
Unlike some other tools, it is not as opinionated, and is highly configurable.
While it uses standard requirements files, a parser can be written for any
other file type.

## Recommended convention

Files to use:

- **requirements.txt** for used project packages
- **requirements.lock** for deployment packages
- **requirements-dev.txt** for used development packages
- **requirements-dev.lock** for all test environment packages

Lock files enforce exact versions for all packages.
When deploying and preparing the environment only install from lock files.

## Installation

Dante can be found on PyPI and can simply be installed with:

    pip install dante

Since version 2, it no longer installs it's own dependencies, but instead
vendors them to avoid possible false positives.

## Configuration

Dante has a default configuration which can be overridden using a standard
`setup.cfg` file. Configurable properties are as follows:


|Property|Description|
|---|---|
|**checks**|Checks to run when calling the `check` command. Defaults are `conflicts`, `cyclic`, `missing`, `validate`.|
|**ignore_list**|List of package keys to ignore. Defaults are `dante`, `pip`, `setuptools`, and `wheel`.|
|**allow_named_versions**|Whether to allow custom named versions (invalid by default) for packages. Default is `false`.|
|**named_version_patterns**|List of regex patterns that will determine named versions. Default is empty.|
|**requirements_files**|List of requirement files used in the project. Defaults to `requirements.txt`.|
|**lock_files**|List of lock files used in the project. Defaults to `requirements.lock`.|
|**lock_file_path**|Path of the lock file that will be generated with `dante lock --save`.|
|**parser**|Parser to use to read/write requirements/lock files. Currently only the default is supported.|
|**any_version**|Undefined version name. Default is `Any`.|
|**graph_name**|Name of the graph that will be created. Defaults to `dante-graph`.|
|**graph_filename**|Filename of the graph that will be created. Defaults to `dante-graph.pdf` in the working directory.|
|**graph_format**|Format of the graph that will be created. Defaults to `pdf`. Supports all graphviz formats.|
|**graph_engine**|Engine of the graph that will be created. Defaults to `dot`. Supports all graphviz engines.|
|**graph_attributes**|Custom graph attributes. Supports all graphviz attributes.|
|**graph_strict**|Whether the graphviz graph follows strict rules. Defaults to `True`.|
|**graph_node_attributes**|Custom graph node attributes. Defaults to setting `shape` to `box3d`. Supports all graphviz node attributes.|
|**graph_edge_attributes**|Custom graph edge attributes. Defaults to setting `fontsize` to `10`. Supports all graphviz edge attributes.|


## Functionality

### Commands

|Command|Description|
|---|---|
|**list**|List all dependencies
|**tree**|Show dependency tree
|**config**|Print configuration
|**validate**|Validate requirements and lock files
|**conflicts**|Check for conflicts in required dependencies
|**cyclic**|Check for cyclic dependencies
|**missing**|Show missing dependencies
|**check**|Run a complete list of checks
|**lock**|Display or generate lock file from environment and/or requirements file(s)
|**graph**|Export a dependency graph using graphviz


Note: Almost all command flags have shorthands that are equivalent to the first
letter of their name. They can be displayed with the help command.

### Version

The version flag will get dante to display it's installed version end exit:

    dante --version

### Dante command

Dante has several flags on the CLI's top level:

- `--all` - Shows all packages (Does not use the ignore list)
- `--ignore IGNORE` - Ignore specified package. Can be used multiple times.

### Dependency list

Lists all packages relevant to the project:

    dante list [--requirements REQUIREMENTS]

Flag|Shorthand|Description
|---|---|---|
|**--requirements**|**-r**|Requirements file to use (will ignore `setup.cfg`)|

Unlike `pip freeze` unless it's used with the `--all` flag dante will only
display packages that are required for the project. This is determined by using
installed packages and requirements files.

### Dependency tree

Displays a dependency tree for a single package or the entire environment:

    dante tree [--package PACKAGE] [--requirements REQUIREMENTS]

Flag|Shorthand|Description
|---|---|---|
|**--package**|**-p**|Package to display the tree for|
|**--requirements**|**-r**|Requirements file to use (will ignore `setup.cfg`)|

### Configuration

Displays the current configuration in JSON format:

    dante config

Example result:
~~~json
{
    "dante": {
        "any_version": "Any",
        "checks": [
            "conflicts",
            "cyclic",
            "missing",
            "validate"
        ],
        "ignore_list": [
            "dante",
            "pip",
            "setuptools",
            "wheel"
        ],
        "allow_named_versions": true,
        "named_version_patterns": [
            "0.*version"
        ],
        "lock_file_path": "requirements-dev.lock",
        "requirements_files": [
            "requirements-dev.lock"
        ],
        "lock_files": [
            "requirements-dev.lock"
        ],
        "graph_name": "dante-graph",
        "graph_filename": null,
        "graph_format": "pdf",
        "graph_engine": "dot",
        "graph_strict": true
    },
    "graph_attributes": {},
    "graph_node_attributes": {
        "shape": "box3d"
    },
    "graph_edge_attributes": {
        "fontsize": "10"
    }
}
~~~

### Validation

Performs various checks on requirements and lock files:

    dante validate [-requirments REQUIREMENTS] [--lock LOCK] [--strict]

Flag|Shorthand|Description
|---|---|---|
|**--requirements**|**-r**|Requirements file to use (will ignore `setup.cfg`)|
|**--lock**|**-l**|Lock file to use (will ignore `setup.cfg`)|
|**--strict**|**-r**|Run strict checks|

The checks performed are as follows:
- Check if all set requirements are set to a version or a version range
- Check if all locked requirements are set to an exact version
- Check if all installed package versions match the locked requirement versions
- Check if all required versions match the locked requirement versions

Successful run will print out:

    All set requirements locked
    No unset locks found
    All package versions matching
    All requirement versions matching

Running validation with the `--strict` flag will add some additional checks:

- Check if there are installed packages that are not required by anything
- Check if there are locked requirements that are not required by anything

It is recommended to use the strict check whenever it's possible.

Successful run will print out:

    No non-required packages found
    No non-required locks found

### Conflicting dependencies

Detects conflicts between installed packages:

    dante conflicts

Conflicts can occur when multiple packages require the same package with
incompatible versions (e.g. one requires <1.0.0 and the other >2.0.0).
Successful run will print out:

    No conflicts found

### Cyclic dependencies

Detects cyclical dependencies in installed packages:

    dante cyclic

This can occur when there is a cyclical path in package dependencies (e.g.
`package1` requires `package2` which requires `package3`, which in turn
requires `package1`). Successful run will print out:

    No cyclic dependencies found

### Missing dependencies

Detects if there are required packages that are not installed in the environment:

    dante missing [--requirements REQUIREMENTS]

Flag|Shorthand|Description
|---|---|---|
|**--requirements**|-r|Requirements file to use (will ignore `setup.cfg`)|


Successful run will print out:

    No missing dependencies found

## Check

Runs all defined checks at once:

    dante check [--requirements REQUIREMENTS] [--lock LOCK] [--strict]

Flag|Shorthand|Description
|---|---|---|
|**--requirements**|**-r**|Requirements file to use (will ignore `setup.cfg`)|
|**--lock**|**-l**|Lock file to use (will ignore `setup.cfg`)|
|**--strict**|**-r**|Run strict checks|


Successful run with all checks will print out:

    All set requirements locked
    No unset locks found
    All package versions matching
    All requirement versions matching
    No non-required packages found
    No non-required locks found
    No conflicts found
    No cyclic dependencies found
    No missing dependencies found

## Lock

Displays or saves locked requirements for the current project:

    dante lock [--requirements REQUIREMENTS] [--save] [--file FILE]

Flag|Shorthand|Description
|---|---|---|
|**--requirements**|**-r**|Requirements file to use (will ignore `setup.cfg`)|
|**--save**|**-s**|Save to file|
|**--file**|**-f**|Filename to save to (will override `setup.cfg`)|

Locked requirements are determined by walking through all installed packages
and provided requirements recursively retrieving their dependencies.

Only the requirements that are needed for the project will be returned.

## Graph

Returns a dependency graph description or renders it to a file:

    dante graph [--strict] [--render] [--view] [--name NAME] [--filename FILENAME]
                       [--format FORMAT] [--engine ENGINE]
                       [--graph_attr GRAPH_ATTR] [--node_attr NODE_ATTR]
                       [--edge_attr EDGE_ATTR]

Flag|Shorthand|Description
|---|---|---|
|**--render**|**-r**|Render graph to file|
|**--view**|**-v**|Display graph after rendering|
|**--strict**|**-s**|Use strict graph rules|
|**--name**| |Graph name|
|**--filename**| |Filename to save graph to|
|**--format**| |Graph file format|
|**--engine**| |Graph engine|
|**--graph_attr**| |Graph attributes|
|**--node_attr**| |Graph node attributes|
|**--edge_attr**| |Graph edge attributes|

## Api

Dante exposes it's operations through the api module, so they can be imported
and used in your libraries/applications:

Example for retrieving installed packages:
~~~python
from dante.api import dependency_list
installed_packages = dependency_list()
~~~

## CI

Dante can be used as a CI checking tool, with proper configuration in
`setup.cfg` configured, all it takes to run a check on any CI is:

    dante check

Dante includes error codes when run through the CLI, so it will fail the build
if any problems are detected.

Note: It's recommended to use the strict check whenever it's possible, since
unnecessary requirements can still cause problems in the environments
(e.g. can overwrite other package's files...):

    dante check --strict

## Tests

To run tests simply install all dependencies from `requirements-dev.lock` and run:
~~~
pytest --cov-config setup.cfg
~~~


## Roadmap:

- Full documentation
