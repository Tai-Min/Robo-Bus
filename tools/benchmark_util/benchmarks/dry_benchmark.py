"""
Noop benchmark.
"""
import logging
import asyncio
import argparse

from helpers.stats.data.base_stats_history import BaseStatsHistory
from helpers.stats.printer_logger.generic_stats import GenericStatsPrinterLogger
from devices.ppk2.wait_for_dut import wait_for_dut_none
from helpers.stats.csv_writer import CsvWriter
from devices.ppk2.ppk2 import PPK2
from task import task

STATS_PRINT_PERIOD = 0.1
STATS_LOG_PERIOD = 2.0

DRY = "DRY"
PKK2_NAME = "PKK2"
PKK2_READING_PERIOD = 0.2
PKK2_VOLTAGE_MA = 5000


logger = logging.getLogger(__name__)


def add_args(parser : argparse.ArgumentParser):
    """
    Add command line arguments to parser.

    @param parser: Parser to add arguments to.
    """
    parser.add_argument(
        "--use-ppk2",
        action=argparse.BooleanOptionalAction,
        help="Whether to use PPK2 for DUT current measurements"
    )


def benchmark(args: argparse.Namespace, csv_writer: CsvWriter):
    """
    Benchmark entry.

    @param args: Command line arguments
    @param csv_writer: CSV writer instance
    """
    logger.info("Starting benchmark")

    use_ppk2 = args.use_ppk2

    ppk2 = None
    if use_ppk2:
        ppk2 = PPK2(PKK2_NAME, PKK2_VOLTAGE_MA, PKK2_READING_PERIOD, csv_writer, wait_for_dut_none)

    all_devices = []
    all_helpers = []
    if csv_writer:
        all_helpers.append(csv_writer)
    if ppk2:
        stats = BaseStatsHistory(DRY, [ppk2.get_measurement()])
        stats_printer_logger = GenericStatsPrinterLogger(DRY, stats, True)

        all_devices.append(ppk2)
        all_helpers.append(stats_printer_logger)

    asyncio.run(task(all_devices, all_helpers))
