from dante.vendor import colorama


DEFAULT_ERROR = colorama.Fore.RED
DEFAULT_PACKAGE = colorama.Fore.CYAN
DEFAULT_SUCCESS = colorama.Fore.GREEN
DEFAULT_WARNING = colorama.Fore.YELLOW
DEFAULT_FOREGROUND = colorama.Fore.WHITE


def set_color(message, message_color, foreground_color):
    """Set color characters around a message
    :param message: Message string
    :param message_color: Message color
    :param foreground_color: Color that the output will be reset to
    :return: Message wrapped in color characters
    """
    return '{message_color}{message}{foreground_color}'.format(
        message_color=message_color,
        message=message,
        foreground_color=foreground_color
    )
