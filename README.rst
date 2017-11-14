Dante
=====

|PypI| |License|

Dante is a utility library for managing python dependencies.

Why use Dante?
==============

When a python application is setup, it’s common practice to include a
requirements file. The requirements file contains all the necessary
packages the application needs to function properly. The problem arises
when those packages’ dependencies get new versions. These updates can
break existing applications. Using this library, a project maintainer
can check which packages need to be constrained to a specific version or
a range so that their application will still function as intended.

Dante should be used as a warning tool for now, since there is always a
possibility of false positives.

Installation
============

Dante can be installed using pip.

::

    pip install dante

Dante also supports colored output, to use it install Dante with:

::

    pip install dante[color]

What to do?
===========

Requirements should be split into two files. The production requirements
or **requirements.txt** and development requirements or
**requirements-dev**.

The **requirements-dev.txt** should start with:

::

    -r requirements.txt

so it will install production requirements as well when it’s called.

When you’ve separated the requirements files, you can call dante’s check
function and add them as parameters. Dante will list: \* Conflicts
cyclical dependencies (solved by installing the required versions) \*
The possible missing requirements (some of them are false positives,
Dante’s own libraries can’t be excluded because some of them might be
used by your project) \* If some requirements are not pinned to a
specific version \* Constraints that are not set (packages required by
packages in requirements that do not have a set version inside those
packages). \* Constraints that are restricted with a minimal allowed
version only (not set as equal to a specific version)

Constraints serve to limit the requirements of the specified
requirements. They should also be split into two files (constraints.txt
and constraints-dev.txt). Dependencies for a specific package can be
displayed with the dependencies function using the package name as an
argument.

The **constraints-dev.txt** should start with:

::

    -c constraints.txt

so it will install production constraints as well when it’s called.

When all this is done you should be left with a matching constraints
file for each requirements file: \* **requirements.txt** \*
**constraints.txt** \* **requirements-dev.txt** \*
**constraints-dev.txt**

Finally when:

::

    pip install -r requirements.txt -c constraints.txt

is called, production requirements and constraints will be installed.
All packages that are installed as dependencies of packages in the
requirements file will be constrained by versions set in the constraints
file.

To install development requirements:

::

    pip install -r requirements-dev.txt -c constraints-dev.txt

This will install production requirements and constraints as well,
because they were previously linked in their respective dev requirement
and constraint files.

Functionality
=============

List
----

List current environment dependencies (top level and secondary)

::

    dante list [-m] [-s]
    dante list [--main] [--secondary]

Example:

::

    $ dante list
        
    colorama==0.3.7
    coverage==4.3.4
    django-encrypted-cookie-session==3.2.0
    django-user-agents==0.3.0
    gevent==1.2.1
    ...

Conflicts
---------

Find conflicts and cyclic dependencies

::

    dante conflicts

Example:

::

    $ dante conflicts
        
    Conflicts detected
    Conflicting package  Required by        Required    Installed
    -------------------  -----------------  ----------  -----------
    requests             sbg-common         ==2.7.0     2.13.0
    six                  sbg-common         ==1.9.0     1.10.0
    cryptography         sbg-openid-client  ==1.5.2     1.8.1
    No cyclic dependencies detected.

Dependency tree
---------------

Show a dependency tree for the entire environment or a specific package

::

    dante dependency [-p PACKAGENAME]
    dante dependency [--package_name PACKAGENAME]

Example:

::

    $ dante dependencies -p twilio
        
    twilio [Installed: 5.7.0]
      httplib2 [Installed: 0.10.3 | Required: >=0.7]
      pysocks [Installed: 1.6.7 | Required: Any]
      pytz [Installed: 2016.10 | Required: Any]
      six [Installed: 1.10.0 | Required: Any]

Upgrades
--------

Check for and display available upgrades for installed packages.

::

    dante upgrades

Examples:

::

    $ dante upgrades
        
    Package           Required    Installed    Latest
    ----------------  ----------  -----------  --------
    alembic           ==0.6.7     0.6.7        0.9.1
    cryptography      ==1.5.2     1.7.2        1.8.1
    futures           ==2.1.6     2.1.6        3.0.5
    Inject            ==3.3.0     3.3.0        3.3.1
    ipython-genutils  Any         0.1.0        0.2.0
    ...

Using an optional -r (–requirements) option, it will display the top
level package required version as well.

::

    $ dante upgrades -r requirements.txt
        
    Package           Required    Installed    Latest
    ----------------  ----------  -----------  --------
    ...
    ipython-genutils  ==0.1.0     0.1.0        0.2.0
    ...

Check files
-----------

Check requirement and constraint files for possible errors (multiple
files can be included for both requirements and constraints). This
command checks for missing and unpinned requirements and suggested
constraints for secondary dependencies that are not constrained by
packages that use them.

::

    dante check [-r [REQUIREMENTS [REQUIREMENTS ...]]] [-c [CONSTRAINTS [CONSTRAINTS ...]]]
    dante check [--requirements [REQUIREMENTS [REQUIREMENTS ...]]] [--constraints [CONSTRAINTS [CONSTRAINTS ...]]]

Example:

::

    $ dante check -r requirements.txt -r requirements-dev.txt -c constraints.txt
        
    Conflicts detected
    Conflicting        Dependency    Required    Installed
    -----------------  ------------  ----------  -----------
    sbg-common         requests      ==2.7.0     2.13.0
    sbg-common         six           ==1.9.0     1.10.0
    sbg-openid-client  cryptography  ==1.5.2     1.8.1
    No cyclic dependencies detected.
    WARNING - Possibly missing requirements:
    coverage==4.3.4
    django-encrypted-cookie-session==3.2.0
    django-user-agents==0.3.0
    gevent==1.2.1
    gnureadline==6.3.3
    gunicorn==19.7.0
    ...
    All requirements pinned.
    WARNING - Constraints not set:
    Package            Required     Installed
    -----------------  -----------  -----------
    appdirs            >=1.4.0      1.4.3
    appnope            Any          0.1.0
    babel              !=2.0,>=1.3  2.3.4
    certifi            Any          2017.1.23
    cffi               >=1.4.1      1.9.1
    decorator          Any          4.0.11
    Django             >=1.4        1.10.6
    ...

Ignoring packages
-----------------

Packages can be excluded from checks by using the -i (–ignore) optional
argument.

::

    dante -i FIRST_PACKAGE_NAME -i SECOND_PACKAGE_NAME ...

Example

::

    $ dante list
        
    colorama==0.3.7
    pip==9.0.1
    pipdeptree==0.9.0
    setuptools==28.8.0
    tabulate==0.7.7

::

    $ dante -i pip -i setuptools list
        
    colorama==0.3.7
    pipdeptree==0.9.0
    tabulate==0.7.7

Tests
=====

To run tests, checkout the repository and install requirements with:

::

    pip install -r requirements-dev.txt -c constraints.txt

and run tox or pytest.

Dante roadmap
=============

-  Generate requirements files
-  Generate constraints files based on specified requirements files
-  In upgrades, list only top level or secondary requirements depending
   on input args
-  Code analysis to find used libraries


.. |PyPi| image:: https://badge.fury.io/py/dante.svg
    :target: https://badge.fury.io/py/dante

.. |License| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :target: https://github.com/sbg/dante/blob/master/LICENSE
