"""Dante entry point"""

import sys
from dante.cli import cli


def main():
    """Dante main function"""
    from dante.config import Config

    # Read from config file when used in cli mode
    Config.read_from_file()

    parser = cli()
    if len(sys.argv) == 1:
        # Print help if no arguments are passed
        parser.print_help()
    else:
        # Otherwise run the command
        args = parser.parse_args()
        args.func(args) if hasattr(args, 'func') else parser.print_help()


if __name__ == '__main__':
    sys.exit(main())
