try:
    import colorama
except ImportError:
    colorama = None


class Printer:
    """Printer is used for formatting and printing dante's messages"""
    def __init__(self, package_color=None, success_color=None,
                 warning_color=None, foreground_color=None):

        self.package_color = (
            package_color or (colorama.Fore.CYAN if colorama else '')
        )
        self.success_color = (
            success_color or (colorama.Fore.GREEN if colorama else '')
        )
        self.warning_color = (
            warning_color or (colorama.Fore.YELLOW if colorama else '')
        )
        self.foreground_color = (
            foreground_color or (colorama.Fore.WHITE if colorama else '')
        )

    def printable_message(self, message, color=None):
        """Returns colored message
        :param message: message string
        :param color: color to write the string in
        :return: colored message string
        """
        color = color or self.foreground_color
        return '{}{}{}'.format(color, message, self.foreground_color)

    def _printable_warning(self, message):
        """Returns colored warning message for console output
        :param message: warning string
        :return: colored warning string
        """
        return self.printable_message(message, self.warning_color)

    def _printable_success(self, message):
        """Returns colored success message for console output
        :param message: message string
        :return: colored success string
        """
        return self.printable_message(message, self.success_color)

    def printable_package(self, package_name):
        """Returns colored package name for console output
        :param package_name: package name string
        :return: colored package string
        """
        return self.printable_message(package_name, self.package_color)

    def printable_package_versioned(self, package_name, package_version):
        """Print versioned package
        :param package_name: package name string
        :param package_version: package version
        """
        return "{}=={}".format(
            self.printable_package(package_name),
            package_version
        )

    def _tabulate_data(self, tabular_data, headers, column_spacing=2,
                       divider='-'):
        """Tabulate data and return output string
        :param tabular_data: list of rows of table data
        :param headers: table headers
        :param column_spacing: spacing between two columns
        :param divider: symbol used between headers and data
        """
        max_lengths = [len(str(header)) for header in headers]
        for data_row in tabular_data:
            for column_index, item in enumerate(data_row):
                item = str(item).replace(self.package_color, '')
                item = str(item).replace(self.foreground_color, '')
                if len(str(item)) > max_lengths[column_index]:
                    max_lengths[column_index] = len(str(item))

        dividers = [divider * length for length in max_lengths]

        def tabulate_row(items):
            row = ''
            item_template = '{item}{spacing}'
            for i, row_item in enumerate(items):

                # clear colors before calculating
                colorless_item = str(row_item).replace(self.package_color, '')
                colorless_item = colorless_item.replace(
                    self.foreground_color, '')

                item_spacing = ' ' * (
                    max_lengths[i] + column_spacing - len(str(colorless_item)))
                row += item_template.format(
                    item=row_item, spacing=item_spacing)
            return row.strip() + '\n'

        result = tabulate_row(items=headers)
        result += tabulate_row(items=dividers)
        for data_row in tabular_data:
            result += tabulate_row(items=data_row)

        return result.rstrip()

    def table(self, tabular_data, headers):
        """Prints table data
        :param tabular_data: data to fill the table with
        :param headers: table headers
        :return: None
        """
        table = self._tabulate_data(
            tabular_data=tabular_data,
            headers=headers)
        print(table)

    def info(self, message):
        """Print message
        :param message: message string
        """
        print(self.printable_message(message, self.foreground_color))

    def warning(self, message):
        """Print colored warning
        :param message: message string
        """
        print(self._printable_warning(message))

    def success(self, message):
        """Print colored success
        :param message: message string
        """
        print(self._printable_success(message))

    def package(self, package_name):
        """Print colored package
        :param package_name: message string
        """
        print(self.printable_package(package_name))

    def package_versioned(self, package_name, package_version):
        """Print colored package
        :param package_name: message string
        :param package_version: package version
        """
        print(self.printable_package_versioned(package_name, package_version))

    def dependency_package(self, package_name, required_version,
                           installed_version, indent):
        """Print dependency tree package
        :param package_name: name of package
        :param required_version: package required version
        :param installed_version: package installed version
        :param indent: Indentation of row
        """
        required_text = (
            ' | Required: {}'.format(
                required_version
            )
            if indent != 0 else ''
        )
        formatted_package = '{}{} [Installed: {}{}]'.format(
            ' ' * indent,
            self.printable_package(package_name=package_name),
            installed_version,
            required_text,
        )
        print(formatted_package)

    def package_list(self, package_list):
        """Prints the package list to standard output
        :param package_list: list of packages
        """
        printable = [
            self.printable_package_versioned(
                package['name'], package['version'])
            for package in package_list
        ]
        for package in sorted(printable, key=lambda item: item):
            print(package)
