"""
Provides implementation of BaseStatsHistory class, a base class for storing multiple unit objects.
"""
import logging
from helpers.stats.data.unit import Unit
from helpers.stats.data.unit_history import UnitHistory


logger = logging.getLogger(__name__)


class BaseStatsHistory():
    """
    Base class for storing multiple unit objects.
    """
    def __init__(self, name: str, unit_list: list[UnitHistory|Unit]):
        """
        Constructor.

        @param name: Name of the stats object.
        @param hist_list: List of UnitHistory objects.
        @param csv_writer: CSV writer object.
        """
        logger.debug("%s: Init", name)
        self._name = name
        self._unit_list = unit_list


    def get_name(self) -> str:
        """
        Get name of the Stats object.

        @return Name of the Stats object.
        """
        return self._name


    def get_unit_list(self) -> list[UnitHistory|Unit]:
        """
        Get list of Hist objects.

        @return List of Hist objects.
        """
        return self._unit_list


    def has_unit(self) -> bool:
        """
        Whether this stats history stores at least one Unit object.

        @return True if so.
        """
        for hist in self._unit_list:
            if isinstance(hist, Unit):
                return True
        return False

    def add_extern_unit_history(self, hist: UnitHistory|Unit):
        """
        Add an externally managed object to the stats history.

        @param hist: UnitHistory object to add.
        """
        if hist is None:
            logger.warning("%s: hist is None", self._name)
            return

        self._unit_list.append(hist)
