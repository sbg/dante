try:
    import colorama
except ImportError:
    colorama = None

from dante.core.printer import Printer


class Precondition:
    def __init__(self):
        self.printer = PrinterPrecondition()


class PrinterPrecondition:

    @staticmethod
    def _default():
        package_color = colorama.Fore.CYAN if colorama else ''
        success_color = colorama.Fore.GREEN if colorama else ''
        warning_color = colorama.Fore.YELLOW if colorama else ''
        foreground_color = colorama.Fore.WHITE if colorama else ''

        return {
            'package_color': package_color,
            'success_color': success_color,
            'warning_color': warning_color,
            'foreground_color': foreground_color
        }

    def exists(self, **printer_info):
        info = self._default()
        info.update(printer_info)
        printer = Printer(**info)
        return printer
