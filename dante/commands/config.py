from dante.config import Config
from dante.core.printer import Printer


def config_command(_):
    """Print current configuration
    :param _: Command arguments
    :return: None
    """
    printer = Printer()
    message = Config.to_json()
    printer.print_message(message=message)
