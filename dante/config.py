import os
import json
from copy import deepcopy
from collections import OrderedDict
from configparser import ConfigParser


class Config:
    PARENT_DIR = os.path.abspath(os.getcwd())
    CONFIG_FILE = os.path.join(PARENT_DIR, 'setup.cfg')

    SECTION = 'dante'
    GRAPH_ATTRIBUTE_SECTION = 'dante:graph_attributes'
    GRAPH_NODE_SECTION = 'dante:graph_node_attributes'
    GRAPH_EDGE_SECTION = 'dante:graph_edge_attributes'

    DEFAULT_PARSER = None
    DEFAULT_ANY_VERSION = 'Any'
    DEFAULT_CHECKS = ['conflicts', 'cyclic', 'missing', 'validate']
    DEFAULT_IGNORE_LIST = [
        'dante', 'pip', 'setuptools', 'wheel',
    ]
    DEFAULT_ALLOW_NAMED_VERSIONS = False
    DEFAULT_NAMED_VERSION_PATTERNS = []

    DEFAULT_REQUIREMENTS_FILE_PATH = 'requirements.txt'
    DEFAULT_LOCK_FILE_PATH = 'requirements.lock'

    DEFAULT_REQUIREMENTS_FILES = ['requirements.txt']
    DEFAULT_LOCK_FILES = ['requirements.lock']

    GRAPH_DEFAULT_NAME = 'dante-graph'
    GRAPH_DEFAULT_FILENAME = None
    GRAPH_DEFAULT_FORMAT = 'pdf'
    GRAPH_DEFAULT_ENGINE = 'dot'
    GRAPH_DEFAULT_STRICT = True

    GRAPH_DEFAULT_ATTRIBUTES = {}
    GRAPH_DEFAULT_NODE_ATTRIBUTES = {
        'shape': 'box3d',
    }
    GRAPH_DEFAULT_EDGE_ATTRIBUTES = {
        'fontsize': '10',
    }

    parser = DEFAULT_PARSER
    any_version = DEFAULT_ANY_VERSION
    checks = DEFAULT_CHECKS
    ignore_list = DEFAULT_IGNORE_LIST
    allow_named_versions = DEFAULT_ALLOW_NAMED_VERSIONS
    named_version_patterns = DEFAULT_NAMED_VERSION_PATTERNS
    requirements_files = DEFAULT_REQUIREMENTS_FILES
    lock_files = DEFAULT_LOCK_FILES
    lock_file_path = DEFAULT_LOCK_FILE_PATH
    graph_name = GRAPH_DEFAULT_NAME
    graph_filename = GRAPH_DEFAULT_FILENAME
    graph_format = GRAPH_DEFAULT_FORMAT
    graph_engine = GRAPH_DEFAULT_ENGINE
    graph_attributes = GRAPH_DEFAULT_ATTRIBUTES
    graph_strict = GRAPH_DEFAULT_STRICT
    graph_node_attributes = GRAPH_DEFAULT_NODE_ATTRIBUTES
    graph_edge_attributes = GRAPH_DEFAULT_EDGE_ATTRIBUTES

    def __getattribute__(self, item):
        """Return a copy of the attribute if that attribute is a list or a dict
        :param item: Requested attribute
        :return: Attribute or copy of that attribute
        """
        if isinstance(item, list) or isinstance(item, dict):
            return deepcopy(item)

        return item

    @staticmethod
    def absolute_path(file_path):
        """Get absolute path for a file
        :param file_path: Relative filepath
        :return: Absolute path string
        """
        return os.path.join(Config.PARENT_DIR, file_path)

    @classmethod
    def read_from_file(cls):
        """Read and set configuration from file
        :return: None
        """
        if not os.path.exists(cls.CONFIG_FILE):
            # If config file does not exist use default config
            return

        parser = ConfigParser()
        parser.read(cls.CONFIG_FILE)

        if parser.has_section(cls.SECTION):
            cls.any_version = cls.get_option(
                parser, cls.SECTION, 'any_version', cls.any_version
            )
            cls.checks = cls.get_list(
                parser, cls.SECTION, 'checks', cls.checks
            )
            cls.ignore_list = cls.get_list(
                parser, cls.SECTION, 'ignore_list', cls.ignore_list
            )
            allow_named_versions = cls.get_option(
                parser,
                cls.SECTION,
                'allow_named_versions',
                cls.allow_named_versions
            )
            cls.allow_named_versions = (
                str(allow_named_versions).lower() == 'true'
            )
            cls.named_version_patterns = cls.get_list(
                parser,
                cls.SECTION,
                'named_version_patterns',
                cls.named_version_patterns
            )
            cls.lock_file_path = cls.get_option(
                parser,
                cls.SECTION,
                'lock_file_path',
                cls.lock_file_path
            )
            cls.requirements_files = [
                cls.absolute_path(file_) for file_ in cls.get_list(
                    parser,
                    cls.SECTION,
                    'requirements_files',
                    cls.requirements_files
                )
            ]
            cls.lock_files = [
                cls.absolute_path(file_) for file_ in cls.get_list(
                    parser,
                    cls.SECTION,
                    'lock_files',
                    cls.lock_files
                )
            ]
            cls.graph_name = cls.get_option(
                parser, cls.SECTION, 'graph_name', cls.graph_name
            )
            cls.graph_filename = cls.get_option(
                parser, cls.SECTION, 'graph_filename', cls.graph_filename
            )
            cls.graph_format = cls.get_option(
                parser, cls.SECTION, 'graph_format', cls.graph_format
            )
            cls.graph_engine = cls.get_option(
                parser, cls.SECTION, 'graph_engine', cls.graph_engine
            )
            graph_strict = cls.get_option(
                parser, cls.SECTION, 'graph_strict', cls.graph_strict
            )
            cls.graph_strict = (
                str(graph_strict).lower() == 'true'
            )

        if parser.has_section(cls.GRAPH_ATTRIBUTE_SECTION):
            items = cls.GRAPH_DEFAULT_ATTRIBUTES.copy()
            items.update(dict(parser.items(
                section=cls.GRAPH_ATTRIBUTE_SECTION
            )))
            cls.graph_attributes = items

        if parser.has_section(cls.GRAPH_NODE_SECTION):
            items = cls.GRAPH_DEFAULT_NODE_ATTRIBUTES.copy()
            items.update(dict(parser.items(section=cls.GRAPH_NODE_SECTION)))
            cls.graph_node_attributes = items

        if parser.has_section(cls.GRAPH_EDGE_SECTION):
            items = cls.GRAPH_DEFAULT_EDGE_ATTRIBUTES.copy()
            items.update(dict(parser.items(section=cls.GRAPH_EDGE_SECTION)))
            cls.graph_edge_attributes = items

    @staticmethod
    def get_option(parser, section, option, default):
        """Get option from parser
        :param parser: Option parser
        :param section: Option section in config file
        :param option: Option name
        :param default: Default value for option
        :return: Option value
        """
        return (
            parser.get(section, option)
            if parser.has_option(section, option)
            else default
        )

    @staticmethod
    def get_list(parser, section, option, default):
        """Get option from parser in list format
        :param parser: Option parser
        :param section: Option section in config file
        :param option: Option name
        :param default: Default value for option
        :return: Option value
        """
        result = Config.get_option(parser, section, option, default)
        try:
            if isinstance(result, str):
                return [item for item in result.split('\n') if item]
            if isinstance(result, list):
                return result
            return default
        except ValueError:
            return default

    @classmethod
    def to_json(cls):
        """Return options in json format
        :return: json string with options as keys
        """
        return json.dumps(OrderedDict((
            ('dante', OrderedDict((
                ('any_version', cls.any_version),
                ('checks', cls.checks),
                ('ignore_list', cls.ignore_list),
                ('allow_named_versions', cls.allow_named_versions),
                ('named_version_patterns', cls.named_version_patterns),
                ('lock_file_path', cls.lock_file_path),
                ('requirements_files', cls.lock_files),
                ('lock_files', cls.lock_files),
                ('graph_name', cls.graph_name),
                ('graph_filename', cls.graph_filename),
                ('graph_format', cls.graph_format),
                ('graph_engine', cls.graph_engine),
                ('graph_strict', cls.graph_strict)))),
            ('graph_attributes', cls.graph_attributes),
            ('graph_node_attributes', cls.graph_node_attributes),
            ('graph_edge_attributes', cls.graph_edge_attributes),
            )), indent=4)
