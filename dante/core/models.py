import re
import abc
import copy
from functools import reduce
from collections import OrderedDict

from dante.vendor import pkg_resources
from dante.vendor.packaging.specifiers import (
    Version,
    SpecifierSet,
)
# noinspection PyProtectedMember
from dante.vendor.pkg_resources import RequirementParseError
from dante.vendor.packaging.requirements import InvalidRequirement

from dante import messages
from dante.config import Config


class VersionData:

    operators = OrderedDict([
        ('equal', '=='),
        ('not_equal', '!='),
        ('less_than_equal', '<='),
        ('greater_than_equal', '>='),
        ('less_than', '<'),
        ('greater_than', '>'),
    ])

    def __init__(self, obj):
        """Create version from object
        :param obj: Any object
        """
        self.obj = obj
        if isinstance(obj, VersionData):
            self.id = obj.id
        elif isinstance(obj, str):
            self.id = self.from_string(obj)
        elif isinstance(obj, Version):
            self.id = self.from_packaging_version(version=obj)
        elif isinstance(obj, SpecifierSet):
            self.id = self.from_specifier_set(version=obj)
        else:
            self.id = str(obj)

    def is_named(self, named_version_patterns=None):
        """Determines whether a version matches a named version pattern
        :param named_version_patterns: List of regex patterns
        :return: Whether a match is found
        """
        named_version_patterns = (
            named_version_patterns or Config.named_version_patterns or []
        )
        for pattern in named_version_patterns:
            if re.match(pattern=pattern, string=self.id):
                return True
        return False

    @property
    @abc.abstractmethod
    def specifier(self):
        """Get version specifier
        :return: version specifier
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def from_string(version):
        """Get version from string
        :param version:
        :return: VersionData
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def from_specifier_set(version):
        """Create version from specifier set
        :param version: Version specifier set
        :return: VersionData
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def from_packaging_version(version):
        """Create version from packaging version
        :param version: Packaging version
        :return: VersionData
        """
        pass

    @staticmethod
    def strip_operators(version):
        """Strip operators from version
        :param version: Version string
        :return: Version string without operators
        """
        for operator in VersionData.operators.values():
            version = version.replace(operator, '')
        return version


class InstalledVersion(VersionData):

    def __repr__(self):
        """Represent installed version with version id
        :return: Version id string
        """
        return self.id

    @property
    def specifier(self):
        """Get Version specifier
        :return: Version specifier
        """
        return (
            self.operators['equal'] + self.id
            if self.id != Config.any_version
            else Config.any_version
        )

    # noinspection PyBroadException
    @staticmethod
    def from_string(version):
        """Get version from string
        :param version: Version string
        :return: InstalledVersion object
        """
        cleaned_version = InstalledVersion.strip_operators(version=version)
        try:
            return str(Requirement.parse(version_string=cleaned_version))
        except Exception:
            return cleaned_version

    @staticmethod
    def from_specifier_set(version):
        """Get installed version from specifier set
        :param version: version specifier
        :return: Installed version object
        """
        if len(version) > 1:
            return Config.any_version
        return InstalledVersion.strip_operators(str(version))

    @staticmethod
    def from_packaging_version(version):
        """Get installed version from packaging version format
        :param version: version in packaging format
        :return: Installed version object
        """
        return (
            InstalledVersion.strip_operators(str(version))
            if version else Config.any_version
        )

    def __eq__(self, other):
        """Override equality for easier version comparison
        :param other: Version compared with
        :return: Comparison result
        """
        other_id = (
            other.id if isinstance(other, InstalledVersion) else

            InstalledVersion.strip_operators(other.id)
            if isinstance(other, RequiredVersion) else

            other if isinstance(other, str) else
            str(other)
        )

        return (
            self.id == other_id and
            self.id != Config.any_version and
            other_id != Config.any_version
        )


class RequiredVersion(VersionData):

    def __repr__(self):
        """Represent required version with version id
        :return: Requirement version id
        """
        return self.id

    @property
    def specifier(self):
        """Retrieve version specifier
        :return: Version specifier
        """
        return self.id if self.id != Config.any_version else Config.any_version

    # noinspection PyBroadException
    @staticmethod
    def from_string(version):
        """Create required version from string
        :param version: Version string
        :return: RequiredVersion object
        """
        specs = version.split(',')
        if len(specs) > 1:
            for spec in specs:
                spec = RequiredVersion.strip_operators(spec)
                Requirement.parse(version_string=spec)
            return version

        version = RequiredVersion.strip_operators(version=version)
        try:
            return (
                RequiredVersion.operators['equal'] +
                str(Requirement.parse(version_string=version))
            )
        except Exception:
            return version

    @staticmethod
    def from_specifier_set(version):
        """Create version from specifier set
        :param version: Version specifier set
        :return: Version string
        """
        return str(version) if version else Config.any_version

    @staticmethod
    def from_packaging_version(version):
        """Create version from packaging version
        :param version: Packaging version
        :return: Version string
        """
        return RequiredVersion.operators['equal'] + str(version)

    def __eq__(self, other):
        """Override equality operator to make comparisons easier
        :param other: Version compared with
        :return: Comparison result
        """
        other_id = (
            other.id if isinstance(other, RequiredVersion) else

            VersionData.operators['equal'] + other.id
            if isinstance(other, InstalledVersion) else

            other if isinstance(other, str) else
            str(other)
        )

        return (
            self.id == other_id and
            self.id != Config.any_version and
            other_id != Config.any_version
        )


class Dependency:
    def __init__(self, key, name, obj, version, _ignore_list=None):
        """Create dependency object
        :param key: Dependency key
        :param name: Dependency name
        :param obj: Object the dependency was created from
        :param version: Dependency version
        :param _ignore_list: Ignore list (used for retrieving requirements)
        """
        self.key = key
        self.name = name
        self.obj = obj
        self.version = VersionData(obj=version)
        self._ignore_list = _ignore_list or Config.ignore_list

    def __lt__(self, other):
        """Override lesser than operator for easier comparisons
        :param other: Dependency compared to
        :return: Comparison result
        """
        return self.key < other.key

    def __gt__(self, other):
        """Override greater than operator for easier comparisons
        :param other: Dependency compared to
        :return: Comparison result
        """
        return self.key > other.key

    def __eq__(self, other):
        """Override equality operator for easier comparisons
        :param other: Dependency compared to
        :return: Comparison result
        """
        return (
            self.key == other.key and
            self.version == other.version
        )

    def __hash__(self):
        """Set dependency hash to key hash
        :return: Dependency hash
        """
        return hash(self.key)

    def __repr__(self):
        """Represent dependency with it's key
        :return: Dependency representation
        """
        return '<{classname}: {key}>'.format(
            classname=str(self.__class__),
            key=self.key
        )

    @property
    def package(self):
        """Retrieve dependency package
        :return: Package object
        """
        return self


class Package(Dependency):
    def __init__(self, key, name, obj, version, _ignore_list=None):
        """Create package object
        :param key: Package key
        :param name: Package name
        :param obj: Object the package is created from
        :param version: Package version
        :param _ignore_list: Ignore list (used for retrieving requirements)
        """
        super().__init__(
            key=key,
            name=name,
            obj=obj,
            version=version,
            _ignore_list=_ignore_list
        )
        self.key = key
        self.name = name
        self.obj = obj
        self.version = InstalledVersion(obj=version)
        self._ignore_list = _ignore_list or Config.ignore_list

    @property
    def version_id(self):
        """Get version id
        :return: Version id
        """
        return self.version.id

    @version_id.setter
    def version_id(self, version_id):
        """Set version id
        :param version_id: Version id string
        :return: None
        """
        self.version_id = version_id

    @property
    def specified_version(self):
        """Get version specifier
        :return: Version specifier
        """
        return self.version.specifier

    @property
    def requirements(self):
        """Retrieve package requirements
        :return: RequirementCollection object
        """
        return RequirementCollection(sorted([
            Requirement(
                key=requirement.key.lower(),
                name=requirement.name,
                obj=requirement,
                version=RequiredVersion(obj=requirement.specifier),
                _ignore_list=self._ignore_list
            )
            for requirement in self.obj.requires()
            if requirement.key.lower() not in self._ignore_list
        ]))


class PackageCollection(list):
    def __repr__(self):
        """Represent package with it's key
        :return: Package representation
        """
        return '<PackageCollection: {}>'.format(len(self))

    def get(self, key):
        """Retrieve package that matches the provided key
        :param key: Package key
        :return: Package object
        """
        return next(package for package in self if package.key == key)

    @staticmethod
    def from_distributions(packages, ignore_list=None):
        """Create package collection from package distribution object
        :param packages: Source packages
        :param ignore_list: List of ignored package keys
        :return: PackageCollection object
        """
        ignore_list = ignore_list or []

        return PackageCollection(sorted([
            Package(
                key=package.key.lower(),
                name=package.project_name,
                obj=package,
                version=InstalledVersion(obj=package.parsed_version),
                _ignore_list=ignore_list
            )
            for package in packages
            if package.key.lower() not in ignore_list
        ], key=lambda p: p.key))

    @staticmethod
    def installed_packages(packages=None, list_all=False, ignore_list=None):
        """Retrieve installed packages
        :param packages: Source packages
        :param list_all: Whether to list all packages
        :param ignore_list: List of ignored package keys
        :return: PackageCollection object
        """
        ignore_list = ignore_list or []
        packages = packages or pkg_resources.working_set

        default_ignore_list = Config.ignore_list

        if not list_all:
            ignore_list.extend(default_ignore_list)
            packages = [
                package for package in packages
                if package.key not in ignore_list
            ]

        return PackageCollection.from_distributions(
            packages=packages, ignore_list=ignore_list
        )

    def keys(self):
        """Retrieve keys for all packages in collection
        :return: List of package keys
        """
        return [package.key for package in self]

    @property
    def requirements(self):
        """Requirements for all packages in collection
        :return: RequirementCollection object
        """
        if not self:
            return RequirementCollection()
        return RequirementCollection(
            reduce(
                lambda x, y: x + y,
                [package.requirements for package in self]
            )
        )

    @property
    def independent_packages(self):
        """Retrieve packages that do not depend on another package
        :return: PackageCollection object
        """
        return PackageCollection([
            package for package in self
            if package.key not in self.requirements.keys()
        ])

    @property
    def dependent_packages(self):
        """Retrieve packages that depend on another package
        :return: PackageCollection object
        """
        return PackageCollection([
            package for package in self
            if package.key in self.requirements.keys()
        ])

    @property
    def cyclic_dependencies(self):
        """Retrieve cyclical dependencies
        :return: List of cyclical paths
        """
        cyclic = []
        for package in self:
            PackageCollection._find_cyclic_dependencies(
                dependency=package, paths=cyclic
            )
        return cyclic

    @staticmethod
    def _find_cyclic_dependencies(dependency, paths, path=None):
        """Find cyclic dependencies by using a depth first search algorithm
        :param dependency: Dependency for which to find cyclical paths
        :param paths: Container for all detected cyclical paths
        :param path: Current path
        :return: Cyclical path or None
        """
        path = copy.copy(path) or []

        # End when no more requirements exist
        if not dependency.requirements:
            return []

        # Add path if detected cyclical dependency
        if dependency.key in map(lambda d: d.key, path):
            return [node for node in path]

        # add dependency to current path
        path.append(dependency.package)

        for requirement in dependency.requirements:
            # get path for each requirement
            new_path = (
                PackageCollection._find_cyclic_dependencies(
                    dependency=requirement, paths=paths, path=path
                )
            )

            # Add to paths and ignore duplicates
            if (new_path and sorted(new_path)
                    not in map(sorted, paths)):
                paths.append(new_path)

        return []


class Requirement(Dependency):

    def __init__(self, key, name, obj, version=None, _ignore_list=None):
        """Create requirement object
        :param key: Requirement key
        :param name: Requirement name
        :param obj: The object requirement is made from
        :param version: Requirement version
        :param _ignore_list: Ignore list (used for retrieving requirements)
        """
        super().__init__(
            key=key,
            name=name,
            obj=obj,
            version=version,
            _ignore_list=_ignore_list
        )
        self.key = key
        self.name = name
        self.obj = obj
        self.version = RequiredVersion(obj=version) or Config.any_version
        self._ignore_list = _ignore_list or Config.ignore_list

    @property
    def specified_version(self):
        """Get version specifier
        :return: Version specifier
        """
        return self.version.specifier

    @classmethod
    def from_setuptools_requirement(cls, requirement):
        """Create requirement from setuptools requirement object
        :param requirement: Setuptools requirement object
        :return: Requirement object
        """
        return cls(
            key=requirement.key.lower(),
            name=requirement.name,
            obj=requirement,
            version=RequiredVersion(obj=requirement.specifier),
        )

    @classmethod
    def from_requirement_string(cls, requirement_string):
        """Create requirement from requirement string
        :param requirement_string: Requirement string
        :return: Requirement object
        """
        return cls.from_setuptools_requirement(
            requirement=Requirement.parse(version_string=requirement_string)
        )

    @classmethod
    def from_package(cls, package):
        """Create requirement from package
        :param package: Package object
        :return: Requirement object
        """
        # noinspection PyProtectedMember
        return cls(
            key=package.key,
            name=package.name,
            obj=package,
            version=RequiredVersion(package.version.specifier),
            _ignore_list=package._ignore_list,
        )

    @property
    def package(self):
        """Get installed package for requirement
        :return: Package object
        """
        distribution = pkg_resources.working_set.by_key.get(self.key)
        if distribution is None:
            return None

        return Package(
            key=distribution.key.lower(),
            name=distribution.project_name,
            obj=distribution,
            version=InstalledVersion(obj=distribution.parsed_version),
            _ignore_list=self._ignore_list
        )

    @property
    def requirements(self):
        """Retrieve requirements for calling requirement
        :return: RequirementCollection object
        """
        return (
            self.package.requirements
            if self.package
            else RequirementCollection()
        )

    @property
    def version_id(self):
        """Retrieve version id
        :return: Version id string
        """
        version = getattr(self.package, 'version', Config.any_version)
        return getattr(version, 'id', Config.any_version)

    @version_id.setter
    def version_id(self, version_id):
        """Set version id
        :param version_id: version string
        :return: None
        """
        self.version_id = version_id

    def conflicting(self, allow_named_versions=False,
                    named_version_patterns=None):
        """Find if requirement conflicts with other requirements or packages.

        Named versions will not be detected as conflicts if enabled.

        :param allow_named_versions: Whether named versions are allowed
        :param named_version_patterns: Patterns for matching named versions
        :return: Whether there is a conflict
        """
        allow_named_versions = (
            allow_named_versions or Config.allow_named_versions or False
        )
        named_version_patterns = (
            named_version_patterns or Config.named_version_patterns or []
        )

        version_string = (
            '{}{}'.format(self.key, self.specified_version)
        )
        required_versions = Requirement.parse(version_string=version_string)
        installed_version = self.version_id

        allowed_named_version_package = (
            self.package.version.is_named(
                named_version_patterns=named_version_patterns
            ) if allow_named_versions else False
        ) if self.package else False

        return (
            installed_version != Config.any_version and
            installed_version not in required_versions and
            not allowed_named_version_package
        )

    @staticmethod
    def parse(version_string):
        """Parse requirement from a version string. Can cause an exception
            when a version string is invalid.
        :param version_string: Version string
        :return: Parsed requirement string
        """
        try:
            return pkg_resources.Requirement.parse(version_string)
        except (InvalidRequirement, RequirementParseError):
            raise Exception('{}: "{}"'.format(
                messages.INVALID_REQUIREMENT, version_string
            ))


class RequirementCollection(list):
    def __repr__(self):
        """Represent requirement collection with a number of items
        :return: Requirement collection representation
        """
        return '<RequirementCollection: {}>'.format(len(self))

    def get(self, key):
        """Return requirement that matches the provided key
        :param key: Requirement key
        :return: Requirement
        """
        return next(
            requirement for requirement in self if requirement.key == key
        )

    def keys(self):
        """Return all requirement keys
        :return: list of keys
        """
        return [requirement.key for requirement in self]

    def flatten(self, requirements=None, result=None):
        """Return all non top level requirements in a list
        :param requirements: Requirements collection
        :param result: Current result
        :return: list of requirements
        """
        requirements = requirements or self

        result = result or RequirementCollection()
        for requirement in requirements:
            if requirement.key not in result.keys():
                result.append(requirement)
            new = [
                item for item in requirement.requirements if item not in result
            ]
            if new:
                self.flatten(new, result)
        return result

    @staticmethod
    def from_file(filepath):
        """Create a requirement collection from a file
        :param filepath: Requirement file path
        :return: Requirements collection
        """
        from dante.parsers import Parser
        return Parser.parse_requirements_file(filepath=filepath)

    @staticmethod
    def from_files(filepaths):
        """Create a requirement collection from multiple files
        :param filepaths: Requirement file paths
        :return: Requirements collection
        """
        requirements = RequirementCollection()
        for requirements_file in filepaths:
            requirements.extend(
                RequirementCollection.from_file(filepath=requirements_file)
            )
        return requirements

    def save_lock_file(self, filepath):
        """Save requirements to a lockfile
        :param filepath: Filepath of the lockfile
        :return: None
        """
        from dante.parsers import Parser
        Parser.save_lock_file(requirements=self, filepath=filepath)
