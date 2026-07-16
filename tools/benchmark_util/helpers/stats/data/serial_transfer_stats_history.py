"""
Provides implementation of SerialTransferStatsHistory class to represent a history of statistics of the serial transfer.
"""
import logging
from helpers.stats.csv_writer import CsvWriter
from helpers.stats.data.unit_history import UnitHistory
from helpers.stats.data.base_stats_history import BaseStatsHistory


logger = logging.getLogger(__name__)


class SerialTransferStatsHistory(BaseStatsHistory):
    """
    Stats object that stores all statistics of the serial transfer.
    """
    def __init__(self, name: str, csv_writer: CsvWriter):
        """
        Constructor.
    
        @param name: Name of the stats object.
        @param csv_writer: CSV writer object.
        """
        logger.debug("%s: Init", name)
        self._timeout_receive_cnt = UnitHistory(
            name, "Timeout receive", "", csv_writer)
        self._success_receive_cnt = UnitHistory(
            name, "Success receive", "", csv_writer)
        self._mangled_bytes_cnt = UnitHistory(
            name, "Mangled bytes", "bytes", csv_writer)
        self._good_bytes_cnt = UnitHistory(
            name, "Good bytes", "bytes", csv_writer)
        self._total_desired_bytes_cnt = UnitHistory(
            name, "Total desired bytes", "bytes", csv_writer)
        self._total_received_bytes_cnt = UnitHistory(
            name, "Total received bytes", "bytes", csv_writer)
        self._skipped_bytes_cnt = UnitHistory(
            name, "Skipped bytes", "bytes", csv_writer)
        hist_list = [self._success_receive_cnt, self._timeout_receive_cnt, \
                           self._good_bytes_cnt, self._mangled_bytes_cnt, \
                           self._skipped_bytes_cnt, self._total_desired_bytes_cnt, \
                           self._total_received_bytes_cnt]
        super().__init__(name, hist_list)

    def rate_payload(self, desired: str, received: str):
        """
        Compare desired to received and update bytes statistics.

        @param desired: Desired payload.
        @param received: Received payload.
        """
        loop = len(desired)
        if len(received) < loop:
            loop = len(received)

        mangled = 0
        for i in range(loop):
            if desired[i] != received[i]:
                mangled += 1

        diff = len(desired) - len(received)
        self._mangled_bytes_cnt.add_to_history(mangled)
        self._good_bytes_cnt.add_to_history(len(desired) - mangled)
        self._total_desired_bytes_cnt.add_to_history(len(desired))
        self._total_received_bytes_cnt.add_to_history(len(received))
        if diff > 0:
            self._skipped_bytes_cnt.add_to_history(diff)


    def add_success_receive(self):
        """
        Add one transfer as successful.
        """
        logger.debug("%s: Received success", self._name)
        self._success_receive_cnt.add_to_history(1)


    def add_timeout_receive(self):
        """
        Add one transfer as timed out.
        """
        logger.debug("%s: Received failure", self._name)
        self._timeout_receive_cnt.add_to_history(1)
