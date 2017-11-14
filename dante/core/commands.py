"""Python dependency management utility"""
import os
import io
import sys
import json
import tempfile
import contextlib

import pip
import pip.req
import pipdeptree

from dante.core.printer import Printer
from dante.core.utils import filter_tree


VERSION_ANY = 'Any'
printer = Printer()


def get_package_tree(ignore_list=None, include_only=None):
    """Returns dependency package tree
    :param ignore_list: list of dependencies to exclude from tree
    :param include_only: list of dependencies to include if
    :return: dictionary of top level packages with their dependencies
    """
    ignore_list = [i.lower() for i in ignore_list] if ignore_list else []
    include_only = [i.lower() for i in include_only] if include_only else []
    packages = [
        package for package in
        pip.get_installed_distributions()
        if package.key not in ignore_list
    ]

    # if include_only is set, remove other packages
    if include_only:
        packages = [
            package for package in packages
            if package.key in include_only
        ]

    dist_index = pipdeptree.build_dist_index(pkgs=packages)
    tree = pipdeptree.construct_tree(index=dist_index)
    return tree


def get_all_packages(tree):
    """Returns all packages
    :param tree: dictionary of dependencies
    :return: flat dictionary of all dependencies
    """
    return filter_tree(
        tree=tree,
        list_all=True
    )


def get_main_packages(tree):
    """Returns top level packages
    :param tree: dictionary of dependencies
    :return: flat dictionary of top level dependencies
    """
    return filter_tree(
        tree=tree,
        list_all=False
    )


def get_secondary_packages(tree):
    """Returns secondary dependencies
    :param tree: dictionary of dependencies
    :return: flat dictionary of secondary dependencies
    """
    dependencies = []
    for package in tree:
        for dependency in tree.get(package, VERSION_ANY):
            if (not next((d for d in dependencies
                          if d.key == dependency.key), None) and
                    (dependency.key in [key.key for key in tree.keys()])):
                dependencies.append(dependency)

    return sorted(dependencies, key=lambda d: d.name)


def get_installed_package_version(package):
    """Returns installed package version
    :param package: package for which the version is requested
    :return: version string
    """
    package_version = None
    if isinstance(package, pipdeptree.ReqPackage):
        return package.installed_version
    elif isinstance(package, pipdeptree.DistPackage):
        package_version = package.version
    return package_version or VERSION_ANY


def get_required_package_version(package):
    """Returns required version for a package
    :param package: package for which the required version is requested
    :return: version string
    """
    package_version = None
    if isinstance(package, pipdeptree.ReqPackage):
        package_version = package.version_spec
    return package_version or VERSION_ANY


def get_package_list(tree):
    """Returns list of package dicts with name and version
    :param tree: tree from which to create package list
    :return: list of dicts of packages
    """
    return [
        {
            'name': package.key,
            'version': get_installed_package_version(package)
        } for package in tree
    ]


def list_dependencies(args):
    """Prints a list of dependencies
    :param args: command line args
    :return: None
    """
    ignore_list = args.ignore
    dependencies_main = args.main
    dependencies_secondary = args.secondary

    tree = get_package_tree(ignore_list=ignore_list)
    filtered_tree = {}

    if not dependencies_main and not dependencies_secondary:
        filtered_tree = get_all_packages(tree)
    elif dependencies_main:
        filtered_tree = get_main_packages(tree)
    elif dependencies_secondary:
        filtered_tree = get_secondary_packages(tree)

    package_list = get_package_list(filtered_tree)
    printer.package_list(package_list)


def get_conflicting_dependencies(tree):
    """Returns sorted conflicting dependencies
    :param tree: dictionary of dependencies
    :return: sorted dict of conflicting dependencies
    """
    conflicting_dependencies = dict(pipdeptree.conflicting_deps(tree))

    if conflicting_dependencies:
        conflicting_data = []
        for package in sorted(conflicting_dependencies, key=lambda p: p.key):
            for dependency in sorted(
                    conflicting_dependencies[package], key=lambda d: d.key):
                conflicting_data.append([
                    printer.printable_package(dependency.key),
                    package.key,
                    get_required_package_version(dependency),
                    get_installed_package_version(dependency),
                ])
        return conflicting_data


def get_cyclic_dependencies(tree):
    """Returns sorted cyclic dependencies
    :param tree: dictionary of dependencies
    :return: sorted dict of cyclic dependencies
    """
    cyclic_dependencies = dict(pipdeptree.cyclic_deps(tree))

    if cyclic_dependencies:
        cyclic_data = []
        for package in sorted(
                cyclic_dependencies,
                key=lambda p: p.key):
            for dependency in sorted(
                    cyclic_dependencies[package],
                    key=lambda d: d.key):
                cyclic_data.append([
                    printer.printable_package(dependency.key),
                    package.key,
                    get_required_package_version(dependency),
                    get_installed_package_version(dependency)
                ])
        return cyclic_data


def check_conflicts(tree):
    """Prints conflicts in dependencies
    :param tree: dictionary of dependencies
    :return: None
    """
    # Argparse inserts namespace as an argument, this will check if
    # the tree was passed as a dict, and if not, create it
    if not isinstance(tree, dict):
        tree = get_package_tree()

    conflicting_data = get_conflicting_dependencies(tree=tree)
    cyclic_data = get_cyclic_dependencies(tree=tree)

    if conflicting_data:
        printer.warning('Conflicts detected')
        printer.table(
            tabular_data=conflicting_data,
            headers=[
                'Conflicting package', 'Required by', 'Required', 'Installed'
            ]
        )
    else:
        printer.success('No conflicts detected.')
    if cyclic_data:
        printer.warning('Cyclic dependencies detected')
        printer.table(
            tabular_data=cyclic_data,
            headers=[
                'Conflicting package', 'Required by', 'Required', 'Installed'
            ]
        )
    else:
        printer.success('No cyclic dependencies detected.')


def get_outdated_package_table_data(required_packages, secondary_packages,
                                    outdated_packages):
    data = []
    for package in outdated_packages:
        secondary_package = next(
            (
                item for item in secondary_packages
                if item.key == package['name'].lower()
            ),
            None
        )

        if secondary_package:
            specified_version = get_required_package_version(secondary_package)
        elif required_packages:
            specified_version = next((
                required_packages[key] for key in required_packages
                if key.lower() == package['name'].lower()
            ), VERSION_ANY)
        else:
            specified_version = VERSION_ANY
        data.append([
            printer.printable_package(package['name']),
            specified_version,
            package['version'],
            package['latest_version']
        ])
    return data


def check_for_upgrades(args):
    """Prints available upgrades to installed packages
    :param args: Command line args
    :return: None
    """
    ignore_list = args.ignore
    requirements_files = args.requirements or []

    required_packages = get_requirements_packages(
        requirements_files=requirements_files)

    output_json = io.StringIO()
    with contextlib.redirect_stdout(output_json):
        pip.main(['list', '--outdated', '--format=json'])
    outdated_packages = json.loads(output_json.getvalue())

    tree = get_package_tree(ignore_list=ignore_list)
    secondary_packages = get_secondary_packages(tree)

    data = get_outdated_package_table_data(
        required_packages=required_packages,
        secondary_packages=secondary_packages,
        outdated_packages=outdated_packages
    )

    if data:
        headers = ['Package', 'Required', 'Installed', 'Latest']
        printer.table(tabular_data=data, headers=headers)
    else:
        printer.success('All packages are at the latest version.')


def get_package_dependencies(key_tree, package, dependencies=None):
    """Get dependencies of specified package
    :param key_tree: dictionary of package names
    :param package: package for which to get dependencies
    :param dependencies: package dependencies
    :return: dictionary of dependencies
    """
    if dependencies is None:
        dependencies = {}

    unfiltered_children_list = key_tree.get(package.key, [])

    # Remove duplicates
    children_list = []
    children_keys = []
    for child in unfiltered_children_list:
        if child.key not in children_keys:
            children_list.append(child)
            children_keys.append(child.key)

    children = {c: {} for c in children_list}
    dependencies[package] = children

    for dependency in children:
        get_package_dependencies(key_tree, dependency, children)

    return dependencies


def print_dependencies(package_name, dependencies, indent=0):
    """Prints dependencies of entire environment or specified package
    :param package_name: name of package to print dependencies of
    :param dependencies: dependencies of the specified package
    :param indent: line indentation for printing to standard output
    :return:
    """
    for package in sorted(dependencies, key=lambda d: d.key):
        required_version = get_required_package_version(package)
        installed_version = get_installed_package_version(package)

        printer.dependency_package(
            package.key, required_version, installed_version, indent)

        print_dependencies(
            package_name,
            dependencies[package],
            indent=indent+2
        )


def get_dependencies(tree, package_name=None):
    """Return dependencies for entire tree or a specified package
    :param tree: dictionary of dependencies
    :param package_name: name of package to get dependencies for
    :return: dependencies
    """
    key_tree = dict((k.key, v) for k, v in tree.items())
    dependencies = []
    if package_name:
        package = next((item for item in tree
                        if item.key == package_name.lower()), None)
        if package:
            children = get_package_dependencies(key_tree, package)
            dependencies.append({
                'name': package_name,
                'children': children
            })
    else:
        for package in sorted(get_main_packages(tree), key=lambda p: p.key):
            children = get_package_dependencies(key_tree, package)
            dependencies.append({
                'name': package.key,
                'children': children
            })

    return dependencies


def print_dependency_tree(args):
    """Prints dependency tree
    :param args: Command line args
    :return: None
    """
    ignore_list = args.ignore
    package_name = args.package_name or None
    tree = get_package_tree(ignore_list=ignore_list)

    dependencies = get_dependencies(tree=tree, package_name=package_name)

    for dependency in dependencies:
        print_dependencies(dependency['name'], dependency['children'])


def parse_requirement_file(req_file, constraint=False):
    """Returns dependencies parsed from a requirement file
    :param req_file: file to parse
    :param constraint: if file a constraints file
    :return: dictionary of dependencies
    """
    if not os.path.exists(req_file):
        printer.warning('Requirement file "{}" not found'.format(req_file))
        sys.exit()

    with open(req_file, 'r') as requirements_file:
        with tempfile.NamedTemporaryFile('r+', delete=False) as temp_file:

            requirements_lines = requirements_file.readlines()

            # Ignore links
            data = [
                line for line in requirements_lines
                if not line.startswith('-r') and not line.startswith('-c')
            ]

            data = "".join(data)
            temp_file.write(data)
            processed_file_path = temp_file.name

    requirements = {
        item.name: item.req.specifier or None
        for item in pip.req.parse_requirements(
            filename=processed_file_path,
            session='session',
            constraint=constraint
        )
        if isinstance(item, pip.req.InstallRequirement)
    }

    # Delete temporary file
    with contextlib.suppress(FileNotFoundError):
        os.remove(processed_file_path)

    return requirements


def get_missing_requirements(required_packages, main_packages):
    """Returns possibly missing requirements
    :param required_packages: required packages
    :param main_packages: top level packages
    :return: list of possibly missing requirements
    """
    return [
        package for package in main_packages
        if package.key not in [key.lower() for key in required_packages.keys()]
    ]


def check_requirements_missing(required_packages, main_packages):
    """Print if all needed packages are present
    :param required_packages: required packages
    :param main_packages: top level packages
    :return: None
    """
    requirements_missing = get_missing_requirements(
        required_packages=required_packages,
        main_packages=main_packages
    )

    if requirements_missing:
        printer.warning('WARNING - Possibly missing requirements:')
        for requirement in requirements_missing:
            printer.package_versioned(
                package_name=requirement.key,
                package_version=requirement.version)
    else:
        printer.success('All packages in requirements.')


def get_invalid_requirements(tree, required_packages):
    """Returns requirements that are not pinned or are not installed
    :param tree: dictionary of dependencies
    :param required_packages: required packages
    :return: list of unpinned requirements
    """
    unpinned_requirements = []
    missing_requirements = []
    for required_package in required_packages:

        package = next((
            item for item in tree
            if item.key == required_package.lower()
        ), None)

        if package is None:
            missing_requirements.append({
                'package_name': required_package.lower()})
            continue

        if required_packages[required_package] is None:
            unpinned_requirements.append({
                'package_name': package.key,
                'package_version': get_installed_package_version(package)
            })
    return unpinned_requirements, missing_requirements


def check_requirements_not_pinned(tree, required_packages):
    """Print if all requirements are pinned and present
    :param required_packages: required packages
    :param tree: dictionary of dependencies
    :return: None
    """
    unpinned_requirements, missing_requirements = get_invalid_requirements(
        tree=tree,
        required_packages=required_packages
    )

    if missing_requirements:
        printer.warning('WARNING - Requirements not installed:')
        for requirement in missing_requirements:
            printer.package(package_name=requirement['package_name'])

    if unpinned_requirements:
        printer.warning('WARNING - Requirements not pinned:')
        for requirement in unpinned_requirements:
            printer.package_versioned(
                package_name=requirement['package_name'],
                package_version=requirement['package_version']
            )

    if not missing_requirements and not unpinned_requirements:
        printer.success('All set requirements installed and pinned.')


def get_unset_constraints(required_packages, constrained_packages,
                          secondary_packages):
    """Return constraints that are not set
    :param required_packages: required_packages
    :param constrained_packages: constrained packages
    :param secondary_packages: secondary packages
    :return: list of unset constraints
    """
    unset_constraints = []
    for package in secondary_packages:

        # check if package is already limited in requirements
        if package.key in required_packages:
            continue

        # check if package is already limited in parent
        specified_version = get_required_package_version(package)
        if specified_version != VERSION_ANY and '==' in specified_version:
            continue

        # check if package is already limited in project
        set_version = constrained_packages.get(package.key, None)
        if set_version is not None and '==' in str(set_version):
            continue

        # if constraint is not limited add the package to the list
        unset_constraints.append(package)

    return unset_constraints


def get_constraints_not_limited(constrained_packages):
    """Returns constraints that are not limited
    :param constrained_packages: constrained packages
    :return: list of constraints that are not limited
    """
    return [
        package for package in constrained_packages
        if constrained_packages[package] is None or
        '==' not in str(constrained_packages[package])
    ]


def check_constraints_set_and_limited(required_packages, constrained_packages,
                                      secondary_packages):
    """Check if all constraints are set
    :param required_packages: required packages
    :param constrained_packages: constrained packages
    :param secondary_packages: secondary packages in dependency tree
    :return: None
    """
    unset_constraints = get_unset_constraints(
        required_packages=required_packages,
        constrained_packages=constrained_packages,
        secondary_packages=secondary_packages
    )

    if unset_constraints:
        data = [[
            printer.printable_package(package.key),
            get_required_package_version(package),
            get_installed_package_version(package)
        ] for package in unset_constraints]
        headers = ['Package', 'Required', 'Installed']
        printer.warning('WARNING - Constraints not set:')
        printer.table(tabular_data=data, headers=headers)
    else:
        # check if all constraints are limited
        constraints_not_limited = get_constraints_not_limited(
            constrained_packages=constrained_packages
        )

        printer.success('All constraints set.')
        if constraints_not_limited:
            printer.warning('WARNING - Constraints not limited:')
            for package_name in constraints_not_limited:
                printer.package(package_name=package_name)
        else:
            printer.success('All set constraints limited.')


def get_requirements_packages(requirements_files):
    """Returns packages from requirements files
    :param requirements_files: requirements file list
    :return: requirements package list
    """
    req_packages = {}
    for req_file in requirements_files:
        req_packages.update(
            parse_requirement_file(req_file=req_file)
        )
    return {k.lower(): v for k, v in req_packages.items()}


def get_constraints_packages(constraints_files):
    """Returns packages from constraints files
    :param constraints_files: constraints file list
    :return: constraints package list
    """
    con_packages = {}
    for con_file in constraints_files:
        con_packages.update(
            parse_requirement_file(
                req_file=con_file, constraint=True))
    return {k.lower(): v for k, v in con_packages.items()}


def check(args):
    """Checks requirement and constraint files for possible errors
    :param args: Command line args
    :return: None
    """
    ignore_list = args.ignore
    requirements_files = args.requirements or []
    constraints_files = args.constraints or []

    tree = get_package_tree(ignore_list=ignore_list)
    main_packages = get_main_packages(tree=tree)
    secondary_packages = get_secondary_packages(tree=tree)

    required_packages = get_requirements_packages(
        requirements_files=requirements_files)

    constrained_packages = get_constraints_packages(
        constraints_files=constraints_files)

    # Checks
    check_conflicts(tree=tree)

    check_requirements_missing(
        required_packages=required_packages, main_packages=main_packages)

    check_requirements_not_pinned(
        tree=tree, required_packages=required_packages)

    check_constraints_set_and_limited(
        required_packages=required_packages,
        constrained_packages=constrained_packages,
        secondary_packages=secondary_packages)
