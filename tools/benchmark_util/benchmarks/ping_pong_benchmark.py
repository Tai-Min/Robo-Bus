"""
Ping pong benchmark.
Two devices send data to each other and gather statistics.
"""
import asyncio
import logging
import argparse

from devices.ppk2.wait_for_dut import wait_for_dut_serial
from helpers.stats.csv_writer import CsvWriter
from devices.ppk2.ppk2 import PPK2
from helpers.stats.data.serial_transfer_stats_history import SerialTransferStatsHistory
from helpers.stats.printer_logger.generic_stats import GenericStatsPrinterLogger
from helpers.stats.printer_logger.generic_stats_combiner import GenericStatsCombinerPrinterLogger
from devices.sync import WriterReceiverSync
from devices.serial.half_duplex_serial import HalfDuplexSerial
from task import task


logger = logging.getLogger(__name__)


DEFAULT_TABULAR_OUTPUT = "DUT"
DEFAULT_TESTER_PORT = "/dev/RS485"
DEFAULT_DUT_PORT = "/dev/BridgeRS485"
DEFAULT_BAUD = 1000000
DEFAULT_PAYLOAD_SIZE = 256

DUT_PPK2_TIMEOUT_SECONDS = 5
DUT_PKK2_READING_PERIOD = 0.2
DUT_PKK2_VOLTAGE_MV = 5000

NO_OUTPUT = "NoOutput"
TESTER = "Tester"
DUT = "DUT"
TOTAL = "Total"
COMBINED = "Combined"


def add_args(parser : argparse.ArgumentParser):
    """
    Add command line arguments to parser.

    @param: parser: Parser to add arguments to.
    """
    parser.add_argument(
        "--tabular-output",
        type=str,
        default=DEFAULT_TABULAR_OUTPUT,
        choices=[NO_OUTPUT, DUT, TESTER, TOTAL, COMBINED],
        help="What to live output in tabular format to stdout. Not used if --log-stdout is set to True"
    )
    parser.add_argument(
        "--payload-size",
        type=int,
        default=DEFAULT_PAYLOAD_SIZE,
        help="Size of the payload to generate and send"
    )
    parser.add_argument(
        "--dut-serial",
        default=DEFAULT_DUT_PORT,
        help="Path to DUT serial device"
    )
    parser.add_argument(
        "--tester-serial",
        default=DEFAULT_TESTER_PORT,
        help="Path to tester serial device"
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=DEFAULT_BAUD,
        help="Serial baud rate"
    )
    parser.add_argument(
        "--use-dut-ppk2",
        action=argparse.BooleanOptionalAction,
        help="Whether to use PPK2 for DUT current measurements"
    )


def benchmark(args: argparse.Namespace, csv_writer: CsvWriter):
    """
    Benchmark entry.

    @param: args: Command line arguments
    @param: csv_writer: CSV writer instance
    """
    logger.info("Starting benchmark")

    tester_port = args.tester_serial
    dut_port = args.dut_serial
    baud = args.baud
    payload_size = args.payload_size
    use_dut_ppk2 = args.use_dut_ppk2
    tabular_output = args.tabular_output
    log_to_stdout = args.log_to_stdout

    if log_to_stdout:
        tabular_output = NO_OUTPUT

    dut_ppk2 = None
    if use_dut_ppk2:
        dut_ppk2 = PPK2(DUT, DUT_PKK2_VOLTAGE_MV, DUT_PKK2_READING_PERIOD,
                        csv_writer, wait_for_dut_serial,
                        port=dut_port, timeout=DUT_PPK2_TIMEOUT_SECONDS)

    tester_rs485_stats = SerialTransferStatsHistory(TESTER, csv_writer)
    dut_rs485_stats = SerialTransferStatsHistory(DUT, csv_writer)
    if dut_ppk2:
        dut_rs485_stats.add_extern_unit_history(dut_ppk2.get_measurement())
    total_stats = SerialTransferStatsHistory(TOTAL, csv_writer)
    combined_stats = [tester_rs485_stats, dut_rs485_stats, total_stats]

    tester_rs485_stats_printer_logger = GenericStatsPrinterLogger(
        TESTER, tester_rs485_stats, (tabular_output == TESTER))
    dut_rs485_stats_printer_logger = GenericStatsPrinterLogger(
        DUT, dut_rs485_stats, (tabular_output == DUT))
    total_stats_printer_logger = GenericStatsPrinterLogger(
        TOTAL, total_stats, (tabular_output == TOTAL))
    stats_combiner_printer_logger = GenericStatsCombinerPrinterLogger(
        COMBINED, combined_stats, (tabular_output == COMBINED))

    tester_rs485_sync = WriterReceiverSync(TESTER, True)
    dut_rs485_sync = WriterReceiverSync(DUT, False)
    tester_rs485_sync.set_friend(dut_rs485_sync)
    dut_rs485_sync.set_friend(tester_rs485_sync)

    tester_rs485 = HalfDuplexSerial(TESTER, tester_port, baud, payload_size,
                                    tester_rs485_sync, [tester_rs485_stats, total_stats])
    dut_rs485 = HalfDuplexSerial(
        DUT, dut_port, baud, payload_size, dut_rs485_sync, [dut_rs485_stats, total_stats])

    all_devices = [tester_rs485, dut_rs485]
    all_helpers = [tester_rs485_stats_printer_logger, dut_rs485_stats_printer_logger,
                   total_stats_printer_logger, stats_combiner_printer_logger]
    if csv_writer:
        all_helpers.append(csv_writer)
    if dut_ppk2:
        all_devices.append(dut_ppk2)

    asyncio.run(task(all_devices, all_helpers))
