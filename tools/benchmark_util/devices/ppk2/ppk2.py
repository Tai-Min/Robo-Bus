"""
Implements Power Profiler Kit 2 device for current measurements.
"""
import asyncio
import logging
from collections.abc import Awaitable, Callable
from ppk2_api.ppk2_api import PPK2_API
from devices.abc_device import Device
from helpers.stats.csv_writer import CsvWriter
from helpers.stats.data.unit import Unit


logger = logging.getLogger(__name__)


class PPK2(Device):
    """
    Power Profiler Kit 2 device for current measurements.
    """

    DUT_MIN_VOLTAGE_MV = 800
    DUT_MAX_VOLTAGE_MV = 5000
    DUT_ON = "ON"
    DUT_OFF = "OFF"


    def __init__(self, name: str, dut_voltage: int, reading_period: float,
                 csv_writer: CsvWriter, wait_dut_fn: Callable[[], Awaitable[bool]], **kwargs):
        """
        Constructor.

        @param name: Name of the PPK2 device.
        @param dut_voltage: Voltage to power on DUT .
        @param reading_period: How frequently poll for current readings in seconds.
        @param csv_writer: CSV writer object.
        @param wait_dut_fn: Function that the PPK2 helper will call on connect to wait for DUT state to stabilize.
        @param args: Arguments to pass to wait_dut_fn.
        """
        if dut_voltage < self.DUT_MIN_VOLTAGE_MV or \
            dut_voltage > self.DUT_MAX_VOLTAGE_MV:
            e = f"{name}: DUT voltage ({dut_voltage}) is not within allowed range ({self.DUT_MIN_VOLTAGE_MV}, {self.DUT_MAX_VOLTAGE_MV})"
            logger.error(e)
            raise ValueError(e)

        if reading_period <= 0:
            e = f"{name}: Reading perios must be greater than zero, {reading_period} provided"
            logger.error(e)
            raise ValueError(e)

        super().__init__(name, priority=0)
        logger.debug("%s: Init", name)
        self._dut_voltage = dut_voltage
        self.reading_period = reading_period
        self._ppk2: PPK2_API = None
        self._wait_dut_fn = wait_dut_fn
        self._wait_dut_fn_params = kwargs
        self._csv_writer = csv_writer
        self._measurement = Unit(self._name, "Current consumption", "microamps", self._csv_writer)
        self._connected = False
        self._loop_stopped_flag = asyncio.Event()
        self._loop_stopped_flag.set()
        self._exit_flag = asyncio.Event()


    def get_measurement(self) -> Unit:
        """
        Get current measurement Unit object.

        @return Current measurement Unit object.
        """
        return self._measurement


    async def open(self) -> bool:
        """
        Connect to the PPK2, enable DUT and start measurements.
        """
        ppk2s_connected = PPK2_API.list_devices()
        ppk2_port = None
        if len(ppk2s_connected) == 1:
            ppk2_port = ppk2s_connected[0]
            logger.info("%s: Found PPK2 device on port %s", self._name, ppk2_port)
        else:
            logger.error("%s: Expected to find 1 PPK2 device, but found %d",
                          self._name, len(ppk2s_connected))
            return False

        self._ppk2 = PPK2_API(ppk2_port, timeout=1, write_timeout=1, exclusive=True)
        self._ppk2.get_modifiers()
        self._ppk2.set_source_voltage(self._dut_voltage)
        self._ppk2.use_source_meter()

        logger.info("%s: Turning on power and starting measurements...", self._name)
        self._ppk2.toggle_DUT_power(self.DUT_ON)
        self._ppk2.start_measuring()

        if self._wait_dut_fn is not None:
            logger.info("%s: Waiting for DUT to power on and stabilize...", self._name)

            if not await self._wait_dut_fn(self._wait_dut_fn_params):
                logger.error("%s: DUT detection timeout", self._name)
                raise ConnectionError("{self._name}: DUT detection timeout")

            logger.info("%s: Waiting done", self._name)
        self._connected = True
        return True

    async def loop(self):
        """
        Loop current readings.
        """
        self._loop_stopped_flag.clear()

        while not self._exit_flag.is_set():
            read_data = self._ppk2.get_data()
            if read_data != b"":
                samples = self._ppk2.get_samples(read_data)
                if len(samples) == 0 or len(samples[0]) == 0:
                    continue
                reading = sum(samples[0])/len(samples[0])
                self._measurement.update_value(reading)
            await asyncio.sleep(self.reading_period)

        self._loop_stopped_flag.set()

    async def stop(self):
        """
        Stop the PPK2 device.
        """
        logger.info("%s: Stopping PPK2", self._name)

        self._exit_flag.set()

        if not self._loop_stopped_flag.is_set():
            await self._loop_stopped_flag.wait()

        if self._connected:
            self._ppk2.stop_measuring()
            self._ppk2.toggle_DUT_power(self.DUT_OFF)

        logger.info("%s: PPK2 stopped", self._name)
