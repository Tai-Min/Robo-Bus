"""
Main file. Parses command line arguments, sets up logging and runs the selected benchmark.
"""
import argparse
import os
import sys
import logging

from helpers.stats.csv_writer import CsvWriter
import benchmarks.dry_benchmark as dry_benchmark
import benchmarks.ping_pong_benchmark as ping_pong_benchmark


logger = logging.getLogger(__name__)


DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = "benchmark.log"
DEFAULT_CSV_FILE = "output.csv"

LOG_FORMAT = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"

CSV_WRITER = "CSV Writer"

DRY_BENCHMARK = "dry"
PING_PONG_BENCHMARK = "ping-pong"

benchmarks = {
    DRY_BENCHMARK: dry_benchmark,
    PING_PONG_BENCHMARK: ping_pong_benchmark
}


def log_stdout(level: int):
    """
    Enable logging to stdout.

    @param level: Log level.
    """
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logging.getLogger().addHandler(handler)


def set_log_level(level: int):
    """
    Set log level across the application.

    @param level: Log level.
    """
    # pylint: disable=no-member
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for curr_logger in loggers:
        curr_logger.setLevel(level)


def add_default_args(parser: argparse.ArgumentParser):
    """
    Add default command line arguments to parser.
    """
    parser.add_argument(
        "--log-level",
        type=str,
        default=DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"],
        help="Logging level. Not used if both --log-to-stdout and --log-to-file are set to False"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=DEFAULT_LOG_FILE,
        help="Log file path. Not used if --log-to-file is set to False"
    )
    parser.add_argument(
        "--log-to-file",
        action=argparse.BooleanOptionalAction,
        help="Whether to log to file"
    )
    parser.add_argument(
        "--log-to-stdout",
        action=argparse.BooleanOptionalAction,
        help="whether to log to stdout"
    )
    parser.add_argument(
        "--csv-file",
        type=str,
        default=DEFAULT_CSV_FILE,
        help="CSV file path to write stats to. Not used if --write-to-csv is set to False"
    )
    parser.add_argument(
        "--write-to-csv",
        action=argparse.BooleanOptionalAction,
        help="Whether to log stats to CSV file"
    )


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="Run various hardware benchmarks"
    )

    subparsers = parser.add_subparsers(dest="benchmark", help="Benchmark type")
    dry_parser = subparsers.add_parser(DRY_BENCHMARK,
                                       help="Dry benchmark without any actual data transfer, used for testing the benchmark framework")
    ping_pong_parser = subparsers.add_parser(PING_PONG_BENCHMARK,
                                             help="Half duplex ping-pong benchmark between two serial devices")
    subparsers_list = {
        DRY_BENCHMARK: dry_parser,
        PING_PONG_BENCHMARK: ping_pong_parser
    }

    for benchmark_name, benchmark_module in benchmarks.items():
        add_default_args(subparsers_list[benchmark_name])
        benchmark_module.add_args(subparsers_list[benchmark_name])

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    log_to_file = args.log_to_file
    log_file = args.log_file
    log_level = getattr(logging, args.log_level, DEFAULT_LOG_LEVEL)
    log_to_stdout = args.log_to_stdout

    write_to_csv = args.write_to_csv
    csv_file = args.csv_file

    if log_to_file:
        logging.basicConfig(filename=log_file, format=LOG_FORMAT)
    elif log_to_stdout: # Will log to stdout otherwise
        logging.basicConfig(format=LOG_FORMAT)

    set_log_level(log_level)

    # Additional log to stdout
    # if log to file is enabled
    if log_to_file and log_to_stdout:
        log_stdout(log_level)

    csv_writer = None
    if write_to_csv:
        csv_writer = CsvWriter(CSV_WRITER, csv_file, 1.0)

    if args.benchmark:
        logger.info("Running benchmark: %s", args.benchmark)
        benchmarks[args.benchmark].benchmark(args, csv_writer)
