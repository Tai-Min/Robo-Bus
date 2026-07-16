"""
Implementation of stats combiner helper. Combines multiple stats history into one table to print.
"""
import logging
from tabulate import tabulate
from helpers.stats.printer_logger.abc_stats_printer_logger import ABCStatsPrinterLogger
from helpers.stats.data.unit import Unit
from helpers.stats.data.unit_history import UnitHistory
from helpers.stats.data.base_stats_history import BaseStatsHistory


logger = logging.getLogger(__name__)


class GenericStatsCombinerPrinterLogger(ABCStatsPrinterLogger):
    """
    Combines multiple stats objects into one table to print.
    """
    def __init__(self, name: str, stat_list: list[BaseStatsHistory], print_log: bool = False):
        """
        Constructor.

        @param name: Name of the stats object.
        @param stat_list: List of Stats objects to combine.
        @param print_log: Whether to print stats to stdout. Only one of print PrinterLogger shall have this flag enabled.
        """

        # TODO: sanity check stopped here
        super().__init__(name, print_log)
        logger.debug("%s: Init", self._name)
        self._stat_list = stat_list


    def _get_hists_str(self, is_log: bool) -> str:
        """
        Get pretty formatted hists table.

        @param is_log: Whether table goes to log file.
        @return Hists table.
        """
        if len(self._stat_list) == 0:
            return ""

        # Add headers (first row)
        headers = [f"Stats ({self._name})"]
        for stat in self._stat_list:
            headers.append(f"Sum: {stat.get_name()}")
            headers.append(f"unit/sec: {stat.get_name()}")
            if stat.has_unit():
                headers.append(f"Newest: {stat.get_name()}")

        # Add other rows
        # Column is the title, i.e 'Success receive'
        # Next are set to default '-'
        table = []
        added_titles = []
        for stat in self._stat_list:
            for hist in stat.get_unit_list():
                title = hist.get_title()
                if title not in added_titles:
                    added_titles.append(title)
                    table.append([title] + ["-"] * (len(headers) - 1))

        # Replace '-' with value if exists
        stat_offset = 0
        for stat in self._stat_list:
            stat_offset_curr = 2
            if stat.has_unit():
                stat_offset_curr = 3
            for i, hist in enumerate(stat.get_unit_list()):
                hist_title = hist.get_title()
                if table[i][0] == hist_title:
                    if isinstance(hist, Unit):
                        table[i][stat_offset + 3] = hist.get_value_str()
                    elif isinstance(hist, UnitHistory):
                        table[i][stat_offset + 1] = hist.get_sum_str()
                        table[i][stat_offset + 2] = hist.get_fn_per_sec_str()
            stat_offset += stat_offset_curr

        res = ""
        if is_log:
            res = "\n"
        return res + str(tabulate(table, headers=headers, tablefmt="fancy_outline"))
