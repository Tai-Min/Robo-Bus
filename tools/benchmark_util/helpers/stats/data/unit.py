"""
Provides implementation of Unit class to represent a single unit of measurement.
"""
import logging
from helpers.stats.csv_writer import CsvWriter
from helpers.stats.data.base_unit import BaseUnit
from helpers.stats.data.formatters import pretty_format_bytes, pretty_format_microamps, UnitTypes


logger = logging.getLogger(__name__)


class Unit(BaseUnit):
    """
    Represents a single unit of measurement for statistics.
    """
    def __init__(self, group: str, title: str, unit: str, csv_writer: CsvWriter):
        """
        Constructor.

        @param group: Group of the stat, e.g 'DUT'.
        @param title: Title of the stat, e.g. 'Current consumption'.
        @param unit: Unit of the stat from formatters.UnitTypes.
        @param csv_writer: CSV writer object.
        """
        super().__init__(group, title, unit, csv_writer)
        logger.debug("(%s) %s: Init", group, title)
        self._value = 0

        csv_group = self._group.replace(' ', '_').lower()
        csv_title = self._title.replace(' ', '_').lower()
        csv_unit = self._unit.replace(' ', '_').lower()
        self._csv_stat_name = f"{csv_group}_{csv_title}_{csv_unit}"

        self._csv_register_stat(self._csv_stat_name)


    def update_value(self, new_val: float):
        """
        Update stored value.

        @param new_val: New value.
        """
        self._value = new_val
        self._csv_update_stat(self._csv_stat_name, self._value)


    def get_value_str(self) -> str:
        """
        Get stored value as a pretty formatted string with unit attached.

        @return Pretty string.
        """
        if self._unit == UnitTypes.BYTES_UNIT:
            return pretty_format_bytes(self._value)

        if self._unit == UnitTypes.MICROAMPS_UNIT:
            return pretty_format_microamps(self._value)

        return str(self._value)
