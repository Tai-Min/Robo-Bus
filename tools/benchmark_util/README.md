# TODO: rewrite examples and usages
# Benchmark runner

Python script to benchmark various hardware.

## Features

* Live command line tabular output with benchmark statistics
* Logging to CSV file
* Support for [Power Profiler Kit II](https://www.nordicsemi.com/Products/Development-hardware/Power-Profiler-Kit-2)

## Usage

```bash
usage: benchmark.py [-h] {dry,ping-pong} ...

Run various hardware benchmarks

positional arguments:
  {dry,ping-pong}  Benchmark type
    dry            Dry benchmark without any actual data transfer, used for testing the benchmark framework
    ping-pong      Ping Pong benchmark between two serial devices

options:
  -h, --help       show this help message and exit
```

### DRY

Do nothing benchmark. Somewhat minimal example of a benchmark implementation.

Example live output: (with `--use-ppk2`):
```
╒═════════════════════╤═══════╤══════════════╤══════════╕
│ Stats (DRY)         │ Sum   │ Per second   │ Newest   │
╞═════════════════════╪═══════╪══════════════╪══════════╡
│ Current consumption │ -     │ -            │ 45.57mA  │
╘═════════════════════╧═══════╧══════════════╧══════════╛
```

Without `--use-ppk2` this benchmark will return instantly.

Usage:

```bash
usage: benchmark.py ping-pong [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL,NOTSET}] [--log-file LOG_FILE] [--log-to-file | --no-log-to-file] [--log-to-stdout | --no-log-to-stdout]
                              [--csv-file CSV_FILE] [--write-to-csv | --no-write-to-csv] [--tabular-output {NoOutput,DUT,Tester,Total,Combined}] [--payload-size PAYLOAD_SIZE]
                              [--dut-serial DUT_SERIAL] [--tester-serial TESTER_SERIAL] [--baud BAUD] [--use-dut-ppk2 | --no-use-dut-ppk2]

options:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL,NOTSET}
                        Logging level. Not used if both --log-to-stdout and --log-to-file are set to False
  --log-file LOG_FILE   Log file path. Not used if --log-to-file is set to False
  --log-to-file, --no-log-to-file
                        Whether to log to file
  --log-to-stdout, --no-log-to-stdout
                        whether to log to stdout
  --csv-file CSV_FILE   CSV file path to write stats to. Not used if --write-to-csv is set to False
  --write-to-csv, --no-write-to-csv
                        Whether to log stats to CSV file
  --tabular-output {NoOutput,DUT,Tester,Total,Combined}
                        What to live output in tabular format to stdout. Not used if --log-stdout is set to True
  --payload-size PAYLOAD_SIZE
                        Size of the payload to generate and send
  --dut-serial DUT_SERIAL
                        Path to DUT serial device
  --tester-serial TESTER_SERIAL
                        Path to tester serial device
  --baud BAUD           Serial baud rate
  --use-dut-ppk2, --no-use-dut-ppk2
                        Whether to use PPK2 for DUT current measurements
```

### Ping-Pong

Send randomly generated payload between two half duplex serial devices.

Example live output (with `--use-dut-ppk2`):

```bash
╒══════════════════════╤═══════════════╤══════════════════╤════════════╤═══════════════╤═══════════════╤══════════════╤═════════════════╕
│ Stats (Combined)     │ Sum: Tester   │ FN/sec: Tester   │ Sum: DUT   │ FN/sec: DUT   │ Newest: DUT   │ Sum: Total   │ FN/sec: Total   │
╞══════════════════════╪═══════════════╪══════════════════╪════════════╪═══════════════╪═══════════════╪══════════════╪═════════════════╡
│ Success receive      │ 920           │ 226.39/s         │ 920        │ 226.41/s      │ -             │ 1840         │ 443.38/s        │
│ Timeout receive      │ 0             │ 0/s              │ 0          │ 0/s           │ -             │ 0            │ 0/s             │
│ Good bytes           │ 115.0KB       │ 28.3KB/s         │ 115.0KB    │ 28.3KB/s      │ -             │ 230.0KB      │ 55.42KB/s       │
│ Mangled bytes        │ 0.0B          │ 0.0B/s           │ 0.0B       │ 0.0B/s        │ -             │ 0.0B         │ 0.0B/s          │
│ Skipped bytes        │ 0.0B          │ 0.0B/s           │ 0.0B       │ 0.0B/s        │ -             │ 0.0B         │ 0.0B/s          │
│ Total desired bytes  │ 115.0KB       │ 28.3KB/s         │ 115.0KB    │ 28.3KB/s      │ -             │ 230.0KB      │ 55.42KB/s       │
│ Total received bytes │ 115.0KB       │ 28.3KB/s         │ 115.0KB    │ 28.3KB/s      │ -             │ 230.0KB      │ 55.42KB/s       │
│ Current consumption  │ -             │ -                │ -          │ -             │ 68.22mA       │ -            │ -               │
╘══════════════════════╧═══════════════╧══════════════════╧════════════╧═══════════════╧═══════════════╧══════════════╧═════════════════╛
```

Usage:

```bash
usage: benchmark.py ping-pong [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL,NOTSET}] [--log-file LOG_FILE] [--log-to-file | --no-log-to-file] [--log-to-stdout | --no-log-to-stdout] [--csv-file CSV_FILE] [--write-to-csv | --no-write-to-csv]
                              [--tabular-output {DUT,Tester,Total,Combined}] [--payload-size PAYLOAD_SIZE] [--dut-serial DUT_SERIAL] [--tester-serial TESTER_SERIAL] [--baud BAUD] [--use-dut-ppk2 | --no-use-dut-ppk2]

options:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL,NOTSET}
                        Logging level. Not used if both --log-to-stdout and --log-to-file are set to False
  --log-file LOG_FILE   Log file path. Not used if --log-to-file is set to False
  --log-to-file, --no-log-to-file
                        Whether to log to file
  --log-to-stdout, --no-log-to-stdout
                        whether to log to stdout
  --csv-file CSV_FILE   CSV file path to write stats to. Not used if --write-to-csv is set to False
  --write-to-csv, --no-write-to-csv
                        Whether to log stats to CSV file
  --tabular-output {DUT,Tester,Total,Combined}
                        What to live output in tabular format to stdout. Not used if --log-stdout is set to True
  --payload-size PAYLOAD_SIZE
                        Size of the payload to generate and send
  --dut-serial DUT_SERIAL
                        Path to DUT serial device
  --tester-serial TESTER_SERIAL
                        Path to tester serial device
  --baud BAUD           Serial baud rate
  --use-dut-ppk2, --no-use-dut-ppk2
                        Whether to use PPK2 for DUT current measurements
```
