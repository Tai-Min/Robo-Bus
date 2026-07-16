"""
Abstract base class for stats printer and loggers.
"""
import logging
import asyncio
import os
import sys
from abc import abstractmethod
from helpers.abc_helper import Helper

STATS_PRINT_PERIOD = 0.1
STATS_LOG_PERIOD = 2.0


logger = logging.getLogger(__name__)


class ABCStatsPrinterLogger(Helper):
    """
    Abstract stats printer to stdout and logger.
    """
    def __init__(self, name: str, print_log: bool):
        """
        Constructor.

        @param name: Name of the stats object.
        @param print_log: Whether to print stats to stdout. Only one of print PrinterLogger shall have this flag enabled.
        @param print_period: Period in seconds of printing stats.
        @param log_period: Period in seconds of logging stats.
        """
        logger.debug("%s: Init", name)
        self._name = name
        self._print_log = print_log
        self._printer_stopped_flag = asyncio.Event()
        self._printer_stopped_flag.set()
        self._logger_stopped_flag = asyncio.Event()
        self._logger_stopped_flag.set()
        self._exit_flag = asyncio.Event()


    @abstractmethod
    def _get_hists_str(self, is_log: bool) -> str:
        """
        Get pretty formatted hists table.

        @return Hists table.
        """
        raise NotImplementedError(
            "Get hists string method should be implemented by all Stats objects")


    async def _print_stats_loop(self):
        """
        Print stats to stdout constantly.
        Will return instantly if logging to stdout is enabled
        """

        # Don't run print if logging to stdout is enabled
        for handler in logging.getLogger().handlers:
            if handler.stream == sys.stdout:
                self._printer_stopped_flag.set()
                return

        self._printer_stopped_flag.clear()
        logger.info("%s: Starting print stats loop", self._name)

        os.system('cls' if os.name == 'nt' else 'clear')

        while not self._exit_flag.is_set():
            await asyncio.sleep(STATS_PRINT_PERIOD)
            print("\x1b[H\x1b[3J", end="")
            print(self._get_hists_str(False))

        logger.info("%s: Stopping print stats loop", self._name)
        self._printer_stopped_flag.set()


    async def _log_stats_loop(self):
        """
        Log stats constantly.
        """
        self._logger_stopped_flag.clear()
        logger.info("%s: Starting log stats loop", self._name)

        while not self._exit_flag.is_set():
            await asyncio.sleep(STATS_LOG_PERIOD)
            logger.info(self._get_hists_str(True))

        logger.info("%s: Stopping log stats loop", self._name)

        self._logger_stopped_flag.set()


    async def stop(self):
        """
        Stop looping stats reporting.
        """
        logger.info("%s: Stopping stats", self._name)
        self._exit_flag.set()

        if not self._printer_stopped_flag.is_set():
            logger.debug("%s: Waiting for printer loop to stop...", self._name)
            await self._printer_stopped_flag.wait()

        if not self._logger_stopped_flag.is_set():
            logger.debug("%s: Waiting for logger loop to stop...", self._name)
            while not self._logger_stopped_flag.is_set():
                await self._logger_stopped_flag.wait()

        logger.info("%s: Stopped", self._name)


    async def loop(self):
        """
        Loop stats reporting.

        @param print_stats: Whether to print stats to stdout.
        """

        if self._print_log:
            await asyncio.gather(self._print_stats_loop(), self._log_stats_loop())
        else:
            await self._log_stats_loop()
