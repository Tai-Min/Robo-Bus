"""
Provides implementation of BaseUnit class, 
a base class for objects that store some physical values.
"""
import logging
from helpers.stats.csv_writer import CsvWriter


logger = logging.getLogger(__name__)


class BaseUnit():
    """
    Base class for objects that store some physical values.
    """
    def __init__(self, group: str, title: str, unit: str, csv_writer: CsvWriter):
        """
        Constructor.

        @param group: Group to which this unit belongs to.
        @param title: Title of the unit.
        @param unit: Unit name from formatters.UnitTypes
        @param csv_writer: CSV writer object.
        """
        logger.debug("(%s) %s: Init", group, title)
        self._group = group
        self._title = title
        self._unit = unit
        self.__csv_writer = csv_writer


    def _csv_register_stat(self, name: str):
        """
        Register new statistic in csv writer.

        @param name: Name of the statistic.
        """
        if self.__csv_writer is not None:
            self.__csv_writer.register_new_stat(name)
        else:
            logger.debug("No CSV writter set")


    def _csv_update_stat(self, name: str, value: float):
        """
        Update statistic in csv writer.

        @param name: Name of the statistic.
        @param value: New value.
        """
        if self.__csv_writer is not None:
            self.__csv_writer.update_stat(name, value)


    def get_title(self) -> str:
        """
        Get title of the UnitHistory object.

        @return Title.
        """
        return self._title
