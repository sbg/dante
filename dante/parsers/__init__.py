from dante.config import Config
from dante.parsers.pip import PipParser


class Parser:
    """Class used to call set parser's methods"""

    # New parsers should be added here under configurable keys
    parser_map = {}

    @staticmethod
    def parse_requirements_file(*args, **kwargs):
        """Run set parser's requirements file parse method"""
        return (
            Parser.parser_map.get(Config.parser, PipParser)
            .parse_requirements_file(*args, **kwargs)
        )

    @staticmethod
    def save_lock_file(*args, **kwargs):
        """Run set parser's lock file save method"""
        return (
            Parser.parser_map.get(Config.parser, PipParser)
            .save_lock_file(*args, **kwargs)
        )
