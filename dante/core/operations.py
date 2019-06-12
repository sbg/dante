from collections import OrderedDict

from dante.config import Config
from dante.core.models import (
    Requirement,
    PackageCollection,
    RequirementCollection,
)
from dante.core.graph import create_dependency_graph, render_dependency_graph


def dependency_list(list_all=False, ignore_list=None, requirements=None):
    """Returns all installed packages
    :param list_all: Enable/disable filtering packages with ignore_list
    :param ignore_list: List of package keys to ignore
    :param requirements: Collection of requirements
    :return: List of packages
    """
    installed_packages = PackageCollection.installed_packages(
        list_all=list_all,
        ignore_list=ignore_list
    )

    # If requirements files are specified filter out other packages
    if requirements:
        return PackageCollection([
            package for package in installed_packages
            if package.key in requirements.flatten().keys()
        ])

    # Otherwise just return all installed packages
    return installed_packages


def required_by(requirement, packages=None):
    """Returns all packages that require the provided requirement
    :param requirement: Requirement object
    :param packages: Collection of packages
    :return: Packages that require the requirement
    """
    packages = packages or PackageCollection()

    return [
        (package, package_requirement.specified_version)
        for package in packages
        for package_requirement in package.requirements
        if requirement.key == package_requirement.key
    ]


def conflicting_dependencies(packages=None, allow_named_versions=False,
                             named_version_patterns=None):
    """Returns all dependencies with conflicting versions
    :param packages: Collection of packages
    :param allow_named_versions: Allow named versions to circumvent conflicts
    :param named_version_patterns: List of patterns that determine named
        versions
    :return: List of requirements and packages that require them with
        the required version
    """
    packages = packages or PackageCollection()

    return [
        (requirement, required_by(requirement, packages))
        for requirement in packages.requirements
        if requirement.conflicting(
            allow_named_versions=allow_named_versions,
            named_version_patterns=named_version_patterns
        )
    ]


def cyclic_dependencies(packages=None):
    """Returns all cyclic dependencies
    :param packages: Collection of packages
    :return: List of found cyclic paths
    """
    packages = packages or PackageCollection()
    return packages.cyclic_dependencies


def missing_requirements(packages=None, requirements=None):
    """Returns all requirements that are not installed
    :param packages: Collection of packages
    :param requirements: Collection of requirements
    :return: All requirements that are not found in packages
    """
    packages = packages or PackageCollection()
    requirements = requirements or RequirementCollection()

    return [
        (requirement, required_by(requirement, packages))
        for requirement in requirements.flatten()
        if requirement.key not in packages.keys()
    ]


def unset_requirements(packages=None, requirements=None):
    """Returns all package requirements that are not in provided requirements
    :param packages: Collection of packages
    :param requirements: Collection of requirements
    :return: All requirements that are not in requirements
    """
    packages = packages or PackageCollection()
    requirements = requirements or RequirementCollection()

    return RequirementCollection((
        package for package in packages.independent_packages
        if package.key not in requirements.keys()
    ))


def unlocked_requirements(requirements=None):
    """Returns all requirements that do not have a set version
    :param requirements: Collection of requirements
    :return: Requirements whose versions are not set
    """
    requirements = requirements or RequirementCollection()

    return RequirementCollection(sorted((
        requirement for requirement in requirements
        if str(requirement.specified_version) == Config.any_version
    )))


def unset_locks(requirements=None, locked=None):
    """Returns all requirements that are not version locked
    :param requirements: Collection of requirements
    :param locked: Collection of locked requirements
    :return: Requirements that are not locked
    """
    requirements = requirements or RequirementCollection()
    locked = locked or RequirementCollection()

    return RequirementCollection(sorted([
        requirement for requirement in set(requirements.flatten())
        if requirement.key not in locked.keys()
    ]))


def package_dependency_tree(dependency):
    """Returns a dependency tree for a single package
    :param dependency: Requirement or Package
    :return: Dependency tree for the specified package or requirement
    """
    return OrderedDict(sorted({
        requirement: package_dependency_tree(dependency=requirement)
        for requirement in dependency.requirements
    }.items()))


def dependency_tree(packages=None, requirements=None):
    """Returns a dependency tree for all packages
    :param packages: Collection of packages
    :param requirements: Collection of requirements
    :return: Dependency tree for all packages
    """
    packages = packages or PackageCollection()

    tree = OrderedDict(sorted({
        package: package_dependency_tree(dependency=package)
        for package in packages
        if package.key in packages.independent_packages.keys() and (
            # Include only the branches from provided requirements
            # if they were provided
            requirements is None or
            (requirements is not None and package.key in requirements.keys())
        )
    }.items()))

    return tree


def locked_requirements(packages=None, requirements=None):
    """Returns all requirements locked to the required versions
    :param packages: Collection of packages
    :param requirements: Collection of requirements
    :return: All requirements locked to their installed versions
    """
    packages = packages or PackageCollection()
    requirements = requirements or RequirementCollection()

    if not requirements:
        return RequirementCollection(sorted([
            Requirement.from_package(package=package) for package in packages
        ]))

    locked = []
    for package in packages:
        specified_in_requirements = package.key in requirements.keys()
        required_by_requirements = required_by(
            requirement=package,
            packages=requirements.flatten()
        )

        if specified_in_requirements or required_by_requirements:
            locked.append(package)

    return RequirementCollection(sorted([
        requirement for requirement in locked
    ]))


def lock_version_mismatch(packages=None, locked=None):
    """Return detected version mismatches between packages and locked
        requirements
    :param packages: Collection of packages
    :param locked: Collection of locked requirements
    :return: All detected mismatches between installed packages and
        locked requirements
    """
    packages = packages or PackageCollection()
    locked = locked or RequirementCollection()

    return [
        (package, str(lock.specified_version))
        for package in packages for lock in locked
        if package.key == lock.key and
        package.specified_version != lock.specified_version
    ]


def required_version_mismatch(requirements=None, locked=None):
    """Return detected version mismatches between requirements and locked
        requirements
    :param requirements: Collection of requirements
    :param locked: All detected mismatches between set requirements and
        locked requirements
    :return: All detected mismatches between requirements and locked
        requirements
    """
    requirements = requirements or RequirementCollection()
    locked = locked or RequirementCollection()

    return [
        (requirement, str(lock.specified_version))
        for requirement in requirements for lock in locked
        if requirement.key == lock.key and requirement.conflicting()
    ]


def unnecessary_packages(packages=None, requirements=None, locked=None):
    """Return locked packages that are not required by specified requirements
        or locked requirements
    :param packages: Collection of packages
    :param requirements: Collection of requirements
    :param locked: Collection of locked requirements
    :return: All packages that are not required
    """
    packages = packages or PackageCollection()
    requirements = requirements or RequirementCollection()
    locked = locked or RequirementCollection()
    unset = unset_locks(requirements=requirements, locked=locked)

    return PackageCollection(sorted([
        package for package in packages
        if package.key not in locked.keys() and
        package.key not in unset.keys()
    ]))


def unnecessary_locks(requirements=None, locked=None, ignore_list=None):
    """Return locked requirements that are not required by requirements files
    :param requirements: Collection of requirements
    :param locked: Collection of locked requirements
    :param ignore_list: List of package keys to ignore
    :return: All packages that do not need to be locked
    """
    requirements = requirements or RequirementCollection()
    locked = locked or RequirementCollection()
    ignore_list = ignore_list or Config.ignore_list

    return RequirementCollection(sorted([
        lock for lock in locked
        if lock.key not in requirements.flatten().keys() and
        lock.key not in ignore_list
    ]))


def get_graph(packages=None, name=None, filename=None, file_format=None,
              engine=None, strict=True, graph_attr=None, node_attr=None,
              edge_attr=None):
    """Creates a dependency graph
    :param packages: Installed packages
    :param name: Graph name
    :param filename: Export filename
    :param file_format: Export format
    :param engine: Rendering engine
    :param strict: Rendering should merge multi-edges
    :param graph_attr: Graph attributes
    :param node_attr: Node attributes
    :param edge_attr: Edge attributes
    :return: Graph object
    """
    packages = packages or PackageCollection()

    return create_dependency_graph(
        packages=packages, name=name, filename=filename,
        file_format=file_format, engine=engine, strict=strict,
        edge_attr=edge_attr, graph_attr=graph_attr, node_attr=node_attr,
    )


def render_graph(packages=None, graph=None, view=False):
    """Renders a dependency graph
    :param packages: Installed packages
    :param graph: Graph to render
    :param view: Display created graph
    :return: Saved render filepath
    """
    packages = packages or PackageCollection()
    graph = graph or create_dependency_graph(packages=packages)
    return render_dependency_graph(graph=graph, view=view)
