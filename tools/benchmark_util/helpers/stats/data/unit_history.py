"""
Provides implementation of UnitHistory class to represent
a history of values of a single unit of measurement.
"""
import logging
import timeit
from helpers.stats.csv_writer import CsvWriter
from helpers.stats.data.base_unit import BaseUnit
from helpers.stats.data.formatters import pretty_format_bytes, pretty_format_microamps, UnitTypes


logger = logging.getLogger(__name__)


class UnitHistory(BaseUnit):
    """
    Stores history of a value and can return result of arithmetic function
    per second of values in history as pretty formatted string.
    """
    def __init__(self, group: str, title: str, unit: str, csv_writer: CsvWriter):
        """
        Constructor.

        @param group: Group of the UnitHistory object.
        @param title: Title of the UnitHistory object.
        @param unit: Unit of the values in history. Currently "bytes", "microamps" or "" (no unit)
        @param csv_writer: CSV writer object.
        """
        super().__init__(group, title, unit, csv_writer)
        logger.debug("(%s) %s: Init", group, title)
        self._sum = 0
        self._is_first_reading = True
        self._first_reading_timestamp = 0
        csv_group = self._group.replace(' ', '_').lower()
        csv_title = self._title.replace(' ', '_').lower()
        csv_unit = self._unit.replace(' ', '_').lower()
        self._csv_sum_stat_name = f"{csv_group}_{csv_title}_{csv_unit}_sum"
        self._csv_fn_per_sec_stat_name = f"{csv_group}_{csv_title}_{csv_unit}_fn_per_sec"

        self._csv_register_stat(self._csv_sum_stat_name)
        self._csv_register_stat(self._csv_fn_per_sec_stat_name)


    def _get_fn_per_sec(self) -> float:
        """
        Get result of arithmetic function per second of values in history.

        @return Result of arithmetic function per second.
        """
        time_diff = timeit.default_timer() - self._first_reading_timestamp
        if time_diff <= 0:
            return 0
        return round(self._sum / time_diff, 2)


    def add_to_history(self, val: int):
        """
        Add value to history.

        @param val: Value to add.
        """
        logger.debug("(%s) %s: Adding value to history: %s", self._group, self._title, val)

        if self._is_first_reading:
            self._first_reading_timestamp = timeit.default_timer()
            self._is_first_reading = False

        self._sum += val

        self._csv_update_stat(self._csv_sum_stat_name, self._sum)
        self._csv_update_stat(self._csv_fn_per_sec_stat_name, self._get_fn_per_sec())


    def get_title(self) -> str:
        """
        Get title of the UnitHistory object.

        @return Title.
        """
        return self._title


    def get_sum_str(self) -> str:
        """
        Get sum of values in history 
        as pretty formatted string.

        @return Sum.
        """
        if self._unit == UnitTypes.BYTES_UNIT:
            return pretty_format_bytes(self._sum)

        if self._unit == UnitTypes.MICROAMPS_UNIT:
            return pretty_format_microamps(self._sum)

        return str(self._sum)


    def get_fn_per_sec_str(self) -> str:
        """
        Get result of arithmetic function per second of values
        in history as pretty formatted string.

        @return Result of arithmetic function per second.
        """
        if self._unit == UnitTypes.BYTES_UNIT:
            return pretty_format_bytes(self._get_fn_per_sec()) + "/s"

        if self._unit == UnitTypes.MICROAMPS_UNIT:
            return pretty_format_microamps(self._get_fn_per_sec()) + "/s"

        return str(self._get_fn_per_sec()) + "/s"
