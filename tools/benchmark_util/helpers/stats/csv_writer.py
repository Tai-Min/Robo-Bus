"""
Generic CSV writer helper implementation.
"""
import asyncio
import logging
import csv
import timeit
from helpers.abc_helper import Helper

TIMESTAMP = "timestamp"


logger = logging.getLogger(__name__)


class CsvWriter(Helper):
    """
    Helper that writes stats to a csv file.
    """
    def __init__(self, name: str, filename: str, write_period: float):
        """
        Constructor.

        @param name: Name of the csv writer.
        @param filename: Path to the csv file to write to.
        @param write_period: Period at which to write stats.
        """
        if filename is None or filename == "":
            e = f"{name}: Filename must be provided"
            logger.error(e)
            raise ValueError(e)

        if write_period <= 0:
            e = f"{name}: Write period must be greater than 0"
            logger.error(e)
            raise ValueError(e)

        logger.debug("%s: Init", name)
        self._name = name
        self._filename = filename
        self._start_time = timeit.default_timer()
        self._stats = {}
        self._write_period = write_period
        self._writer_stopped_flag = asyncio.Event()
        self._writer_stopped_flag.set()
        self._exit_flag = asyncio.Event()

        self.register_new_stat(TIMESTAMP, 0)


    def _write_stats_to_csv(self):
        """
        Write stats to the csv file.
        """
        if self._writer_stopped_flag.is_set():
            logger.warning(
                "%s: Cannot write stats to csv file while writer loop is not running", self._name)
            return

        self.update_stat(TIMESTAMP, timeit.default_timer() - self._start_time)

        with open(self._filename, 'a', newline='', encoding='utf-8') as csvfile:
            csv_file = csv.DictWriter(csvfile, fieldnames=list(self._stats.keys()))
            csv_file.writerow(self._stats)


    def register_new_stat(self, stat_name: str, initial_value: float = 0):
        """
        Register a new stat to write to the csv file.
        All stats must be registered before starting the writer loop.

        @param stat_name: Name of the stat to register.
        """
        if not self._writer_stopped_flag.is_set():
            logger.warning(
                "%s: Cannot register new stat '%s' while writer loop is running",
                 self._name, stat_name)
            return

        if stat_name in self._stats:
            logger.warning("%s: Stat '%s' is already registered", self._name, stat_name)
            return

        self._stats[stat_name] = initial_value


    def update_stat(self, stat_name: str, value):
        """
        Update the value of a stat.

        @param stat_name: Name of the stat to update.
        @param value: New value of the stat.
        @param force_write: Whether to force a write operation.
        """
        if stat_name not in self._stats:
            logger.warning("%s: Stat '%s' is not registered", self._name, stat_name)
            return

        self._stats[stat_name] = value


    async def loop(self):
        """
        Write stats to CSV constantly.
        """
        with open(self._filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_file = csv.DictWriter(csvfile, fieldnames=list(self._stats.keys()))
            csv_file.writeheader()

        self._writer_stopped_flag.clear()
        logger.info("%s: Starting csv writer loop", self._name)

        while not self._exit_flag.is_set():
            await asyncio.sleep(self._write_period)
            self._write_stats_to_csv()

        logger.info("%s: Stopping csv writer loop", self._name)

        self._writer_stopped_flag.set()


    async def stop(self):
        """
        Stop the writer.
        """
        logger.info("%s: Stopping csv writer", self._name)
        self._exit_flag.set()

        if not self._writer_stopped_flag.is_set():
            logger.debug("%s: Waiting for stats writer loop to stop...", self._name)
            await self._writer_stopped_flag.wait()

        logger.info("%s: Stopped", self._name)
