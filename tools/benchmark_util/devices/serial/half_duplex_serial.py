"""
Provides implementation of HalfDuplexSerial class.
Write / read is managed by Sync object.
"""
import asyncio
import serial_asyncio
import logging
import random
import string

from devices.serial.serial_protocol import Protocol
from helpers.stats.data.serial_transfer_stats_history import SerialTransferStatsHistory
from devices.sync import WriterReceiverSync
from devices.abc_device import Device


logger = logging.getLogger(__name__)


class HalfDuplexSerial(Device):
    """
    Half duplex serial implementation. Writes dummy randomly generated data
    when is allowed by WriterReceiverSync object.
    """

    BAUD_RATE_MIN = 9600

    def __init__(self, name: str, port: str, baud: int, payload_size: int,
                 sync: WriterReceiverSync, stats: list[SerialTransferStatsHistory] = None,
                 priority: int = 999):
        """
        Constructor.

        @param name: Name of the serial device.
        @param port: Serial port to use.
        @param baud: Baud rate to use.
        @param payload_size: Size of the payload to generate and send.
        @param sync: Sync object to control the write/receive flow.
        @param stats: Stats object to report stats to.
        @param priority: Priority of the device. Devices with lower priority will be started first.
        """

        if port is None or port == "":
            e = f"{name}: Port must be specified"
            logger.error(e)
            raise ValueError(e)

        if baud < self.BAUD_RATE_MIN:
            e = f"{name}: Baud rate minimum is {self.BAUD_RATE_MIN}"
            logger.error(e)
            raise ValueError(e)

        if payload_size <= 0:
            e = f"{name}: Payload size must be bigger than 0"
            logger.error(e)
            raise ValueError(e)

        super().__init__(name, priority)
        logger.debug("%s: Init", name)
        self._stats = stats
        self._port = port
        self._baud = baud
        self._payload_size = payload_size

        self._payload_time = (self._payload_size * 8) / self._baud
        self._byte_time = self._payload_time / self._payload_size

        self._writer_receiver_sync = sync
        if self._writer_receiver_sync is not None:
            self._writer_receiver_sync.set_writer_role_timeout(self._payload_time * 2)

        self._protocol: Protocol = None
        self._reader_task: asyncio.Task = None
        self._current_payload = b""
        self._exit_flag = asyncio.Event()
        self._writer_stopped_flag = asyncio.Event()
        self._writer_stopped_flag.set()


    def _generate_payload(self) -> bytes:
        """
        Generate random payload of specified size.

        @return Random payload.
        """
        res = "".join(random.choices(string.ascii_uppercase + string.digits, k=self._payload_size))
        return res.encode()


    def _data_received(self, payload: bytes):
        """
        Called by protocol when it receives a complete data transfer.

        @param bytes: Bytes received by protocol.
        """
        logger.debug("%s: Received: %s", self._name, payload)
        self._writer_receiver_sync.notify_friend_delivered(payload)


    def _rate_delivered_payload(self):
        """
        Rate delivered payload.
        """
        if self._stats is None:
            return

        for stat in self._stats:
            stat.rate_payload(self._current_payload.decode(errors="ignore"), \
                              self._writer_receiver_sync.get_last_payload().decode(errors="ignore"))
            stat.add_success_receive()


    def _rate_timeout_payload(self):
        """
        Rate timeout payload.
        """
        if self._stats is None:
            return

        for stat in self._stats:
                    stat.add_timeout_receive()


    async def open(self) -> bool:
        """
        Open serial port and start reading.
        """
        logger.debug("%s: Opening serial port port=%s baud=%s", self._name, self._port, self._baud)
        try:
            _, self._protocol = await serial_asyncio.create_serial_connection( \
            asyncio.get_running_loop(), Protocol, self._port, baudrate=self._baud)
        # pylint: disable=broad-except
        except Exception as e:
            logger.error("%s: Failed to open serial port: %s", self._name, e)
            raise ConnectionError(f"{self._name}: Failed to open serial port: {self._port}") from e
        self._protocol.set_data_callback(self._data_received)
        self._protocol.set_name(self._name)
        self._protocol.set_expected_payload_size(self._payload_size)
        self._protocol.set_silence_time(self._byte_time * 10)
        self._reader_task = asyncio.get_running_loop().create_task(self._protocol.loop_reader())
        return True


    async def loop(self):
        """
        Endlessly wait for it's turn to write -> write data -> \
        wait for receive notify or timeout, collect stats.
        """
        self._writer_stopped_flag.clear()
        logger.info("%s: Starting serial writer loop", self._name)

        while not self._exit_flag.is_set():
            logger.debug("%s: Waiting for my turn...", self._name)
            await self._writer_receiver_sync.wait_for_writer_role()

            logger.debug("%s: Writing payload", self._name)
            self._current_payload = self._generate_payload()
            self._protocol.data_write(self._current_payload)

            logger.debug("%s: Waiting for delivery...", self._name)
            await self._writer_receiver_sync.wait_for_delivery()

            if self._writer_receiver_sync.is_delivered():
                logger.debug("%s: Friend has received the payload, \
                             giving up writer role to friend", self._name)

                self._rate_delivered_payload()

                self._writer_receiver_sync.pass_writer_role_to_friend()
            else:
                logger.debug("%s: Payload not delivered, retrying", self._name)

                self._rate_timeout_payload()

        logger.info("%s: Stopping serial writer loop", self._name)
        self._writer_stopped_flag.set()


    async def stop(self):
        """
        Stop the serial.
        """
        logger.info("%s: Stopping serial", self._name)
        self._exit_flag.set()

        if not self._writer_stopped_flag.is_set():
            logger.debug("%s: Waiting for writer loop to stop...", self._name)
            await self._writer_stopped_flag.wait()

        if self._protocol:
            logger.debug("%s: Stopping protocol", self._name)
            await self._protocol.stop()

        logger.info("%s: Stopped", self._name)
