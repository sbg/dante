from dante.core import color


class Printer:
    def __init__(
        self, foreground_color=None, color_info=None,
        color_success=None, color_error=None, color_warning=None,
        color_package=None
    ):
        self.color_error = color_error or color.DEFAULT_ERROR
        self.color_info = color_info or color.DEFAULT_FOREGROUND
        self.color_success = color_success or color.DEFAULT_SUCCESS
        self.color_package = color_package or color.DEFAULT_PACKAGE
        self.color_warning = color_warning or color.DEFAULT_WARNING
        self.color_foreground = foreground_color or color.DEFAULT_FOREGROUND

    def colored_message(self, message, message_color):
        return color.set_color(
            message=message,
            message_color=message_color,
            foreground_color=self.color_foreground
        )

    def print_message(self, message, message_color=None):
        message_color = message_color or self.color_info
        print(
            self.colored_message(
                message=message,
                message_color=message_color
            )
        )

    def info(self, message):
        self.print_message(
            message=message,
            message_color=self.color_info
        )

    def success(self, message):
        self.print_message(
            message=message,
            message_color=self.color_success
        )

    def error(self, message):
        self.print_message(
            message=message,
            message_color=self.color_error
        )

    def warning(self, message):
        self.print_message(
            message=message,
            message_color=self.color_warning
        )

    def package(self, message):
        self.print_message(
            message=message,
            message_color=self.color_package
        )

    def _tabulate_data(
        self, headers, tabular_data, column_spacing=2, divider='-'
    ):
        """Tabulate data and return output string
        :param headers: table headers
        :param tabular_data: list of rows of table data
        :param column_spacing: spacing between two columns
        :param divider: symbol used between headers and data
        """
        max_lengths = [len(str(header)) for header in headers]
        for data_row in tabular_data:
            for column_index, item in enumerate(data_row):
                item = str(item).replace(self.color_package, '')
                item = str(item).replace(self.color_foreground, '')
                if len(str(item)) > max_lengths[column_index]:
                    max_lengths[column_index] = len(str(item))

        dividers = [divider * length for length in max_lengths]

        def tabulate_row(items):
            row = ''
            item_template = '{item}{spacing}'
            for i, row_item in enumerate(items):

                # clear colors before calculating
                colorless_item = (
                    str(row_item).replace(self.color_package, '')
                )
                colorless_item = colorless_item.replace(
                    self.color_foreground, '')

                item_spacing = ' ' * (
                    max_lengths[i] +
                    column_spacing -
                    len(str(colorless_item))
                )
                row += item_template.format(
                    item=row_item, spacing=item_spacing)
            return row.strip() + '\n'

        result = tabulate_row(items=headers)
        result += tabulate_row(items=dividers)
        for data_row in tabular_data:
            result += tabulate_row(items=data_row)

        return result.rstrip()

    def table(self, headers, tabular_data):
        """Prints table data
        :param headers: table headers
        :param tabular_data: data to fill the table with
        :return: None
        """
        table = self._tabulate_data(
            tabular_data=tabular_data,
            headers=headers)
        print(table)
