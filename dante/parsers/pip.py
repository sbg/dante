from dante.config import Config
from dante.core.models import RequirementCollection, Requirement
from dante.parsers.base import BaseParser


class PipParser(BaseParser):
    """Parser for pip's standard requirements files"""

    @staticmethod
    def parse_requirements_file(filepath):
        """Parse requirements file and return a collection of requirements
        :param filepath: Filepath of requirements file
        :return: Collection of requirements
        """
        with open(str(filepath), 'r') as requirements_file:
            data = [
                # Remove whitespaces and newlines
                row.replace(' ', '').strip()

                # In every row
                for row in requirements_file.readlines()

                # Ignore comments and empty lines
                if not row.startswith('#') and
                not row.startswith('-r ') and
                not row.startswith('-c ') and
                row != '\n'
            ]

        requirements = RequirementCollection([
            Requirement.from_requirement_string(row)
            for row in data
        ])
        return requirements

    @staticmethod
    def save_lock_file(requirements, filepath):
        """Save locked requirements to a lock file
        :param requirements: Collection of requirements
        :param filepath: Filepath for lock file
        """
        filepath = str(filepath or Config.lock_file_path)
        with open(filepath, 'w') as lock_file:
            data = [
                '{package_key}=={version}\n'.format(
                    package_key=requirement.key,
                    version=requirement.version_id
                ) for requirement in sorted(requirements, key=lambda p: p.key)
            ]
            lock_file.writelines(data)
