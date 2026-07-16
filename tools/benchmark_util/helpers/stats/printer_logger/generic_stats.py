"""
Implementation of stdout printer and logger for benchmark statiscics.
"""
import logging
from tabulate import tabulate
from helpers.stats.data.unit import Unit
from helpers.stats.data.unit_history import UnitHistory
from helpers.stats.printer_logger.abc_stats_printer_logger import ABCStatsPrinterLogger
from helpers.stats.data.base_stats_history import BaseStatsHistory


logger = logging.getLogger(__name__)


class GenericStatsPrinterLogger(ABCStatsPrinterLogger):
    """
    Stats object that stores statistics of the benchmark and can print them to stdout or log file.
    """
    def __init__(self, name: str, stats: BaseStatsHistory, print_log: bool = False):
        """
        Constructor.

        @param name: Name of the stats object.
        @param stats: Statistics object.
        @param print_log: Whether to print stats to stdout. Only one of print PrinterLogger shall have this flag enabled.
        """

        if stats is None:
            e = f"{name}: Stats must be provided"
            logger.error(e)
            raise ValueError(e)

        super().__init__(name, print_log)
        logger.debug("%s: Init", self._name)
        self._stats = stats


    def _get_hists_str(self, is_log: bool) -> str:
        """
        Get pretty formatted hists table.

        @return Hists table.
        """
        has_unit = self._stats.has_unit()
        headers = [f"Stats ({self._name})", "Sum", "Per second"]
        if has_unit:
            headers.append("Newest")

        table = []
        for hist in self._stats.get_unit_list():
            if isinstance(hist, Unit):
                table.append([hist.get_title(), "-", "-", hist.get_value_str()])
            elif isinstance(hist, UnitHistory):
                if has_unit:
                    table.append(
                        [hist.get_title(), hist.get_sum_str(), hist.get_fn_per_sec_str(), "-"])
                else:
                    table.append([hist.get_title(), hist.get_sum_str(), hist.get_fn_per_sec_str()])

        res = ""
        if is_log:
            res = "\n"
        return res + str(tabulate(table, headers=headers, tablefmt="fancy_outline"))
